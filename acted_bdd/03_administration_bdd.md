# Administrer une base de données de projet

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Base d'exercice : `exercices/acted_bdd.db`. Script de sauvegarde exécutable : `exercices/sauvegarde_acted.sh`. Les temps de réponse et les sorties de commandes de ce module ont été mesurés réellement.*

---

## Pourquoi ce module existe

Le TDR contient une ligne que beaucoup de candidats lisent trop vite : « mettre en œuvre des procédures appropriées de sauvegarde, de restauration, de validation des données et de sécurité pour garantir l'intégrité et la disponibilité des données ». Quatre procédures, une exigence — intégrité et disponibilité.

C'est le cœur du métier d'administrateur. L'analyste produit un chiffre. L'administrateur garantit que le chiffre sera encore produisible dans dix-huit mois, après une coupure de courant, un vol de portable, une erreur de manipulation ou un audit du bailleur. Le poste ACTED demande explicitement les deux casquettes, et ce module couvre la seconde.

---

## 1. La panne qu'on n'oublie pas

Voici le scénario, et il est banal. Un vendredi soir, dans un bureau de Gonaïves, le portable qui héberge la base du projet ne redémarre plus. Le disque est mort. La dernière copie date d'une clé USB « faite le mois dernier », que personne ne retrouve.

Fais le calcul de ce que cela coûte. Depuis un mois, environ 200 ménages ont été enregistrés, 300 assistances saisies et une centaine d'enquêtes post-distribution importées. Il faut retourner sur le terrain, retrouver les fiches papier si elles existent, ressaisir. Le rapport bailleur du 15 sera en retard. Et surtout, personne ne pourra jamais affirmer avec certitude que les données reconstituées sont complètes, parce qu'il n'existe aucune référence à laquelle les comparer.

La perte technique se répare. La perte de **confiance dans le chiffre** ne se répare pas.

Tout le reste de ce module découle de cette scène. Une base de données n'est pas un fichier, c'est un actif du projet, et un actif se protège selon une procédure écrite que quelqu'un d'autre que toi peut exécuter.

---

## 2. Sauvegarder

### 2.1 Les deux familles de sauvegarde

La **sauvegarde logique** exporte le contenu sous forme d'instructions SQL : `pg_dump` pour PostgreSQL, `mysqldump` pour MySQL, `.dump` pour SQLite. Le résultat est un fichier texte lisible, compressible, comparable d'une version à l'autre, et restaurable sur une autre version du moteur ou même sur un autre serveur. C'est lent sur de gros volumes, mais c'est portable.

La **sauvegarde physique** copie les fichiers du moteur : `pg_basebackup`, la copie du répertoire de données à froid, ou pour SQLite la commande `.backup`. C'est rapide et fidèle bit à bit, mais la restauration exige la même version du moteur et souvent la même architecture.

En bureau terrain, on fait les deux, parce qu'elles couvrent des risques différents. La copie physique répond au disque mort ; le dump logique répond à la migration vers un nouveau serveur et à l'audit, parce qu'on peut l'ouvrir et le lire.

Le piège à ne jamais commettre : **copier avec `cp` un fichier de base pendant qu'une application écrit dedans**. La copie attrape la base au milieu d'une transaction et produit un fichier incohérent qui s'ouvre sans erreur, ce qui est le pire des cas — on croit avoir une sauvegarde. La commande `.backup` de SQLite prend un verrou cohérent et fonctionne à chaud ; c'est pour cela que le script du dépôt l'utilise.

### 2.2 Complète, différentielle, incrémentale

Une sauvegarde **complète** copie tout. Elle est simple à restaurer — un seul fichier — mais lourde à produire.

Une sauvegarde **différentielle** copie ce qui a changé depuis la dernière complète. La restauration demande deux éléments : la complète, puis la différentielle la plus récente.

Une sauvegarde **incrémentale** copie ce qui a changé depuis la dernière sauvegarde, quelle qu'elle soit. Elle est la plus légère, mais la restauration exige la chaîne entière, et si un maillon manque, tout ce qui suit est perdu.

Le schéma classique en bureau terrain combine les trois : complète le dimanche soir, incrémentale les autres soirs, archive mensuelle conservée un an. Sur une base SQLite de moins d'un gigaoctet, on simplifie : une complète chaque soir suffit, parce que le dump compressé de notre base d'exercice pèse 184 kilooctets.

