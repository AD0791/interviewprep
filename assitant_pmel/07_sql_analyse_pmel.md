# SQL pour l'analyse de données PMEL

*Module 7 — Préparation Assistant PMEL. Base d'exercice : `sql_exercices/meal_haiti.db`. Les trente exercices sont corrigés, et **toutes les requêtes de correction ont été exécutées** : les résultats affichés sont réels.*

> Ce module est orienté **analyse**, pour un test de type « écrivez la requête qui répond à cette question ». Le volet administration de base — index, plans d'exécution, transactions, N+1, deadlocks — est traité dans [`../acted_bdd/01_sql_analyste_et_gestion_bdd.md`](../acted_bdd/01_sql_analyste_et_gestion_bdd.md), qui vise le poste ACTED.

---

## 1. Pourquoi SQL sur un poste PMEL

L'offre de Parole et Action ne mentionne que Word, Excel et PowerPoint. Il est donc possible que SQL ne soit jamais évoqué. Mais deux raisons justifient de s'y préparer.

D'abord, si le Data Center est une plateforme de gestion, ses données vivent dans une base relationnelle, et savoir les interroger directement plutôt que d'attendre un export est un avantage décisif. Ensuite, une question SQL en test technique est une occasion de démontrer une rigueur d'analyste — le raisonnement qu'on met dans une requête est le même que celui qu'on met dans un tableau croisé, mais il est explicite et vérifiable.

La bonne posture en entretien : ne pas présenter SQL comme ton outil principal si l'offre ne le demande pas, mais savoir répondre avec assurance si la question vient.

---

## 2. Ouvrir la base

Pas besoin d'installer un serveur : la base est en SQLite, un simple fichier.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect("sql_exercices/meal_haiti.db")

# Une requête, un DataFrame
df = pd.read_sql("""
    SELECT nom_region, COUNT(*) AS nb_ecoles
    FROM ecoles e JOIN regions r ON r.id_region = e.id_region
    GROUP BY nom_region
""", con)
print(df)
```

Les tables : `regions` (4 lignes), `ecoles` (30), `eleves` (3 148, dont 25 doublons volontaires), `suivi_hebdo` (360 relevés propres), `distributions` (983), et `staging_data_center` (356 lignes sales, identiques au fichier du [module Excel](04_excel_data_center.md)).

---

## 3. Les six réflexes qui font la différence

Avant les exercices, six principes. Ils reviennent dans presque toutes les corrections, et les énoncer à voix haute pendant un test technique vaut autant que la requête elle-même.

**Premier réflexe : forcer le décimal.** En SQL, la division de deux entiers renvoie souvent un entier. `SUM(presents)/SUM(inscrits)` renvoie 0. Il faut écrire `100.0 * SUM(presents) / SUM(inscrits)`.

**Deuxième réflexe : le taux est un rapport de sommes.** Jamais `AVG(presents/inscrits)`, qui donne le même poids à une école de 80 élèves et à une école de 320. Toujours `SUM(presents) / SUM(inscrits)`. C'est le même piège qu'au [module Excel](04_excel_data_center.md) et au [module statistiques](02_statistiques_pmel.md), et il vaut la peine d'être signalé spontanément : *« j'utilise le rapport des sommes et non la moyenne des taux, parce que la moyenne simple n'est pas pondérée par la taille des écoles »*.

**Troisième réflexe : protéger la division par zéro** avec `NULLIF(dénominateur, 0)`.

**Quatrième réflexe : distinguer `WHERE` et `HAVING`.** `WHERE` filtre les lignes avant le regroupement, `HAVING` filtre les groupes après. Une condition portant sur un `SUM` ou un `COUNT` va nécessairement dans `HAVING`.

**Cinquième réflexe : `LEFT JOIN` pour ne perdre personne.** Un `INNER JOIN` fait disparaître silencieusement les écoles sans distribution ou les élèves sans suivi. Sur un rapport de redevabilité, une ligne qui disparaît est une erreur grave — c'est exactement le principe « une absence n'est pas un zéro » transposé en SQL.

**Sixième réflexe : compter les lignes attendues.** Trente écoles sur douze semaines font 360 relevés. Toute requête qui en renvoie un autre nombre doit être expliquée avant d'être exploitée.

---

## 4. Les trente exercices corrigés

### Bloc A — Sélection et filtrage

**E1. Lister les écoles du département de l'Ouest, de la plus grande à la plus petite en nombre de salles.**

```sql
SELECT e.code_ecole, e.nom_ecole, e.commune, e.nb_salles
FROM ecoles e
JOIN regions r ON r.id_region = e.id_region
WHERE r.nom_region = 'Ouest'
ORDER BY e.nb_salles DESC;
```

**E2. Combien d'écoles n'ont pas de cantine, et lesquelles ?**

```sql
SELECT code_ecole, nom_ecole FROM ecoles WHERE cantine = 'Non';
```

**E3. Compter les élèves par sexe et par statut de parrainage.**

```sql
SELECT sexe,
       SUM(parraine)              AS parraines,
       COUNT(*) - SUM(parraine)   AS non_parraines,
       ROUND(100.0 * SUM(parraine) / COUNT(*), 1) AS pct_parraines
