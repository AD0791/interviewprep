#!/usr/bin/env python3
"""
Aplatir un export contenant des groupes repetes (begin_repeat).
Un export Kobo/Ona produit UNE table par repetition, reliee a la table
principale par _parent_index (ou _submission__uuid). Ce script rejoint
le tout et produit un fichier analysable, plus des controles de coherence.

Usage : python3 aplatir_soumissions.py export_kobo_simule.xlsx
Dependances : pandas, openpyxl
"""
import sys
import pandas as pd

CLES = [("_parent_index", "_index"), ("_submission__uuid", "_uuid"),
        ("_parent_table_name", None)]

def charger(chemin):
    feuilles = pd.read_excel(chemin, sheet_name=None)
    noms = list(feuilles)
    principal = noms[0]
    repetitions = [n for n in noms[1:]]
    return feuilles, principal, repetitions

def trouver_cle(df_rep, df_pri):
    for gauche, droite in CLES:
        if droite and gauche in df_rep.columns and droite in df_pri.columns:
            return gauche, droite
    raise ValueError("Aucune cle de jointure trouvee entre la repetition et la table principale")

def aplatir(chemin):
    feuilles, principal, repetitions = charger(chemin)
    pri = feuilles[principal]
    print(f"Table principale '{principal}' : {len(pri)} soumissions, {len(pri.columns)} colonnes")

    resultats = {}
    for rep in repetitions:
        r = feuilles[rep]
        g, d = trouver_cle(r, pri)
        # on isole la cle parente sous un nom non ambigu : _index existe
        # dans les DEUX tables, et la fusion le rendrait indistinguable
        pri_j = pri.rename(columns={d: "_cle_parent"}).copy()
        pri_j["_parent_trouve"] = True
        fusion = r.merge(pri_j, left_on=g, right_on="_cle_parent", how="left",
                         suffixes=(f"_{rep}", "_soumission"))
        print(f"Repetition '{rep}' : {len(r)} lignes -> {len(fusion)} apres jointure sur {g} = {d}")
        orphelines = fusion[fusion["_parent_trouve"].isna()]
        if len(orphelines):
            print(f"  ATTENTION : {len(orphelines)} ligne(s) orpheline(s) sans soumission parente")
        resultats[rep] = fusion
    return pri, resultats

def controles(df):
    """Regles de triangulation appliquees a la table aplatie."""
    tests = {
        "R1 presents > inscrits":            df.presents > df.inscrits,
        "R2 parraines > presents":           df.presents_parraines > df.presents,
        "R3 repas > presents x jours":       df.repas > df.presents * df.jours_classe,
        "R4 enseignant absent, eleves presents": (df.ens_present == "non") & (df.presents > 0),
    }
    print("\nControles de coherence :")
    for nom, masque in tests.items():
        print(f"  {nom:42s} : {int(masque.sum()):3d} ligne(s)")
    return df.assign(**{n.split()[0]: m for n, m in tests.items()})

def duree_entretien(pri):
    """Metadonnees start/end : detection de saisies anormalement rapides."""
    d = pri.copy()
    d["duree_min"] = (pd.to_datetime(d["end"]) - pd.to_datetime(d["start"])).dt.total_seconds() / 60
    print("\nDuree de saisie (minutes) :")
    print(f"  mediane {d.duree_min.median():.1f} | min {d.duree_min.min():.1f} | max {d.duree_min.max():.1f}")
    suspects = d[d.duree_min < d.duree_min.median() * 0.3]
    print(f"  soumissions anormalement rapides : {len(suspects)}")
    return d

def verifier_totaux(pri, plat):
    """Le calcul sum() du formulaire doit egaler la somme des lignes repetees."""
    recalc = plat.groupby("_parent_index").agg(
        presents_calcules=("presents", "sum"),
        repas_calcules=("repas", "sum")).reset_index()
    ctrl = pri.merge(recalc, left_on="_index", right_on="_parent_index")
    ecart_p = (ctrl.total_presents - ctrl.presents_calcules).abs().sum()
    ecart_r = (ctrl.total_repas - ctrl.repas_calcules).abs().sum()
    print("\nVerification des totaux calcules dans le formulaire :")
    print(f"  ecart total sur les presents : {ecart_p}")
    print(f"  ecart total sur les repas    : {ecart_r}")
    return ctrl

if __name__ == "__main__":
    chemin = sys.argv[1] if len(sys.argv) > 1 else "export_kobo_simule.xlsx"
    pri, tables = aplatir(chemin)
    plat = list(tables.values())[0]
    plat = controles(plat)
    duree_entretien(pri)
    verifier_totaux(pri, plat)
    sortie = "donnees_aplaties.xlsx"
    with pd.ExcelWriter(sortie, engine="openpyxl") as w:
        plat.to_excel(w, sheet_name="donnees_aplaties", index=False)
        pri.to_excel(w, sheet_name="soumissions", index=False)
    print(f"\nEcrit : {sortie} ({len(plat)} lignes)")
