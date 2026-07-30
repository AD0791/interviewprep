# Examen blanc corrigé — écrit et pratique

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Épreuve calibrée sur 2 h 30 : 45 minutes d'écrit, 75 minutes de pratique sur ordinateur, 30 minutes d'étude de cas rédigée. Base de travail : `exercices/acted_bdd.db`. Toutes les corrections ont été exécutées sur cette base et les résultats affichés sont réels.*

---

## Comment utiliser ce module

Fais l'épreuve **en conditions réelles avant de lire les corrigés** : chronomètre, pas de recherche en ligne, feuille et ordinateur avec la base ouverte. Le corrigé n'a d'intérêt que si tu as d'abord buté sur les questions ; lu à l'avance, il donne l'illusion de savoir.

Un conseil de méthode qui vaut plusieurs points. Sur un test écrit, réponds d'abord à toutes les questions que tu sais, puis reviens sur les autres. Sur un test pratique, écris d'abord la requête la plus simple qui produit **quelque chose**, vérifie que le nombre de lignes est plausible, puis raffine. Un candidat qui rend cinq requêtes justes et une non finie passe devant un candidat qui rend une requête parfaite et cinq cases vides.

---

## Partie A — Questionnaire à choix multiples (20 questions, 20 points, 25 minutes)

**1.** Dans une requête SQL, quelle clause filtre les lignes **avant** l'agrégation ?
`a) HAVING` · `b) WHERE` · `c) GROUP BY` · `d) ORDER BY`

**2.** Quel type de jointure conserve toutes les lignes de la table de gauche même sans correspondance à droite ?
`a) INNER JOIN` · `b) CROSS JOIN` · `c) LEFT JOIN` · `d) SELF JOIN`

**3.** `COUNT(colonne)` par rapport à `COUNT(*)` :
`a) donne toujours le même résultat` · `b) ignore les valeurs NULL` · `c) compte les valeurs distinctes` · `d) est plus lent`

**4.** Quelle contrainte garantit qu'un ménage ne peut pas recevoir deux fois la même activité le même jour ?
`a) NOT NULL` · `b) CHECK` · `c) UNIQUE composite` · `d) FOREIGN KEY`

**5.** Une clé étrangère sert à :
`a) accélérer les requêtes` · `b) garantir l'intégrité référentielle` · `c) identifier une ligne` · `d) chiffrer une colonne`

**6.** Dans un index composite sur `(date, id_menage)`, quelle requête **ne** bénéficie **pas** de l'index ?
`a) filtre sur date` · `b) filtre sur date et id_menage` · `c) filtre sur id_menage seul` · `d) tri par date`

**7.** Que signifie l'acronyme ACID ?
`a) Atomicité, Cohérence, Isolation, Durabilité` · `b) Accès, Contrôle, Index, Données` · `c) Analyse, Collecte, Import, Diffusion` · `d) Atomicité, Concurrence, Intégrité, Duplication`

**8.** La troisième forme normale exige que :
`a) chaque cellule soit atomique` · `b) tout attribut dépende de toute la clé` · `c) aucun attribut non clé ne dépende d'un autre attribut non clé` · `d) chaque table ait une clé étrangère`

**9.** Une sauvegarde jamais restaurée est :
`a) suffisante si elle est quotidienne` · `b) une hypothèse, pas une sauvegarde` · `c) valide si le fichier existe` · `d) acceptable si elle est chiffrée`

**10.** Que fait `PRAGMA foreign_key_check` en SQLite ?
`a) active les clés étrangères` · `b) liste les violations d'intégrité référentielle` · `c) crée les index manquants` · `d) vérifie la corruption du fichier`

**11.** Le principe du moindre privilège consiste à :
`a) donner tous les droits à l'administrateur` · `b) donner à chaque compte exactement les droits nécessaires` · `c) utiliser un compte partagé pour la saisie` · `d) limiter le nombre de comptes`

**12.** Un fichier dont on a retiré les noms est :
`a) anonyme` · `b) potentiellement réidentifiable par recoupement` · `c) libre de toute contrainte de partage` · `d) conforme par construction`