FROM eleves
GROUP BY sexe;
```

| sexe | parraines | non_parraines | pct_parraines |
|---|---|---|---|
| F | 741 | 868 | 46,1 |
| M | 682 | 857 | 44,3 |

*Lecture : la part de filles parrainées dépasse légèrement celle des garçons, de 1,8 point. Un écart de cette ampleur ne justifie pas de conclusion sans test statistique.*

**E4. Calculer le taux d'abandon par département.**

```sql
SELECT r.nom_region,
       COUNT(*) AS eleves,
       SUM(CASE WHEN el.statut = 'abandon' THEN 1 ELSE 0 END) AS abandons,
       ROUND(100.0 * SUM(CASE WHEN el.statut = 'abandon' THEN 1 ELSE 0 END) / COUNT(*), 1) AS taux_abandon
FROM eleves el
JOIN ecoles  e ON e.code_ecole = el.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region
ORDER BY taux_abandon DESC;
```

| nom_region | eleves | abandons | taux_abandon |
|---|---|---|---|
| Centre | 679 | 36 | 5,3 |
| Sud | 667 | 34 | 5,1 |
| Ouest | 894 | 38 | 4,3 |
| Artibonite | 908 | 34 | 3,7 |

*Le motif `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` est le comptage conditionnel : à mémoriser, il sert partout.*

**E5. Trouver les écoles sans point d'eau potable et leur nombre d'élèves.**

```sql
SELECT e.nom_ecole, COUNT(el.id_eleve) AS eleves
FROM ecoles e
LEFT JOIN eleves el ON el.code_ecole = e.code_ecole
WHERE e.eau_potable = 'Non'
GROUP BY e.nom_ecole
ORDER BY eleves DESC;
```

### Bloc B — Agrégation et indicateurs

**E6. Taux de présence pondéré par département.**

```sql
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

**À dire pendant le test** : le module de statistiques calcule sur les mêmes données un taux **non pondéré** de 79,24 % pour le Sud. L'écart de 3,2 points vient de ce que les grandes écoles du Sud performent mieux, et la moyenne simple ne leur donnait pas leur poids réel.

**E7. Même indicateur, mais par école, en ne gardant que celles sous 70 %.**

```sql
SELECT e.nom_ecole,
       ROUND(100.0 * SUM(s.eleves_presents) / SUM(s.eleves_inscrits), 1) AS taux
FROM suivi_hebdo s
JOIN ecoles e ON e.code_ecole = s.code_ecole
GROUP BY e.nom_ecole
HAVING taux < 70
ORDER BY taux;
```

*Le filtre porte sur un agrégat, donc `HAVING` et non `WHERE`.*

**E8. Comparer la part des parrainés parmi les présents à leur part parmi les inscrits.**

```sql
SELECT r.nom_region,
       ROUND(100.0 * SUM(s.eleves_presents_parraines) / SUM(s.eleves_presents), 1) AS part_parmi_presents,
       ROUND(100.0 * SUM(CASE WHEN el.parraine = 1 THEN 1 ELSE 0 END) / COUNT(el.id_eleve), 1) AS part_parmi_inscrits
FROM suivi_hebdo s
JOIN ecoles  e  ON e.code_ecole = s.code_ecole
JOIN regions r  ON r.id_region  = e.id_region
JOIN eleves  el ON el.code_ecole = e.code_ecole
GROUP BY r.nom_region;
```

