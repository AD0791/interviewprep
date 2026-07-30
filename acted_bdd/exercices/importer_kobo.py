#!/usr/bin/env python3
# Gist: importer_kobo.py
#
# Use Case  : chaine d'import d'un export KoboToolbox brut vers la base projet ACTED.
# Purpose   : montrer une ingestion defendable : on normalise, on valide, on deduplique,
#             on charge ce qui passe, et on archive dans une table de rejets tout ce qui
#             ne passe pas — avec le motif. Rien n'est jete silencieusement.
# Key points: reconciliation ligne a ligne (lues = chargees + rejetees + doublons),
#             idempotence (relancer l'import ne cree pas de doublon),
#             journal d'import horodate exploitable dans un rapport de qualite.
#
# Execution : python3 importer_kobo.py export_kobo_pdm_brut.csv acted_bdd.db

import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime

# --------------------------------------------------------------------------------------
# 1. Normalisation — transformer une valeur brute en valeur exploitable, ou en None
# --------------------------------------------------------------------------------------

# Table d'harmonisation des libelles de commune. Elle est explicite et versionnee :
# une correspondance devinee par un algorithme flou n'est jamais auditable.
CORRESPONDANCE_COMMUNES = {
    "gonaives": "Gonaives", "gonaive": "Gonaives", "gonayiv": "Gonaives",
    "saintmarc": "Saint-Marc", "stmarc": "Saint-Marc",
    "dessalines": "Dessalines", "dessaline": "Dessalines",
    "grosmorne": "Gros-Morne", "verrettes": "Verrettes",
    "portauprince": "Port-au-Prince", "croixdesbouquets": "Croix-des-Bouquets",
    "leogane": "Leogane", "mirebalais": "Mirebalais", "caphaitien": "Cap-Haitien",
}

ACCENTS = str.maketrans("àáâãäçèéêëìíîïñòóôõöùúûüÿ", "aaaaaceeeeiiiinooooouuuuy")


def cle_normalisee(texte):
    """Reduit un libelle a sa forme comparable : minuscules, sans accent ni separateur."""
    if texte is None:
        return ""
    t = texte.strip().lower().translate(ACCENTS)
    return re.sub(r"[^a-z0-9]", "", t)


def normaliser_commune(valeur):
    return CORRESPONDANCE_COMMUNES.get(cle_normalisee(valeur))


def normaliser_date(valeur):
    """Accepte les trois formats rencontres sur le terrain, refuse le reste."""
    if not valeur:
        return None
    for gabarit in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(valeur.strip(), gabarit).date().isoformat()
        except ValueError:
            continue
    return None


def normaliser_entier(valeur, mini=None, maxi=None):
    """Retire les separateurs de milliers et les unites collees, puis borne."""
    if valeur is None:
        return None
    t = str(valeur).strip().replace(" ", "").replace(" ", "").replace(",", "")
    t = re.sub(r"[^0-9.\-]", "", t)
    if t in ("", "-", "."):
        return None
    try:
        n = int(float(t))
    except ValueError:
        return None
    if mini is not None and n < mini:
        return None
    if maxi is not None and n > maxi:
        return None
    return n


def normaliser_decimal(valeur, mini=None, maxi=None):
    if valeur is None:
        return None
    t = str(valeur).strip().replace(",", ".")
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        return None
    x = float(t)
    if mini is not None and x < mini:
        return None
    if maxi is not None and x > maxi:
        return None
    return x


def normaliser_telephone(valeur):
    """Un numero haitien valide compte 8 chiffres apres l'indicatif +509."""
    if not valeur:
        return None
    chiffres = re.sub(r"\D", "", valeur)
    if chiffres.startswith("509"):
        chiffres = chiffres[3:]
    return f"+509{chiffres}" if len(chiffres) == 8 else None


