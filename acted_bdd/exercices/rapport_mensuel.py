#!/usr/bin/env python3
# Gist: rapport_mensuel.py
#
# Use Case  : produire le rapport mensuel du projet directement depuis la base, sans
#             passer par un copier-coller Excel.
# Purpose   : montrer la chaine complete requete SQL -> tableau -> graphique -> livrable,
#             avec des chiffres qui ne peuvent pas diverger d'une version a l'autre.
# Key points: une requete nommee par indicateur, chaque graphique choisi pour ce qu'il
#             doit montrer, axes partant de zero, effectifs affiches a cote des
#             pourcentages, et un classeur Excel produit pour ceux qui veulent creuser.
#
# Execution : python3 rapport_mensuel.py acted_bdd.db sortie/

import os
import sqlite3
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
import pandas as pd               # noqa: E402

# Palette sobre : une couleur d'accent, des gris pour le reste. Un rapport n'est pas
# une affiche — la couleur doit signifier quelque chose, sinon elle distrait.
ACCENT = "#1f4e79"
GRIS = "#9aa5b1"
ALERTE = "#c0392b"

REQUETES = {
    "couverture": """
        SELECT d.nom_departement AS departement,
               COUNT(DISTINCT CASE WHEN m.statut_selection = 'Selectionne'
                                   THEN m.id_menage END) AS cibles,
               COUNT(DISTINCT a.id_menage)               AS atteints
        FROM menages m
        JOIN sites        s ON s.code_site      = m.code_site
        JOIN communes     c ON c.id_commune     = s.id_commune
        JOIN departements d ON d.id_departement = c.id_departement
        LEFT JOIN assistances a ON a.id_menage  = m.id_menage
        GROUP BY 1 ORDER BY cibles DESC
    """,
    "fcs": """
        SELECT CASE WHEN score_fcs <= 21 THEN 'Pauvre'
                    WHEN score_fcs <= 35 THEN 'Limite'
                    ELSE 'Acceptable' END AS classe,
               COUNT(*) AS menages
        FROM pdm_reponses GROUP BY 1
    """,
    "satisfaction": """
        SELECT satisfaction, COUNT(*) AS menages
        FROM pdm_reponses GROUP BY 1 ORDER BY 1
    """,
    "desagregation": """
        SELECT d.nom_departement AS departement, m.sexe_chef AS sexe,
               COUNT(DISTINCT a.id_menage) AS menages_assistes,
               SUM(m.taille_menage)        AS personnes_couvertes
        FROM assistances a
        JOIN menages m      ON m.id_menage      = a.id_menage
        JOIN sites s        ON s.code_site      = m.code_site
        JOIN communes c     ON c.id_commune     = s.id_commune
        JOIN departements d ON d.id_departement = c.id_departement
        GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "ecarts_montant": """
        SELECT COUNT(*) AS enquetes,
               SUM(CASE WHEN p.montant_recu_htg <> a.montant_htg THEN 1 ELSE 0 END) AS ecarts,
               CAST(SUM(a.montant_htg - p.montant_recu_htg) AS INTEGER) AS manquant_htg
        FROM pdm_reponses p
        JOIN assistances a ON a.id_menage = p.id_menage AND a.id_activite = 3
    """,
    "plaintes": """
        SELECT categorie,
               COUNT(*) AS recues,
               SUM(CASE WHEN statut = 'Cloturee' THEN 1 ELSE 0 END) AS cloturees
        FROM plaintes GROUP BY 1 ORDER BY recues DESC
    """,
}


def charger(con):
    return {nom: pd.read_sql_query(sql, con) for nom, sql in REQUETES.items()}


def graphique_couverture(df, chemin):
    """Barres horizontales : comparaison entre categories, la lecture est immediate."""
    df = df.copy()
    df["taux"] = 100 * df["atteints"] / df["cibles"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.barh(df["departement"], df["cibles"], color=GRIS, label="Ménages ciblés")
    ax.barh(df["departement"], df["atteints"], color=ACCENT, height=0.55,
            label="Ménages atteints")
    for i, ligne in df.iterrows():
        ax.text(ligne["cibles"] + 4, i, f"{ligne['taux']:.1f} %", va="center", fontsize=9)
    ax.set_xlabel("Nombre de ménages")
    ax.set_title("Couverture par département — ménages ciblés et atteints")
    # barh empile de bas en haut : on inverse pour retrouver l'ordre du tableau,
    # et on sort la legende du cadre pour qu'elle ne recouvre aucune barre.
    ax.invert_yaxis()
    ax.set_xlim(0, df["cibles"].max() * 1.18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2,
              frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(chemin, dpi=150)
    plt.close(fig)


def graphique_fcs(df, chemin):
    """Barres verticales ordonnees par severite : l'ordre porte du sens, on le respecte."""
    ordre = ["Pauvre", "Limite", "Acceptable"]
    df = df.set_index("classe").reindex(ordre).reset_index()
    total = df["menages"].sum()
    couleurs = [ALERTE, "#e0a458", ACCENT]
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    barres = ax.bar(df["classe"], df["menages"], color=couleurs)
    for barre, n in zip(barres, df["menages"]):
        ax.text(barre.get_x() + barre.get_width() / 2, n + 4,
                f"{n}\n({100 * n / total:.1f} %)", ha="center", fontsize=9)
    ax.set_ylabel("Nombre de ménages")
    ax.set_ylim(0, df["menages"].max() * 1.25)
    ax.set_title(f"Score de consommation alimentaire (n = {total})")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(chemin, dpi=150)
    plt.close(fig)


def graphique_plaintes(df, chemin):
    """Barres empilees : recues et cloturees, pour montrer le reste a traiter."""
    df = df.copy()
    df["en_cours"] = df["recues"] - df["cloturees"]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar(df["categorie"], df["cloturees"], color=ACCENT, label="Clôturées")
    ax.bar(df["categorie"], df["en_cours"], bottom=df["cloturees"], color=GRIS,
           label="Ouvertes ou en cours")
    ax.set_ylabel("Nombre de plaintes")
    ax.set_title("Plaintes reçues et traitées, par catégorie")
    ax.legend(frameon=False, fontsize=8)
    ax.tick_params(axis="x", rotation=20)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(chemin, dpi=150)
    plt.close(fig)


def produire(chemin_db, dossier_sortie):
    os.makedirs(dossier_sortie, exist_ok=True)
    con = sqlite3.connect(chemin_db)
    tables = charger(con)
    con.close()

    graphique_couverture(tables["couverture"], os.path.join(dossier_sortie, "01_couverture.png"))
    graphique_fcs(tables["fcs"], os.path.join(dossier_sortie, "02_fcs.png"))
    graphique_plaintes(tables["plaintes"], os.path.join(dossier_sortie, "03_plaintes.png"))

    chemin_xlsx = os.path.join(dossier_sortie, "rapport_mensuel.xlsx")
    with pd.ExcelWriter(chemin_xlsx, engine="openpyxl") as writer:
        for nom, df in tables.items():
            df.to_excel(writer, sheet_name=nom[:31], index=False)

    # Sortie console : les memes chiffres que ceux du rapport, pour verification a l'oeil.
    for nom, df in tables.items():
        print(f"\n== {nom} ==")
        print(df.to_string(index=False))
    print(f"\nGraphiques et classeur ecrits dans {dossier_sortie}")


if __name__ == "__main__":
    produire(sys.argv[1] if len(sys.argv) > 1 else "acted_bdd.db",
             sys.argv[2] if len(sys.argv) > 2 else "sortie_rapport")