| nom_region | part_parmi_presents | part_parmi_inscrits |
|---|---|---|
| Artibonite | 50,2 | 44,9 |
| Centre | 49,9 | 43,4 |
| Ouest | 48,9 | 45,2 |
| Sud | 49,6 | 47,4 |

*Interprétation prudente : les parrainés sont sur-représentés parmi les présents de 2 à 6 points selon la région, ce qui suggère qu'ils viennent plus régulièrement. **Mais attention au biais de sélection** — les parrainés ne sont pas tirés au sort, ils sont choisis sur critères de vulnérabilité, donc cet écart ne mesure pas uniquement l'effet du parrainage. Formuler cette réserve spontanément est ce qui distingue un analyste.*

**E9. Nombre total de repas servis par département et par mois.**

```sql
SELECT r.nom_region,
       CASE WHEN s.semaine <= 4 THEN 'Mois 1'
            WHEN s.semaine <= 8 THEN 'Mois 2'
            ELSE 'Mois 3' END AS periode,
       SUM(s.repas_servis) AS repas
FROM suivi_hebdo s
JOIN ecoles  e ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region, periode;
```

**E10. Évolution globale mois par mois.**

```sql
SELECT CASE WHEN semaine <= 4 THEN 'Mois 1'
            WHEN semaine <= 8 THEN 'Mois 2'
            ELSE 'Mois 3' END AS periode,
       ROUND(100.0 * SUM(eleves_presents) / SUM(eleves_inscrits), 2) AS taux,
       SUM(repas_servis) AS repas
FROM suivi_hebdo
GROUP BY periode;
```

| periode | taux | repas |
|---|---|---|
| Mois 1 | 76,81 | 69 151 |
| Mois 2 | 77,00 | 70 616 |
| Mois 3 | 73,50 | 66 688 |

*La baisse du mois 3 est nette : 3,5 points. Rappel du [module statistiques](02_statistiques_pmel.md) : en milieu scolaire, une baisse peut être saisonnière ; on compare idéalement à la même période de l'année précédente avant de conclure.*

**E11. Nombre moyen de jours de classe effectifs, par département.**

```sql
SELECT r.nom_region, ROUND(AVG(s.jours_classe), 2) AS jours_moyens
FROM suivi_hebdo s
JOIN ecoles  e ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region;
```

**E12. Ratio repas servis sur élèves-jours présents, par école.**

```sql
SELECT e.nom_ecole, e.cantine,
       ROUND(1.0 * SUM(s.repas_servis)
             / NULLIF(SUM(s.eleves_presents * s.jours_classe), 0), 2) AS ratio
FROM suivi_hebdo s
JOIN ecoles e ON e.code_ecole = s.code_ecole
GROUP BY e.nom_ecole, e.cantine
ORDER BY ratio DESC;
```

| nom_ecole | cantine | ratio |
|---|---|---|
| Ecole Thomazeau | Oui | 0,96 |
| Ecole Petite-Riviere | Oui | 0,95 |
| Ecole Anse-Rouge | Oui | 0,94 |

*Ce ratio devrait valoir au plus 1. Toute valeur supérieure signale une incohérence. Sur les données propres, le maximum est 0,96 : la table est saine. Noter le `NULLIF` qui évite la division par zéro pour les écoles sans cantine.*

**E13. Nombre de distributions par type de kit.**

```sql
SELECT type_kit, COUNT(*) AS distributions, COUNT(DISTINCT id_eleve) AS beneficiaires
FROM distributions GROUP BY type_kit ORDER BY distributions DESC;
```

**E14. Effectif moyen par salle de classe, par école.**

