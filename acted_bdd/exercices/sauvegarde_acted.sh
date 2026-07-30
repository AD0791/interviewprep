#!/usr/bin/env bash
# Gist: sauvegarde_acted.sh
#
# Use Case  : sauvegarde quotidienne de la base projet ACTED sur un poste de bureau terrain.
# Purpose   : produire une copie coherente, compressee, horodatee et verifiee, avec
#             rotation automatique et journal d'execution.
# Key points : copie a chaud via `sqlite3 .backup` (jamais `cp` sur une base ouverte),
#             empreinte SHA-256, restauration de controle, retention 14 jours + 12 mois,
#             sortie journalisee pour pouvoir prouver au bailleur que la sauvegarde tourne.
#
# Usage : ./sauvegarde_acted.sh /chemin/acted_bdd.db /chemin/sauvegardes
# Cron  : 0 19 * * *  /srv/acted/sauvegarde_acted.sh /srv/acted/acted_bdd.db /srv/acted/sauvegardes

set -euo pipefail

BASE="${1:?Usage: $0 <base.db> <dossier_sauvegardes>}"
DEST="${2:?Usage: $0 <base.db> <dossier_sauvegardes>}"
HORODATAGE="$(date +%Y%m%d_%H%M%S)"
JOUR="$(date +%Y%m%d)"
NOM="acted_bdd_${HORODATAGE}"
JOURNAL="${DEST}/journal_sauvegarde.log"

mkdir -p "${DEST}/quotidien" "${DEST}/mensuel"

journaliser() {
  printf '%s | %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" | tee -a "${JOURNAL}"
}

journaliser "DEBUT sauvegarde de ${BASE}"

# 1. Controle d'integrite AVANT de sauvegarder : sauvegarder une base corrompue
#    revient a propager la corruption dans toutes les copies de la rotation.
INTEGRITE="$(sqlite3 "${BASE}" 'PRAGMA integrity_check;')"
if [ "${INTEGRITE}" != "ok" ]; then
  journaliser "ECHEC integrite : ${INTEGRITE}"
  exit 1
fi
journaliser "Integrite verifiee : ok"

# 2. Copie a chaud. La commande .backup de SQLite prend un verrou coherent et
#    fonctionne meme si une application ecrit pendant l'operation, ce que `cp` ne
#    garantit pas. L'equivalent PostgreSQL est pg_dump, l'equivalent MySQL mysqldump.
sqlite3 "${BASE}" ".backup '${DEST}/quotidien/${NOM}.db'"
journaliser "Copie creee : ${NOM}.db"

# 3. Dump logique en parallele : lisible, diffable, restaurable sur une autre version
#    du moteur. La copie binaire est rapide, le dump texte est portable — on garde les deux.
sqlite3 "${BASE}" .dump | gzip -9 > "${DEST}/quotidien/${NOM}.sql.gz"
journaliser "Dump logique compresse : ${NOM}.sql.gz"

# 4. Empreinte : permet de prouver plus tard que le fichier restaure est bien
#    celui qui a ete sauvegarde, et de detecter une alteration silencieuse du disque.
( cd "${DEST}/quotidien" && sha256sum "${NOM}.db" "${NOM}.sql.gz" >> "empreintes_${JOUR}.sha256" )
journaliser "Empreintes SHA-256 enregistrees"

# 5. Restauration de controle. Une sauvegarde jamais restauree n'est pas une
#    sauvegarde : on la remonte dans un fichier temporaire et on recompte les lignes.
TEMPO="$(mktemp -d)"
gunzip -c "${DEST}/quotidien/${NOM}.sql.gz" | sqlite3 "${TEMPO}/controle.db"
SRC_MENAGES="$(sqlite3 "${BASE}" 'SELECT COUNT(*) FROM menages;')"
DST_MENAGES="$(sqlite3 "${TEMPO}/controle.db" 'SELECT COUNT(*) FROM menages;')"
if [ "${SRC_MENAGES}" != "${DST_MENAGES}" ]; then
  journaliser "ECHEC restauration de controle : ${SRC_MENAGES} vs ${DST_MENAGES} menages"
  rm -rf "${TEMPO}"
  exit 1
fi
journaliser "Restauration de controle reussie : ${DST_MENAGES} menages"
rm -rf "${TEMPO}"

# 6. Archive mensuelle : le 1er du mois, la copie du jour est promue en archive longue duree.
if [ "$(date +%d)" = "01" ]; then
  cp "${DEST}/quotidien/${NOM}.sql.gz" "${DEST}/mensuel/"
  journaliser "Archive mensuelle creee"
fi

# 7. Rotation : 14 jours en quotidien, 12 mois en mensuel.
find "${DEST}/quotidien" -type f -mtime +14 -delete
find "${DEST}/mensuel"  -type f -mtime +365 -delete
journaliser "Rotation appliquee (14 jours / 365 jours)"

# 8. Rappel de la regle 3-2-1 : la copie locale ne suffit pas. Le miroir hors site
#    (disque chiffre emporte au bureau de coordination, ou espace cloud du siege)
#    doit etre declenche ici, apres validation, jamais avant.
journaliser "FIN sauvegarde — penser a la synchronisation hors site"
