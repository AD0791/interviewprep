# Fiche de révision — jour de l'examen ACTED

*Assistant(e) Base de Données · Réf. ASSISTBDD_2607 · Port-au-Prince · Responsable direct : Responsable MEAL*

**Comment utiliser cette fiche.** Elle est faite pour deux moments et deux seulement. La veille au soir, tu la lis en entier une fois, calmement, en t'arrêtant sur ce qui ne te revient pas immédiatement — et tu retournes au module concerné pour ces points-là uniquement. Le matin de l'épreuve, tu relis les sections 2, 11 et 12, qui sont les chiffres, les phrases à savoir dire et les erreurs à ne pas commettre. Ne relis rien pendant les trente minutes qui précèdent : à ce stade, tu ne gagnes plus rien et tu perds du calme.

---

## 1. Le poste, en une page

ACTED cherche quelqu'un qui **crée et maintient les bases de données de tous les projets** et qui **fournit des analyses précises, fiables et perspicaces**. Le TDR décline cela en cinq blocs qu'il faut avoir en tête, parce que toute question posée en relèvera.

| Bloc du TDR | Ce qu'ils veulent réellement entendre | Module |
|---|---|---|
| Système de gestion des bases | Concevoir, maintenir, contrôler la qualité, sauvegarder, sécuriser, dépanner | [02](02_modelisation_et_conception.md) · [03](03_administration_bdd.md) |
| Enregistrement et ciblage | Coder le questionnaire Kobo avec formules avancées, former, détecter les doublons | [05](05_kobo_ciblage_et_pdm.md) |
| Enquêtes PDM et endline | Coder, appuyer les équipes, nettoyer, garantir la qualité et le stockage | [05](05_kobo_ciblage_et_pdm.md) |
| Analyse des données | Extraire requêtes, chiffres et rapports ; produire graphiques et tableaux | [07](07_analyse_visualisation_reporting.md) |
| Autre | Rendre compte au superviseur, participer aux ateliers, appui technique | [06](06_gestion_information_archivage.md) |

Les compétences exigées : diplôme pertinent, deux ans d'expérience en gestion de l'information dans une ONG, maîtrise d'Excel, expérience ODK/KOBO, collecte et analyse, formulation d'exigences techniques et de procédures, connaissance de l'Artibonite, expérience RRM appréciée, **français et créole**.

Le message de fond à faire passer, quelle que soit la question : **tu es celui qui garantit que le chiffre est juste, reproductible et défendable, et qui protège les données des personnes derrière le chiffre.**

---

## 2. Les chiffres à avoir en tête

### Bases d'exercice

