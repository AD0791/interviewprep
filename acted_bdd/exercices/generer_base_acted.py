#!/usr/bin/env python3
# Gist: generer_base_acted.py
#
# Use Case  : construire la base d'exercice du module ACTED — Assistant Base de Donnees.
# Purpose   : produire `acted_bdd.db` (SQLite), son dump `acted_bdd.sql` et l'export brut
#             `export_kobo_pdm_brut.csv` qui simule un telechargement KoboToolbox non nettoye.
# Key points: donnees deterministes (seed fixe), contraintes reelles dans le schema,
#             defauts de qualite injectes volontairement pour les exercices de nettoyage.
#
# Execution : python3 generer_base_acted.py
#
# Le contexte reproduit une intervention ACTED en Haiti : reponse WASH et securite
# alimentaire dans l'Artibonite et l'Ouest, avec enregistrement de menages, ciblage
# par score de vulnerabilite, distributions monetaires et en nature, puis enquetes PDM.

import csv
import os
import random
import sqlite3
from datetime import date, timedelta

RACINE = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(RACINE, "acted_bdd.db")
CHEMIN_SQL = os.path.join(RACINE, "acted_bdd.sql")
CHEMIN_CSV = os.path.join(RACINE, "export_kobo_pdm_brut.csv")

random.seed(2607)  # reference du poste : ASSISTBDD_2607

# --------------------------------------------------------------------------------------
# 1. Schema
# --------------------------------------------------------------------------------------

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE departements (
  id_departement INTEGER PRIMARY KEY,
  nom_departement TEXT NOT NULL UNIQUE,
  code_admin      TEXT NOT NULL UNIQUE
);

CREATE TABLE communes (
  id_commune     INTEGER PRIMARY KEY,
  id_departement INTEGER NOT NULL,
  nom_commune    TEXT NOT NULL,
  code_admin     TEXT NOT NULL UNIQUE,
  FOREIGN KEY (id_departement) REFERENCES departements(id_departement),
  UNIQUE (id_departement, nom_commune)
);

CREATE TABLE sites (
  code_site   TEXT PRIMARY KEY,
  id_commune  INTEGER NOT NULL,
  nom_site    TEXT NOT NULL,
  type_site   TEXT NOT NULL CHECK (type_site IN ('Camp','Quartier','Localite rurale')),
  latitude    REAL CHECK (latitude  BETWEEN 17.5 AND 20.5),
  longitude   REAL CHECK (longitude BETWEEN -75.0 AND -71.5),
  acces_eau   TEXT CHECK (acces_eau IN ('Oui','Non')),
  FOREIGN KEY (id_commune) REFERENCES communes(id_commune)
);

CREATE TABLE projets (
  code_projet   TEXT PRIMARY KEY,
  intitule      TEXT NOT NULL,
  bailleur      TEXT NOT NULL,
  secteur       TEXT NOT NULL CHECK (secteur IN ('WASH','Securite alimentaire','RRM','Agriculture')),
  date_debut    DATE NOT NULL,
  date_fin      DATE NOT NULL,
  budget_usd    REAL CHECK (budget_usd > 0),
  CHECK (date_fin > date_debut)
);

CREATE TABLE activites (
  id_activite   INTEGER PRIMARY KEY,
  code_projet   TEXT NOT NULL,
  type_activite TEXT NOT NULL CHECK (type_activite IN
                 ('Cash inconditionnel','Kit hygiene','Kit alimentaire','Bon alimentaire','Rehabilitation point eau')),
  unite         TEXT NOT NULL,
  cible         INTEGER CHECK (cible > 0),
  FOREIGN KEY (code_projet) REFERENCES projets(code_projet)
);

