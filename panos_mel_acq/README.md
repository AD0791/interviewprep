# Institut Panos — Responsable MEL/ACQ (AFGHS-PANOS) : préparation d'entretien

**Poste :** Responsable Suivi, Évaluation et Apprentissage / Amélioration Continue de la Qualité,
aussi intitulé Conseiller·ère Technique Principal·e en Information Stratégique, programme
AFGHS-PANOS « Renforcement de la prestation de services de santé intégrés en Haïti ».
**Rattachement :** Chief of Party. **Durée :** six mois renouvelables, conditionnés au financement.
**Lieu :** Port-au-Prince, hybride ou à distance envisageable.
**Entretien : vendredi 25 septembre 2026 à 13 h, sur Zoom.**

L'entretien couvre trois blocs techniques (le VIH et les indicateurs MER, le rôle MEL, l'analyse de
données), un bloc sur le parcours et la personne, et, vraisemblablement, des mises en situation pour
voir si tu tiens sous pression. Le fil conducteur de toute cette préparation est une phrase de
l'annonce que presque aucun candidat ne comprendra : les **paiements du mécanisme dépendent
directement des indicateurs et des jalons**. Elle explique le poste, et le module 01 lui est
consacré.

---

## L'ordre de lecture

**Ce soir, dans cet ordre.** [`FICHE_SYNTHESE.md`](FICHE_SYNTHESE.md) d'abord, une heure, toute la
préparation condensée. Puis
[`../cmmb_meal_officer/FICHE_MER_INDICATEURS.md`](../cmmb_meal_officer/FICHE_MER_INDICATEURS.md),
trente minutes, pour les indicateurs MER. Puis le module 06 **à voix haute**, idéalement filmé.
Les autres modules sont la profondeur derrière chaque fiche, à lire selon le temps : commence par
01 et 02, qui sont ceux qui te distinguent.

**Demain matin**, seulement [`07_fiche_jour_j.md`](07_fiche_jour_j.md), et la fiche de synthèse si tu
as une heure.

| Fichier | Sujet | Pourquoi il existe |
|---|---|---|
| [`FICHE_SYNTHESE.md`](FICHE_SYNTHESE.md) | **La passe d'une heure : commence ici** | Tout, condensé, dans l'ordre de l'entretien |
| [`00_institut_panos.md`](00_institut_panos.md) | L'organisation, lue sur tout son site et dans la presse | « Que savez-vous de nous ? », et le passage de la portée au service rendu |
| [`01_afghs_et_jalons.md`](01_afghs_et_jalons.md) | AFGHS, le paiement sur jalons, la vérification, la réconciliation | La phrase la plus importante de l'annonce |
| [`02_chaine_mel_bout_en_bout.md`](02_chaine_mel_bout_en_bout.md) | La chaîne complète, du cadre au tableau de bord, sur un jeu de données | La démonstration « je sais monter tout le système, vite » |
| [`03_vih_pour_panos.md`](03_vih_pour_panos.md) | Le VIH vu depuis leur mandat : interruption, retour, charge virale, PrEP | Le bloc technique VIH, sans refaire la piste CMMB |
| [`04_analyse_et_tableaux_de_bord.md`](04_analyse_et_tableaux_de_bord.md) | File active, agrégation, Power BI, statistique de vérification | Le bloc « analyste de données » |
| [`05_parcours_pression_hybride.md`](05_parcours_pression_hybride.md) | Pitch, limites, questions difficiles, récits de pression, travail hybride | Toi |
| [`06_simulation_entretien.md`](06_simulation_entretien.md) | Entretien blanc, mises en situation, partie en anglais, tes questions | Pour répéter à voix haute |
| [`07_fiche_jour_j.md`](07_fiche_jour_j.md) | La page du matin, logistique Zoom comprise | Tout tient sur une page |
| [`sources.md`](sources.md) | Toutes les sources, datées du 24 septembre 2026 | Un chiffre attribué est défendable |
| [`exercices/`](exercices/) | Jeu de données fictif de traçage, son générateur, les requêtes du module 02 | Pour que chaque chiffre du module sorte d'une vraie requête |