def normaliser_oui_non(valeur):
    return {"oui": 1, "wi": 1, "yes": 1, "1": 1,
            "non": 0, "no": 0, "0": 0}.get(cle_normalisee(valeur))


# --------------------------------------------------------------------------------------
# 2. Validation — regles metier qui decident si une ligne entre dans la base
# --------------------------------------------------------------------------------------

def valider(ligne, menages_connus):
    """Retourne (enregistrement, motifs_de_rejet). Une ligne peut cumuler les motifs."""
    motifs = []

    code = (ligne.get("code_menage") or "").strip()
    if not re.fullmatch(r"MEN-\d{5}", code):
        motifs.append("code_menage malforme")
    elif code not in menages_connus:
        motifs.append("code_menage inconnu de la base")

    date_enquete = normaliser_date(ligne.get("date_enquete"))
    if date_enquete is None:
        motifs.append("date_enquete illisible")

    satisfaction = normaliser_entier(ligne.get("satisfaction"), 1, 5)
    if satisfaction is None:
        motifs.append("satisfaction hors echelle 1-5 ou non numerique")

    montant = normaliser_entier(ligne.get("montant_recu_htg"), 0, 50000)
    if montant is None:
        motifs.append("montant_recu_htg non numerique")

    fcs = normaliser_decimal(ligne.get("score_fcs"), 0, 112)
    if fcs is None:
        motifs.append("score_fcs absent ou hors bornes 0-112")

    rcsi = normaliser_entier(ligne.get("score_rcsi"), 0, 56)
    delai = normaliser_entier(ligne.get("delai_reception_jours"), 0, 180)
    commune = normaliser_commune(ligne.get("commune"))
    if commune is None:
        motifs.append("libelle de commune non reconnu")

    # Un entretien PDM complet ne peut pas durer moins de huit minutes : en dessous,
    # l'hypothese la plus probable est que l'enqueteur a rempli le formulaire sans
    # poser les questions. La ligne part en rejet pour verification, pas a la poubelle.
    duree = normaliser_entier(ligne.get("duree_entretien_min"), 0, 600)
    if duree is not None and duree < 8:
        motifs.append("duree d entretien inferieure a 8 minutes")

    latitude = normaliser_decimal(ligne.get("gps_latitude"), 17.5, 20.5)
    longitude = normaliser_decimal(ligne.get("gps_longitude"), -75.0, -71.5)

    enregistrement = {
        "code_menage": code, "date_enquete": date_enquete,
        "enqueteur": (ligne.get("enqueteur") or "").strip(),
        "satisfaction": satisfaction, "delai_reception_jours": delai,
        "montant_recu_htg": montant,
        "utilisation_principale": (ligne.get("utilisation_principale") or "").strip() or None,
        "connait_mecanisme_plainte": normaliser_oui_non(ligne.get("connait_mecanisme_plainte")),
        "score_fcs": fcs, "score_rcsi": rcsi,
        "latitude": latitude, "longitude": longitude,
        "commune_normalisee": commune,
        "telephone_normalise": normaliser_telephone(ligne.get("telephone")),
        "duree_entretien_min": duree,
    }
    return enregistrement, motifs


def completude(enregistrement):
    """Nombre de champs renseignes — sert de regle de conservation entre doublons."""
    return sum(1 for v in enregistrement.values() if v not in (None, ""))


# --------------------------------------------------------------------------------------
# 3. Chargement
# --------------------------------------------------------------------------------------