```sql
SELECT e.nom_ecole, e.nb_salles, COUNT(el.id_eleve) AS eleves,
       ROUND(1.0 * COUNT(el.id_eleve) / NULLIF(e.nb_salles, 0), 1) AS eleves_par_salle
FROM ecoles e
LEFT JOIN eleves el ON el.code_ecole = e.code_ecole
GROUP BY e.nom_ecole, e.nb_salles
ORDER BY eleves_par_salle DESC;
```

**E15. Taux de présence des enseignants par département.**

```sql
SELECT r.nom_region,
       ROUND(100.0 * SUM(s.enseignants_presents) / SUM(s.enseignants_prevus), 1) AS taux_enseignants
FROM suivi_hebdo s
JOIN ecoles  e ON e.code_ecole = s.code_ecole
JOIN regions r ON r.id_region  = e.id_region
GROUP BY r.nom_region
ORDER BY taux_enseignants;
```

| nom_region | taux_enseignants |
|---|---|
| Ouest | 85,3 |
| Centre | 88,9 |
| Sud | 89,1 |
| Artibonite | 92,7 |

*Résultat contre-intuitif à commenter : l'Artibonite a le meilleur taux d'encadrement (92,7 %) et le plus faible taux de présence des élèves (71,66 %). L'absentéisme des élèves n'y est donc pas explicable par l'absence des enseignants — il faut chercher ailleurs. **Ce type de croisement, qui invalide une hypothèse évidente, est exactement ce qu'on attend d'un analyste.***

### Bloc C — Jointures

**E16. Élèves parrainés n'ayant reçu aucune distribution.**

```sql
SELECT el.id_eleve, el.nom, el.prenom, el.code_ecole
FROM eleves el
LEFT JOIN distributions d ON d.id_eleve = el.id_eleve
WHERE el.parraine = 1 AND d.id_distribution IS NULL;
-- 440 élèves
```

*Le motif `LEFT JOIN ... WHERE clé_droite IS NULL` est l'anti-jointure : à mémoriser absolument. Il répond à toutes les questions de type « qui n'a pas reçu ».*

**E17. Écoles n'ayant jamais reçu de distribution.**

```sql
SELECT e.code_ecole, e.nom_ecole
FROM ecoles e
LEFT JOIN distributions d ON d.code_ecole = e.code_ecole
WHERE d.id_distribution IS NULL;
```

**E18. Tableau de bord par école : élèves, distributions, taux de présence.**

```sql
SELECT e.nom_ecole,
       COUNT(DISTINCT el.id_eleve) AS eleves,
       COUNT(DISTINCT d.id_distribution) AS distributions,
       ROUND(100.0 * SUM(s.eleves_presents) / NULLIF(SUM(s.eleves_inscrits), 0), 1) AS taux
FROM ecoles e
LEFT JOIN eleves       el ON el.code_ecole = e.code_ecole
LEFT JOIN distributions d ON d.code_ecole = e.code_ecole
LEFT JOIN suivi_hebdo   s ON s.code_ecole = e.code_ecole
GROUP BY e.nom_ecole;
```

**Attention au piège de la multiplication des lignes** : joindre trois tables filles à une table mère démultiplie les lignes, et `SUM(s.eleves_presents)` sera gonflé. La solution propre est d'agréger chaque table séparément dans des CTE avant de les rassembler.

```sql
WITH par_eleves AS (
  SELECT code_ecole, COUNT(*) AS eleves FROM eleves GROUP BY code_ecole),
par_distrib AS (
  SELECT code_ecole, COUNT(*) AS distributions FROM distributions GROUP BY code_ecole),
par_suivi AS (
  SELECT code_ecole,
         100.0 * SUM(eleves_presents) / SUM(eleves_inscrits) AS taux
  FROM suivi_hebdo GROUP BY code_ecole)
SELECT e.nom_ecole,
       COALESCE(a.eleves, 0)        AS eleves,
       COALESCE(b.distributions, 0) AS distributions,
       ROUND(c.taux, 1)             AS taux
FROM ecoles e
LEFT JOIN par_eleves  a ON a.code_ecole = e.code_ecole
LEFT JOIN par_distrib b ON b.code_ecole = e.code_ecole
LEFT JOIN par_suivi   c ON c.code_ecole = e.code_ecole
ORDER BY taux;
```