CREATE TABLE menages (
  id_menage           INTEGER PRIMARY KEY,
  code_menage         TEXT NOT NULL UNIQUE,
  code_site           TEXT NOT NULL,
  nom_chef            TEXT NOT NULL,
  prenom_chef         TEXT NOT NULL,
  sexe_chef           TEXT NOT NULL CHECK (sexe_chef IN ('F','M')),
  date_naissance_chef DATE,
  piece_identite      TEXT,
  telephone           TEXT,
  taille_menage       INTEGER NOT NULL CHECK (taille_menage BETWEEN 1 AND 20),
  nb_enfants_moins5   INTEGER NOT NULL DEFAULT 0 CHECK (nb_enfants_moins5 >= 0),
  nb_femmes_enceintes INTEGER NOT NULL DEFAULT 0 CHECK (nb_femmes_enceintes >= 0),
  nb_handicap         INTEGER NOT NULL DEFAULT 0 CHECK (nb_handicap >= 0),
  statut_deplacement  TEXT CHECK (statut_deplacement IN ('Deplace','Hote','Residant','Retourne')),
  date_enregistrement DATE NOT NULL,
  score_vulnerabilite INTEGER CHECK (score_vulnerabilite BETWEEN 0 AND 100),
  statut_selection    TEXT NOT NULL CHECK (statut_selection IN ('Selectionne','Non selectionne','En attente')),
  agent_enregistrement TEXT,
  FOREIGN KEY (code_site) REFERENCES sites(code_site),
  CHECK (nb_enfants_moins5 <= taille_menage)
);

CREATE TABLE individus (
  id_individu    INTEGER PRIMARY KEY,
  id_menage      INTEGER NOT NULL,
  nom            TEXT NOT NULL,
  prenom         TEXT NOT NULL,
  sexe           TEXT CHECK (sexe IN ('F','M')),
  date_naissance DATE,
  lien_chef      TEXT CHECK (lien_chef IN ('Chef','Conjoint','Enfant','Parent','Autre')),
  scolarise      INTEGER CHECK (scolarise IN (0,1)),
  FOREIGN KEY (id_menage) REFERENCES menages(id_menage)
);

CREATE TABLE assistances (
  id_assistance   INTEGER PRIMARY KEY,
  id_menage       INTEGER NOT NULL,
  id_activite     INTEGER NOT NULL,
  date_assistance DATE NOT NULL,
  modalite        TEXT NOT NULL CHECK (modalite IN ('Cash','Kit','Bon','Service')),
  montant_htg     REAL CHECK (montant_htg >= 0),
  quantite        INTEGER CHECK (quantite > 0),
  agent_saisie    TEXT,
  FOREIGN KEY (id_menage)   REFERENCES menages(id_menage),
  FOREIGN KEY (id_activite) REFERENCES activites(id_activite),
  UNIQUE (id_menage, id_activite, date_assistance)
);

CREATE TABLE pdm_reponses (
  id_pdm                   INTEGER PRIMARY KEY,
  id_menage                INTEGER NOT NULL,
  date_enquete             DATE NOT NULL,
  enqueteur                TEXT NOT NULL,
  satisfaction             INTEGER CHECK (satisfaction BETWEEN 1 AND 5),
  delai_reception_jours    INTEGER CHECK (delai_reception_jours >= 0),
  montant_recu_htg         REAL CHECK (montant_recu_htg >= 0),
  utilisation_principale   TEXT CHECK (utilisation_principale IN
                            ('Nourriture','Sante','Education','Dette','Agriculture','Logement','Autre')),
  connait_mecanisme_plainte INTEGER CHECK (connait_mecanisme_plainte IN (0,1)),
  score_fcs                REAL CHECK (score_fcs BETWEEN 0 AND 112),
  score_rcsi               INTEGER CHECK (score_rcsi BETWEEN 0 AND 56),
  latitude                 REAL,
  longitude                REAL,
  FOREIGN KEY (id_menage) REFERENCES menages(id_menage),
  UNIQUE (id_menage, date_enquete)
);

CREATE TABLE plaintes (
  id_plainte     INTEGER PRIMARY KEY,
  code_menage    TEXT,
  date_reception DATE NOT NULL,
  canal          TEXT CHECK (canal IN ('Ligne verte','Boite a suggestions','Agent terrain','Comite communautaire')),
  categorie      TEXT CHECK (categorie IN ('Ciblage','Montant','Delai','Comportement staff','Information','Autre')),
  sensible       INTEGER NOT NULL DEFAULT 0 CHECK (sensible IN (0,1)),
  statut         TEXT NOT NULL CHECK (statut IN ('Ouverte','En cours','Cloturee')),
  date_cloture   DATE,
  CHECK (date_cloture IS NULL OR date_cloture >= date_reception)
);

