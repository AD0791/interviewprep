# SQL pour analyste de données et gestionnaire de base

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Base d'exercice fournie : `meal_haiti.db` (SQLite) et son dump `meal_haiti.sql`. Toutes les requêtes de ce module ont été exécutées sur cette base ; les résultats affichés sont réels.*

> **Où ce module se situe dans le parcours.** Il couvre le SQL de l'analyste et les fondamentaux de gestion. Le poste ACTED va au-delà : la conception d'un schéma est traitée dans [Modélisation et conception](02_modelisation_et_conception.md), l'administration complète — sauvegarde, restauration, permissions, maintenance — dans [Administration de base de données](03_administration_bdd.md), et la protection des données bénéficiaires dans [Sécurité et protection des données](04_securite_protection_donnees.md). Ces trois modules travaillent sur une seconde base, `exercices/acted_bdd.db`, calquée sur un projet WASH et sécurité alimentaire réel avec ménages, assistances, enquêtes PDM et plaintes. Le présent module reste sur `meal_haiti.db`, plus simple, qui suffit à apprendre le SQL lui-même.

---

## Pourquoi ce module est différent des autres

Ta lettre de candidature à ACTED avance des affirmations techniques précises : résolution de boucles N+1 chez Tekkod avec un passage de 36 secondes à moins de 0,5 seconde, index composites pour éliminer verrous et blocages, administration de bases MySQL et mWater à la Fondation Caris et pour HANWASH, dédoublonnage systématique. Un examen technique ACTED sondera exactement ces points. Ce module a donc deux objectifs : te rendre fluide en SQL analytique, et te rendre capable de **défendre chacune de ces affirmations en trente secondes**.

---

## 1. Le problème avant l'outil

Tu disposes de trente écoles, 3 148 élèves, 360 relevés hebdomadaires et 983 distributions de kits. On te demande : quels élèves parrainés n'ont jamais reçu de kit ?

Dans Excel, cela suppose de croiser deux tables de tailles différentes, avec des recherches qui échouent silencieusement quand une clé manque, sur des volumes où le fichier commence à ramer. Et il faudra tout refaire le mois prochain.

En SQL, c'est six lignes, exécutées en quelques millisecondes, réutilisables indéfiniment, et surtout **exactes** : la jointure externe distingue formellement « n'a rien reçu » de « n'existe pas dans la table ». C'est ce que fait une base de données, et c'est pourquoi ACTED recrute un assistant base de données plutôt qu'un utilisateur d'Excel.

```sql
SELECT COUNT(*) AS parraines_sans_kit
FROM eleves el
LEFT JOIN distributions d ON d.id_eleve = el.id_eleve
WHERE el.parraine = 1 AND d.id_distribution IS NULL;
-- Résultat réel : 440
```

Quatre cent quarante élèves parrainés n'ont reçu aucune distribution. Voilà une information de redevabilité qu'aucun tableau croisé ne t'aurait donnée aussi sûrement.

---

## 2. La base d'exercice

Cinq tables de production plus une table de travail.

`regions` contient les quatre départements. `ecoles` contient trente écoles avec leur région, commune, milieu, nombre de salles, présence d'une cantine et d'un point d'eau. `eleves` contient 3 148 élèves avec nom, prénom, sexe, date de naissance, statut de parrainage et statut de scolarité — **dont 25 doublons volontaires** pour l'exercice de dédoublonnage. `suivi_hebdo` contient les 360 relevés hebdomadaires propres. `distributions` contient 983 distributions de kits.

Enfin `staging_data_center` contient les **356 lignes sales** du module Excel : doublons, texte dans les colonnes numériques, incohérences métier, libellés non harmonisés. C'est la table sur laquelle s'entraîner au nettoyage en SQL.

Pour ouvrir la base :

```bash
python3 -c "
import sqlite3, pandas as pd
con = sqlite3.connect('meal_haiti.db')
print(pd.read_sql('SELECT * FROM ecoles LIMIT 5', con))
"
```

Le schéma :

```sql
CREATE TABLE regions(
  id_region INTEGER PRIMARY KEY,
  nom_region TEXT NOT NULL UNIQUE);

CREATE TABLE ecoles(
  code_ecole  TEXT PRIMARY KEY,
  nom_ecole   TEXT NOT NULL,
  id_region   INTEGER NOT NULL,
  commune     TEXT,
  milieu      TEXT CHECK(milieu IN ('Rural','Peri-urbain')),
  nb_salles   INTEGER CHECK(nb_salles > 0),
  cantine     TEXT CHECK(cantine IN ('Oui','Non')),
  eau_potable TEXT CHECK(eau_potable IN ('Oui','Non')),
  FOREIGN KEY(id_region) REFERENCES regions(id_region));

CREATE TABLE eleves(
  id_eleve   INTEGER PRIMARY KEY,
  code_ecole TEXT NOT NULL,
  nom TEXT NOT NULL, prenom TEXT NOT NULL,
  sexe TEXT CHECK(sexe IN ('F','M')),
  date_naissance DATE,
  parraine INTEGER NOT NULL CHECK(parraine IN (0,1)),
  date_inscription DATE,
  statut TEXT CHECK(statut IN ('actif','abandon','transfere')),
  FOREIGN KEY(code_ecole) REFERENCES ecoles(code_ecole));

CREATE TABLE suivi_hebdo(
  id_suivi INTEGER PRIMARY KEY,
  code_ecole TEXT NOT NULL,
  semaine INTEGER NOT NULL CHECK(semaine BETWEEN 1 AND 52),
  date_saisie DATE,
  jours_classe INTEGER CHECK(jours_classe BETWEEN 0 AND 6),
  eleves_inscrits INTEGER, eleves_presents INTEGER,
  eleves_presents_parraines INTEGER, repas_servis INTEGER,
  enseignants_prevus INTEGER, enseignants_presents INTEGER,
  FOREIGN KEY(code_ecole) REFERENCES ecoles(code_ecole),
  UNIQUE(code_ecole, semaine));
```

Observe la dernière ligne. La contrainte `UNIQUE(code_ecole, semaine)` **rend physiquement impossible** d'insérer deux relevés pour la même école la même semaine. C'est le prolongement direct du principe des modules précédents : la qualité se garantit d'abord dans le formulaire, ensuite dans le schéma, et seulement en dernier recours dans le nettoyage. Savoir dire cela lors d'un entretien base de données est un argument fort.

---

## 3. Le modèle relationnel