### 2.3 La restauration à un instant donné

C'est la notion qui distingue un candidat qui a lu la documentation d'un candidat qui a administré. PostgreSQL journalise toutes les modifications dans les fichiers WAL, pour *write-ahead log*. En conservant une sauvegarde de base plus les WAL produits depuis, on peut restaurer la base **à n'importe quelle seconde** entre les deux.

L'intérêt n'est pas théorique. Le cas réel est celui de l'erreur humaine : à 14 h 20, quelqu'un lance un `UPDATE` sans clause `WHERE` et écrase le statut de sélection des 1 218 ménages. Une sauvegarde de la veille au soir fait perdre une journée de saisie. La restauration à un instant donné permet de revenir à 14 h 19 et de ne rien perdre du tout.

MySQL offre l'équivalent avec le journal binaire, `binlog`. SQLite n'a pas de mécanisme comparable, ce qui est l'un des arguments qui justifient de migrer vers PostgreSQL dès que la base devient critique — un point à mentionner si on te demande les limites de ton outil.

### 2.4 La règle 3-2-1

Trois copies des données, sur deux supports différents, dont une hors site. En contexte haïtien, cette dernière condition est la plus importante et la plus négligée : si les trois copies sont dans le même bureau, un incendie, une inondation ou une intrusion les emporte ensemble.

La déclinaison pratique tient en trois lieux : la base vive sur le poste de travail, la sauvegarde quotidienne sur un disque externe chiffré rangé dans un autre local, et une synchronisation hebdomadaire vers l'espace du bureau de coordination ou le stockage cloud du siège. Le mot **chiffré** n'est pas décoratif : un disque de sauvegarde contenant des noms, des numéros de téléphone et des adresses de bénéficiaires est un fichier de personnes vulnérables, et sa perte est un incident de protection. Le module [Sécurité et protection des données](04_securite_protection_donnees.md) développe ce point.

### 2.5 La règle qui vaut toutes les autres

**Une sauvegarde jamais restaurée n'est pas une sauvegarde.** C'est une hypothèse.

C'est pourquoi le script `exercices/sauvegarde_acted.sh` ne se contente pas de produire un fichier : il le remonte immédiatement dans une base temporaire et compare le nombre de ménages avec la source. Voici sa sortie réelle.

```
2026-07-29 21:23:46 | DEBUT sauvegarde de /tmp/actedgen/acted_bdd.db
2026-07-29 21:23:46 | Integrite verifiee : ok
2026-07-29 21:23:46 | Copie creee : acted_bdd_20260729_212346.db
2026-07-29 21:23:46 | Dump logique compresse : acted_bdd_20260729_212346.sql.gz
2026-07-29 21:23:46 | Empreintes SHA-256 enregistrees
2026-07-29 21:23:46 | Restauration de controle reussie : 1218 menages
2026-07-29 21:23:46 | Rotation appliquee (14 jours / 365 jours)
2026-07-29 21:23:46 | FIN sauvegarde — penser a la synchronisation hors site
```

Observe l'ordre des étapes, parce qu'il encode des décisions. Le contrôle d'intégrité vient **avant** la copie : sauvegarder une base corrompue propage la corruption dans toute la rotation, et au bout de quatorze jours il ne reste plus une seule copie saine. L'empreinte SHA-256 vient après la copie, pour pouvoir prouver plus tard que le fichier restauré est bien celui qui a été sauvegardé. La rotation vient en dernier, après validation : on ne supprime jamais l'ancienne sauvegarde avant d'avoir vérifié la nouvelle.

Au-delà du script automatique, la bonne pratique est un **exercice de restauration trimestriel** effectué à la main, chronométré, sur un poste qui n'est pas celui de production, et documenté dans une fiche d'une page. Proposer cet exercice en entretien est un signal très fort, parce que c'est ce que les organisations font le moins.

---

## 3. Vérifier l'intégrité

Sauvegarder ne suffit pas si l'on sauvegarde une base déjà abîmée. Trois niveaux de contrôle existent, et il faut savoir les distinguer.

### 3.1 L'intégrité physique

```sql
PRAGMA integrity_check;
```

```
ok
```

Cette commande parcourt les pages du fichier et vérifie la cohérence interne des structures : arbres d'index, chaînages, pages libres. Une réponse autre que `ok` signifie que le fichier est endommagé, en général par une coupure de courant pendant une écriture ou par un support défaillant. L'équivalent PostgreSQL passe par les sommes de contrôle de pages, activables à l'initialisation du cluster, et l'outil `amcheck` pour les index.