CREATE TABLE utilisateurs (
  id_utilisateur INTEGER PRIMARY KEY,
  identifiant    TEXT NOT NULL UNIQUE,
  nom_complet    TEXT NOT NULL,
  role           TEXT NOT NULL CHECK (role IN ('lecture','saisie','analyste','administrateur')),
  actif          INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0,1)),
  date_creation  DATE NOT NULL
);

CREATE TABLE journal_audit (
  id_journal       INTEGER PRIMARY KEY,
  table_cible      TEXT NOT NULL,
  cle_cible        TEXT NOT NULL,
  action           TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
  champ            TEXT,
  ancienne_valeur  TEXT,
  nouvelle_valeur  TEXT,
  identifiant_util TEXT NOT NULL,
  horodatage       TEXT NOT NULL,
  motif            TEXT
);

CREATE TABLE rejets (
  id_rejet       INTEGER PRIMARY KEY,
  table_source   TEXT NOT NULL,
  cle_source     TEXT,
  contenu        TEXT NOT NULL,
  motif_rejet    TEXT NOT NULL,
  date_rejet     TEXT NOT NULL,
  statut         TEXT NOT NULL DEFAULT 'A traiter'
                 CHECK (statut IN ('A traiter','Corrige','Ecarte definitivement'))
);