| Base | Contenu |
|---|---|
| `meal_haiti.db` | 4 régions, 30 écoles, 3 148 élèves (dont 25 doublons volontaires), 360 relevés hebdo, 983 distributions, 356 lignes sales en staging |
| `exercices/acted_bdd.db` | 4 départements, 10 communes, 38 sites, 1 218 ménages (dont 18 doublons de pièce d'identité), 7 004 individus, 1 428 assistances, 567 enquêtes PDM, 240 plaintes (17 sensibles), 589 lignes brutes Kobo en staging |

### Résultats à pouvoir citer

| Constat | Chiffre |
|---|---|
| Ménages enregistrés / sélectionnés / assistés | 1 218 / 601 / 600 |
| Couverture Artibonite | 267 ciblés, 266 atteints — 1 sélectionné jamais servi (MEN-00981, score 57) |
| Import Kobo | 589 lues → 56 rejets documentés, 18 doublons, 515 chargées ; réconciliation à zéro |
| Motif de rejet principal | 28 satisfaction hors échelle, 20 entretiens de moins de 8 minutes |
| Harmonisation | 19 graphies de commune → 10 communes réelles |
| Écart PDM / distribution | 39 ménages sur 567 (6,9 %), 95 500 HTG d'écart cumulé |
| Sécurité alimentaire (FCS) | Pauvre 56 (9,9 %), Limite 186 (32,8 %), Acceptable 325 (57,3 %) |
| Satisfaction ≥ 4 | 369 / 567, soit 65,1 % |
| Réidentification | 245 ménages sur 1 218 (1 sur 5) uniques sur 4 quasi-identifiants ; 24 seulement après généralisation |
| Gain d'un index | 3 000 recherches par pièce d'identité : environ 0,18 s → 0,018 s, facteur 10 |

### Tes propres chiffres

Trente-six secondes ramenées à moins d'une demi-seconde sur la résolution d'un N+1 chez Tekkod. Index composites ayant supprimé verrous et blocages. Administration de bases MySQL et mWater à la Fondation Caris et pour HANWASH. Dédoublonnage systématique des listes de bénéficiaires. **Chacune de ces affirmations doit se défendre en trente secondes** — les formulations sont en section 12.

---

## 3. SQL — l'essentiel

### Ordre logique d'exécution

`FROM` → `JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT`

Deux conséquences : un alias défini dans le `SELECT` n'existe pas encore dans le `WHERE` ; et `WHERE` filtre les lignes avant l'agrégation quand `HAVING` filtre les groupes après.

### Les NULL

Logique ternaire : vrai, faux, inconnu. `= NULL` ne renvoie jamais rien, il faut `IS NULL`. `COUNT(*)` compte les lignes, `COUNT(colonne)` ignore les NULL. `AVG` divise par le nombre de valeurs non nulles. Un NULL dans un `NOT IN` fait échouer toute la condition — utiliser `NOT EXISTS`. `COALESCE(a,b)` renvoie la première valeur non nulle, `NULLIF(x,0)` évite la division par zéro.

### Jointures et motifs

| Besoin | Motif |
|---|---|
| Qui n'a pas reçu / n'a pas rapporté | `LEFT JOIN ... WHERE clé_droite IS NULL` |
| Compter des entités, pas des lignes | `COUNT(DISTINCT id_menage)` |
| Compter sous condition dans un groupe | `SUM(CASE WHEN cond THEN 1 ELSE 0 END)` |
| Tableau croisé | `AVG(CASE WHEN periode=1 THEN valeur END)` par colonne |
| Grille théorique complète | `CROSS JOIN` puis `LEFT JOIN` et `IS NULL` |
| Empiler des contrôles | `UNION ALL`, une ligne par contrôle, tous à zéro |
| Écarts entre deux listes | `EXCEPT` |

### Fonctions fenêtre

`ROW_NUMBER()` numérote sans ex æquo, `RANK()` laisse des trous, `DENSE_RANK()` n'en laisse pas, `NTILE(4)` découpe en quartiles, `LAG`/`LEAD` regardent la ligne précédente ou suivante, `SUM() OVER (ORDER BY ...)` cumule, `AVG() OVER (... ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` lisse.

**Une fonction fenêtre ne se filtre pas dans le `WHERE`** : il faut l'encapsuler dans une sous-requête ou une CTE.

### Dédoublonnage

```sql
WITH numerotes AS (
  SELECT id, ROW_NUMBER() OVER (PARTITION BY clé_métier
                                ORDER BY règle_de_conservation) AS rang
  FROM table)
SELECT * FROM numerotes WHERE rang > 1;
```

Les trois précautions, à citer systématiquement : `SELECT` avant `DELETE`, transaction, archivage en table de rejets.

### Écriture

`BEGIN` / `COMMIT` / `ROLLBACK` encadrent toute écriture réelle. L'`UPSERT` s'écrit `INSERT ... ON CONFLICT (clé) DO UPDATE SET col = excluded.col`, et c'est lui qui rend un import **idempotent**. Attention : seules les colonnes citées dans le `DO UPDATE` changent. `DELETE` se filtre et s'annule ; `TRUNCATE` ne se filtre pas et ne s'annule pas.

### Chaînes et dates

Nettoyage : `TRIM`, `UPPER`, `REPLACE`, `SUBSTR`, `LENGTH`, `||`. Dates SQLite : `strftime('%Y-%m', d)`, `julianday(a)-julianday(b)`, `date('now','-7 days')`. PostgreSQL : `date_trunc`, `age`. MySQL : `DATE_FORMAT`, `DATEDIFF`. Une fonction appliquée à une colonne dans le `WHERE` **annule l'index**.

---

## 4. Modélisation

**Vocabulaire MERISE** : entité, association, propriété, cardinalité, MCD → MLD → MPD.

**Cardinalités** : `0,n` d'un côté et `1,1` de l'autre donne une relation un-à-plusieurs, et la clé va du côté `1,1`. `0,n` des deux côtés donne une relation plusieurs-à-plusieurs, qui devient **toujours une table d'association** portant les deux clés plus les propriétés de la rencontre.

**Formes normales** : 1FN, chaque cellule est atomique — une virgule dans une cellule signale une table manquante. 2FN, tout attribut non clé dépend de toute la clé. 3FN, aucun attribut non clé ne dépend d'un autre attribut non clé. La formule : *chaque attribut dépend de la clé, de toute la clé, et de rien que la clé.*

**Clés** : clé primaire technique sans signification métier, plus la clé métier en contrainte `UNIQUE` à côté. Raison : tout identifiant porteur de sens finit par changer.

**Contraintes** : `NOT NULL` pour l'indispensable, `CHECK` pour les listes fermées et les règles à deux colonnes, `UNIQUE` composite pour la clé métier — c'est elle qui rend le double paiement impossible plutôt que détectable, `FOREIGN KEY` pour l'intégrité référentielle.

**Suppression** : `RESTRICT` par défaut sur les bénéficiaires, `CASCADE` seulement pour ce qui n'a pas d'existence propre. En pratique **on ne supprime pas, on désactive**.

**Piège SQLite** : les clés étrangères ne sont pas vérifiées sans `PRAGMA foreign_keys = ON` à chaque connexion.

**Migration** : jamais de modification manuelle en production ; script numéroté, transactionnel, documenté, réversible.

---

## 5. Administration

**Sauvegarde** : logique (`pg_dump`, `mysqldump`, `.dump`) portable et lisible ; physique (`.backup`, `pg_basebackup`) rapide et fidèle. Ne **jamais** copier une base ouverte avec `cp`. Complète, différentielle, incrémentale. Restauration à un instant donné via WAL en PostgreSQL, binlog en MySQL, impossible en SQLite.

**Règle 3-2-1** : trois copies, deux supports, une hors site — et chiffrée.

**RPO** : perte maximale acceptable, fixe la fréquence. **RTO** : délai de rétablissement acceptable, fixe la préparation.

**La phrase** : une sauvegarde jamais restaurée n'est pas une sauvegarde, c'est une hypothèse. D'où le contrôle d'intégrité **avant** la copie, la restauration automatique de contrôle après, et l'exercice trimestriel documenté.

**Intégrité, trois niveaux** : physique (`PRAGMA integrity_check`), référentielle (`PRAGMA foreign_key_check`), métier (tableau de bord de validation, une dizaine de requêtes qui doivent toutes renvoyer zéro). Le schéma empêche ce qu'on peut empêcher, les contrôles détectent le reste.

**Index** : préfixe le plus à gauche ; coût en écriture ; inutile sur colonne peu sélective ; annulé par une fonction ; index couvrant. On lit le plan avant, on ajoute, on relit, on remesure.

**Maintenance** : `ANALYZE` pour les statistiques, `VACUUM` pour l'espace, `REINDEX` pour la fragmentation.

**Permissions** : moindre privilège, comptes nominatifs, jamais de `DELETE` pour un compte applicatif, droits colonne par colonne quand c'est possible, revue trimestrielle, désactivation le jour du départ. SQLite n'a aucun système de comptes — c'est l'argument de migration vers PostgreSQL.

---

## 6. Sécurité et protection des données

**Identifiants directs** : nom, pièce, téléphone, GPS, photo. **Quasi-identifiants** : commune, sexe, taille du ménage, statut de déplacement — c'est leur combinaison qui trahit.

**k-anonymat** : chaque combinaison doit être partagée par au moins *k* personnes. Sur la base d'exercice, 245 ménages sur 1 218 sont uniques sur quatre quasi-identifiants ; après généralisation en tranches, il n'en reste que 24.

**Anonymisation** irréversible contre **pseudonymisation** réversible : la seconde reste une donnée personnelle. Un fichier pseudonymisé mais réidentifiable par recoupement n'est pas anonyme.

**Minimisation** : pour chaque question, quelle décision la réponse change-t-elle ? Sinon elle sort du formulaire. Une donnée non collectée ne peut pas fuir.

**Export sûr** : aucune colonne nominative, quasi-identifiants généralisés, seuil `HAVING COUNT(*) >= 5`, et le tout dans une **vue** sur laquelle on accorde le droit de lecture — la protection devient structurelle.

**Traçabilité** : déclencheur d'audit sur les champs sensibles, avec utilisateur et motif ; table de journal en écriture seule.

**Partage** : bailleur et cluster reçoivent des agrégats ; partenaire de mise en œuvre reçoit sa zone sous accord écrit ; toute demande d'une autorité remonte au coordonnateur et au responsable protection, jamais traitée seul.

**Incident** : contenir, évaluer, notifier, corriger, documenter. On ne dissimule jamais.

**La phrase qui résume** : en Haïti, une liste nominative de personnes ayant reçu du cash, avec coordonnées et localisation, est une liste de cibles potentielles. Ce n'est pas une hypothèse théorique.

---

## 7. Kobo, ciblage et PDM

**Colonnes XLSForm** : `type`, `name`, `label`, `required`, `relevant` (affichage conditionnel), `constraint` (valeur interdite), `constraint_message`, `calculation`, `choice_filter` (listes en cascade), `appearance`.

**Règle de conception** : on **bloque l'impossible** par `constraint`, on **alerte sur l'improbable** par une note conditionnelle. Bloquer l'improbable pousse à saisir n'importe quoi.

**Score de vulnérabilité** : décomposé en points partiels nommés, plafonné par composante et au total, seuils affichés — et toujours la mention que la décision finale appartient au comité communautaire. *Un algorithme classe, il ne sélectionne pas.*

**FCS** : huit groupes alimentaires, fréquence sur 7 jours, pondérations 2 / 3 / 1 / 1 / 4 / 4 / 0,5 / 0,5. Seuils : ≤ 21 pauvre, ≤ 35 limite, au-delà acceptable.

**rCSI** : cinq stratégies, sévérités 1 / 2 / 1 / 3 / 1, score de 0 à 56. Un FCS acceptable avec un rCSI élevé décrit une situation fragile.

**Consentement** : question bloquante en tête, tous les groupes suivants en `relevant` sur la réponse positive ; refuser n'a aucune conséquence sur l'accès à l'assistance.

**Contrôles de collecte quotidiens** : durée médiane par enquêteur, taux de valeurs manquantes, dispersion GPS, variance des réponses, taux de refus. La durée d'entretien se calcule dans le formulaire par `int((decimal-date-time(${end}) - decimal-date-time(${start})) * 1440)`.

**Chaîne d'import, quatre étapes** : archiver le brut sans le modifier, normaliser, valider avec rejets documentés, dédupliquer sur la clé métier avec règle de conservation explicite, charger de façon idempotente. **La réconciliation doit boucler** : lues − rejets − doublons − retenues = 0.

**Formation des enquêteurs** : le sens avant l'outil, traduction créole validée collectivement, jeux de rôle, pilote hors zone, supervision du premier jour, contrôle qualité chaque soir.

---

## 8. Gestion de l'information

**Nomenclature** : `AAAAMMJJ_PROJET_TYPE_DESCRIPTION_vN.ext`. Date en tête pour que le tri alphabétique soit chronologique. Jamais d'espace, d'accent, ni de mot « final ».

**Arborescence** : formulaires, données brutes (jamais modifiées), bases, rapports, données restreintes (accès limité), archives papier.

**Requête de données** : référence unique, réponse écrite, échéance de deux semaines, ton descriptif et non accusateur. Alimentée automatiquement par la table de rejets.

**Archive papier** : référence unique et inventaire, chaîne de responsabilité tracée, numérisation avec le même nom, stockage fermé et surélevé, destruction réelle en fin de conservation.

**Support technique** : reproduire avant de proposer, isoler entre machine, compte, fichier et réseau, puis registre des incidents pour transformer les interruptions en priorités de formation.

**Rendre compte** : chaque vendredi, cinq lignes — fait, chiffres, bloqué, semaine prochaine, besoin d'arbitrage.

---

## 9. Analyse et restitution

**Un indicateur = une requête nommée**, écrite une fois, stockée, exécutée à chaque production. C'est ce qui empêche trois personnes d'annoncer trois chiffres.

**Avant le SQL** : définir le numérateur, choisir et afficher le dénominateur, fixer la période et la désagrégation.

**Choix du graphique** : barres pour comparer, courbe pour le temps, barres empilées plutôt que camembert, histogramme pour une distribution, nuage pour une relation, et souvent une phrase pour un seul chiffre.

**Règles d'honnêteté** : axe des barres à zéro, effectif toujours à côté du pourcentage, catégories ordonnées dans leur ordre naturel, couleur porteuse de sens, titre énonçant le constat.

**Commentaire en quatre temps** : constat chiffré, comparaison, hypothèse formulée comme telle, recommandation adressée à quelqu'un de précis.

**Trois interdits** : pas de pourcentage sans effectif, pas de causalité tirée d'une corrélation, pas de limite passée sous silence.

**Piège de désagrégation** : « ménages dirigés par une femme » n'est pas « femmes bénéficiaires ». Le second se compte dans la table des individus.

---

## 10. Les définitions à restituer sans hésiter

| Terme | En une phrase |
|---|---|
| Clé primaire | Identifie une ligne de façon unique, non nulle et unique |
| Clé étrangère | Référence la clé primaire d'une autre table, garantit l'intégrité référentielle |
| Index | Structure auxiliaire qui évite de parcourir toute la table, comme l'index d'un livre |
| Transaction | Unité atomique : tout réussit ou rien n'a lieu |
| ACID | Atomicité, Cohérence, Isolation, Durabilité |
| Deadlock | Deux transactions s'attendent mutuellement ; remède : même ordre d'accès, transactions courtes, index adaptés |
| N+1 | Une requête par élément d'une liste au lieu d'une jointure unique |
| Vue | Requête enregistrée, recalculée à chaque appel ; matérialisée, elle est stockée et rafraîchie |
| Normalisation | Chaque fait écrit à un seul endroit |
| Dénormalisation | Duplication assumée pour la performance en lecture ; table dérivée, jamais saisie |
| Idempotence | Rejouer l'opération ne change pas le résultat |
| Pseudonymisation | Réversible via une table de correspondance ; reste une donnée personnelle |
| k-anonymat | Chaque combinaison de quasi-identifiants partagée par au moins k personnes |
| RPO / RTO | Perte maximale acceptable / délai de rétablissement acceptable |
| FCS / rCSI | Score de consommation alimentaire pondéré / indice réduit des stratégies de survie |
| PDM | Post-distribution monitoring, enquête de suivi après distribution |
| RRM | Mécanisme de réponse rapide |

---

## 11. Les douze phrases à savoir dire

Elles sont courtes, exactes, et chacune répond à une famille entière de questions. Apprends-les au sens, pas au mot.

1. « La qualité se garantit d'abord dans le formulaire, ensuite dans le schéma, et seulement en dernier recours dans le nettoyage. »
2. « Le schéma empêche ce qu'on peut empêcher, les contrôles détectent le reste. »
3. « Une contrainte d'unicité sur le triplet ménage, activité et date rend le double paiement impossible plutôt que détectable. »
4. « Une sauvegarde jamais restaurée n'est pas une sauvegarde, c'est une hypothèse. »
5. « Je ne devine pas, je mesure : je lis le plan d'exécution avant de toucher à quoi que ce soit. »
6. « On n'exporte jamais plus de données que ce que la question posée exige. »
7. « Retirer les noms n'anonymise pas : un ménage sur cinq reste identifiable sur quatre quasi-identifiants. »
8. « Le rapprochement approximatif produit des candidats à vérifier, jamais des fusions automatiques. »
9. « Un algorithme classe, il ne sélectionne pas : la décision appartient au comité communautaire. »
10. « Un import qui ne boucle pas perd des données sans le dire. »
11. « Sur des données de bénéficiaires, on ne supprime pas, on désactive. »
12. « Un bailleur pardonne une donnée imparfaite documentée ; il ne pardonne pas une donnée imparfaite dissimulée. »

---

## 12. Réponses calibrées

### Le pitch de 90 secondes

« Je suis développeur et gestionnaire de données, avec une expérience partagée entre l'ingénierie logicielle et le suivi-évaluation d'ONG en Haïti. Côté technique, j'ai administré des bases MySQL et des systèmes de collecte mWater à la Fondation Caris et pour le programme HANWASH, et j'ai travaillé sur l'optimisation de bases en production : sur un projet, j'ai identifié et corrigé un problème de requêtes N+1 qui faisait passer une page de trente-six secondes à moins d'une demi-seconde, et j'ai ajouté des index composites qui ont supprimé les blocages en accès concurrent. Côté gestion de l'information, j'ai construit et nettoyé des listes de bénéficiaires, avec un travail systématique de dédoublonnage, et produit les analyses et les tableaux de bord attendus par les bailleurs. Ce qui m'intéresse dans ce poste, c'est qu'il réunit exactement ces deux faces : concevoir et administrer proprement la base, et en tirer des analyses fiables. Je travaille en français et en créole, je connais le terrain haïtien, et j'ai l'habitude de documenter mes procédures pour qu'elles survivent à mon départ. »

### « Pourquoi devrions-nous vous choisir ? »

« Parce que je couvre les deux moitiés du poste. Beaucoup de candidats savent faire des tableaux croisés et lire un export Kobo ; moins savent concevoir un schéma, poser les bonnes contraintes, écrire un script d'import réconcilié et défendable, mettre en place une sauvegarde qui se restaure vraiment et une matrice de droits. Et je fais attention à ce que la plupart oublient : la protection des données des bénéficiaires, qui en Haïti n'est pas une formalité administrative. Concrètement, dans mon premier mois je vous livrerais trois choses : un dictionnaire de données qui relie chaque champ de la base à la question Kobo qui l'alimente, une sauvegarde automatique avec restauration de contrôle, et un tableau de bord de validation dont toutes les lignes doivent renvoyer zéro avant chaque rapport. »

### « Votre principale faiblesse ? »

« J'ai tendance à vouloir bien faire les choses du premier coup, à automatiser et documenter avant que ce soit strictement nécessaire, et sur un projet en urgence cela peut retarder une livraison. Ce que j'ai appris à faire, c'est de distinguer explicitement ce qui est urgent de ce qui est structurant, et de livrer d'abord une version qui répond au besoin du jour, quitte à la reprendre ensuite. Sur un rapport de mi-parcours dû dans trois semaines, je produis le rapport et je construis la base en le produisant, plutôt que de construire la base puis le rapport. »

### Les cinq questions techniques les plus probables

Pour chacune, la réponse développée est dans le module indiqué, et elle est rédigée telle qu'on la dit à l'oral.

| Question | Où |
|---|---|
| Différence entre `WHERE` et `HAVING` | [01](01_sql_analyste_et_gestion_bdd.md) |
| Comment identifiez-vous et supprimez-vous des doublons | [01](01_sql_analyste_et_gestion_bdd.md) |
| Une requête est devenue lente, comment procédez-vous | [01](01_sql_analyste_et_gestion_bdd.md) · [03](03_administration_bdd.md) |
| Décrivez votre stratégie de sauvegarde | [03](03_administration_bdd.md) |
| Comment protégez-vous les données personnelles | [04](04_securite_protection_donnees.md) |

### Les questions à poser en fin d'entretien

Trois suffisent, et elles doivent montrer que tu penses déjà au poste. Quels sont aujourd'hui les outils en place — une base existante, des classeurs Excel, un serveur Kobo ? Quel est le rythme de reporting attendu par les bailleurs principaux, et quels indicateurs sont les plus scrutés ? Comment se répartissent les responsabilités entre l'assistant base de données, le responsable MEAL et les superviseurs de collecte sur la qualité des données ?

Sur la question du salaire, réponds par une fourchette annoncée calmement, en précisant qu'elle tient compte du niveau du poste, de l'échelle salariale de l'organisation et du contexte de Port-au-Prince — et demande la grille si elle existe, ce qui est le cas dans la plupart des ONG internationales.

---

## 13. Les dix erreurs qui coûtent des points

Elles sont classées par fréquence, pas par gravité.

Oublier le `DISTINCT` quand on compte des entités et non des lignes, ce qui gonfle le chiffre d'un facteur deux ou trois.

Utiliser un `INNER JOIN` là où un `LEFT JOIN` s'impose, ce qui fait disparaître silencieusement les cas à zéro — précisément ceux qui intéressent la redevabilité.

Écrire `100` au lieu de `100.0` dans un calcul de pourcentage, ce qui renvoie zéro par division entière.

Comparer une colonne à `NULL` avec `=` au lieu de `IS NULL`.

Filtrer une fonction fenêtre dans le `WHERE` sans l'encapsuler.

Annoncer un pourcentage sans son effectif.

Confondre « ménages dirigés par une femme » et « femmes bénéficiaires ».

Affirmer qu'un fichier sans noms est anonyme.

Répondre à une question de suppression sans mentionner les trois précautions — `SELECT` avant `DELETE`, transaction, table de rejets.

Et la plus coûteuse en entretien : présenter un outil ou une technique sans dire quel problème il résout. Chaque réponse doit commencer par le problème.

---

## 14. Checklist du jour J

**La veille** : relire cette fiche une fois en entier ; refaire les six requêtes de la partie C de l'[examen blanc](08_examen_blanc_corrige.md) sur la base, sans regarder le corrigé ; vérifier que l'ordinateur portable démarre, que SQLite et Excel s'ouvrent, et que les fichiers d'exercice sont accessibles hors connexion ; préparer les documents demandés — CV, diplômes, pièce d'identité, références ; dormir.

**Le matin** : relire les sections 2, 11 et 12 uniquement. Emporter de quoi écrire, une bouteille d'eau, une copie papier du CV, et si l'épreuve est sur ordinateur, une clé USB avec la base d'exercice.

**Pendant l'écrit** : lire toutes les questions avant de commencer, répondre d'abord à ce qui est sûr, marquer les questions laissées pour la fin, garder cinq minutes de relecture.

**Pendant le pratique** : ouvrir la base et **regarder le schéma avant d'écrire la première requête** — deux minutes investies là évitent dix minutes d'erreurs. Écrire d'abord la requête la plus simple qui produit un résultat, vérifier que le nombre de lignes est plausible, puis raffiner. Commenter à voix haute si quelqu'un observe : on note aussi le raisonnement. Ne jamais laisser une case vide — une requête imparfaite avec une phrase d'explication vaut mieux que rien.

**Pendant l'oral** : commencer par le problème, pas par l'outil. Donner un chiffre quand tu en as un. Dire « je ne sais pas, voici comment je le trouverais » plutôt que d'inventer — c'est une réponse qui rassure un responsable MEAL, parce que c'est exactement ce qu'on attend de quelqu'un qui manipule des données.

---

*Modules du parcours : [01 SQL](01_sql_analyste_et_gestion_bdd.md) · [02 Modélisation](02_modelisation_et_conception.md) · [03 Administration](03_administration_bdd.md) · [04 Sécurité](04_securite_protection_donnees.md) · [05 Kobo et PDM](05_kobo_ciblage_et_pdm.md) · [06 Gestion de l'information](06_gestion_information_archivage.md) · [07 Analyse et visualisation](07_analyse_visualisation_reporting.md) · [08 Examen blanc](08_examen_blanc_corrige.md)*