### 3.2 L'intégrité référentielle

```sql
PRAGMA foreign_key_check;
```

```
(aucune ligne)
```

Aucune ligne renvoyée signifie qu'aucune clé étrangère ne pointe dans le vide. Le contrôle est indispensable en SQLite précisément parce que les clés étrangères n'y sont pas vérifiées par défaut : si une application a inséré des données sans avoir activé `PRAGMA foreign_keys = ON`, la base peut contenir des assistances rattachées à des ménages inexistants sans que rien ne l'ait signalé.

### 3.3 L'intégrité métier

Les deux premiers contrôles disent que la base est techniquement saine. Ils ne disent rien sur le fait qu'elle décrive correctement la réalité. Le troisième niveau est une batterie de requêtes de cohérence, écrites une fois et exécutées à chaque cycle de reporting.

```sql
-- Tableau de bord de validation : chaque ligne doit afficher zero.
SELECT 'V1 menages selectionnes sans assistance' AS controle, COUNT(*) AS anomalies
FROM menages m LEFT JOIN assistances a ON a.id_menage = m.id_menage
WHERE m.statut_selection = 'Selectionne' AND a.id_assistance IS NULL
UNION ALL
SELECT 'V2 assistances a des menages non selectionnes', COUNT(*)
FROM assistances a JOIN menages m ON m.id_menage = a.id_menage
WHERE m.statut_selection <> 'Selectionne'
UNION ALL
SELECT 'V3 PDM sans assistance prealable', COUNT(*)
FROM pdm_reponses p LEFT JOIN assistances a ON a.id_menage = p.id_menage
WHERE a.id_assistance IS NULL
UNION ALL
SELECT 'V4 enfants de moins de 5 ans superieurs a la taille', COUNT(*)
FROM menages WHERE nb_enfants_moins5 > taille_menage
UNION ALL
SELECT 'V5 pieces d identite dupliquees', COUNT(*)
FROM (SELECT piece_identite FROM menages
      GROUP BY piece_identite HAVING COUNT(*) > 1);
```

| controle | anomalies |
|---|---|
| V1 menages selectionnes sans assistance | 1 |
| V2 assistances a des menages non selectionnes | 0 |
| V3 PDM sans assistance prealable | 0 |
| V4 enfants de moins de 5 ans superieurs a la taille | 0 |
| V5 pieces d identite dupliquees | 18 |

Lis le tableau comme un rapport de santé. Les contrôles V2, V3 et V4 sont à zéro parce que le schéma les rend impossibles : la contrainte `CHECK (nb_enfants_moins5 <= taille_menage)` fait le travail de V4 en amont. Le contrôle V1 remonte un ménage sélectionné qui n'a rien reçu, ce qui n'est pas une erreur technique mais une question de gestion à poser à l'équipe distribution. Le contrôle V5 remonte 18 pièces d'identité présentes deux fois, et c'est le vrai problème de la base : ce sont des ménages enregistrés deux fois par deux équipes différentes, traités en détail dans le module [SQL et qualité](01_sql_analyste_et_gestion_bdd.md).

La distinction à formuler en entretien : **le schéma empêche les erreurs qu'on peut empêcher, les contrôles détectent celles qu'on ne peut pas.** Un doublon d'identité ne peut pas être interdit par une contrainte `UNIQUE`, parce que le numéro de pièce est parfois absent, parfois mal saisi, et parfois légitimement partagé par erreur administrative. Il relève donc de la détection et de l'arbitrage humain.

---

## 4. Les permissions

### 4.1 Le principe du moindre privilège

Chaque compte reçoit exactement les droits nécessaires à son travail, et rien de plus. Ce n'est pas de la méfiance envers les collègues, c'est une protection **contre l'accident**. La personne qui ne peut pas supprimer ne supprimera pas par erreur.

Traduit sur le projet, cela donne quatre profils, exactement ceux de la table `utilisateurs` de la base d'exercice.

| Rôle | Droits | Qui |
|---|---|---|
| `lecture` | `SELECT` sur les vues de reporting uniquement | Bailleur, chargé de communication |
| `saisie` | `SELECT` et `INSERT` sur les tables de collecte, `UPDATE` sur ses propres saisies du jour | Opérateurs de saisie terrain |
| `analyste` | `SELECT` sur tout, `INSERT` sur les tables de travail | Responsable MEAL, assistant BDD en analyse |
| `administrateur` | Tous droits, y compris la structure | Assistant BDD, une seule personne |