**13.** Dans XLSForm, quelle colonne empêche la saisie d'une valeur impossible ?
`a) relevant` · `b) required` · `c) constraint` · `d) appearance`

**14.** Dans XLSForm, `relevant` sert à :
`a) rendre obligatoire` · `b) afficher la question sous condition` · `c) calculer une valeur` · `d) traduire le libellé`

**15.** Le Food Consumption Score se calcule à partir de :
`a) la dépense alimentaire mensuelle` · `b) la fréquence de consommation de groupes alimentaires pondérés` · `c) le nombre de repas par jour` · `d) le périmètre brachial`

**16.** Un ménage avec un FCS acceptable mais un rCSI élevé :
`a) est en bonne situation` · `b) mange correctement au prix de stratégies de survie sévères` · `c) présente une donnée aberrante` · `d) doit être exclu de l'analyse`

**17.** Dans un graphique en barres, l'axe des valeurs :
`a) peut être tronqué pour mieux voir l'écart` · `b) doit partir de zéro` · `c) doit être logarithmique` · `d) n'a pas d'importance`

**18.** Un taux de couverture de 60 % annoncé sans effectif est :
`a) suffisant` · `b) incomplet, car 60 % de 5 et 60 % de 500 ne se valent pas` · `c) faux` · `d) acceptable en interne uniquement`

**19.** Devant deux enregistrements de bénéficiaires très semblables, la bonne pratique est de :
`a) fusionner automatiquement` · `b) supprimer le plus récent` · `c) produire une liste de candidats vérifiée par un humain` · `d) conserver les deux sans rien signaler`

**20.** Une durée d'entretien PDM de trois minutes signale le plus probablement :
`a) un enquêteur efficace` · `b) un formulaire rempli sans que les questions soient posées` · `c) un ménage peu bavard` · `d) un bogue de l'application`

---

### Corrigé de la partie A

Les réponses sont, dans l'ordre : **1b, 2c, 3b, 4c, 5b, 6c, 7a, 8c, 9b, 10b, 11b, 12b, 13c, 14b, 15b, 16b, 17b, 18b, 19c, 20b.**

Cinq d'entre elles méritent une explication, parce que ce sont celles où l'on se trompe.

La **question 3** teste la logique ternaire de SQL. `COUNT(*)` compte les lignes ; `COUNT(colonne)` compte les valeurs non nulles de cette colonne. La conséquence pratique est immédiate : si l'on veut connaître le taux de réponse à une question, on compare les deux, et l'écart donne exactement le nombre de non-réponses.

La **question 6** teste la règle du préfixe le plus à gauche, qui est l'une des questions d'entretien les plus fréquentes sur les index. Un index composite se lit de gauche à droite comme un annuaire trié par nom puis prénom : on y trouve instantanément tous les « Pierre », et tous les « Pierre Jean », mais retrouver tous les « Jean » quel que soit le nom oblige à tout parcourir.

La **question 12** est la question de protection des données. Retirer les noms ne suffit pas, parce que la combinaison de quelques quasi-identifiants — commune, sexe, taille du ménage, statut de déplacement — désigne souvent une seule personne. Sur la base d'exercice, un ménage sur cinq est ainsi réidentifiable de façon unique.

La **question 16** teste la lecture croisée de deux indicateurs. Un ménage peut afficher une consommation alimentaire acceptable précisément **parce qu'**il applique des stratégies coûteuses : les adultes se privent au profit des enfants, on emprunte de la nourriture. Un seul des deux indicateurs masquerait la fragilité.

La **question 19** est la question d'éthique du dédoublonnage. Fusionner par erreur deux bénéficiaires distincts prive quelqu'un de son assistance, ce qui est une faute bien plus grave que de laisser passer un doublon. Le rapprochement approximatif produit donc des candidats, jamais des décisions.

---

## Partie B — Questions ouvertes courtes (5 questions, 20 points, 20 minutes)

**B1.** Expliquez la différence entre `WHERE` et `HAVING`, avec un exemple tiré d'un projet de distribution. *(4 points)*

