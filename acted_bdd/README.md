# ACTED — Assistant(e) Base de Données

**Réf. ASSISTBDD_2607 · Port-au-Prince · Responsable direct : Responsable MEAL · Langue : français**

Le poste ne se limite pas à l'analyse de données : le TDR demande de **créer et maintenir** les bases de tous les projets, d'en assurer la sauvegarde, la sécurité et l'intégrité, de coder les questionnaires Kobo de ciblage et de PDM, de classer les archives papier et électroniques, et de fournir un appui technique aux équipes. Ce parcours couvre l'ensemble du périmètre, pas seulement le volet analytique.

---

## Ordre de lecture

| # | Fichier | Contenu |
|---|---|---|
| 00 | [Fiche de révision examen](00_fiche_revision_examen.md) | **La veille et le matin.** Chiffres, définitions, 12 phrases à savoir dire, checklist du jour J |
| 01 | [SQL analyste et gestion de base](01_sql_analyste_et_gestion_bdd.md) | SQL analytique, qualité, dédoublonnage, DDL/DML/transactions, index et plans, N+1 |
| 02 | [Modélisation et conception](02_modelisation_et_conception.md) | MERISE, cardinalités, formes normales, clés, contraintes, migrations |
| 03 | [Administration de base de données](03_administration_bdd.md) | Sauvegarde, restauration, RPO/RTO, intégrité, permissions, maintenance, plan de reprise |
| 04 | [Sécurité et protection des données](04_securite_protection_donnees.md) | PII, k-anonymat, anonymisation, chiffrement, journal d'audit, partage, incident |
| 05 | [Kobo, ciblage et PDM](05_kobo_ciblage_et_pdm.md) | Score de vulnérabilité codé dans le formulaire, FCS/rCSI, formation, chaîne d'import |
| 06 | [Gestion de l'information et archivage](06_gestion_information_archivage.md) | Nomenclature, flux de données, requête de données, archive papier, support technique |
| 07 | [Analyse, visualisation et reporting](07_analyse_visualisation_reporting.md) | Requêtes nommées, choix de graphique, règles d'honnêteté, rapport mensuel |
| 08 | [Examen blanc corrigé](08_examen_blanc_corrige.md) | Épreuve de 2 h 30 : QCM, questions ouvertes, pratique SQL, étude de cas, barème |

**Méthode.** Traite l'examen blanc (08) *en conditions réelles avant* de lire les corrigés — lu à l'avance, il donne l'illusion de savoir. La fiche 00 se lit deux fois : une fois en entier la veille, puis seulement les sections 2, 11 et 12 le matin.

---

## Les deux bases d'exercice

**`meal_haiti.db`** (+ son dump `meal_haiti.sql`) — contexte scolaire, plus simple, utilisée par le module 01 pour apprendre le SQL lui-même. Quatre régions, 30 écoles, 3 148 élèves dont 25 doublons volontaires, 360 relevés hebdomadaires, 356 lignes sales en staging.

**`exercices/acted_bdd.db`** — contexte WASH et sécurité alimentaire, calquée sur une intervention ACTED réelle. Utilisée par les modules 02 à 08.

| Table | Lignes |
|---|---|
| `menages` | 1 218 (dont 18 doublons de pièce d'identité) |
| `individus` | 7 004 |
| `assistances` | 1 428 |
| `pdm_reponses` | 567 |
| `plaintes` | 240 (dont 17 sensibles) |
| `staging_kobo_pdm` | 589 lignes brutes avec défauts injectés |

```bash
cd exercices
python3 generer_base_acted.py        # regenere la base (deterministe, seed fixe)
```

---

## Les scripts livrés, tous exécutables

| Script | Ce qu'il fait |
|---|---|
| `exercices/generer_base_acted.py` | Construit `acted_bdd.db`, son dump et l'export Kobo brut |
| `exercices/construire_xlsforms.py` | Produit les deux XLSForm — ciblage et PDM — validés par pyxform |
| `exercices/importer_kobo.py` | Chaîne d'import réconciliée et idempotente, avec table de rejets |
| `exercices/sauvegarde_acted.sh` | Sauvegarde avec contrôle d'intégrité, empreinte et restauration de contrôle |
| `exercices/verifier_nomenclature.py` | Audite un dossier partagé contre la nomenclature convenue |
| `exercices/rapport_mensuel.py` | Produit les graphiques et le classeur du rapport mensuel |

Les deux formulaires `exercices/xlsform_ciblage_menage.xlsx` et `exercices/xlsform_pdm_cash.xlsx` compilent sans avertissement et sont déployables tels quels sur KoboToolbox.

---

## Ce qu'il faut savoir démontrer, pas seulement expliquer

Trois démonstrations valent plus que dix définitions, et elles se font en direct sur la base.

Tenter d'insérer un doublon d'assistance et **montrer que la contrainte `UNIQUE` refuse** — la preuve qu'on conçoit des garanties, pas des tables.

Mesurer le **k-anonymat** : 245 ménages sur 1 218 restent identifiables de façon unique sur quatre quasi-identifiants, ce qui prouve que retirer les noms n'anonymise pas.

Lancer l'import Kobo et montrer que la **réconciliation boucle** : 589 lues − 56 rejets − 18 doublons − 515 retenues = 0.

---

## Modules liés

Le volet PMEL — processus MEAL, statistiques, XLSForm de zéro, Excel, indicateurs — est traité dans [`../assitant_pmel/`](../assitant_pmel/README.md) et référencé plutôt que répété ici.

Source de vérité pour toute affirmation sur ton parcours : `../../curiculum-vitae-and-letter/alexandrodislaResume.tex`.

---

## Conventions

Chaque chiffre affiché dans ces modules provient de l'exécution réelle de la requête montrée ; 22 valeurs clés sont revérifiées après toute reconstruction de la base. N'ouvre pas la base directement depuis un dossier synchronisé — copie-la d'abord dans un dossier local, SQLite supporte mal certains montages réseau.