Une **clé primaire** identifie de manière unique une ligne : elle est non nulle et unique. Une **clé étrangère** référence la clé primaire d'une autre table et garantit l'intégrité référentielle — impossible d'enregistrer un suivi pour une école qui n'existe pas.

La **normalisation** élimine la redondance. En première forme normale, chaque cellule contient une valeur atomique — pas de liste dans une colonne. En deuxième forme normale, tout attribut non clé dépend de la totalité de la clé. En troisième forme normale, aucun attribut non clé ne dépend d'un autre attribut non clé.

L'exemple concret sur notre base : si l'on stockait le nom de la région directement dans la table `ecoles`, il faudrait le corriger trente fois en cas de changement, avec le risque d'oublis créant des incohérences. En le sortant dans une table `regions` reliée par un identifiant, on ne le corrige qu'une fois. C'est **exactement** le problème des libellés d'écoles non harmonisés du module Excel, mais résolu structurellement.

Il faut aussi savoir défendre la **dénormalisation** : pour du reporting lourd, on accepte parfois de dupliquer des données afin d'éviter des jointures coûteuses. C'est un arbitrage entre intégrité en écriture et performance en lecture, pas une faute.

---

## 4. SQL analytique

### 4.1 L'ordre logique d'exécution

À connaître par cœur, car il explique la plupart des erreurs de débutant :

```
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

Deux conséquences directes. Premièrement, **on ne peut pas utiliser dans le `WHERE` un alias défini dans le `SELECT`**, puisque le `WHERE` s'exécute avant. Deuxièmement, **`WHERE` filtre les lignes avant l'agrégation, `HAVING` filtre les groupes après**. C'est la question d'entretien la plus fréquente sur le sujet.

### 4.2 Les NULL, piège à trois valeurs

La logique SQL est ternaire : vrai, faux, inconnu. Toute comparaison avec `NULL` renvoie « inconnu », donc `WHERE colonne = NULL` ne renvoie jamais rien. Il faut écrire `IS NULL` ou `IS NOT NULL`.

Conséquences à connaître : `COUNT(*)` compte toutes les lignes, `COUNT(colonne)` ignore les `NULL`. `SUM` et `AVG` ignorent les `NULL` — et donc `AVG` divise par le nombre de valeurs non nulles, pas par le nombre de lignes, ce qui peut surprendre. `NULL` dans un `NOT IN` fait échouer toute la condition, un piège redoutable qu'on contourne avec `NOT EXISTS`.

`COALESCE(a, b, c)` renvoie la première valeur non nulle. `NULLIF(a, b)` renvoie `NULL` si les deux sont égales — utile pour éviter une division par zéro : `x / NULLIF(y, 0)`.

**Le lien métier** : dans notre contexte, `NULL` signifie « non collecté » et zéro signifie « aucun ». Les confondre fausse tous les indicateurs. C'est le même principe que dans le module Excel, mais SQL a l'avantage de les distinguer nativement.

### 4.3 Agrégation

```sql
-- Taux de présence pondéré par région
SELECT r.nom_region,
       COUNT(*) AS observations,
       ROUND(100.0 * SUM(s.eleves_presents) / SUM(s.eleves_inscrits), 2) AS taux_pondere
FROM suivi_hebdo s
JOIN ecoles  e ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region
ORDER BY taux_pondere DESC;
```

| nom_region | observations | taux_pondere |
|---|---|---|
| Sud | 84 | 82,45 |
| Centre | 72 | 79,41 |
| Ouest | 96 | 72,69 |
| Artibonite | 108 | 71,66 |

**Comparaison instructive** : le module de statistiques calculait sur les mêmes données un taux **non pondéré** de 79,24 % pour le Sud. La version pondérée donne 82,45 %, soit **3,2 points d'écart**. La différence vient du fait que les grandes écoles du Sud ont de meilleurs taux, et la moyenne simple ne leur donnait pas leur poids réel. C'est la démonstration chiffrée du piège de la moyenne non pondérée — un exemple à raconter en entretien, avec les deux chiffres.

Note aussi le `100.0` plutôt que `100` : en SQL, la division de deux entiers renvoie un entier dans de nombreux moteurs, et l'on obtiendrait zéro. Forcer un opérande en décimal est un réflexe à avoir.

### 4.4 Les jointures

`INNER JOIN` ne conserve que les lignes appariées des deux côtés. `LEFT JOIN` conserve toutes les lignes de gauche, en remplissant de `NULL` ce qui manque à droite. `RIGHT JOIN` fait l'inverse. `FULL OUTER JOIN` conserve tout. `CROSS JOIN` produit le produit cartésien. Une **auto-jointure** joint une table à elle-même.

Le cas d'usage humanitaire canonique — et probablement une question d'examen ACTED — est **l'anti-jointure** : trouver ce qui n'existe pas dans l'autre table.

```sql
-- Élèves parrainés n'ayant reçu aucune distribution
SELECT el.id_eleve, el.nom, el.prenom, el.code_ecole
FROM eleves el
LEFT JOIN distributions d ON d.id_eleve = el.id_eleve
WHERE el.parraine = 1
  AND d.id_distribution IS NULL;
-- 440 lignes
```

Le motif `LEFT JOIN ... WHERE clé_droite IS NULL` est **le** motif à mémoriser. Il répond à toutes les questions de type « qui n'a pas reçu », « quelles écoles n'ont pas rapporté », « quels bénéficiaires ciblés n'ont pas été atteints ».

Le `CROSS JOIN` a aussi un usage précieux : **générer la grille théorique complète** pour mesurer la complétude.

```sql
-- Toutes les combinaisons école × semaine attendues, et ce qui manque
WITH semaines(s) AS (
  SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
  UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
  UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12)
SELECT e.code_ecole, sem.s AS semaine
FROM ecoles e
CROSS JOIN semaines sem
LEFT JOIN suivi_hebdo sh
       ON sh.code_ecole = e.code_ecole AND sh.semaine = sem.s
WHERE sh.id_suivi IS NULL;
```

Sur la table propre `suivi_hebdo`, cette requête ne renvoie rien : 360 relevés pour 360 attendus, complétude parfaite. Exécutée contre `staging_data_center`, elle révèle les sept absences du module Excel. **C'est la traduction en SQL du contrôle de complétude** — le premier réflexe de tout analyste.

### 4.5 Sous-requêtes et CTE

Une **CTE** (*Common Table Expression*), introduite par `WITH`, nomme un résultat intermédiaire. Elle rend une requête complexe lisible, et c'est un marqueur de maturité — un candidat qui écrit des CTE plutôt que des sous-requêtes imbriquées sur trois niveaux se remarque.

```sql
WITH taux_ecole AS (
  SELECT s.code_ecole,
         SUM(s.eleves_presents) AS presents,
         SUM(s.eleves_inscrits) AS inscrits,
         100.0 * SUM(s.eleves_presents) / SUM(s.eleves_inscrits) AS taux
  FROM suivi_hebdo s
  GROUP BY s.code_ecole
),
moyenne_generale AS (
  SELECT AVG(taux) AS moy FROM taux_ecole
)
SELECT e.nom_ecole, ROUND(t.taux, 1) AS taux,
       ROUND(t.taux - m.moy, 1) AS ecart_a_la_moyenne