*Savoir expliquer pourquoi la première version est fausse et la seconde correcte est une excellente réponse d'entretien.*

**E19. Complétude des remontées par département, sur la table sale.**

```sql
SELECT r.nom_region,
       COUNT(DISTINCT d.code_ecole || '-' || d.semaine) AS recues,
       COUNT(DISTINCT e.code_ecole) * 12 AS attendues,
       ROUND(100.0 * COUNT(DISTINCT d.code_ecole || '-' || d.semaine)
             / (COUNT(DISTINCT e.code_ecole) * 12), 1) AS completude
FROM ecoles e
JOIN regions r ON r.id_region = e.id_region
LEFT JOIN staging_data_center d ON d.code_ecole = e.code_ecole
GROUP BY r.nom_region;
```

| nom_region | recues | attendues | completude |
|---|---|---|---|
| Artibonite | 105 | 108 | 97,2 |
| Centre | 68 | 72 | 94,4 |
| Ouest | 96 | 96 | 100,0 |
| Sud | 84 | 84 | 100,0 |

*C'est le premier tableau à produire chaque mois. **Aucun indicateur ne devrait être publié sans lui.***

**E20. Lister précisément les couples école-semaine manquants.**

```sql
WITH semaines(n) AS (
  SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3  UNION ALL SELECT 4
  UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7  UNION ALL SELECT 8
  UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12)
SELECT e.code_ecole, s.n AS semaine
FROM ecoles e
CROSS JOIN semaines s
LEFT JOIN staging_data_center d
       ON d.code_ecole = e.code_ecole AND d.semaine = s.n
WHERE d.code_ecole IS NULL
ORDER BY 1, 2;
```

Résultat réel : `EC018` aux semaines 9, 10, 11 et 12 ; `EC022` aux semaines 5 et 6 ; `EC030` à la semaine 12. La même requête exécutée sur `suivi_hebdo` ne renvoie **aucune ligne** — la table de production est complète.

*Le `CROSS JOIN` qui génère la grille théorique est la traduction SQL de la matrice de complétude du [module Excel](04_excel_data_center.md).*

### Bloc D — Fonctions fenêtre

**E21. Classer les écoles au sein de leur département et ne garder que les trois dernières.**

```sql
WITH t AS (
  SELECT r.nom_region, e.nom_ecole,
         100.0 * SUM(s.eleves_presents) / SUM(s.eleves_inscrits) AS tx
  FROM suivi_hebdo s
  JOIN ecoles  e ON e.code_ecole = s.code_ecole
  JOIN regions r ON r.id_region  = e.id_region
  GROUP BY r.nom_region, e.nom_ecole)
SELECT nom_region, nom_ecole, ROUND(tx, 1) AS taux, rang
FROM (SELECT *, RANK() OVER (PARTITION BY nom_region ORDER BY tx) AS rang FROM t)
WHERE rang <= 3
ORDER BY nom_region, rang;
```

*Rappel : on ne peut pas filtrer une fonction fenêtre dans le `WHERE`, car elle est calculée après. Il faut l'encapsuler.*

**E22. Écart de chaque école à la moyenne de son département.**

```sql
WITH t AS (
  SELECT r.nom_region, e.nom_ecole,
         100.0 * SUM(s.eleves_presents) / SUM(s.eleves_inscrits) AS tx
  FROM suivi_hebdo s
  JOIN ecoles  e ON e.code_ecole = s.code_ecole
  JOIN regions r ON r.id_region  = e.id_region
  GROUP BY r.nom_region, e.nom_ecole)
SELECT nom_region, nom_ecole, ROUND(tx, 1) AS taux,
       ROUND(AVG(tx) OVER (PARTITION BY nom_region), 1) AS moyenne_region,
       ROUND(tx - AVG(tx) OVER (PARTITION BY nom_region), 1) AS ecart
FROM t
ORDER BY ecart
LIMIT 5;
```

| nom_region | nom_ecole | taux | moyenne_region | ecart |
|---|---|---|---|---|
| Ouest | Ecole Gressier | 56,8 | 74,6 | −17,8 |
| Sud | Ecole Chantal | 63,3 | 79,2 | −15,9 |
| Artibonite | Ecole Anse-Rouge | 56,5 | 72,0 | −15,5 |
| Centre | Ecole Hinche | 65,7 | 78,0 | −12,3 |
| Sud | Ecole Marceline | 67,7 | 79,2 | −11,5 |