def importer(chemin_csv, chemin_db):
    con = sqlite3.connect(chemin_db)
    con.execute("PRAGMA foreign_keys = ON")
    menages = {r[0]: r[1] for r in
               con.execute("SELECT code_menage, id_menage FROM menages").fetchall()}

    lues = 0
    valides, rejets = [], []
    for ligne in csv.DictReader(open(chemin_csv, encoding="utf-8")):
        lues += 1
        enregistrement, motifs = valider(ligne, menages)
        if motifs:
            rejets.append((ligne, motifs))
        else:
            valides.append((ligne.get("uuid"), enregistrement))

    # Deduplication sur la cle metier : un menage, une date d'enquete.
    # On conserve la soumission la plus complete, comme le ferait un agent qui
    # arbitre entre deux versions du meme formulaire renvoye apres coupure reseau.
    meilleurs = {}
    doublons = 0
    for uuid, e in valides:
        cle = (e["code_menage"], e["date_enquete"])
        if cle in meilleurs:
            doublons += 1
            if completude(e) > completude(meilleurs[cle][1]):
                meilleurs[cle] = (uuid, e)
        else:
            meilleurs[cle] = (uuid, e)

    # Insertion idempotente : relancer l'import ne cree pas de seconde ligne,
    # grace a la contrainte UNIQUE(id_menage, date_enquete) et a ON CONFLICT.
    charges = 0
    for uuid, e in meilleurs.values():
        cur = con.execute("""
            INSERT INTO pdm_reponses
              (id_menage, date_enquete, enqueteur, satisfaction, delai_reception_jours,
               montant_recu_htg, utilisation_principale, connait_mecanisme_plainte,
               score_fcs, score_rcsi, latitude, longitude)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id_menage, date_enquete) DO NOTHING
        """, (menages[e["code_menage"]], e["date_enquete"], e["enqueteur"],
              e["satisfaction"], e["delai_reception_jours"], e["montant_recu_htg"],
              e["utilisation_principale"], e["connait_mecanisme_plainte"],
              e["score_fcs"], e["score_rcsi"], e["latitude"], e["longitude"]))
        charges += cur.rowcount if cur.rowcount > 0 else 0

    horodatage = datetime.now().isoformat(timespec="seconds")
    for ligne, motifs in rejets:
        con.execute("""INSERT INTO rejets (table_source, cle_source, contenu, motif_rejet, date_rejet)
                       VALUES (?,?,?,?,?)""",
                    ("staging_kobo_pdm", ligne.get("uuid"),
                     json.dumps(ligne, ensure_ascii=False), " ; ".join(motifs), horodatage))
    con.commit()

    # --- Rapport de reconciliation ---------------------------------------------------
    print(f"Lignes lues dans l'export         : {lues}")
    print(f"  rejetees (motif documente)      : {len(rejets)}")
    print(f"  doublons ecartes (meme cle)     : {doublons}")
    print(f"  retenues apres deduplication    : {len(meilleurs)}")
    print(f"  effectivement inserees          : {charges}")
    print(f"  deja presentes (import rejoue)  : {len(meilleurs) - charges}")
    ecart = lues - (len(rejets) + doublons + len(meilleurs))
    print(f"Controle : lues - rejets - doublons - retenues = {ecart} (doit valoir 0)")

    print("\nMotifs de rejet par frequence :")
    compteur = Counter(m for _l, ms in rejets for m in ms)
    for motif, n in compteur.most_common():
        print(f"  {n:>4}  {motif}")

    # Harmonisation : combien de graphies distinctes l'export contenait-il, et combien
    # de communes reelles se cachaient derriere ? C'est l'indicateur qui justifie
    # aupres du responsable MEAL le temps passe a maintenir la table de correspondance.
    brutes = Counter()
    for ligne in csv.DictReader(open(chemin_csv, encoding="utf-8")):
        brutes[(ligne.get("commune") or "").strip()] += 1
    harmonisees = {normaliser_commune(b) for b in brutes if normaliser_commune(b)}
    print(f"\nHarmonisation des libelles de commune : {len(brutes)} graphies distinctes "
          f"ramenees a {len(harmonisees)} communes.")
    con.close()


if __name__ == "__main__":
    csv_source = sys.argv[1] if len(sys.argv) > 1 else "export_kobo_pdm_brut.csv"
    base = sys.argv[2] if len(sys.argv) > 2 else "acted_bdd.db"
    importer(csv_source, base)