FROM taux_ecole t
JOIN ecoles e ON e.code_ecole = t.code_ecole
CROSS JOIN moyenne_generale m
WHERE t.taux < m.moy
ORDER BY t.taux
LIMIT 5;
```

| nom_ecole | taux |
|---|---|
| Ecole Anse-Rouge | 56,5 |
| Ecole Gressier | 56,8 |
| Ecole Gonaives | 60,7 |
| Ecole Verrettes | 61,0 |
| Ecole Chantal | 63,3 |

Une **sous-requête corrélée** s'exécute une fois par ligne de la requête externe. Elle est expressive mais **coûteuse** : c'est l'une des formes que prend le problème N+1 en SQL pur, et l'on préfère presque toujours une jointure ou une fonction fenêtre.

### 4.6 Les fonctions fenêtre

C'est l'outil qui sépare l'analyste débutant du confirmé. Une fonction fenêtre calcule une valeur agrégée **sans réduire le nombre de lignes**.

```sql
SELECT semaine,
       ROUND(100.0*eleves_presents/eleves_inscrits, 1) AS taux,
       ROUND(AVG(100.0*eleves_presents/eleves_inscrits)
             OVER (ORDER BY semaine ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS moyenne_mobile_3,
       ROUND(100.0*eleves_presents/eleves_inscrits
             - LAG(100.0*eleves_presents/eleves_inscrits) OVER (ORDER BY semaine), 1) AS evolution
FROM suivi_hebdo
WHERE code_ecole = 'EC001'
ORDER BY semaine;
```

| semaine | taux | moyenne_mobile_3 | evolution |
|---|---|---|---|
| 1 | 69,5 | 69,5 | |
| 2 | 82,3 | 75,9 | 12,8 |
| 3 | 73,0 | 74,9 | −9,2 |
| 4 | 74,5 | 76,6 | 1,4 |
| 5 | 78,0 | 75,2 | 3,5 |
| 6 | 75,2 | 75,9 | −2,8 |

La moyenne mobile lisse le bruit hebdomadaire pour faire apparaître la tendance, et `LAG` donne l'évolution d'une semaine à l'autre. Ces deux colonnes sont exactement ce qu'attend un rapport mensuel.

Le classement par groupe :

```sql
SELECT nom_region, nom_ecole, taux FROM (
  SELECT r.nom_region, e.nom_ecole,
         ROUND(100.0*SUM(s.eleves_presents)/SUM(s.eleves_inscrits), 1) AS taux,
         RANK() OVER (PARTITION BY r.nom_region
                      ORDER BY SUM(s.eleves_presents)*1.0/SUM(s.eleves_inscrits) DESC) AS rg
  FROM suivi_hebdo s
  JOIN ecoles e  ON e.code_ecole = s.code_ecole
  JOIN regions r ON r.id_region  = e.id_region
  GROUP BY r.nom_region, e.nom_ecole)
WHERE rg = 1;
```

| nom_region | nom_ecole | taux |
|---|---|---|
| Artibonite | Ecole Dessalines | 89,1 |
| Centre | Ecole Thomonde | 93,2 |
| Ouest | Ecole Kenscoff | 87,1 |
| Sud | Ecole Camp-Perrin | 92,2 |

Différences à connaître : `ROW_NUMBER` numérote sans ex æquo, `RANK` laisse des trous après une égalité (1, 1, 3), `DENSE_RANK` n'en laisse pas (1, 1, 2). `NTILE(4)` découpe en quartiles. `SUM() OVER (ORDER BY ...)` donne un cumul.

**Il faut aussi savoir pourquoi on ne peut pas filtrer sur une fonction fenêtre dans le `WHERE`** : elle est calculée après le `WHERE` dans l'ordre d'exécution. Il faut donc l'encapsuler dans une sous-requête ou une CTE, comme ci-dessus.

### 4.7 Pivoter avec CASE

SQL standard n'a pas d'opérateur `PIVOT` universel. On l'obtient par agrégation conditionnelle.

```sql
SELECT r.nom_region,
  ROUND(AVG(CASE WHEN s.semaine BETWEEN 1  AND 4  THEN 100.0*s.eleves_presents/s.eleves_inscrits END), 1) AS periode_1,
  ROUND(AVG(CASE WHEN s.semaine BETWEEN 5  AND 8  THEN 100.0*s.eleves_presents/s.eleves_inscrits END), 1) AS periode_2,
  ROUND(AVG(CASE WHEN s.semaine BETWEEN 9  AND 12 THEN 100.0*s.eleves_presents/s.eleves_inscrits END), 1) AS periode_3
FROM suivi_hebdo s
JOIN ecoles e  ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region;
```

| nom_region | periode_1 | periode_2 | periode_3 |
|---|---|---|---|
| Artibonite | 74,3 | 72,5 | 69,1 |
| Centre | 77,5 | 81,6 | 74,9 |
| Ouest | 74,6 | 74,8 | 74,3 |
| Sud | 80,4 | 80,7 | 76,6 |

Une lecture immédiate : l'Artibonite décroche continûment (74,3 → 72,5 → 69,1) tandis que l'Ouest reste stable. C'est le type de tableau qui ouvre un rapport mensuel.

L'astuce à retenir : `CASE` sans `ELSE` renvoie `NULL`, et `AVG` ignore les `NULL`. La moyenne ne porte donc que sur les lignes de la période — pas besoin de filtrer.

---

## 5. Qualité des données et dédoublonnage

C'est le cœur du poste ACTED.

### 5.1 Profilage

```sql
-- Portrait d'une table en une requête
SELECT COUNT(*) AS lignes,
       COUNT(DISTINCT code_ecole) AS ecoles,
       SUM(CASE WHEN eleves_presents IS NULL THEN 1 ELSE 0 END) AS presents_manquants,
       MIN(eleves_inscrits) AS min_inscrits,
       MAX(eleves_inscrits) AS max_inscrits,
       ROUND(AVG(eleves_inscrits), 1) AS moy_inscrits
FROM suivi_hebdo;
```

Sur `staging_data_center`, SQLite permet un contrôle particulièrement élégant du typage :

```sql
SELECT typeof(eleves_presents) AS type_reel, COUNT(*)
FROM staging_data_center GROUP BY 1;
```

Il révèle immédiatement les cellules stockées en texte dans une colonne censée être numérique — l'équivalent SQL du test `NBVAL` moins `NB` du module Excel.

### 5.2 Détecter les doublons

```sql
-- Groupes de doublons sur la clé métier
SELECT code_ecole, nom, prenom, date_naissance, COUNT(*) AS occurrences
FROM eleves
GROUP BY code_ecole, nom, prenom, date_naissance
HAVING COUNT(*) > 1;
-- 25 groupes
```

Sur la table sale, la clé métier est le couple école-semaine :

```sql
SELECT code_ecole, semaine, COUNT(*) FROM staging_data_center
GROUP BY 1,2 HAVING COUNT(*) > 1;
-- 3 groupes en double
```

### 5.3 Dédoublonner proprement

La technique reine, et **celle qui justifie l'affirmation « élimination des doublons » de ta lettre** :

```sql
WITH numerotes AS (
  SELECT id_eleve,
         ROW_NUMBER() OVER (
           PARTITION BY code_ecole, nom, prenom, date_naissance
           ORDER BY id_eleve                     -- règle de conservation
         ) AS rang
  FROM eleves
)
SELECT COUNT(*) FROM numerotes WHERE rang > 1;
-- 25 lignes à supprimer
```

Le principe : on partitionne sur ce qui définit un doublon, on ordonne selon la règle qui détermine la ligne à conserver — la plus ancienne, la plus récente, la plus complète — et l'on ne garde que le rang 1. La suppression devient alors :

```sql
DELETE FROM eleves
WHERE id_eleve IN (
  SELECT id_eleve FROM (
    SELECT id_eleve,
           ROW_NUMBER() OVER (PARTITION BY code_ecole, nom, prenom, date_naissance
                              ORDER BY id_eleve) AS rang
    FROM eleves)
  WHERE rang > 1);
```

**Trois précautions à énoncer en entretien**, et elles comptent autant que la requête. D'abord, on exécute toujours le `SELECT` avant le `DELETE` pour voir ce qu'on s'apprête à détruire. Ensuite, on travaille dans une transaction, ce qui permet d'annuler. Enfin, on archive les lignes supprimées dans une table de rejets plutôt que de les perdre, parce qu'une décision de dédoublonnage peut se révéler fausse.

### 5.4 Le rapprochement approximatif

Les doublons parfaits sont les plus faciles. Le vrai problème est le nom haïtien orthographié de trois façons : « Jean-Baptiste », « Jean Baptiste », « Jn Baptiste ».

La première ligne de défense est la **normalisation** : passer en majuscules, supprimer les espaces, retirer la ponctuation, puis comparer.

```sql
SELECT UPPER(TRIM(REPLACE(REPLACE(nom,'-',''),' ',''))) AS nom_norm,
       COUNT(*) AS occurrences
FROM eleves
GROUP BY nom_norm
HAVING COUNT(*) > 1
ORDER BY occurrences DESC
LIMIT 10;
```

Au-delà, les moteurs proposent des outils phonétiques et de distance. `SOUNDEX` code un mot selon sa sonorité et regroupe les orthographes proches — disponible nativement dans MySQL, et dans PostgreSQL via l'extension `fuzzystrmatch`. La **distance de Levenshtein** compte le nombre minimal d'insertions, suppressions ou substitutions pour passer d'une chaîne à l'autre : deux chaînes à distance 1 ou 2 sont probablement la même personne mal saisie. PostgreSQL propose aussi l'extension `pg_trgm` et sa fonction `similarity()`, fondée sur les trigrammes, particulièrement efficace sur les noms.

**La règle de méthode**, plus importante que l'outil : un rapprochement approximatif produit des **candidats à vérifier**, jamais des fusions automatiques. Fusionner deux bénéficiaires distincts est une faute grave — elle prive quelqu'un de son assistance. On génère une liste de paires suspectes classées par score de similarité, et un humain arbitre. C'est exactement la même leçon que les faux positifs du module Excel.

### 5.5 Les contrôles de cohérence

Les règles de triangulation, transposées en SQL :

```sql
SELECT code_ecole, semaine,
  CASE WHEN eleves_presents > eleves_inscrits           THEN 'R1 presents>inscrits' END AS r1,
  CASE WHEN eleves_presents_parraines > eleves_presents THEN 'R2 parraines>presents' END AS r2,
  CASE WHEN repas_servis > eleves_presents*jours_classe  THEN 'R3 repas>maximum' END AS r3,
  CASE WHEN enseignants_presents = 0 AND eleves_presents > 0 THEN 'R4 sans enseignant' END AS r4
FROM staging_data_center
WHERE eleves_presents > eleves_inscrits
   OR eleves_presents_parraines > eleves_presents
   OR repas_servis > eleves_presents*jours_classe
   OR (enseignants_presents = 0 AND eleves_presents > 0);
```

Exécutée sur `suivi_hebdo` (données propres), elle ne renvoie **aucune ligne** — la preuve que la table de production est saine. Exécutée sur `staging_data_center`, elle remonte les violations du module Excel. **Faire tourner le même contrôle sur les deux tables et montrer que la première est propre est une excellente démonstration en examen.**

Mieux encore, on peut empêcher ces lignes d'exister :

```sql
ALTER TABLE suivi_hebdo ADD CONSTRAINT chk_presents
  CHECK (eleves_presents <= eleves_inscrits);
```

Encore le même fil : contrainte dans le formulaire, contrainte dans le schéma, nettoyage en dernier recours.

---

## 6. Écrire dans la base : DDL, DML et transactions

Les sections précédentes lisent. Le poste ACTED demande aussi d'écrire, et c'est là que les erreurs coûtent cher, parce qu'une requête de lecture ratée ne détruit rien.

### 6.1 Les deux familles d'instructions

Le **DDL**, *data definition language*, définit la structure : `CREATE`, `ALTER`, `DROP`, `TRUNCATE`. Le **DML**, *data manipulation language*, manipule le contenu : `INSERT`, `UPDATE`, `DELETE`, `SELECT`. La distinction n'est pas académique : dans la plupart des moteurs, le DDL déclenche une validation implicite, ce qui veut dire qu'un `ALTER TABLE` ne s'annule pas par un `ROLLBACK`. SQLite et PostgreSQL font exception et savent annuler du DDL ; MySQL ne le sait pas. C'est une différence que peu de candidats connaissent.

Il faut aussi distinguer `DELETE` de `TRUNCATE`. Le premier supprime ligne à ligne, se filtre par une clause `WHERE`, déclenche les déclencheurs et s'annule. Le second vide la table d'un coup, ne se filtre pas, ne déclenche rien et, dans la plupart des moteurs, ne s'annule pas. Sur une table de bénéficiaires, `TRUNCATE` ne doit jamais être tapé.

### 6.2 La transaction, démontrée

Une transaction regroupe plusieurs opérations en une unité atomique : tout réussit, ou rien n'a lieu. C'est ce qui permet de corriger une donnée **et** de journaliser la correction sans risquer que l'une des deux passe sans l'autre.

Le relevé de l'école EC016 en semaine 6 affiche 155 élèves présents pour 201 inscrits, et le coordonnateur confirme que le bon chiffre est 175.

```sql
BEGIN TRANSACTION;

UPDATE suivi_hebdo
SET eleves_presents = 175
WHERE code_ecole = 'EC016' AND semaine = 6;

INSERT INTO journal_corrections
  (code_ecole, semaine, champ, ancienne_valeur, nouvelle_valeur, motif, horodatage)
VALUES
  ('EC016', 6, 'eleves_presents', '155', '175',
   'confirme par coordonnateur', datetime('now'));

ROLLBACK;   -- ou COMMIT
```

Après le `ROLLBACK`, une vérification montre que `eleves_presents` vaut toujours 155 **et** que la table `journal_corrections` est vide. Les deux opérations ont disparu ensemble : c'est l'atomicité. Si l'on avait écrit `COMMIT`, les deux seraient présentes ensemble.

La discipline pratique qui en découle vaut d'être énoncée à l'oral. Avant toute écriture sur des données réelles, on ouvre une transaction, on exécute, on **vérifie par un `SELECT` à l'intérieur de la transaction**, et on ne valide qu'après. Un `ROLLBACK` coûte zéro ; une restauration de sauvegarde coûte une demi-journée.

### 6.3 La règle du SELECT avant le DELETE

C'est la règle la plus importante de cette section, et elle tient en une phrase : **on écrit toujours le `SELECT` avec exactement la même clause `WHERE` avant de la transformer en `DELETE` ou en `UPDATE`.**

```sql
-- 1. On regarde
SELECT COUNT(*) FROM eleves WHERE statut = 'abandon' AND date_inscription < '2025-01-01';
-- 2. Seulement ensuite, et dans une transaction
BEGIN;
DELETE FROM eleves WHERE statut = 'abandon' AND date_inscription < '2025-01-01';
COMMIT;
```

Le piège classique, qui a détruit plus de bases que n'importe quelle panne matérielle, est le `UPDATE` dont la clause `WHERE` a été oubliée ou tronquée. `UPDATE eleves SET statut = 'actif'` sans `WHERE` met 3 148 lignes à jour en une milliseconde et rien ne prévient. La parade est la transaction, et la vérification du nombre de lignes affectées : si le moteur annonce 3 148 lignes modifiées alors qu'on en attendait douze, on annule.

### 6.4 L'insertion avec gestion de conflit

Le besoin est constant en import : on reçoit un lot de relevés dont certains existent déjà. Insérer bêtement viole la contrainte d'unicité et interrompt tout le traitement.

```sql
INSERT INTO suivi_hebdo (code_ecole, semaine, eleves_inscrits, eleves_presents)
VALUES ('EC001', 1, 200, 180);
-- Runtime error: UNIQUE constraint failed: suivi_hebdo.code_ecole, suivi_hebdo.semaine
```

Trois solutions existent, et le choix dépend de l'intention. `INSERT OR IGNORE` passe silencieusement la ligne en conflit, ce qui convient quand la donnée déjà présente fait foi. `ON CONFLICT ... DO NOTHING` fait la même chose de façon explicite et lisible, et c'est la forme à préférer. `ON CONFLICT ... DO UPDATE`, appelé *upsert*, met à jour la ligne existante avec les nouvelles valeurs.

```sql
INSERT INTO suivi_hebdo (code_ecole, semaine, eleves_inscrits, eleves_presents)
VALUES ('EC001', 1, 200, 180)
ON CONFLICT (code_ecole, semaine)
DO UPDATE SET eleves_presents = excluded.eleves_presents;
```

Le mot-clé `excluded` désigne la ligne qu'on tentait d'insérer. Après exécution, la ligne affiche `eleves_presents = 180` mais `eleves_inscrits = 141`, sa valeur d'origine : **seules les colonnes citées dans le `DO UPDATE` sont modifiées.** C'est un piège classique — on croit avoir remplacé la ligne, on n'en a remplacé qu'une colonne.

L'équivalent MySQL s'écrit `INSERT ... ON DUPLICATE KEY UPDATE`. L'intérêt de ce motif pour le poste est direct : c'est lui qui rend un import **idempotent**, c'est-à-dire rejouable sans créer de doublon, propriété indispensable en bureau terrain où l'on relance un traitement parce qu'on ne sait plus s'il a abouti.

### 6.5 Les opérations ensemblistes

`UNION` empile deux résultats en éliminant les doublons ; `UNION ALL` les empile sans dédoublonner et coûte moins cher. `INTERSECT` garde ce qui est dans les deux ; `EXCEPT`, appelé `MINUS` sous Oracle, garde ce qui est dans le premier et pas dans le second.

```sql
SELECT 'propre' AS source, COUNT(*) FROM suivi_hebdo
UNION ALL
SELECT 'sale',            COUNT(*) FROM staging_data_center;
```

| source | count |
|---|---|
| propre | 360 |
| sale | 356 |

C'est le motif du tableau de bord de validation : une ligne par contrôle, empilées par `UNION ALL`, chacune devant afficher zéro. Le module [Administration](03_administration_bdd.md) en donne la version complète.

`EXCEPT` a un usage précieux en réconciliation : la liste des couples école-semaine attendus moins la liste des couples reçus donne exactement les relevés manquants, sans écrire de jointure.

### 6.6 Dates et chaînes, les fonctions qui servent vraiment

Le traitement des dates est la source d'erreur numéro un des imports. En SQLite, `strftime('%Y-%m', date_saisie)` extrait le mois, ce qui permet de grouper par période, et `julianday(a) - julianday(b)` donne un écart en jours, utilisé pour mesurer un délai entre annonce et distribution. `date('now', '-7 days')` calcule une borne glissante. En PostgreSQL, on écrit `date_trunc('month', d)` et `age(a, b)` ; en MySQL, `DATE_FORMAT` et `DATEDIFF`.

Côté chaînes, cinq fonctions couvrent l'essentiel du nettoyage : `TRIM` retire les espaces de bord, `UPPER` et `LOWER` uniformisent la casse, `REPLACE` supprime la ponctuation, `SUBSTR` extrait un fragment, `LENGTH` détecte les valeurs tronquées, et `||` concatène — `CONCAT` sous MySQL. La combinaison `UPPER(TRIM(REPLACE(REPLACE(nom,'-',''),' ','')))` produit la clé normalisée qui sert à rapprocher « Jean-Baptiste », « Jean Baptiste » et « JEAN BAPTISTE ».

Le rappel qui accompagne toujours ces fonctions : **appliquer une fonction à une colonne dans une clause `WHERE` annule l'usage de l'index**. Si l'on doit filtrer souvent sur une valeur normalisée, on stocke la colonne normalisée à côté, ou l'on crée un index fonctionnel.

---

## 7. Gestion et performance de base de données

Cette section adresse directement les affirmations de ta lettre ACTED.

### 7.1 Les index

Un index est une structure auxiliaire — typiquement un arbre B — qui permet de retrouver des lignes sans parcourir toute la table. L'analogie : l'index d'un livre, qui évite de lire les 400 pages pour trouver un mot.

```sql
CREATE INDEX idx_suivi_ecole_semaine ON suivi_hebdo(code_ecole, semaine);
CREATE INDEX idx_eleves_ecole        ON eleves(code_ecole);
CREATE INDEX idx_distrib_eleve       ON distributions(id_eleve);
```

Ce qu'il faut savoir expliquer :

**L'ordre des colonnes dans un index composite est décisif.** Un index sur `(code_ecole, semaine)` sert une requête filtrant sur `code_ecole` seul, ou sur les deux, mais **pas** une requête filtrant sur `semaine` seule. C'est la règle du préfixe le plus à gauche, et c'est une question d'entretien très fréquente. On place donc en premier la colonne la plus sélective ou la plus souvent filtrée.

**Un index a un coût.** Il accélère la lecture mais ralentit chaque insertion, mise à jour et suppression, puisqu'il faut le maintenir. Il consomme aussi de l'espace disque. Indexer toutes les colonnes est une erreur de débutant.

**Un index sur une colonne peu sélective est inutile.** Indexer une colonne « sexe » à deux valeurs n'apporte rien : le moteur préférera parcourir la table.

**Un index composite couvrant** contient toutes les colonnes nécessaires à la requête, qui peut alors être résolue sans jamais lire la table elle-même — on parle d'*index-only scan*.

**Une fonction appliquée à la colonne annule l'index.** Écrire `WHERE UPPER(nom) = 'JEAN'` empêche l'usage d'un index sur `nom` ; il faut soit créer un index fonctionnel, soit réécrire la condition.

### 7.2 Lire un plan d'exécution

```sql
EXPLAIN QUERY PLAN
SELECT * FROM suivi_hebdo s
JOIN ecoles e ON e.code_ecole = s.code_ecole
WHERE s.semaine = 5;
```

Résultat réel sur la base :

```
SCAN s
SEARCH e USING INDEX sqlite_autoindex_ecoles_1 (code_ecole=?)
```

Interprétation : `SCAN s` signale un parcours complet de `suivi_hebdo`, parce qu'aucun index n'existe sur `semaine` — c'est le point à optimiser. `SEARCH e USING INDEX` indique que la jointure sur `ecoles` utilise l'index automatique de la clé primaire, ce qui est optimal.

En PostgreSQL on écrit `EXPLAIN ANALYZE`, qui exécute réellement la requête et donne les temps mesurés. Le vocabulaire à connaître : *Seq Scan* pour un parcours séquentiel, *Index Scan* pour un accès par index, *Nested Loop* pour une jointure par boucles imbriquées (efficace sur petits volumes), *Hash Join* (efficace sur gros volumes), *Merge Join* (sur données triées). Un *Seq Scan* sur une grande table dans une requête filtrante est le signal d'un index manquant.

En MySQL, la commande est `EXPLAIN` et l'on regarde les colonnes `type` (où `ALL` signale un parcours complet), `key` (l'index effectivement utilisé) et `rows` (l'estimation de lignes lues).

### 7.3 Le problème N+1

C'est l'affirmation la plus technique de ta lettre — il faut pouvoir l'expliquer sans hésiter.

**Le symptôme** : pour afficher une liste de trente écoles avec leur nombre d'élèves, le code exécute une requête pour obtenir les écoles, puis une requête par école pour compter ses élèves. Soit 1 + 30 = 31 allers-retours vers la base. Avec mille écoles, mille et une requêtes. Chaque aller-retour coûte quelques millisecondes de latence réseau, et le total explose alors que le travail réel est minime.

```python
# LE PROBLÈME
ecoles = db.query("SELECT * FROM ecoles")                    # 1 requête
for e in ecoles:
    n = db.query(f"SELECT COUNT(*) FROM eleves WHERE code_ecole='{e.code}'")  # N requêtes
```

**La détection** : activer le journal des requêtes et observer la même requête répétée avec des paramètres différents. C'est le motif visuel caractéristique — une cascade de lignes identiques dans le log.

**La correction** : une seule requête avec jointure et agrégation.

```sql
SELECT e.code_ecole, e.nom_ecole, COUNT(el.id_eleve) AS nb_eleves
FROM ecoles e
LEFT JOIN eleves el ON el.code_ecole = e.code_ecole
GROUP BY e.code_ecole, e.nom_ecole;
```

En ORM, la correction s'appelle le chargement anticipé : `selectinload` ou `joinedload` avec SQLAlchemy, `select_related` et `prefetch_related` avec Django. Le `LEFT JOIN` importe ici : il conserve les écoles sans aucun élève, avec un compte à zéro — un `INNER JOIN` les ferait disparaître silencieusement du rapport.

**Ta version parlée, calibrée sur ta lettre** : « Sur le projet Steam The Streets, la page de connexion mettait trente-six secondes. Le journal des requêtes montrait la même requête répétée des centaines de fois : un N+1 classique, une requête par élément de la liste. J'ai remplacé la boucle par une jointure unique avec agrégation, et ajouté le chargement anticipé côté ORM. Le temps est passé sous la demi-seconde. »

### 7.4 Transactions, verrous et blocages

Une **transaction** regroupe des opérations en une unité atomique. Les propriétés **ACID** : *Atomicité* (tout ou rien), *Cohérence* (les contraintes restent respectées), *Isolation* (les transactions concurrentes ne se marchent pas dessus), *Durabilité* (une transaction validée survit à une panne).

```sql
BEGIN TRANSACTION;
  UPDATE suivi_hebdo SET eleves_presents = 175 WHERE code_ecole='EC016' AND semaine=6;
  INSERT INTO journal_corrections VALUES ('EC016', 6, 'presents', 195, 175, 'confirmé par coordonnateur');
COMMIT;   -- ou ROLLBACK
```

Les **niveaux d'isolation**, du plus permissif au plus strict : *Read Uncommitted* (lectures sales possibles), *Read Committed* (défaut de PostgreSQL), *Repeatable Read* (défaut de MySQL InnoDB), *Serializable* (le plus strict, le plus coûteux). Les anomalies associées à connaître : lecture sale, lecture non répétable, lecture fantôme.

Un **verrou** protège une ressource pendant une modification. Un **blocage mutuel** (*deadlock*) survient quand deux transactions attendent chacune un verrou détenu par l'autre : la transaction A verrouille la ligne 1 et demande la ligne 2, pendant que la transaction B verrouille la ligne 2 et demande la ligne 1. Aucune ne peut avancer. Le moteur détecte la situation et annule l'une des deux.

**Les remèdes**, à savoir énumérer : accéder aux ressources **toujours dans le même ordre** dans tout le code applicatif — c'est la parade la plus efficace ; garder les transactions **courtes** en n'y plaçant jamais d'appel réseau ou d'attente utilisateur ; utiliser des index adaptés, car un verrou posé sur un parcours complet de table verrouille bien plus de lignes qu'un accès indexé — **c'est précisément le lien entre index composites et deadlocks que mentionne ta lettre** ; et prévoir une logique de nouvelle tentative côté application, puisqu'un blocage est un incident normal et non un bug.

**Ta version parlée** : « Lors d'accès concurrents massifs, nous observions des blocages mutuels sur les mises à jour. Deux causes : les transactions verrouillaient plus de lignes que nécessaire faute d'index adapté, et l'ordre d'accès aux tables variait selon les chemins de code. J'ai ajouté des index composites pour que les verrous portent sur des lignes ciblées plutôt que sur des plages entières, uniformisé l'ordre d'accès, et raccourci les transactions. Les blocages ont disparu. »

### 7.5 Vues et vues matérialisées

Une **vue** est une requête enregistrée sous un nom, recalculée à chaque appel. Elle sert à masquer la complexité et à restreindre l'accès.

```sql
CREATE VIEW v_indicateurs_mensuels AS
SELECT r.nom_region, s.semaine,
       SUM(s.eleves_presents) AS presents,
       SUM(s.eleves_inscrits) AS inscrits,
       ROUND(100.0*SUM(s.eleves_presents)/SUM(s.eleves_inscrits), 2) AS taux_presence,
       SUM(s.repas_servis) AS repas
FROM suivi_hebdo s
JOIN ecoles e  ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region, s.semaine;
```

Une **vue matérialisée** (PostgreSQL, Oracle) stocke physiquement le résultat et se rafraîchit à la demande. Elle convient parfaitement à un tableau de bord consulté cent fois par jour sur des données qui ne changent qu'une fois par semaine : on paie le calcul une fois au lieu de cent. MySQL ne les propose pas nativement — on émule avec une table de synthèse rafraîchie par tâche planifiée.

### 7.6 Sauvegarde, permissions, migrations

La sauvegarde se fait par export logique (`pg_dump`, `mysqldump`) ou copie physique, avec une distinction à connaître entre sauvegarde complète, différentielle et incrémentale, et la notion de restauration à un instant donné. **La règle à énoncer : une sauvegarde jamais testée en restauration n'est pas une sauvegarde.**

Les permissions suivent le principe du moindre privilège : `GRANT SELECT` pour un analyste, `GRANT SELECT, INSERT, UPDATE` pour un opérateur de saisie, et jamais `DELETE` sur les tables de production pour un compte applicatif. Sur des données de bénéficiaires, la protection des données personnelles impose en plus le chiffrement et la traçabilité des accès — un point sensible en contexte humanitaire, où l'identification d'un bénéficiaire peut le mettre en danger. **Le mentionner spontanément à ACTED est un très bon signal.**

Les **migrations** versionnent l'évolution du schéma. Alembic pour SQLAlchemy, Flyway ou Liquibase ailleurs. La règle : jamais de modification manuelle du schéma en production, toujours par script versionné et réversible.

### 7.7 MySQL et PostgreSQL

Ta lettre mentionne MySQL, alors sache situer les deux. MySQL avec InnoDB est très répandu, rapide en lecture, propose `SOUNDEX` nativement, et son isolation par défaut est *Repeatable Read*. PostgreSQL est plus strict sur les types et le standard SQL, propose des types avancés (JSONB, tableaux, types géographiques via PostGIS), les vues matérialisées, les index partiels et fonctionnels, les extensions comme `pg_trgm`, et son isolation par défaut est *Read Committed*. En contexte humanitaire, PostgreSQL est souvent préféré pour les données géospatiales et la rigueur transactionnelle.

---

## 8. Trente exercices sur la base fournie

**Fondamentaux.** Lister les écoles de l'Ouest triées par nombre de salles décroissant. Compter les élèves par sexe. Trouver les écoles sans cantine. Afficher les cinq écoles ayant le plus d'élèves parrainés. Compter les élèves ayant abandonné, par région.

**Agrégation.** Calculer le taux de présence pondéré par école. Le nombre total de repas servis par région. La moyenne du nombre de jours de classe par semaine. Le ratio repas sur élèves-jours par école. Le taux de présence des enseignants par région.

**Jointures.** Lister les élèves parrainés n'ayant reçu aucune distribution. Trouver les écoles n'ayant jamais reçu de distribution. Afficher pour chaque école son nombre d'élèves et son nombre de distributions. Identifier les élèves d'écoles sans point d'eau. Comparer, par région, le nombre d'écoles avec et sans cantine.

**Qualité.** Détecter les doublons d'élèves sur nom, prénom, date de naissance et école. Écrire la requête de dédoublonnage par `ROW_NUMBER`. Vérifier la complétude école-semaine par `CROSS JOIN`. Sur `staging_data_center`, détecter les lignes violant chacune des quatre règles de cohérence. Détecter les valeurs textuelles dans les colonnes numériques avec `typeof()`. Lister les libellés d'écoles non harmonisés en comparant à la table `ecoles`.

**Fonctions fenêtre.** Classer les écoles par taux au sein de chaque région. Calculer une moyenne mobile sur trois semaines pour chaque école. Calculer l'évolution semaine à semaine avec `LAG`. Découper les écoles en quartiles de performance avec `NTILE`. Calculer le cumul des repas servis dans le temps.

**Avancé.** Produire le tableau croisé région × période avec `CASE`. Écrire une CTE listant les écoles sous la moyenne nationale. Construire une vue d'indicateurs mensuels. Écrire la requête de détection des repas constants, puis la corriger pour éliminer les faux positifs des écoles sans cantine. Comparer taux pondéré et non pondéré par région et commenter l'écart.

Le dernier exercice est le plus formateur : il relie SQL, statistiques et méthode.

**Écriture et transactions**, à faire sur une copie de la base et jamais sur l'original. Corriger un relevé dans une transaction avec journalisation, puis annuler et vérifier que rien n'a bougé. Écrire l'`UPSERT` qui recharge un lot de relevés sans créer de doublon, et démontrer l'idempotence en le rejouant. Construire le tableau de bord de validation par `UNION ALL`, avec cinq contrôles devant tous renvoyer zéro. Produire par `EXCEPT` la liste des couples école-semaine attendus mais absents. Écrire la requête de suppression des élèves en abandon inscrits avant 2025, précédée de son `SELECT` de contrôle.

---

## Angles d'entretien

**« Quelle est la différence entre WHERE et HAVING ? »**

La différence tient au moment de l'exécution. SQL exécute une requête dans un ordre logique précis : d'abord `FROM` et les jointures, puis `WHERE`, puis `GROUP BY`, puis `HAVING`, puis `SELECT`, et enfin `ORDER BY`. Le `WHERE` intervient donc avant le regroupement : il filtre les lignes individuelles, et il ne peut pas porter sur une fonction d'agrégation puisque celle-ci n'a pas encore été calculée. Le `HAVING` intervient après le regroupement : il filtre les groupes constitués, et c'est là qu'on écrit une condition sur un `COUNT` ou une `SUM`. Concrètement, si je veux les écoles dont le taux de présence moyen dépasse quatre-vingts pour cent en ne considérant que les semaines où il y a eu classe, je mets la condition sur les jours de classe dans le `WHERE`, parce qu'elle porte sur chaque ligne, et la condition sur la moyenne dans le `HAVING`, parce qu'elle porte sur le groupe. Cet ordre d'exécution explique aussi pourquoi je ne peux pas réutiliser dans le `WHERE` un alias que j'ai défini dans le `SELECT` : au moment où le `WHERE` s'exécute, cet alias n'existe pas encore.

**« Comment identifiez-vous et supprimez-vous des doublons ? »**

Je commence toujours par définir ce qu'est un doublon dans le contexte métier, parce que ce n'est jamais évident. Sur une table de bénéficiaires, deux personnes portant le même nom ne sont pas nécessairement la même personne ; je retiens donc une clé métier composée, typiquement nom, prénom, date de naissance et école de rattachement. Je détecte ensuite avec un `GROUP BY` sur cette clé et un `HAVING COUNT` supérieur à un, ce qui me donne les groupes concernés. Pour la suppression, j'utilise la fonction fenêtre `ROW_NUMBER` en partitionnant sur la clé métier et en ordonnant selon la règle qui détermine quelle ligne conserver — la plus ancienne, la plus récente ou la plus complète — puis je ne garde que le rang un. Trois précautions systématiques : j'exécute le `SELECT` avant le `DELETE` pour voir exactement ce que je m'apprête à détruire, je travaille dans une transaction pour pouvoir annuler, et j'archive les lignes supprimées dans une table de rejets plutôt que de les perdre. Pour les doublons approximatifs, qui sont les plus fréquents dans le contexte haïtien où un même nom s'écrit de plusieurs façons, je normalise d'abord — majuscules, suppression des espaces et de la ponctuation — puis j'utilise des outils de similarité comme la distance de Levenshtein ou les trigrammes. Mais je ne fusionne jamais automatiquement : je produis une liste de paires suspectes classées par score, et un humain arbitre. Fusionner par erreur deux bénéficiaires distincts prive quelqu'un de son assistance, c'est une faute bien plus grave que de laisser passer un doublon.

**« Une requête est devenue très lente. Comment procédez-vous ? »**

Je ne devine pas, je mesure. Je commence par le plan d'exécution, avec `EXPLAIN ANALYZE` sur PostgreSQL ou `EXPLAIN` sur MySQL, et je cherche les parcours séquentiels de grandes tables dans une requête qui filtre : c'est le signal d'un index manquant. Je regarde aussi l'écart entre le nombre de lignes estimé et le nombre réellement traité, parce qu'un écart important signale des statistiques périmées. Ensuite je vérifie trois causes classiques. La première est l'index absent ou mal ordonné : sur un index composite, seules les requêtes filtrant sur le préfixe le plus à gauche en bénéficient, donc un index sur école et semaine ne sert à rien si je filtre uniquement sur la semaine. La deuxième est une fonction appliquée à la colonne dans la clause de filtrage, qui annule l'usage de l'index. La troisième est le problème N+1, qui vient du code applicatif plutôt que de la requête elle-même : au lieu d'une requête avec jointure, l'application en exécute une par élément d'une liste. Je l'ai rencontré sur un projet où la page de connexion mettait trente-six secondes ; le journal montrait la même requête répétée des centaines de fois. Je l'ai remplacée par une jointure unique avec agrégation et activé le chargement anticipé dans l'ORM, ce qui a ramené le temps sous la demi-seconde. Enfin, si la requête est intrinsèquement lourde et sert un tableau de bord consulté en permanence sur des données qui changent une fois par semaine, je ne cherche pas à l'optimiser indéfiniment : je la précalcule dans une vue matérialisée rafraîchie à intervalle régulier.

---

*Suite du parcours ACTED : [Modélisation et conception](02_modelisation_et_conception.md) · [Administration de base de données](03_administration_bdd.md) · [Sécurité et protection des données](04_securite_protection_donnees.md) · [Examen blanc corrigé](08_examen_blanc_corrige.md) · [Fiche de révision](00_fiche_revision_examen.md)*

*Modules liés côté PMEL : [Excel et le Data Center](../assitant_pmel/04_excel_data_center.md) · [Statistiques](../assitant_pmel/02_statistiques_pmel.md) · [Le processus MEAL](../assitant_pmel/01_meal_processus.md)*