**B2.** Vous devez concevoir la base d'un nouveau projet de distribution de kits. Citez les tables que vous créeriez et justifiez la présence d'une table d'association. *(4 points)*

**B3.** Décrivez votre stratégie de sauvegarde pour une base de projet dans un bureau terrain, en précisant ce qui distingue une bonne procédure d'une procédure sur le papier. *(4 points)*

**B4.** Quelles précautions prenez-vous avant d'exécuter un `DELETE` sur une table de bénéficiaires ? *(4 points)*

**B5.** Un partenaire demande un export des données de bénéficiaires. Que transmettez-vous et sous quelle forme ? *(4 points)*

---

### Corrigé de la partie B

**B1.** La différence tient au moment de l'exécution. SQL exécute une requête dans un ordre logique précis : d'abord `FROM` et les jointures, puis `WHERE`, puis `GROUP BY`, puis `HAVING`, puis `SELECT`, enfin `ORDER BY`. Le `WHERE` intervient avant le regroupement et filtre donc les lignes individuelles, sans pouvoir porter sur une fonction d'agrégation puisque celle-ci n'est pas encore calculée. Le `HAVING` intervient après et filtre les groupes constitués. Concrètement, si je veux les communes où le taux de sélection dépasse cinquante pour cent en ne considérant que les ménages enregistrés depuis janvier, la condition sur la date va dans le `WHERE` parce qu'elle porte sur chaque ligne, et la condition sur le taux va dans le `HAVING` parce qu'elle porte sur le groupe. Le même ordre d'exécution explique qu'on ne puisse pas réutiliser dans le `WHERE` un alias défini dans le `SELECT`.

**B2.** Je créerais une table de référence pour la géographie, avec départements, communes et sites d'intervention reliés en cascade ; une table `menages` portant l'identité du chef de ménage, la composition et le statut de ciblage ; une table `individus` reliée aux ménages pour permettre la désagrégation par âge et par sexe que les bailleurs exigent ; une table `projets` et une table `activites` qui en dépend ; et une table `assistances`. Cette dernière est une **table d'association**, et sa présence n'est pas un choix mais une nécessité : un ménage peut recevoir plusieurs activités et une activité touche plusieurs ménages, donc la relation est plusieurs-à-plusieurs et aucune des deux tables ne peut porter la clé de l'autre. La table d'association porte en plus les propriétés propres à la rencontre — la date, le montant, la modalité, l'agent qui a saisi — et c'est sur elle que je pose la contrainte d'unicité du triplet ménage, activité et date, qui rend le double paiement impossible.

**B3.** Je pars de deux chiffres validés avec le responsable MEAL : la perte maximale acceptable, qui détermine la fréquence, et le délai de rétablissement acceptable, qui détermine la préparation. Sur un projet de distribution, une sauvegarde complète chaque soir suffit. Je produis deux formats, une copie à chaud prise avec la commande de sauvegarde du moteur et jamais avec une simple copie de fichier qui attraperait la base au milieu d'une transaction, et un dump logique compressé qui reste portable. J'applique la règle trois-deux-un, avec la copie hors site sur un disque chiffré. Ce qui distingue une bonne procédure d'une procédure sur le papier tient en trois points : je vérifie l'intégrité de la base **avant** de la copier, sinon je propage une corruption dans toute ma rotation ; le script restaure automatiquement la sauvegarde du jour dans une base temporaire et recompte les lignes, parce qu'une sauvegarde jamais restaurée est une hypothèse ; et je conduis un exercice de restauration complet chaque trimestre, chronométré, documenté, exécutable par quelqu'un d'autre que moi.

**B4.** Cinq précautions, dans cet ordre. J'exécute d'abord le `SELECT` correspondant exactement à la clause `WHERE` du `DELETE`, pour voir les lignes que je m'apprête à détruire et vérifier que leur nombre est celui que j'attends. Je fais une sauvegarde immédiate de la table ou de la base. Je travaille dans une transaction explicite, ce qui me laisse annuler tant que je n'ai pas validé. J'archive les lignes concernées dans une table de rejets plutôt que de les perdre, parce qu'une décision de suppression peut se révéler fausse. Et je journalise l'opération avec l'utilisateur et le motif. Cela dit, la vraie réponse est en amont : sur des données de bénéficiaires, **on ne supprime pratiquement jamais**. On marque comme inactif, ce qui préserve l'historique, garde reproductibles les rapports déjà transmis, et respecte la piste d'audit que le bailleur peut réclamer des années plus tard.

