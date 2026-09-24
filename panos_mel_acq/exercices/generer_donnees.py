"""
Génère panos_iit.db : un jeu de données FICTIF de traçage des patients en
interruption de traitement (IIT), pour le module 02 de la piste Panos.

Rien ici ne vient d'un vrai programme. Les sites, les codes patients et les
volumes sont inventés ; seule la mécanique est réaliste :

  - un extrait de dispensations d'ARV façon iSanté Plus, avec multi-mois (MMD)
    et des patients qui vont chercher leurs ARV sur un AUTRE site ;
  - une liste IIT produite site par site, à partir des seules dispensations du
    site — ce qui fabrique de « faux IIT » pour les patients servis ailleurs ;
  - des visites de traçage saisies par les relais, avec trois défauts injectés
    exprès : codes patients mal saisis, visites en double, retours déclarés
    qu'aucune dispensation ne confirme.

Déterministe : même graine, même base. Relancer avec
    python3 generer_donnees.py
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

GRAINE = 2026
DATE_LISTE = date(2026, 6, 1)          # date de production de la liste IIT
DEBUT_HISTO = date(2025, 1, 1)
FIN_HISTO = date(2026, 7, 31)          # fin de l'extrait de dispensations
SEUIL_IIT = 28                          # jours au-delà du dernier contact attendu

SITES = [
    ("PV01", "Pétion-Ville", "Ouest"),
    ("DL02", "Delmas", "Ouest"),
    ("CH03", "Cap-Haïtien", "Nord"),
    ("LM04", "Limonade", "Nord"),
    ("CY05", "Les Cayes", "Sud"),
    ("TO06", "Torbeck", "Sud"),
]
AGENTS = [f"R{n:02d}" for n in range(1, 13)]   # douze relais communautaires

rng = random.Random(GRAINE)
chemin = Path(__file__).with_name("panos_iit.db")
if chemin.exists():
    chemin.unlink()
db = sqlite3.connect(chemin)
db.executescript(
    """
    CREATE TABLE sites (
        code_site    TEXT PRIMARY KEY,
        commune      TEXT NOT NULL,
        departement  TEXT NOT NULL
    );
    CREATE TABLE patients (
        code_patient   TEXT PRIMARY KEY,   -- identifiant national, ex. PV01-00123
        site_rattache  TEXT NOT NULL REFERENCES sites(code_site),
        sexe           TEXT NOT NULL CHECK (sexe IN ('F','M')),
        age            INTEGER NOT NULL,
        date_debut_tar TEXT NOT NULL
    );
    -- Extrait façon iSanté Plus : une ligne par dispensation d'ARV.
    CREATE TABLE dispensations (
        code_patient      TEXT NOT NULL REFERENCES patients(code_patient),
        site_dispensation TEXT NOT NULL REFERENCES sites(code_site),
        date_dispensation TEXT NOT NULL,
        jours_fournis     INTEGER NOT NULL
    );
    -- Liste IIT produite par chaque site à partir de SES dispensations.
    CREATE TABLE liste_iit (
        code_patient          TEXT NOT NULL REFERENCES patients(code_patient),
        site                  TEXT NOT NULL REFERENCES sites(code_site),
        date_listage          TEXT NOT NULL,
        dernier_contact_prevu TEXT NOT NULL
    );
    -- Saisie des relais : le code est tapé à la main, d'où les défauts.
    CREATE TABLE visites_tracage (
        visite_id            INTEGER PRIMARY KEY,
        code_patient_saisi   TEXT NOT NULL,
        agent                TEXT NOT NULL,
        date_visite          TEXT NOT NULL,
        resultat             TEXT NOT NULL CHECK (resultat IN
                               ('joint','non_joint','decede','transfere','refus')),
        retour_declare       INTEGER NOT NULL CHECK (retour_declare IN (0,1)),
        date_retour_declaree TEXT
    );
    """
)
db.executemany("INSERT INTO sites VALUES (?,?,?)", SITES)


def jour_aleatoire(debut: date, fin: date) -> date:
    return debut + timedelta(days=rng.randint(0, (fin - debut).days))


# ---------------------------------------------------------------- patients
patients = []
compteur = {code: 0 for code, _, _ in SITES}
for _ in range(900):
    site = rng.choice(SITES)[0]
    compteur[site] += 1
    code = f"{site}-{compteur[site]:05d}"
    debut_tar = jour_aleatoire(date(2019, 1, 1), date(2026, 2, 28))
    patients.append((code, site, rng.choice("FFFM"), rng.randint(15, 64), debut_tar))
db.executemany(
    "INSERT INTO patients VALUES (?,?,?,?,?)",
    [(c, s, sx, a, d.isoformat()) for c, s, sx, a, d in patients],
)

# ----------------------------------------------------------- dispensations
disp = []
servis_ailleurs = {}      # patient -> site où il se sert depuis un déplacement
interrompus = set()
for code, site, _, _, debut_tar in patients:
    jour = max(debut_tar, DEBUT_HISTO) + timedelta(days=rng.randint(0, 20))
    site_courant = site
    # 2 % des patients basculent sur un autre site (déplacement, insécurité).
    date_bascule = None
    if rng.random() < 0.02:
        date_bascule = jour_aleatoire(date(2025, 9, 1), date(2026, 3, 31))
        autres = [s for s, _, _ in SITES if s != site]
        servis_ailleurs[code] = rng.choice(autres)
    while jour <= FIN_HISTO:
        if date_bascule and jour >= date_bascule:
            site_courant = servis_ailleurs[code]
        anciennete = (jour - debut_tar).days
        jours = 90 if anciennete > 180 and rng.random() < 0.6 else 30
        disp.append((code, site_courant, jour.isoformat(), jours))
        # 4 % de risque d'interruption à chaque dispensation.
        if rng.random() < 0.04:
            interrompus.add(code)
            break
        jour = jour + timedelta(days=jours + rng.randint(-3, 10))

# --------------------------------------------------------------- liste IIT
# Chaque site ne voit que ses propres dispensations : c'est la source des
# faux IIT pour les patients servis ailleurs.
derniers = {}
for code, site_disp, jour, jours in disp:
    rattache = code[:4]
    if site_disp != rattache or date.fromisoformat(jour) >= DATE_LISTE:
        continue
    fin_couverture = date.fromisoformat(jour) + timedelta(days=jours)
    if code not in derniers or fin_couverture > derniers[code]:
        derniers[code] = fin_couverture

liste = []
for code, prevu in derniers.items():
    retard = (DATE_LISTE - prevu).days
    if retard > SEUIL_IIT and prevu >= date(2025, 10, 1):
        liste.append((code, code[:4], DATE_LISTE.isoformat(), prevu.isoformat()))
liste.sort()
db.executemany("INSERT INTO liste_iit VALUES (?,?,?,?)", liste)


# ---------------------------------------------------------------- traçage
def mal_saisir(code: str) -> str:
    """Les trois fautes de saisie qu'on retrouve réellement sur le terrain."""
    faute = rng.choice(["minuscules", "espace", "chiffre_perdu"])
    if faute == "minuscules":
        return code.lower()
    if faute == "espace":
        return code.replace("-", " ")
    return code[:5] + code[6:]          # un zéro de tête a sauté : PV01-0123