*Voilà la liste des cinq écoles à visiter en priorité. C'est le type de résultat qui ouvre un plan d'action.*

**E23. Moyenne mobile sur trois semaines et évolution d'une semaine à l'autre, pour une école.**

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

**E24. Détecter les écoles sous 65 % pendant trois semaines consécutives.**

```sql
WITH t AS (
  SELECT code_ecole, semaine, 100.0*eleves_presents/eleves_inscrits AS tx
  FROM suivi_hebdo),
f AS (
  SELECT code_ecole, semaine, tx,
         LAG(tx)   OVER (PARTITION BY code_ecole ORDER BY semaine) AS prec1,
         LAG(tx,2) OVER (PARTITION BY code_ecole ORDER BY semaine) AS prec2
  FROM t)
SELECT code_ecole, semaine, ROUND(tx,1) AS taux
FROM f
WHERE tx < 65 AND prec1 < 65 AND prec2 < 65
ORDER BY code_ecole, semaine;
```

Résultat : `EC003` aux semaines 7, 8 et 9 ; `EC008` de la semaine 3 à la semaine 7.

*Une alerte fondée sur trois semaines consécutives est bien plus robuste qu'une alerte sur une valeur isolée : elle élimine le bruit d'une semaine exceptionnelle. C'est un raisonnement à valoriser — **le seuil ne suffit pas, il faut la persistance**.*

**E25. Découper les écoles en quartiles de performance.**

```sql
SELECT quartile, COUNT(*) AS ecoles,
       ROUND(MIN(tx),1) AS taux_min, ROUND(MAX(tx),1) AS taux_max
FROM (SELECT code_ecole, tx, NTILE(4) OVER (ORDER BY tx) AS quartile
      FROM (SELECT code_ecole,
                   100.0*SUM(eleves_presents)/SUM(eleves_inscrits) AS tx
            FROM suivi_hebdo GROUP BY code_ecole))
GROUP BY quartile;
```

| quartile | ecoles | taux_min | taux_max |
|---|---|---|---|
| 1 | 8 | 56,5 | 67,5 |
| 2 | 8 | 67,6 | 76,4 |
| 3 | 7 | 78,0 | 86,0 |
| 4 | 7 | 87,1 | 93,2 |

*L'écart entre le premier et le dernier quartile est de plus de 30 points. Cette dispersion est en soi une conclusion : le problème n'est pas « le réseau », c'est un quart des écoles.*

**E26. Cumul des repas servis au fil des semaines.**

```sql
SELECT semaine,
       SUM(repas_servis) AS repas_semaine,
       SUM(SUM(repas_servis)) OVER (ORDER BY semaine) AS cumul
FROM suivi_hebdo
GROUP BY semaine;
```

| semaine | repas_semaine | cumul |
|---|---|---|
| 1 | 17 846 | 17 846 |
| 2 | 17 023 | 34 869 |
| 3 | 16 894 | 51 763 |
| 4 | 17 388 | 69 151 |
| 5 | 18 158 | 87 309 |
| 6 | 18 138 | 105 447 |

*Le double `SUM(SUM(...)) OVER (...)` surprend, mais il est correct : l'agrégat interne s'applique au groupe, la fenêtre s'applique ensuite au résultat agrégé.*

### Bloc E — Qualité des données

**E27. Détecter les doublons dans la table sale.**

```sql
SELECT code_ecole, semaine, COUNT(*) AS occurrences
FROM staging_data_center
GROUP BY code_ecole, semaine
HAVING COUNT(*) > 1;
```

| code_ecole | semaine | occurrences |
|---|---|---|
| EC005 | 3 | 2 |
| EC005 | 4 | 2 |
| EC012 | 7 | 2 |

**E28. Détecter les valeurs textuelles dans une colonne numérique.**

```sql
SELECT typeof(eleves_presents) AS type_stocke, COUNT(*) AS lignes
FROM staging_data_center GROUP BY type_stocke;
```