Le `DELETE` n'apparaît nulle part sauf pour l'administrateur, et c'est délibéré. Sur des données de bénéficiaires, on ne supprime pas : on marque comme inactif, ce qui préserve l'historique et la reproductibilité des rapports déjà envoyés.

### 4.2 La mise en œuvre

PostgreSQL raisonne en rôles, qu'on peut imbriquer.

```sql
-- Gist: permissions_acted.sql
CREATE ROLE acted_lecture;
GRANT CONNECT ON DATABASE acted_haiti TO acted_lecture;
GRANT USAGE  ON SCHEMA public         TO acted_lecture;
GRANT SELECT ON v_indicateurs_mensuels, v_couverture_par_commune TO acted_lecture;

CREATE ROLE acted_saisie;
GRANT acted_lecture TO acted_saisie;                  -- heritage des droits de lecture
GRANT INSERT ON menages, individus, assistances TO acted_saisie;
GRANT UPDATE (telephone, statut_selection) ON menages TO acted_saisie;  -- colonnes ciblees

CREATE USER rpierre WITH PASSWORD '...' ;
GRANT acted_saisie TO rpierre;

-- Le compte bailleur ne voit que les vues agregees, jamais les tables nominatives.
CREATE USER bailleur_echo WITH PASSWORD '...' ;
GRANT acted_lecture TO bailleur_echo;
```

Deux détails techniques valent la peine d'être connus. `GRANT UPDATE (telephone, statut_selection)` accorde le droit **colonne par colonne** : l'opérateur de saisie peut corriger un numéro de téléphone mais pas modifier un montant versé. Et un `GRANT SELECT` posé sur les tables existantes ne couvre pas les tables créées après, ce qui se règle avec `ALTER DEFAULT PRIVILEGES`.

Pour aller plus loin, PostgreSQL propose la **sécurité au niveau des lignes**, qui permet qu'un agent de l'Artibonite ne voie que les ménages de l'Artibonite.

```sql
ALTER TABLE menages ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_menages_departement ON menages
  USING (code_site IN (SELECT code_site FROM sites s
                       JOIN communes c ON c.id_commune = s.id_commune
                       WHERE c.id_departement = current_setting('acted.departement')::int));
```

SQLite, lui, n'a **aucun système de permissions** : les droits sont ceux du fichier sur le disque. C'est une limite majeure qu'il faut savoir énoncer, parce qu'elle constitue l'argument principal pour migrer vers PostgreSQL dès que plusieurs personnes accèdent à la même base.

### 4.3 La revue des accès

Une procédure d'administration qui manque presque partout : la **revue trimestrielle des comptes**. On liste les comptes actifs, on vérifie que chacun correspond à une personne encore en poste, et on désactive les autres.

```sql
SELECT identifiant, nom_complet, role, actif, date_creation
FROM utilisateurs
ORDER BY role, identifiant;
```

| identifiant | nom_complet | role | actif | date_creation |
|---|---|---|---|---|
| adisla | Alexandro Disla | administrateur | 1 | 2025-01-10 |
| mjoseph | Marie Joseph | analyste | 1 | 2025-01-12 |
| bailleur_echo | Compte consultation ECHO | lecture | 1 | 2025-05-14 |
| flouis | Fabiola Louis | lecture | 1 | 2025-03-01 |
| gnoel | Guerlande Noel | saisie | 1 | 2025-02-03 |
| kcasseus | Kervens Casseus | saisie | 0 | 2025-02-20 |
| rpierre | Ronald Pierre | saisie | 1 | 2025-02-03 |

Le compte `kcasseus` est déjà désactivé — la personne a quitté le projet. La désactivation vaut mieux que la suppression, car le journal d'audit continue de référencer l'identifiant, et un compte supprimé rend l'historique illisible.

---

## 5. Performance : mesurer, puis agir

### 5.1 La démonstration chiffrée

Un cas très concret du travail quotidien : l'équipe protection appelle pour vérifier si une personne est déjà enregistrée, en donnant son numéro de pièce d'identité. La requête est simple.

```sql
SELECT id_menage, code_menage, nom_chef
FROM menages
WHERE piece_identite = '9975357-5';
```