**B5.** Je ne transmets pas d'export nominatif par défaut. Je demande d'abord à quelle question le partenaire doit répondre, parce que dans la majorité des cas un agrégat suffit : un comptage par commune et par type d'assistance répond au besoin réel. Si un partage ligne à ligne est nécessaire, par exemple parce que le partenaire met en œuvre sur une zone, il passe par un accord de partage écrit précisant la finalité, les champs transmis, la durée de conservation et l'interdiction de retransmission, et il est validé par le coordonnateur, pas par moi seul. Techniquement, je fournis une vue plutôt qu'un fichier libre : aucune colonne nominative, quasi-identifiants généralisés en tranches, et un seuil qui écarte automatiquement toute combinaison correspondant à moins de cinq ménages. Le fichier part chiffré, avec le mot de passe transmis par un autre canal, et l'envoi est consigné.

---

## Partie C — Épreuve pratique sur ordinateur (6 exercices, 40 points, 75 minutes)

*Base : `exercices/acted_bdd.db`. Rends pour chaque exercice la requête et le résultat.*

**C1.** Produis en une seule requête le nombre de ménages enregistrés, le nombre de ménages sélectionnés, le nombre de ménages ayant reçu au moins une assistance et le nombre total de lignes d'assistance. *(5 points)*

**C2.** Liste les cinq communes ayant le taux de sélection le plus élevé, avec l'effectif de ménages et le nombre de sélectionnés. *(6 points)*

**C3.** Détecte les ménages enregistrés deux fois sur la base du numéro de pièce d'identité, puis écris la requête qui identifie les lignes à supprimer en conservant le premier enregistrement. *(8 points)*

**C4.** Calcule, par département, le taux de ménages satisfaits, en définissant « satisfait » comme une note de 4 ou 5. *(6 points)*

**C5.** Trouve les ménages sélectionnés qui n'ont reçu aucune assistance. *(5 points)*

**C6.** Classe les communes par score moyen de vulnérabilité décroissant en utilisant une fonction fenêtre, et n'affiche que les cinq premières. *(10 points)*

---

### Corrigé de la partie C

**C1.** L'astuce est d'utiliser des sous-requêtes scalaires dans le `SELECT` plutôt que de tenter une jointure, parce que les quatre chiffres ne se calculent pas au même grain.

```sql
SELECT (SELECT COUNT(*) FROM menages)                                    AS enregistres,
       (SELECT COUNT(*) FROM menages WHERE statut_selection='Selectionne') AS selectionnes,
       (SELECT COUNT(DISTINCT id_menage) FROM assistances)               AS assistes,
       (SELECT COUNT(*) FROM assistances)                                AS lignes_assistance;
```

| enregistres | selectionnes | assistes | lignes_assistance |
|---|---|---|---|
| 1218 | 601 | 600 | 1428 |

Le point noté est la distinction entre les deux dernières colonnes. Six cents ménages ont reçu quelque chose, mais 1 428 lignes d'assistance existent, parce qu'un même ménage a souvent reçu du cash, un kit et un bon. Confondre les deux est l'erreur la plus fréquente des rapports de distribution.

**C2.** Une agrégation conditionnelle suffit : `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` compte les lignes qui satisfont une condition à l'intérieur d'un groupe.

```sql
SELECT c.nom_commune,
       COUNT(*)                                                                AS menages,
       SUM(CASE WHEN m.statut_selection = 'Selectionne' THEN 1 ELSE 0 END)     AS selectionnes,
       ROUND(100.0 * SUM(CASE WHEN m.statut_selection = 'Selectionne'
                              THEN 1 ELSE 0 END) / COUNT(*), 1)                AS taux
FROM menages m
JOIN sites    s ON s.code_site  = m.code_site
JOIN communes c ON c.id_commune = s.id_commune
GROUP BY 1
ORDER BY taux DESC
LIMIT 5;
```