*Sur cette base, l'import a converti toute la colonne en texte — ce qui est en soi l'anomalie à signaler. Pour retrouver les valeurs non numériques :*

```sql
SELECT code_ecole, semaine, eleves_presents
FROM staging_data_center
WHERE eleves_presents IS NOT NULL
  AND CAST(eleves_presents AS REAL) = 0
  AND eleves_presents NOT IN ('0', '0.0');
```

**E29. Détecter les libellés qui contredisent le référentiel.**

```sql
SELECT DISTINCT d.code_ecole, d.nom_ecole AS libelle_export, e.nom_ecole AS libelle_referentiel
FROM staging_data_center d
JOIN ecoles e ON e.code_ecole = d.code_ecole
WHERE TRIM(d.nom_ecole) <> e.nom_ecole;
```

| code_ecole | libelle_export | libelle_referentiel |
|---|---|---|
| EC009 | Ecole Gonaives | Ecole Puits-Sale |
| EC002 | Ecole  Ganthier II | Ecole Ganthier II |
| EC001 | ecole ganthier i | Ecole Ganthier I |

*Trois cas de gravité très différente. Les deux derniers sont cosmétiques — espaces et casse. Le premier est grave : **le code et le nom désignent deux écoles différentes**. Règle absolue : le code fait foi, on joint sur l'identifiant, jamais sur le libellé.*

**E30. Appliquer les quatre règles de triangulation.**

```sql
SELECT code_ecole, semaine,
       CASE WHEN CAST(eleves_presents AS REAL) > eleves_inscrits
            THEN 'R1 presents > inscrits' END AS r1,
       CASE WHEN eleves_presents_parraines > CAST(eleves_presents AS REAL)
            THEN 'R2 parraines > presents' END AS r2,
       CASE WHEN repas_servis > CAST(eleves_presents AS REAL) * jours_classe
            THEN 'R3 repas > maximum theorique' END AS r3,
       CASE WHEN enseignants_presents = 0 AND CAST(eleves_presents AS REAL) > 0
            THEN 'R4 eleves sans enseignant' END AS r4
FROM staging_data_center
WHERE CAST(eleves_presents AS REAL) > eleves_inscrits
   OR eleves_presents_parraines > CAST(eleves_presents AS REAL)
   OR repas_servis > CAST(eleves_presents AS REAL) * jours_classe
   OR (enseignants_presents = 0 AND CAST(eleves_presents AS REAL) > 0);
```

*Exécutée sur `suivi_hebdo`, cette requête ne renvoie **aucune ligne** : la table de production est saine. Exécutée sur `staging_data_center`, elle remonte les violations du module Excel. **Montrer les deux résultats côte à côte est une démonstration très efficace en test technique** : elle prouve que le contrôle fonctionne et que la base propre le passe.*

---

## 5. Ce qu'il faut savoir dire

Trois formulations à avoir prêtes.

Sur la **méthode** : « Avant d'écrire une requête, je me demande combien de lignes je devrais obtenir. Trente écoles sur douze semaines font trois cent soixante relevés. Si ma requête en renvoie un autre nombre, je cherche pourquoi avant d'exploiter le résultat — c'est souvent une jointure qui démultiplie les lignes ou un `INNER JOIN` qui en fait disparaître. »

Sur le **calcul d'un taux** : « J'utilise toujours le rapport des sommes et non la moyenne des taux, parce que la moyenne simple donne le même poids à une école de quatre-vingts élèves et à une école de trois cent vingt. Sur ces données, l'écart entre les deux méthodes atteint trois points sur un même département. »

Sur la **qualité** : « Je commence toujours par la complétude, avec un `CROSS JOIN` qui génère la grille théorique complète, puis une anti-jointure pour lister ce qui manque. Un indicateur publié sans son taux de complétude n'est pas interprétable. »

---

*Modules liés : [Excel et le Data Center](04_excel_data_center.md) · [Statistiques](02_statistiques_pmel.md) · [MEAL](01_meal_processus.md) · [SQL avancé et administration (piste ACTED)](../acted_bdd/01_sql_analyste_et_gestion_bdd.md)*