---

## Ce que cette piste ne refait pas

La piste CMMB, écrite trois semaines plus tôt pour un poste VIH, contient déjà le VIH pour un
professionnel du suivi-évaluation, les indicateurs MER, les systèmes d'information sanitaire
haïtiens, les statistiques, la négociation salariale et les réponses aux questions RH classiques.
Cette piste s'appuie dessus et y renvoie, sans recopier :

- [`../cmmb_meal_officer/FICHE_MER_INDICATEURS.md`](../cmmb_meal_officer/FICHE_MER_INDICATEURS.md) — les chaînes MER, le linkage, les cinq ratios
- [`../cmmb_meal_officer/03_vih_essentiel.md`](../cmmb_meal_officer/03_vih_essentiel.md) — la cascade, la charge virale, la PTME, l'éthique
- [`../cmmb_meal_officer/06_hmis_et_qualite_donnees.md`](../cmmb_meal_officer/06_hmis_et_qualite_donnees.md) — SISNU, iSanté, MESI, SALVH, la collecte mobile
- [`../cmmb_meal_officer/01_pitch_et_questions_rh.md`](../cmmb_meal_officer/01_pitch_et_questions_rh.md) — les blocs de parcours et les questions RH
- [`../cmmb_meal_officer/02_negociation_salariale.md`](../cmmb_meal_officer/02_negociation_salariale.md) — la méthode salariale
- [`../assitant_pmel/01_meal_processus.md`](../assitant_pmel/01_meal_processus.md) et [`../assitant_pmel/05_indicateurs_et_indices.md`](../assitant_pmel/05_indicateurs_et_indices.md) — la théorie MEAL et les fiches d'indicateurs

Ce qu'elle ajoute : l'organisation, le mécanisme AFGHS et le paiement sur jalons, la vérification
indépendante, la réconciliation avec les systèmes nationaux, la chaîne MEL construite de bout en
bout sur un jeu de données, le mandat VIH propre à Panos, et le travail sous pression et en hybride.

**Une correction à la fiche CMMB**, faite au module 03 § 3 : la ventilation des interruptions dans
`TX_ML` porte sur le temps passé sous traitement **avant** l'interruption, pas sur la durée de
l'absence.

---

## La source de vérité pour tout ce que tu diras

Le dossier déposé chez Panos est dans
[`../../curiculum-vitae-and-letter/specific_situation/panos_mel_acq/`](../../curiculum-vitae-and-letter/specific_situation/panos_mel_acq/) :
`cv_fr.md`, `cover_letter_fr.md`, et `email_prep.md` pour la liste de ce qui ne doit pas être
affirmé. **Le panel a la lettre sous les yeux, et elle contient déjà tes délimitations** : à l'oral,
reprends-les dans les mêmes termes.

Les limites à ne jamais franchir, et à dire toi-même : **pas de master délivré** (DES en attente de
la soutenance du mémoire, jamais « diplômé » ni « lauréat ») ; **pas de poste de conseiller technique
principal**, et cinq ans en ONG dont trois sur le VIH plus huit au ministère du Plan ; **producteur de
données dans DATIM, jamais administrateur de DHIS2** ; **pas de PTME** ; **MESI, SISNU et iSanté Plus
connus comme paysage, jamais exploités** ; **aucun indicateur de traitement revendiqué comme
rapporté** (l'exemple confirmé est `AGYW_PREV` sous DREAMS) ; **pas de Projet Santé** ; **pas de
Stata**.

Et deux informations à connaître sans jamais les dire : **CHAMPIONS a été arrêté** au bout de dix mois
en 2025, et un **audit financier de l'USAID** a porté sur un précédent accord de l'Institut. Le
module 00 explique pourquoi il vaut mieux les savoir.