Sans index, le plan d'exécution est sans appel.

```
SCAN menages
```

`SCAN` signifie que le moteur lit les 1 218 lignes une par une pour en trouver une seule. Sur trois mille recherches consécutives, cela prend **environ 0,18 seconde**. Ajoutons l'index.

```sql
CREATE INDEX idx_menages_piece ON menages(piece_identite);
ANALYZE;
```

Le plan change.

```
SEARCH menages USING INDEX idx_menages_piece (piece_identite=?)
```

Et les mêmes trois mille recherches prennent désormais **environ 0,018 seconde**, soit un facteur **dix**. Sur une base de 1 218 lignes. Sur une base nationale de 200 000 ménages, le même écart se compte en minutes contre millisecondes, et c'est la différence entre un outil que les équipes utilisent et un outil qu'elles contournent en refaisant un fichier Excel dans leur coin.

Retiens la démarche autant que le résultat : **on lit le plan avant, on ajoute l'index, on relit le plan, on remesure.** On ne devine jamais.

### 5.2 Ce qu'il faut savoir dire sur les index

L'ordre des colonnes dans un index composite décide de son utilité. Un index sur `(date_assistance, id_menage)` sert une requête filtrant sur la date seule, ou sur date et ménage, mais **pas** une requête filtrant sur le ménage seul. C'est la règle du préfixe le plus à gauche.

Un index a un coût : il accélère la lecture et ralentit chaque écriture, puisqu'il faut le maintenir. Indexer toutes les colonnes est une erreur de débutant. Sur une table de collecte où l'on insère massivement pendant une distribution, un index de trop se paie en temps de saisie.

Un index sur une colonne peu sélective est inutile. Indexer `sexe_chef`, qui prend deux valeurs, n'apporte rien : le moteur préférera parcourir la table.

Une fonction appliquée à la colonne annule l'index. `WHERE UPPER(nom_chef) = 'PIERRE'` n'utilisera pas un index sur `nom_chef`, ce qui se règle par un index fonctionnel en PostgreSQL, ou en stockant une colonne normalisée à côté.

Enfin, un index dit **couvrant** contient toutes les colonnes dont la requête a besoin, qui peut alors être résolue sans jamais lire la table. Dans les plans SQLite ci-dessus, la mention `COVERING INDEX` signale exactement cela.

### 5.3 La maintenance courante

Les moteurs se dégradent avec l'usage, et trois opérations les remettent d'aplomb.

`ANALYZE` recalcule les statistiques sur la distribution des données. L'optimiseur choisit son plan à partir de ces statistiques ; quand elles sont périmées, il croit qu'une table contient cent lignes alors qu'elle en contient cent mille, et choisit un plan catastrophique. Un écart important entre lignes estimées et lignes réelles dans un plan d'exécution est le symptôme.

`VACUUM` récupère l'espace laissé par les suppressions. La démonstration sur notre base est nette : après suppression d'un tiers des lignes de la table de staging, le fichier pèse encore environ 917 kilooctets et `PRAGMA freelist_count` signale sept pages libres ; après `VACUUM`, il tombe à 852 kilooctets. En PostgreSQL, l'`autovacuum` fait ce travail en continu, et une table dont l'autovacuum ne suit plus le rythme souffre de ce qu'on appelle le gonflement, ou *bloat*.

La **reconstruction d'index** sert quand un index s'est fragmenté au fil des mises à jour. `REINDEX` en PostgreSQL et en SQLite, `OPTIMIZE TABLE` en MySQL.

### 5.4 Surveiller

Quatre indicateurs suffisent en bureau terrain, et il vaut mieux les regarder chaque semaine que d'installer un outil de supervision que personne ne consultera.

La **taille de la base** et sa croissance, parce qu'une croissance anormale signale souvent un import dupliqué. Le **nombre de lignes par table principale**, comparé à la semaine précédente. La **date et le résultat de la dernière sauvegarde réussie**, lue dans le journal du script. Et le **délai de la requête de reporting la plus lourde**, chronométré une fois par semaine sur la même requête, ce qui donne une tendance plutôt qu'une mesure isolée.

