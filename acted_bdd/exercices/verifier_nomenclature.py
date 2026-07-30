#!/usr/bin/env python3
# Gist: verifier_nomenclature.py
#
# Use Case  : auditer un dossier partage de projet et signaler les fichiers qui ne
#             respectent pas la nomenclature convenue.
# Purpose   : rendre une regle de classement executable plutot que declarative. Une
#             convention que personne ne verifie n'est pas une convention.
# Key points: detection des versions concurrentes (final, FINAL_v2, copie de...),
#             des dates non normalisees, des espaces et accents, et surtout des
#             fichiers potentiellement nominatifs poses hors du dossier protege.
#
# Execution : python3 verifier_nomenclature.py /chemin/du/dossier
#
# Nomenclature attendue :
#   AAAAMMJJ_PROJET_TYPE_DESCRIPTION_vN.ext
#   ex. 20260315_PRJ-SECAL-24_PDM_rapport-mensuel_v2.xlsx

import os
import re
import sys
from collections import defaultdict

GABARIT = re.compile(
    r"^(?P<date>\d{8})_"
    r"(?P<projet>[A-Z0-9\-]+)_"
    r"(?P<type>[A-Z]+)_"
    r"(?P<description>[a-z0-9\-]+)"
    r"(?:_v(?P<version>\d+))?"
    r"\.(?P<extension>[a-z0-9]+)$"
)

TYPES_ATTENDUS = {"CIBLAGE", "PDM", "DISTRIB", "RAPPORT", "BASE", "FORM", "SAUV", "PLAINTE"}

MOTS_INTERDITS = ["final", "FINAL", "definitif", "vrai", "copie", "copy", "nouveau",
                  "dernier", "bis", "ok", "corrige2"]

# Un fichier dont le nom evoque une liste nominative ne doit pas se trouver ailleurs
# que dans le dossier a acces restreint. Le controle est grossier et volontairement
# large : mieux vaut une alerte de trop qu'une liste de beneficiaires dans un dossier partage.
INDICES_NOMINATIFS = ["beneficiaire", "menage", "liste", "nominatif", "contact",
                      "telephone", "identite", "plainte"]
DOSSIER_PROTEGE = "05_donnees_restreintes"


def auditer(racine):
    anomalies = defaultdict(list)
    total = 0
    familles = defaultdict(list)

    for dossier, _sous_dossiers, fichiers in os.walk(racine):
        for nom in fichiers:
            if nom.startswith("."):
                continue
            total += 1
            chemin_relatif = os.path.relpath(os.path.join(dossier, nom), racine)

            correspondance = GABARIT.match(nom)
            if not correspondance:
                anomalies["nom non conforme au gabarit"].append(chemin_relatif)
            else:
                if correspondance.group("type") not in TYPES_ATTENDUS:
                    anomalies["type de document inconnu"].append(chemin_relatif)
                # Regroupement par famille pour reperer les versions concurrentes
                cle = (correspondance.group("date"), correspondance.group("projet"),
                       correspondance.group("type"), correspondance.group("description"))
                familles[cle].append(chemin_relatif)

            minuscule = nom.lower()
            if any(mot.lower() in minuscule for mot in MOTS_INTERDITS):
                anomalies["versionnage improvise (final, copie, vrai...)"].append(chemin_relatif)
            if " " in nom:
                anomalies["espace dans le nom"].append(chemin_relatif)
            if any(ord(c) > 127 for c in nom):
                anomalies["caractere accentue ou special"].append(chemin_relatif)
            if (any(indice in minuscule for indice in INDICES_NOMINATIFS)
                    and DOSSIER_PROTEGE not in chemin_relatif):
                anomalies["fichier potentiellement nominatif hors dossier restreint"].append(
                    chemin_relatif)

    for cle, chemins in familles.items():
        if len(chemins) > 1:
            anomalies["versions concurrentes du meme document"].extend(sorted(chemins))

    print(f"Dossier audite : {racine}")
    print(f"Fichiers examines : {total}\n")
    if not anomalies:
        print("Aucune anomalie. La nomenclature est respectee.")
        return 0
    for motif in sorted(anomalies):
        chemins = anomalies[motif]
        print(f"{len(chemins):>4}  {motif}")
        for c in sorted(chemins)[:6]:
            print(f"        {c}")
        if len(chemins) > 6:
            print(f"        ... et {len(chemins) - 6} autre(s)")
        print()
    return len(anomalies)


if __name__ == "__main__":
    auditer(sys.argv[1] if len(sys.argv) > 1 else ".")