| nom_commune | menages | selectionnes | taux |
|---|---|---|---|
| Leogane | 135 | 73 | 54,1 |
| Gonaives | 104 | 54 | 51,9 |
| Gros-Morne | 138 | 71 | 51,4 |
| Mirebalais | 171 | 86 | 50,3 |
| Port-au-Prince | 117 | 58 | 49,6 |

Deux pièges sont notés. Le `100.0` plutôt que `100` évite la division entière, qui renverrait zéro dans plusieurs moteurs. Et l'affichage de l'effectif à côté du taux est attendu : un taux sans effectif ne se lit pas.

**C3.** La détection se fait par regroupement, la sélection des lignes à supprimer par fonction fenêtre.

```sql
-- Detection
SELECT piece_identite, COUNT(*) AS occurrences, GROUP_CONCAT(code_menage) AS codes
FROM menages
GROUP BY piece_identite
HAVING COUNT(*) > 1
ORDER BY piece_identite;
```

| piece_identite | occurrences | codes |
|---|---|---|
| 2407426-3 | 2 | MEN-00643, MEN-01216 |
| 3103567-6 | 2 | MEN-00280, MEN-01218 |
| 3958179-9 | 2 | MEN-00788, MEN-01203 |

Dix-huit groupes au total. On remarque immédiatement que le second code de chaque paire est très élevé : ce sont des réenregistrements tardifs, faits par une autre équipe.

```sql
-- Lignes a ecarter, en conservant le premier enregistrement
WITH numerotes AS (
  SELECT id_menage, code_menage, piece_identite,
         ROW_NUMBER() OVER (PARTITION BY piece_identite
                            ORDER BY date_enregistrement, id_menage) AS rang
  FROM menages
)
SELECT COUNT(*) FROM numerotes WHERE rang > 1;
-- 18
```

La notation porte autant sur la requête que sur ce qui l'accompagne. La règle de conservation doit être **explicite** : ici on garde le plus ancien enregistrement, mais on pourrait garder le plus complet, et le choix doit être écrit. Il faut aussi énoncer les trois précautions — exécuter le `SELECT` avant le `DELETE`, travailler en transaction, archiver dans une table de rejets — et signaler que dix-huit doublons détectés par la pièce d'identité ne sont pas les seuls : la recherche par nom, prénom, date de naissance et site n'en trouve que huit, parce que l'orthographe du nom varie d'un enregistrement à l'autre. Un dédoublonnage sérieux croise plusieurs clés.

**C4.**

```sql
SELECT d.nom_departement,
       COUNT(*)                                                         AS enquetes,
       SUM(CASE WHEN p.satisfaction >= 4 THEN 1 ELSE 0 END)             AS satisfaits,
       ROUND(100.0 * SUM(CASE WHEN p.satisfaction >= 4 THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                             AS taux
FROM pdm_reponses p
JOIN menages      m ON m.id_menage      = p.id_menage
JOIN sites        s ON s.code_site      = m.code_site
JOIN communes     c ON c.id_commune     = s.id_commune
JOIN departements d ON d.id_departement = c.id_departement
GROUP BY 1
ORDER BY taux DESC;
```

| nom_departement | enquetes | satisfaits | taux |
|---|---|---|---|
| Artibonite | 255 | 179 | 70,2 |
| Ouest | 156 | 101 | 64,7 |
| Nord | 77 | 46 | 59,7 |
| Centre | 79 | 43 | 54,4 |

Un point bonus est accordé au candidat qui commente : l'écart de seize points entre l'Artibonite et le Centre mérite une vérification avant d'être interprété, parce qu'avec 79 enquêtes dans le Centre l'intervalle de confiance est large, et parce qu'une enquête de satisfaction menée par l'organisation qui distribue souffre d'un biais de désirabilité.

**C5.** C'est l'anti-jointure, le motif le plus utile du métier.