visites = []
nouvelles_disp = []
vid = 0
for code, site, _, _ in liste:
    if rng.random() > 0.88:             # 12 % des listés ne sont jamais visités
        continue
    faux_iit = code in servis_ailleurs and code not in interrompus
    jour_visite = jour_aleatoire(date(2026, 6, 2), date(2026, 6, 26))
    if faux_iit:
        resultat = "transfere" if rng.random() < 0.6 else "joint"
    else:
        tirage = rng.random()
        resultat = ("joint" if tirage < 0.60 else "non_joint" if tirage < 0.85
                    else "decede" if tirage < 0.89 else "transfere" if tirage < 0.95
                    else "refus")
    declare = 1 if resultat == "joint" and rng.random() < 0.70 else 0
    date_retour = (jour_visite + timedelta(days=rng.randint(0, 10))) if declare else None
    # Le retour réel, celui qui laisse une trace de dispensation.
    reel = (not faux_iit) and resultat == "joint" and (
        rng.random() < (0.75 if declare else 0.05))
    if reel:
        jour_reel = jour_visite + timedelta(days=rng.randint(1, 14))
        nouvelles_disp.append((code, site, jour_reel.isoformat(), 30))
    saisi = mal_saisir(code) if rng.random() < 0.04 else code
    agent = AGENTS[(int(code[-3:]) + SITES.index(next(s for s in SITES if s[0] == site))) % 12]
    vid += 1
    visites.append((vid, saisi, agent, jour_visite.isoformat(), resultat, declare,
                    date_retour.isoformat() if date_retour else None))
    # 3 % des patients visités une seconde fois par un autre relais.
    if rng.random() < 0.03:
        vid += 1
        autre = rng.choice([a for a in AGENTS if a != agent])
        second = jour_visite + timedelta(days=rng.randint(1, 5))
        visites.append((vid, code, autre, second.isoformat(), resultat, declare,
                        date_retour.isoformat() if date_retour else None))

db.executemany("INSERT INTO visites_tracage VALUES (?,?,?,?,?,?,?)", visites)
db.executemany("INSERT INTO dispensations VALUES (?,?,?,?)", disp + nouvelles_disp)
db.commit()

print(f"{len(patients)} patients, {len(disp) + len(nouvelles_disp)} dispensations, "
      f"{len(liste)} listés IIT, {len(visites)} visites -> {chemin.name}")