```sql
-- Photographie hebdomadaire de la base, a archiver dans un fichier de suivi.
SELECT 'menages'      AS table_suivie, COUNT(*) AS lignes FROM menages
UNION ALL SELECT 'individus',    COUNT(*) FROM individus
UNION ALL SELECT 'assistances',  COUNT(*) FROM assistances
UNION ALL SELECT 'pdm_reponses', COUNT(*) FROM pdm_reponses
UNION ALL SELECT 'plaintes',     COUNT(*) FROM plaintes;
```

| table_suivie | lignes |
|---|---|
| menages | 1218 |
| individus | 7004 |
| assistances | 1428 |
| pdm_reponses | 567 |
| plaintes | 240 |

---

## 6. Le plan de reprise

Deux notions structurent toute discussion sérieuse sur la continuité, et il faut connaître les sigles.

Le **RPO**, *recovery point objective*, est la quantité maximale de données qu'on accepte de perdre, exprimée en temps. Une sauvegarde quotidienne à 19 heures donne un RPO de vingt-quatre heures : au pire, on perd une journée de saisie.

Le **RTO**, *recovery time objective*, est le délai maximal acceptable avant de retrouver un service fonctionnel. Il dépend moins de la technique que de l'organisation : disposer d'un second poste préparé fait passer le RTO de deux jours à deux heures.

Le plan tient sur une page, et cette page doit être **imprimée**, parce que le jour où on en a besoin, la base est justement inaccessible. Elle indique où se trouvent les sauvegardes et qui en détient la clé de chiffrement, la procédure de restauration en commandes exactes à recopier, la liste des personnes à prévenir, et la procédure de reconstitution des données saisies depuis la dernière sauvegarde à partir des fiches papier.

En contexte haïtien, trois risques dominent et méritent d'être nommés à l'entretien, parce qu'ils montrent qu'on connaît le terrain. Les **coupures de courant** corrompent les écritures en cours, ce qui plaide pour un onduleur et pour le mode de journalisation WAL, plus résistant. La **connectivité intermittente** rend illusoire toute stratégie fondée uniquement sur une synchronisation cloud, d'où le disque externe chiffré. Les **mouvements de personnel et l'insécurité** imposent qu'aucune procédure ne dépende d'une seule personne : tout est écrit, et une deuxième personne du bureau sait exécuter la restauration.

---

## 7. Huit exercices d'administration

Exécute `exercices/sauvegarde_acted.sh` sur `acted_bdd.db`, puis lis le journal produit et explique à voix haute le rôle de chacune des huit étapes.

Simule une perte : renomme la base, restaure la dernière sauvegarde à partir du dump compressé, et vérifie que le nombre de ménages, d'assistances et d'enquêtes correspond exactement.

Écris la requête de contrôle qui compare, table par table, la base restaurée et la source, et qui renvoie une ligne par écart constaté.

Ajoute volontairement une anomalie référentielle en désactivant `PRAGMA foreign_keys`, puis détecte-la avec `PRAGMA foreign_key_check` et écris la requête qui la corrige.

Mesure l'effet d'un index : chronomètre mille recherches par téléphone avant et après création de l'index, en relevant les deux plans d'exécution.

Rédige la matrice des permissions du projet en quatre rôles, avec pour chacun la liste exacte des tables et des opérations, puis écris les instructions `GRANT` correspondantes en PostgreSQL.

Écris le tableau de bord de validation de la section 3.3 en y ajoutant trois contrôles de ton choix, et explique pour chacun s'il relève du schéma ou de la détection.

Enfin, rédige le plan de reprise du projet sur une page, avec RPO, RTO, emplacement des sauvegardes, commandes de restauration et chaîne d'alerte. C'est l'exercice le plus utile : c'est un livrable que tu peux montrer.

---

## Angles d'entretien

**« Décrivez votre stratégie de sauvegarde pour une base de projet en bureau terrain. »**