```sql
SELECT m.code_menage, m.nom_chef, m.score_vulnerabilite
FROM menages m
LEFT JOIN assistances a ON a.id_menage = m.id_menage
WHERE m.statut_selection = 'Selectionne'
  AND a.id_assistance IS NULL;
```

| code_menage | nom_chef | score_vulnerabilite |
|---|---|---|
| MEN-00981 | Moise | 57 |

Un seul ménage, mais c'est exactement le genre de résultat qui compte : une personne sélectionnée avec un score de 57 n'a rien reçu, et il faut savoir pourquoi. Le motif `LEFT JOIN ... WHERE clé_droite IS NULL` répond à toutes les questions de la forme « qui n'a pas reçu », « quel site n'a pas rapporté », « quel bénéficiaire ciblé n'a pas été atteint ».

**C6.** Une fonction fenêtre ne peut pas être filtrée dans le `WHERE`, puisqu'elle est calculée après lui. Il faut donc l'encapsuler.

```sql
SELECT nom_commune, menages, score_moyen, rang
FROM (
  SELECT c.nom_commune,
         COUNT(*)                               AS menages,
         ROUND(AVG(m.score_vulnerabilite), 1)   AS score_moyen,
         RANK() OVER (ORDER BY AVG(m.score_vulnerabilite) DESC) AS rang
  FROM menages m
  JOIN sites    s ON s.code_site  = m.code_site
  JOIN communes c ON c.id_commune = s.id_commune
  GROUP BY 1
)
WHERE rang <= 5
ORDER BY rang;
```

| nom_commune | menages | score_moyen | rang |
|---|---|---|---|
| Port-au-Prince | 117 | 45,0 | 1 |
| Gonaives | 104 | 45,0 | 2 |
| Verrettes | 97 | 44,0 | 3 |
| Gros-Morne | 138 | 43,7 | 4 |
| Cap-Haitien | 165 | 43,2 | 5 |

Deux points d'attention. L'encapsulation dans une sous-requête est **obligatoire** et c'est le vrai objet de l'exercice. Et l'affichage montre Port-au-Prince et Gonaïves tous deux à 45,0 avec des rangs 1 et 2 : c'est un artefact de l'arrondi, les moyennes réelles diffèrent au-delà de la décimale affichée, et le `RANK()` porte sur la valeur non arrondie. Un candidat qui remarque cela et propose d'afficher deux décimales ou d'utiliser `DENSE_RANK` selon le besoin métier montre qu'il lit ses propres résultats.

---

## Partie D — Épreuve pratique de traitement de données (2 exercices, 20 points, 30 minutes)

**D1.** L'export `exercices/export_kobo_pdm_brut.csv` contient 589 soumissions PDM téléchargées de KoboToolbox. Décris et applique la chaîne de traitement qui permet de le charger dans la base. Rends le nombre de lignes chargées, rejetées et dupliquées, avec les motifs. *(12 points)*

**D2.** Dans ce même export, la colonne `commune` contient plusieurs graphies pour la même commune. Compte les graphies distinctes, propose la méthode d'harmonisation et justifie ton choix entre une table de correspondance et un rapprochement automatique par similarité. *(8 points)*

---

### Corrigé de la partie D

**D1.** La chaîne comporte quatre étapes dans un ordre qui n'est pas interchangeable, et elle est implémentée dans `exercices/importer_kobo.py`.

On **archive** d'abord le fichier brut tel quel, daté, et on ne le modifie plus jamais : tout le nettoyage se fait par script, ce qui rend la chaîne rejouable si une règle change. On **normalise** ensuite : les dates arrivent en trois formats et repartent en un seul, les montants perdent leurs séparateurs de milliers et leurs unités collées, les libellés passent par une table de correspondance. On **valide** contre des règles métier, et toute ligne qui échoue part dans une table de rejets avec son contenu intégral et le motif exact — jamais à la poubelle, parce qu'on veut pouvoir rappeler l'enquêteur et réimporter après correction. On **déduplique** enfin sur la clé métier, ici le couple ménage et date d'enquête, en conservant la soumission la plus complète, puis on charge de façon idempotente grâce à la contrainte d'unicité et à une clause de conflit.

