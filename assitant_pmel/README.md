# Parole et Action — Assistant PMEL

**Superviseur : Hilaire Buissereth, Manager PMEL · Langue : français · Statut : entretien et examen passés**

Parcours construit pour le poste d'assistant PMEL chez Parole et Action, ONG chrétienne haïtienne fondée en 1986, active dans 37 communautés du Sud, de l'Ouest, du Centre et de l'Artibonite. Le dossier reste ici parce qu'il constitue la **base de référence méthodologique** du reste du dépôt : les modules ACTED et Remote Leverage y renvoient plutôt que de répéter la théorie MEAL, les statistiques et XLSForm.

---

## Ordre de lecture

| # | Fichier | Contenu |
|---|---|---|
| 00 | [Fiches de synthèse](00_fiches_synthese.md) | **Le matin de l'épreuve.** L'organisation en dix lignes, MEAL, stats, XLSForm, Excel, pitch |
| 01 | [Le processus MEAL](01_meal_processus.md) | Suivi et évaluation, chaîne de résultats, cadre logique, qualité, triangulation |
| 02 | [Statistiques pour le PMEL](02_statistiques_pmel.md) | Moyennes pondérées, taux et ratios, dispersion, échantillonnage, pièges d'interprétation |
| 03 | [XLSForm, de zéro](03_xlsform_kobo_et_ona.md) | Anatomie du classeur, `relevant`, `constraint`, `calculation`, listes en cascade, multilingue |
| 04 | [Excel appliqué au Data Center](04_excel_data_center.md) | Profilage, nettoyage, doublons, harmonisation, triangulation, tableaux croisés |
| 05 | [Indicateurs et indices](05_indicateurs_et_indices.md) | SMART, CREAM, SPICED, typologie, fiche d'indicateur, construction d'un taux |
| 06 | [Entretien, pitch et Q&A](06_entretien_pitch_et_qa.md) | Pitch, questions probables, réponses parlées |
| 07 | [SQL pour l'analyse PMEL](07_sql_analyse_pmel.md) | SQL analytique appliqué aux données de suivi scolaire |
| 08 | [XLSForm avec Python](08_xlsform_avec_python.md) | Valider, auditer, générer et traduire des formulaires par programme |

---

## Les dossiers d'exercice

`sql_exercices/meal_haiti.db` — base scolaire : 4 régions, 30 écoles, 3 148 élèves, 360 relevés hebdomadaires, 356 lignes sales en staging. C'est la même base que celle reprise par le module 01 du parcours ACTED.

`excel_exercices/` — l'export brut `data_center_export_brut.xlsx` et le corrigé de référence `data_center_propre_reference.csv`, pour l'exercice de nettoyage.

`xlsform_exercices/` — trois formulaires de difficulté croissante : fiche école, présence hebdomadaire, enquête ménage d'impact.

`python_xlsform/` — quatre scripts exécutables : `xlsform_valider.py`, `xlsform_audit.py`, `xlsform_builder.py`, `xlsform_traduire.py`, plus `aplatir_soumissions.py` pour traiter les exports Kobo.

`paroleetaction_interview/paroleetaction_org.md` — la fiche organisation : histoire, direction, partenaires, actualité, piliers.

---

## Ce que ce dossier apporte aux autres parcours

Trois idées structurantes y sont établies une fois et réutilisées partout ailleurs.

**La qualité se garantit d'abord dans le formulaire, ensuite dans le schéma, et seulement en dernier recours dans le nettoyage.** C'est le fil conducteur du parcours ACTED entier.

**La triangulation** — confronter plusieurs sources, méthodes ou observateurs sur le même phénomène — devient, en base de données, la réconciliation entre systèmes ; et, en analytics commercial, le rapprochement entre ce que déclare le bénéficiaire et ce qu'enregistre l'équipe.

**Le piège de la moyenne non pondérée**, démontré chiffres à l'appui sur la base scolaire : 79,24 % en moyenne simple contre 82,45 % en moyenne pondérée pour la même région, soit 3,2 points d'écart. C'est l'exemple à raconter quand on demande un piège d'analyse concret.

---

## Modules liés

Le prolongement base de données du même métier est dans [`../acted_bdd/`](../acted_bdd/README.md) : modélisation, administration, sécurité des données bénéficiaires, Kobo avancé.

La transposition en vocabulaire commercial — même méthode, autre secteur — est dans [`../remote_leverage_data_analyst/`](../remote_leverage_data_analyst/README.md).