CREATE TABLE staging_kobo_pdm (
  uuid                    TEXT,
  code_menage             TEXT,
  nom_chef                TEXT,
  commune                 TEXT,
  date_enquete            TEXT,
  enqueteur               TEXT,
  satisfaction            TEXT,
  delai_reception_jours   TEXT,
  montant_recu_htg        TEXT,
  utilisation_principale  TEXT,
  connait_mecanisme_plainte TEXT,
  score_fcs               TEXT,
  score_rcsi              TEXT,
  telephone               TEXT,
  gps_latitude            TEXT,
  gps_longitude           TEXT,
  duree_entretien_min     TEXT
);
"""

# --------------------------------------------------------------------------------------
# 2. Referentiels
# --------------------------------------------------------------------------------------

DEPARTEMENTS = [
    (1, "Artibonite", "HT03"),
    (2, "Ouest", "HT01"),
    (3, "Centre", "HT02"),
    (4, "Nord", "HT04"),
]

COMMUNES = [
    (1, 1, "Gonaives", "HT0311"), (2, 1, "Saint-Marc", "HT0321"),
    (3, 1, "Dessalines", "HT0331"), (4, 1, "Gros-Morne", "HT0341"),
    (5, 1, "Verrettes", "HT0351"), (6, 2, "Port-au-Prince", "HT0111"),
    (7, 2, "Croix-des-Bouquets", "HT0121"), (8, 2, "Leogane", "HT0131"),
    (9, 3, "Mirebalais", "HT0211"), (10, 4, "Cap-Haitien", "HT0411"),
]

NOMS = ["Jean-Baptiste", "Pierre", "Joseph", "Louis", "Charles", "Fils-Aime", "Desir",
        "Cadet", "Saint-Fleur", "Dorvil", "Etienne", "Belizaire", "Augustin", "Cheri",
        "Delva", "Michel", "Alexis", "Beauvoir", "Toussaint", "Lherisson", "Casseus",
        "Noel", "Sanon", "Georges", "Moise", "Estime", "Duverger", "Lafleur"]

PRENOMS_F = ["Marie", "Rosemene", "Guerlande", "Nadege", "Islande", "Fabiola", "Roseline",
             "Mirlande", "Kettia", "Darline", "Yvrose", "Suzette", "Magalie", "Chrislande"]
PRENOMS_M = ["Jean", "Wilner", "Ronald", "Emmanuel", "Frantz", "Dieuseul", "Marckenson",
             "Jonas", "Wisly", "Kervens", "Josue", "Reginald", "Berthony", "Woodly"]

AGENTS = ["adisla", "mjoseph", "rpierre", "gnoel", "kcasseus", "flouis"]
ENQUETEURS = ["ENQ01 Mirlande Delva", "ENQ02 Kervens Sanon", "ENQ03 Fabiola Cheri",
              "ENQ04 Wisly Dorvil", "ENQ05 Nadege Augustin", "ENQ06 Josue Belizaire"]


def prenom(sexe):
    return random.choice(PRENOMS_F if sexe == "F" else PRENOMS_M)


# --------------------------------------------------------------------------------------
# 3. Construction
# --------------------------------------------------------------------------------------

def construire():
    if os.path.exists(CHEMIN_DB):
        os.remove(CHEMIN_DB)
    con = sqlite3.connect(CHEMIN_DB)
    con.executescript(SCHEMA)
    cur = con.cursor()

    cur.executemany("INSERT INTO departements VALUES (?,?,?)", DEPARTEMENTS)
    cur.executemany("INSERT INTO communes VALUES (?,?,?,?)", COMMUNES)

    # --- sites ---------------------------------------------------------------------
    sites = []
    types = ["Camp", "Quartier", "Localite rurale"]
    numero = 0
    for id_commune, _, nom_commune, _ in [(c[0], c[1], c[2], c[3]) for c in COMMUNES]:
        for k in range(random.randint(3, 5)):
            numero += 1
            sites.append((
                f"S{numero:03d}", id_commune, f"{nom_commune} - Site {k + 1}",
                random.choice(types),
                round(random.uniform(18.4, 19.8), 5),
                round(random.uniform(-74.2, -72.0), 5),
                random.choice(["Oui", "Non"]),
            ))
    cur.executemany("INSERT INTO sites VALUES (?,?,?,?,?,?,?)", sites)
    codes_site = [s[0] for s in sites]

    # --- projets et activites ------------------------------------------------------
    projets = [
        ("PRJ-WASH-24", "Acces a l'eau potable et hygiene - Artibonite", "ECHO", "WASH",
         "2025-01-15", "2026-01-14", 1_250_000),
        ("PRJ-SECAL-24", "Assistance alimentaire d'urgence", "PAM", "Securite alimentaire",
         "2025-03-01", "2026-02-28", 2_100_000),
        ("PRJ-RRM-25", "Mecanisme de reponse rapide", "BHA", "RRM",
         "2025-06-01", "2026-05-31", 900_000),
    ]
    cur.executemany("INSERT INTO projets VALUES (?,?,?,?,?,?,?)", projets)

    activites = [
        (1, "PRJ-WASH-24", "Kit hygiene", "kit", 1200),
        (2, "PRJ-WASH-24", "Rehabilitation point eau", "ouvrage", 40),
        (3, "PRJ-SECAL-24", "Cash inconditionnel", "transfert", 1500),
        (4, "PRJ-SECAL-24", "Bon alimentaire", "bon", 800),
        (5, "PRJ-RRM-25", "Kit alimentaire", "kit", 600),
    ]
    cur.executemany("INSERT INTO activites VALUES (?,?,?,?,?)", activites)

    # --- menages -------------------------------------------------------------------
    menages = []
    debut = date(2025, 2, 1)
    for i in range(1, 1201):
        sexe = random.choices(["F", "M"], weights=[58, 42])[0]
        taille = random.choices(range(1, 13),
                                weights=[3, 6, 10, 14, 16, 15, 12, 9, 6, 4, 3, 2])[0]
        enfants5 = min(taille, random.choices([0, 1, 2, 3], weights=[45, 30, 18, 7])[0])
        enceintes = random.choices([0, 1], weights=[88, 12])[0]
        handicap = random.choices([0, 1, 2], weights=[85, 12, 3])[0]
        statut_depl = random.choices(["Deplace", "Hote", "Residant", "Retourne"],
                                     weights=[28, 17, 45, 10])[0]
        # score de vulnerabilite construit a partir de criteres observables
        score = (min(taille, 10) * 4
                 + enfants5 * 7 + enceintes * 6 + handicap * 8
                 + (10 if sexe == "F" else 0)
                 + {"Deplace": 15, "Hote": 8, "Residant": 0, "Retourne": 10}[statut_depl]
                 + random.randint(-5, 5))
        score = max(0, min(100, score))
        # Seuils de ciblage : 44 points ouvrent l'assistance, la zone 36-43 reste en
        # attente de validation par le comite communautaire.
        selection = "Selectionne" if score >= 44 else ("En attente" if score >= 36 else "Non selectionne")
        enreg = debut + timedelta(days=random.randint(0, 300))
        menages.append((
            i, f"MEN-{i:05d}", random.choice(codes_site),
            random.choice(NOMS), prenom(sexe), sexe,
            (date(1960, 1, 1) + timedelta(days=random.randint(0, 16000))).isoformat(),
            f"{random.randint(1, 9)}{random.randint(100000, 999999)}-{random.randint(1, 9)}",
            f"+509{random.randint(30000000, 49999999)}",
            taille, enfants5, enceintes, handicap, statut_depl,
            enreg.isoformat(), score, selection, random.choice(AGENTS),
        ))
    cur.executemany("INSERT INTO menages VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", menages)

    # --- doublons volontaires -------------------------------------------------------
    # 18 menages reenregistres par une autre equipe : meme personne, code different,
    # orthographe du nom parfois alteree. C'est la matiere de l'exercice de deduplication.
    doublons = random.sample(menages, 18)
    id_suivant = 1201
    for src in doublons:
        nom = src[3]
        if random.random() < 0.5:                      # variation orthographique
            nom = nom.replace("-", " ") if "-" in nom else nom.upper()
        menages_dup = list(src)
        menages_dup[0] = id_suivant
        menages_dup[1] = f"MEN-{id_suivant:05d}"
        menages_dup[3] = nom
        menages_dup[14] = (date.fromisoformat(src[14]) + timedelta(days=random.randint(5, 60))).isoformat()
        menages_dup[17] = random.choice(AGENTS)
        cur.execute("INSERT INTO menages VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    tuple(menages_dup))
        id_suivant += 1
    con.commit()

    tous_menages = cur.execute("SELECT id_menage, taille_menage, sexe_chef, statut_selection "
                               "FROM menages").fetchall()

    # --- individus ------------------------------------------------------------------
    individus = []
    id_ind = 1
    for id_menage, taille, sexe_chef, _ in tous_menages:
        individus.append((id_ind, id_menage, "", "", sexe_chef, None, "Chef", 0))
        id_ind += 1
        for _ in range(taille - 1):
            s = random.choice(["F", "M"])
            lien = random.choices(["Conjoint", "Enfant", "Parent", "Autre"],
                                  weights=[20, 60, 12, 8])[0]
            naissance = date(2026, 1, 1) - timedelta(days=random.randint(200, 25000)
                                                     if lien != "Enfant"
                                                     else random.randint(200, 6500))
            individus.append((id_ind, id_menage, "", "", s, naissance.isoformat(), lien,
                              1 if lien == "Enfant" and random.random() < 0.72 else 0))
            id_ind += 1
    # noms/prenoms remplis apres coup pour rester lisible
    individus = [(a, b, random.choice(NOMS), prenom(e), e, f, g, h)
                 for (a, b, _c, _d, e, f, g, h) in individus]
    cur.executemany("INSERT INTO individus VALUES (?,?,?,?,?,?,?,?)", individus)

    # --- assistances ------------------------------------------------------------------
    selectionnes = [m[0] for m in tous_menages if m[3] == "Selectionne"]
    assistances = []
    id_a = 1
    vus = set()
    for id_menage in selectionnes:
        for id_activite, modalite, montant, quantite in [
            (3, "Cash", None, 1), (1, "Kit", 0, 1), (4, "Bon", None, 1), (5, "Kit", 0, 1)
        ]:
            if random.random() > {3: 0.92, 1: 0.70, 4: 0.45, 5: 0.30}[id_activite]:
                continue
            jour = date(2025, 4, 1) + timedelta(days=random.randint(0, 330))
            cle = (id_menage, id_activite, jour.isoformat())
            if cle in vus:
                continue
            vus.add(cle)
            # Le bareme de transfert depend de la taille du menage : montants ronds,
            # comme dans une grille validee par le cluster Cash.
            m = float(random.choice([6000, 7500, 9000, 12000])) \
                if modalite in ("Cash", "Bon") else 0.0
            assistances.append((id_a, id_menage, id_activite, jour.isoformat(), modalite,
                                m, quantite, random.choice(AGENTS)))
            id_a += 1
    cur.executemany("INSERT INTO assistances VALUES (?,?,?,?,?,?,?,?)", assistances)

    # --- PDM ---------------------------------------------------------------------------
    montant_cash = {a[1]: a[5] for a in assistances if a[4] == "Cash"}
    beneficiaires_cash = sorted(montant_cash)
    echantillon = random.sample(beneficiaires_cash, min(620, len(beneficiaires_cash)))
    pdm = []
    id_p = 1
    for id_menage in echantillon:
        jour = date(2025, 9, 1) + timedelta(days=random.randint(0, 210))
        satisfaction = random.choices([1, 2, 3, 4, 5], weights=[4, 9, 24, 43, 20])[0]
        # Le montant declare par le menage doit normalement egaler le montant enregistre
        # par l'equipe distribution. Dans 8 % des cas il est inferieur : c'est exactement
        # l'ecart que l'exercice de reconciliation doit faire ressortir.
        montant_declare = montant_cash[id_menage]
        if random.random() < 0.08:
            montant_declare = float(round(montant_declare * random.uniform(0.55, 0.9) / 250) * 250)
        fcs = round(random.gauss(38, 12), 1)
        fcs = max(0.0, min(112.0, fcs))
        rcsi = max(0, min(56, int(random.gauss(16, 8))))
        pdm.append((id_p, id_menage, jour.isoformat(), random.choice(ENQUETEURS),
                    satisfaction,
                    max(0, int(random.gauss(9, 5))),
                    montant_declare,
                    random.choices(["Nourriture", "Sante", "Education", "Dette",
                                    "Agriculture", "Logement", "Autre"],
                                   weights=[52, 14, 12, 9, 6, 5, 2])[0],
                    random.choices([0, 1], weights=[38, 62])[0],
                    fcs, rcsi,
                    round(random.uniform(18.4, 19.8), 5),
                    round(random.uniform(-74.2, -72.0), 5)))
        id_p += 1
    cur.executemany("INSERT INTO pdm_reponses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", pdm)

    # --- plaintes -------------------------------------------------------------------
    plaintes = []
    codes = [f"MEN-{i:05d}" for i in range(1, 1201)]
    for i in range(1, 241):
        recu = date(2025, 4, 15) + timedelta(days=random.randint(0, 320))
        statut = random.choices(["Ouverte", "En cours", "Cloturee"], weights=[15, 20, 65])[0]
        cloture = (recu + timedelta(days=random.randint(1, 45))).isoformat() \
            if statut == "Cloturee" else None
        plaintes.append((i,
                         random.choice(codes) if random.random() < 0.85 else None,
                         recu.isoformat(),
                         random.choice(["Ligne verte", "Boite a suggestions",
                                        "Agent terrain", "Comite communautaire"]),
                         random.choices(["Ciblage", "Montant", "Delai", "Comportement staff",
                                         "Information", "Autre"],
                                        weights=[34, 18, 20, 6, 15, 7])[0],
                         1 if random.random() < 0.06 else 0,
                         statut, cloture))
    cur.executemany("INSERT INTO plaintes VALUES (?,?,?,?,?,?,?,?)", plaintes)

    # --- utilisateurs ---------------------------------------------------------------
    utilisateurs = [
        (1, "adisla", "Alexandro Disla", "administrateur", 1, "2025-01-10"),
        (2, "mjoseph", "Marie Joseph", "analyste", 1, "2025-01-12"),
        (3, "rpierre", "Ronald Pierre", "saisie", 1, "2025-02-03"),
        (4, "gnoel", "Guerlande Noel", "saisie", 1, "2025-02-03"),
        (5, "kcasseus", "Kervens Casseus", "saisie", 0, "2025-02-20"),
        (6, "flouis", "Fabiola Louis", "lecture", 1, "2025-03-01"),
        (7, "bailleur_echo", "Compte consultation ECHO", "lecture", 1, "2025-05-14"),
    ]
    cur.executemany("INSERT INTO utilisateurs VALUES (?,?,?,?,?,?)", utilisateurs)

    con.commit()

    # --- export Kobo brut (sale) -----------------------------------------------------
    generer_staging(con, cur, pdm)

    con.commit()

    # --- dump ------------------------------------------------------------------------
    with open(CHEMIN_SQL, "w", encoding="utf-8") as f:
        for ligne in con.iterdump():
            f.write(f"{ligne}\n")

    resume(cur)
    con.close()


def generer_staging(con, cur, pdm):
    """Simule un export KoboToolbox non nettoye a partir des reponses PDM propres.

    Sept familles de defauts sont injectees, chacune correspondant a un exercice :
    doublons de soumission, valeurs textuelles dans des colonnes numeriques, dates
    heterogenes, GPS manquants, libelles de commune non harmonises, telephones
    invalides et valeurs aberrantes de duree d'entretien.
    """
    lignes = []
    communes_libelles = {
        "Gonaives": ["Gonaives", "GONAIVES", "Gonaïves", "gonaives", "Gonaive"],
        "Saint-Marc": ["Saint-Marc", "St-Marc", "SAINT MARC", "st marc"],
        "Dessalines": ["Dessalines", "DESSALINES", "Dessaline"],
    }
    for (id_pdm, id_menage, jour, enqueteur, satisfaction, delai, montant,
         usage, plainte, fcs, rcsi, lat, lon) in pdm[:600]:
        row = cur.execute(
            "SELECT m.code_menage, m.nom_chef, c.nom_commune, m.telephone "
            "FROM menages m JOIN sites s ON s.code_site = m.code_site "
            "JOIN communes c ON c.id_commune = s.id_commune WHERE m.id_menage = ?",
            (id_menage,)).fetchone()
        code_menage, nom_chef, commune, telephone = row
        commune_brute = random.choice(communes_libelles.get(commune, [commune]))

        date_brute = jour
        r = random.random()
        if r < 0.08:
            d = date.fromisoformat(jour)
            date_brute = d.strftime("%d/%m/%Y")
        elif r < 0.12:
            d = date.fromisoformat(jour)
            date_brute = d.strftime("%m-%d-%Y")

        satisfaction_brute = str(satisfaction)
        if random.random() < 0.04:
            satisfaction_brute = random.choice(["N/A", "ND", "", "tres satisfait"])

        montant_brut = str(int(montant))
        if random.random() < 0.05:
            montant_brut = random.choice(["9 000", "9,000", "9000 HTG", "-", ""])

        fcs_brut = str(fcs)
        if random.random() < 0.03:
            fcs_brut = random.choice(["", "non collecte", "999"])

        tel_brut = telephone
        if random.random() < 0.07:
            tel_brut = random.choice(["50937", "n/a", "3712-4498", "+509 37 12 44 98"])

        lat_brut, lon_brut = str(lat), str(lon)
        if random.random() < 0.06:
            lat_brut, lon_brut = "", ""

        duree = str(max(3, int(random.gauss(28, 9))))
        if random.random() < 0.02:
            duree = random.choice(["2", "480", "0"])

        lignes.append((
            f"uuid:{id_pdm:06d}-acted", code_menage, nom_chef, commune_brute, date_brute,
            enqueteur, satisfaction_brute, str(delai), montant_brut, usage,
            "oui" if plainte else "non", fcs_brut, str(rcsi), tel_brut,
            lat_brut, lon_brut, duree,
        ))

    # 22 soumissions dupliquees : l'enqueteur a renvoye le formulaire apres perte de reseau
    for src in random.sample(lignes, 22):
        copie = list(src)
        copie[0] = src[0].replace("-acted", "-acted-bis")
        lignes.append(tuple(copie))

    random.shuffle(lignes)
    cur.executemany(
        "INSERT INTO staging_kobo_pdm VALUES (" + ",".join(["?"] * 17) + ")", lignes)

    with open(CHEMIN_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([d[0] for d in cur.execute("SELECT * FROM staging_kobo_pdm LIMIT 0").description])
        w.writerows(lignes)


def resume(cur):
    print(f"Base ecrite : {CHEMIN_DB}")
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    for nom in tables:
        n = cur.execute(f'SELECT COUNT(*) FROM "{nom}"').fetchone()[0]
        print(f"  {nom:<24} {n:>6}")


if __name__ == "__main__":
    construire()