```
Lignes lues dans l'export         : 589
  rejetees (motif documente)      : 56
  doublons ecartes (meme cle)     : 18
  retenues apres deduplication    : 515
  effectivement inserees          : 515
Controle : lues - rejets - doublons - retenues = 0 (doit valoir 0)

Motifs de rejet par frequence :
    28  satisfaction hors echelle 1-5 ou non numerique
    20  duree d entretien inferieure a 8 minutes
     8  score_fcs absent ou hors bornes 0-112
     5  montant_recu_htg non numerique
```

Trois éléments valent des points au-delà de la mécanique. La **réconciliation qui boucle** : lignes lues moins rejets moins doublons moins retenues doit valoir zéro, sinon l'import perd des données sans le dire. L'**idempotence** : relancer le même import n'insère rien, ce qui se démontre en le relançant. Et le **traitement des vingt soumissions de moins de huit minutes**, qui ne sont pas une erreur de saisie mais un signal de qualité de collecte : elles partent en rejet pour vérification et donnent lieu à une requête de données adressée au superviseur, pas à une suppression silencieuse.

**D2.** L'export contient **19 graphies distinctes** pour **10 communes réelles** : « Gonaives », « GONAIVES », « Gonaïves », « gonaives » et « Gonaive » désignent la même localité, tout comme « Saint-Marc », « St-Marc », « SAINT MARC » et « st marc ».

La méthode retenue est une **table de correspondance explicite**, écrite dans le code, versionnée, relisible. La comparaison se fait sur une clé normalisée — minuscules, accents retirés, ponctuation et espaces supprimés — de sorte que « Saint-Marc », « SAINT MARC » et « st marc » se réduisent tous à `saintmarc`.

Le choix contre le rapprochement automatique par similarité se justifie en deux temps. D'abord, le nombre de valeurs distinctes est petit : dix-neuf graphies se traitent à la main en dix minutes, une fois pour toutes, alors qu'un algorithme de distance demanderait un réglage de seuil et produirait des erreurs sur des communes réellement proches — « Verrettes » et « Verrettes-Bas » ne sont pas la même chose. Ensuite et surtout, une table de correspondance est **auditable** : n'importe qui peut la relire et contester une ligne, alors qu'un rapprochement flou ne laisse aucune trace de sa décision. La règle générale du métier s'applique : le flou produit des candidats à vérifier, jamais des décisions.

La vraie réponse est cependant en amont. Ces dix-neuf graphies n'existeraient pas si la commune avait été posée comme une **liste déroulante en cascade** dans le formulaire Kobo plutôt que comme un champ texte libre. C'est le principe qui traverse tout le poste : la qualité se garantit d'abord dans le formulaire, ensuite dans le schéma, et seulement en dernier recours dans le nettoyage. Un candidat qui termine sa réponse par là marque le point le plus important de l'exercice.

---

## Partie E — Étude de cas rédigée (20 points, 30 minutes)

> Tu prends tes fonctions comme assistant base de données sur un projet WASH dans l'Artibonite, financé par ECHO, qui a démarré il y a huit mois. Tu découvres la situation suivante. Les données de ciblage vivent dans trois classeurs Excel, dont deux portent le mot « final » dans leur nom. Les distributions sont enregistrées sur des feuilles papier scannées, sans saisie. Aucune sauvegarde n'existe en dehors du portable du précédent titulaire du poste, parti il y a six semaines. Le rapport bailleur de mi-parcours est dû dans trois semaines. Le responsable MEAL te demande un plan.
>
> Rédige ce plan en une page, en indiquant tes priorités pour la première semaine, le premier mois, et ce que tu recommandes à moyen terme. Justifie l'ordre.

---

### Corrigé de la partie E

Ce qui est évalué n'est pas l'exhaustivité mais **l'ordre des priorités** et la capacité à distinguer l'urgent du structurant. Voici un plan qui vaut la note maximale.