Je pars de deux chiffres que je fais valider par le responsable MEAL : combien de données on accepte de perdre au pire, et en combien de temps le service doit être rétabli. Sur un projet de distribution où l'on saisit toute la journée, je vise une perte maximale de vingt-quatre heures et un rétablissement en une demi-journée, ce qui donne une sauvegarde complète chaque soir. Techniquement je produis deux formats, parce qu'ils protègent contre des risques différents : une copie à chaud du fichier, prise avec la commande de sauvegarde du moteur et jamais avec une simple copie de fichier qui attraperait la base au milieu d'une transaction, et un dump logique compressé qui reste lisible et restaurable sur une autre machine. J'applique la règle trois-deux-un, c'est-à-dire trois copies sur deux supports dont une hors site, et le support hors site est un disque chiffré, parce qu'une sauvegarde de données bénéficiaires perdue est un incident de protection avant d'être un incident informatique. Trois points font la différence entre une procédure sur le papier et une procédure qui marche. D'abord je vérifie l'intégrité de la base avant de la copier, sinon je propage une corruption dans toute ma rotation et au bout de deux semaines je n'ai plus une seule copie saine. Ensuite le script restaure automatiquement la sauvegarde du jour dans une base temporaire et recompte les lignes, parce qu'une sauvegarde jamais restaurée n'est pas une sauvegarde, c'est une hypothèse. Enfin je fais un exercice de restauration complet chaque trimestre, chronométré et documenté, et la procédure est écrite de façon qu'une autre personne du bureau puisse l'exécuter sans moi.

**« Comment garantissez-vous l'intégrité des données ? »**

Je raisonne sur trois niveaux, parce qu'ils appellent des réponses différentes. Le niveau physique concerne le fichier lui-même, et je le contrôle avec la commande d'intégrité du moteur, qui vérifie les structures internes ; c'est ce qui détecte une corruption due à une coupure de courant. Le niveau référentiel concerne les liens entre tables, et je le garantis avec des clés étrangères déclarées dans le schéma, plus un contrôle périodique, ce qui est indispensable en SQLite où les clés étrangères ne sont pas vérifiées par défaut si on n'active pas le paramètre à chaque connexion. Le niveau métier concerne le fait que les données décrivent correctement la réalité, et là ma règle est de mettre dans le schéma tout ce qui peut y être mis : listes fermées en contraintes de vérification, obligation de saisie sur les champs indispensables, et surtout unicité sur les clés métier — sur la table des assistances, j'ai posé une contrainte d'unicité sur le triplet ménage, activité et date, ce qui rend le double paiement impossible plutôt que détectable après coup. Ce que le schéma ne peut pas empêcher, je le détecte : je maintiens un tableau de bord de validation, une dizaine de requêtes qui doivent toutes renvoyer zéro, que je fais tourner à chaque cycle de reporting. Sur ma base d'exercice, il remonte trois ménages sélectionnés qui n'ont rien reçu et dix-huit pièces d'identité présentes deux fois. Le premier chiffre est une question à poser à l'équipe distribution, le second est un travail de dédoublonnage. La règle qui résume tout : le schéma empêche ce qu'on peut empêcher, les contrôles détectent le reste, et le nettoyage n'intervient qu'en dernier recours.

**« Quels droits donneriez-vous à un collègue qui doit saisir des données ? »**

Je pars du principe du moindre privilège, qui n'est pas une méfiance envers la personne mais une protection contre l'accident. Un opérateur de saisie a besoin de lire les données de son périmètre et d'insérer de nouvelles lignes dans les tables de collecte. Il n'a pas besoin de supprimer, et je ne lui donne donc pas le droit de suppression ; d'ailleurs sur des données de bénéficiaires on ne supprime pratiquement jamais, on marque comme inactif, ce qui préserve l'historique et la reproductibilité des rapports déjà transmis. Pour la modification, j'accorde le droit colonne par colonne quand le moteur le permet : il peut corriger un numéro de téléphone mal saisi, il ne peut pas modifier un montant versé, parce que corriger un montant est une décision qui passe par le responsable MEAL et laisse une trace dans le journal d'audit. Je crée un compte nominatif par personne et jamais un compte partagé, sinon la traçabilité disparaît et on ne peut plus répondre à la question de savoir qui a saisi quoi. Je documente cette matrice de droits dans une page du dossier projet, et je la revois chaque trimestre pour désactiver les comptes des personnes qui ont quitté le projet. Enfin, si plusieurs personnes doivent travailler simultanément sur la même base, c'est le moment de dire que SQLite ne convient plus, puisqu'il n'a aucun système de comptes et que les droits se réduisent aux permissions du fichier : je propose alors une migration vers PostgreSQL, qui apporte les rôles, la granularité par colonne et même la restriction par ligne pour qu'un agent ne voie que son département.

---

*Suite du parcours : [Modélisation et conception](02_modelisation_et_conception.md) · [Sécurité et protection des données](04_securite_protection_donnees.md) · [Gestion de l'information et support](06_gestion_information_archivage.md) · [Fiche de révision](00_fiche_revision_examen.md)*