**La première semaine sert à arrêter l'hémorragie, pas à améliorer quoi que ce soit.** La toute première action est de sauvegarder ce qui existe, en l'état, sans rien nettoyer : les trois classeurs, les scans, tout ce qui traîne, copiés sur deux supports dont un hors site, avec une empreinte. Tant que cette copie n'existe pas, chaque jour de travail est un pari. La deuxième action est un inventaire écrit : quels fichiers existent, qui les a produits, lesquels alimentent quel indicateur du rapport. La troisième est de fixer, avec le responsable MEAL, la définition des trois ou quatre indicateurs qui figureront dans le rapport de mi-parcours, parce que c'est cette définition qui déterminera tout le travail des deux semaines suivantes. La quatrième est de trancher une question difficile : les distributions papier non saisies sont-elles nécessaires au rapport ? Si oui, la saisie est le chemin critique et il faut mobiliser du renfort immédiatement.

**Le premier mois sert à produire le rapport et, en le produisant, à construire la base.** Le point de méthode qui fait la différence est de ne pas faire les deux séparément : on conçoit le schéma minimal qui porte les indicateurs du rapport, on écrit le script d'import qui charge les trois classeurs dans ce schéma en journalisant tout ce qui ne passe pas, et on produit le rapport **depuis la base**. On obtient ainsi le livrable urgent et l'infrastructure durable avec le même effort. La table de rejets produite par l'import est un livrable en soi : elle documente précisément la dette de qualité accumulée en huit mois, ce qui est une information que personne n'a aujourd'hui et qui protège l'organisation lors d'un audit. En parallèle, on met en place la sauvegarde quotidienne automatique avec restauration de contrôle, et la nomenclature de fichiers, parce que ces deux choses coûtent une journée et suppriment définitivement deux classes de problèmes.

**À moyen terme**, on propose trois chantiers, par ordre de rendement décroissant. Le premier est de faire remonter la collecte en amont : porter le formulaire de ciblage sur Kobo avec listes fermées, contrôles de cohérence et score calculé, ce qui supprime à la source les problèmes que le nettoyage traite en aval. Le deuxième est la migration vers PostgreSQL dès que plusieurs personnes doivent accéder simultanément à la base, parce que SQLite n'a aucun système de comptes ni de droits. Le troisième est la documentation : dictionnaire de données, procédure de flux, plan de reprise sur une page imprimée, matrice de permissions — de sorte que le prochain titulaire du poste ne se retrouve pas dans la situation où tu t'es trouvé.

**Deux phrases doivent figurer dans la copie**, et leur absence coûte des points. La première dit que l'on ne nettoie pas les données avant de les avoir sauvegardées. La seconde dit que le rapport de mi-parcours mentionnera explicitement les limites de qualité constatées — nombre d'enregistrements écartés, doublons détectés, distributions non saisies — parce qu'un bailleur pardonne une donnée imparfaite documentée et ne pardonne pas une donnée imparfaite dissimulée.

---

## Barème et lecture du résultat

| Partie | Points | Ce qu'elle teste |
|---|---|---|
| A — QCM | 20 | Connaissances techniques de base, réflexes |
| B — Questions ouvertes | 20 | Capacité à expliquer une procédure |
| C — Pratique SQL | 40 | Compétence réelle sur la base |
| D — Traitement de données | 20 | Méthode de nettoyage et d'import |
| E — Étude de cas | 20 | Jugement, priorisation, sens du contexte |
| **Total** | **120** | |

Au-dessus de 90, le niveau attendu est atteint. Entre 70 et 90, les bases sont là mais il faut retravailler la partie où les points manquent. En dessous de 70, reprends les modules correspondants avant de refaire l'épreuve.

Une remarque pour finir, qui n'est pas de la consolation. Les parties C et D pèsent la moitié du total, et ce sont celles qui se travaillent le plus vite : refaire trois fois les six requêtes de la partie C sur la base d'exercice suffit à les rendre automatiques. Les parties B et E se travaillent en rédigeant réellement les réponses, pas en les lisant.

---

*Suite du parcours : [Fiche de révision du jour J](00_fiche_revision_examen.md) · [SQL analyste et gestion de base](01_sql_analyste_et_gestion_bdd.md) · [Modélisation](02_modelisation_et_conception.md)*
