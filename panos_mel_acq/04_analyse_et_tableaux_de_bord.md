# L'analyse de données et les tableaux de bord, pour ce poste

*Module 4. L'annonce demande de « solides compétences en analyse et visualisation de données » et
la maîtrise de « DHIS2 ou plateformes comparables ». Ce module couvre ce qu'un responsable MEL
analyste doit savoir faire et dire sur ce poste précis : les cinq analyses qui reviennent tout le
temps, les pièges d'agrégation, Power BI et Excel, et la statistique dont on a besoin pour une
vérification. Les statistiques générales sont dans
[`../cmmb_meal_officer/05_statistiques_et_analyse.md`](../cmmb_meal_officer/05_statistiques_et_analyse.md),
et trente exercices SQL corrigés dans
[`../assitant_pmel/07_sql_analyse_pmel.md`](../assitant_pmel/07_sql_analyse_pmel.md). Les
chiffres de requêtes viennent du jeu d'exercice fictif du module 02.*

---

## 1. Le problème : un tableau de bord qui ment en vert

Deux sites de traçage. Le premier a ramené 9 patients sur 10, soit 90 %. Le second en a ramené 60
sur 200, soit 30 %. Le tableau de bord départemental affiche la moyenne des deux taux : **60 %**, en
vert, au-dessus de la cible. Le vrai taux du département est de 69 patients revenus sur 210 listés,
soit **32,9 %**, en rouge. Personne n'a triché : une cellule a été calculée avec `MOYENNE` au lieu
d'un rapport de sommes.

Second exemple, plus sournois. Le taux de suppression virale d'un site passe de 85 à 94 % en un
trimestre. Excellente nouvelle, jusqu'à ce qu'on regarde le dénominateur : le laboratoire a été
fermé six semaines, seuls les patients les plus assidus ont pu faire leur test, et la couverture en
charge virale est tombée de 70 à 35 %. Le taux monte parce que la mesure se dégrade.

Ces deux erreurs ont le même remède, et c'est la règle qui gouverne tout ce module : **un taux ne
s'affiche jamais sans son numérateur et son dénominateur, et un taux agrégé se calcule toujours en
rapportant la somme des numérateurs à la somme des dénominateurs.**

---

## 2. Les cinq analyses qui reviennent sur ce poste

**La cascade.** Listés, visités, joints, revenus, toujours sous traitement à trois mois ; ou, pour
le VIH en général, dépistés, positifs, mis sous traitement, maintenus, supprimés. Chaque étape
rapportée à la précédente dit où l'on perd des gens. Le module 02 § 6 la construit en SQL.

**La file active et la cohorte.** Un patient est actif à une date si ses derniers ARV, délai de
grâce de 28 jours compris, couvrent cette date. La requête (étape 8 de
[`exercices/requetes.sql`](exercices/requetes.sql)) est la suivante, en version abrégée :

```sql
EXISTS (SELECT 1 FROM dispensations x
        WHERE x.code_patient = p.code_patient
          AND x.date_dispensation <= '2026-05-31'
          AND julianday(x.date_dispensation) + x.jours_fournis + 28
              >= julianday('2026-05-31')) AS actif_national
```

En mots : pour chaque patient, la machine cherche une dispensation antérieure à la date de
référence dont la couverture, jours d'ARV fournis plus 28 jours de grâce, atteint cette date. Si
l'on n'accepte que les dispensations du site du patient, on obtient la file active **vue du site** ;
si l'on accepte toutes les dispensations, la file active **nationale**.

```
site   tx_curr_site  tx_curr_national  ecart
-----  ------------  ----------------  -----
CH03   125           126               1
CY05   108           113               5
DL02   101           101               0
LM04   109           113               4
PV01   121           123               2
TO06   102           103               1
TOTAL  666           679               13
```

Les treize patients d'écart sont ceux qui prennent leurs ARV sur un autre site : invisibles pour
leur site d'origine, qui les compte comme perdus, alors qu'ils sont sous traitement. Et si leur
nouveau site les enregistre sous un nouveau code, ils apparaîtront **deux fois** dans la somme
nationale. C'est la même mécanique que les faux interrompus du module 02, vue depuis `TX_CURR`, et
c'est pour cela qu'un `TX_CURR` national n'est jamais la simple somme des `TX_CURR` des sites.

La **cohorte de rétention** se construit sur la même brique : on prend les patients mis sous
traitement (ou revenus) un mois donné, et on compte ceux qui sont encore actifs trois, six ou douze
mois plus tard. Le détail, avec le piège de la censure, est dans le module statistique CMMB § 2.

**La réconciliation.** Pour chaque indicateur, la valeur du programme, celle de chaque système
national, l'écart, sa cause parmi les cinq (définition, périmètre, période, identité, latence) et
l'action. Le modèle est au module 01 § 8.

**La complétude et la promptitude.** La **complétude** rapporte les rapports reçus aux rapports
attendus ; la **promptitude** rapporte les rapports reçus **à temps** aux rapports attendus. Ce sont
les deux indicateurs de qualité que le SISNU et DHIS2 suivent nativement, et ils accompagnent chaque
indicateur de programme dans le tableau de bord, parce qu'une hausse de performance qui coïncide
avec une chute de complétude n'est pas une hausse de performance.

**La détection d'anomalies.** Les contrôles qu'on automatise dès le premier mois : un numérateur
supérieur à son dénominateur ; une variation d'un mois à l'autre au-delà d'un seuil fixé à
l'avance ; la même valeur répétée plusieurs mois de suite ; une préférence pour les nombres ronds ;
des dates de saisie concentrées sur quelques jours, qui trahissent un arriéré saisi en masse après
une panne, avec la fiabilité dégradée que décrit le module HMIS CMMB § 3. La méthode générale est
dans le module statistique CMMB § 5.

---

## 3. Power BI et Excel : ce qu'on peut te demander de faire

Ton CV écrit « Power BI (expert) ». Si l'on te demande de le prouver à l'oral, ne parle pas de
graphiques : parle de **modèle et de mesures**, parce que c'est là que se jouent les erreurs de la
section 1.

**Les mesures, pas les colonnes.** Dans Power BI, un taux se calcule par une **mesure** DAX, qui est
évaluée dans le contexte de chaque visuel (un site, un département, le programme entier), et non par
une colonne calculée qui figerait le taux ligne par ligne. La version juste du taux de retour :

```dax
Vrais IIT       = CALCULATE ( COUNTROWS ( tracage ), tracage[faux_iit] = 0 )
Retours vérifiés = CALCULATE ( COUNTROWS ( tracage ),
                               tracage[faux_iit] = 0, tracage[retour_verifie] = 1 )
% revenus       = DIVIDE ( [Retours vérifiés], [Vrais IIT] )
```

La version fausse, celle qui affiche 60 % au lieu de 32,9 % :

```dax
% revenus (faux) = AVERAGE ( sites[pct_revenus] )
```

La différence tient en une phrase : la première mesure recalcule le rapport des sommes à chaque
niveau d'agrégation, la seconde fait la moyenne de taux qui n'ont pas le même poids. `DIVIDE` sert
en plus à éviter l'erreur de division par zéro d'un site qui n'a encore listé personne.

**La sécurité au niveau des lignes.** Power BI permet de définir des rôles qui filtrent les données
selon l'utilisateur (*row-level security*), par exemple un filtre `[departement] = "Nord"` pour la
direction sanitaire du Nord, ou une règle dynamique fondée sur l'adresse de l'utilisateur connecté.
Sur des données VIH partagées avec des directions départementales, c'est une exigence, pas une
option, et c'est un point que peu de candidats pensent à mentionner.

**Excel**, parce qu'une partie du travail réel se fera encore dans des classeurs. Les fonctions à
nommer : `RECHERCHEX` (`XLOOKUP`) pour rapprocher deux listes, `NB.SI.ENS` et `SOMME.SI.ENS`
(`COUNTIFS`, `SUMIFS`) pour des comptes conditionnels sans tableau croisé, les tableaux croisés
dynamiques pour l'exploration, et **Power Query** pour tout ce qui se répète chaque mois : importer,
nettoyer, fusionner. Une fusion Power Query de type **anti-jointure gauche** donne exactement la
liste des visites dont le code ne correspond à aucun patient, la requête de l'étape 2 du module 02
sans une ligne de SQL. La piste PMEL a un module complet sur Excel :
[`../assitant_pmel/04_excel_data_center.md`](../assitant_pmel/04_excel_data_center.md).

**DHIS2 « ou plateformes comparables ».** Ton expérience réelle de DHIS2 est celle d'un producteur de
données dans DATIM. Ce que tu peux dire avec assurance, c'est que tu connais sa logique : des
**éléments de données** saisis par **unité d'organisation** et par **période**, des **indicateurs**
calculés comme numérateur sur dénominateur, et des **ensembles de données** dont on suit la
complétude. Ce que tu ne dis pas, c'est que tu l'as configuré.

---

## 4. Construire un visuel qui répond à une question

Un tableau de bord n'est pas une collection de graphiques, c'est une collection de réponses. Chaque
visuel se construit à partir de la question qu'il tranche, et le choix de la forme en découle.

Pour une **tendance**, une ligne, avec la cible tracée et les échéances de jalons marquées ; et les
ruptures connues annotées sur la courbe (une panne, une nouvelle version du formulaire, la fermeture
d'une route), parce que sans annotation quelqu'un finira par interpréter une rupture technique comme
un changement de performance. Pour une **comparaison entre sites**, des barres horizontales triées,
avec le dénominateur écrit au bout de chaque barre. Pour **plusieurs départements**, le même petit
graphique répété avec la même échelle, plutôt qu'un graphique surchargé. Jamais de camembert pour un
taux, parce qu'un taux n'est pas une part d'un tout.

Deux contraintes locales à citer. La page destinée aux **relais** est en créole et ne contient pas
de pourcentages, seulement des listes de noms à visiter. Et chaque page existe aussi en **PDF daté**,
parce que la connexion tombe et qu'un vérificateur demande le tableau tel qu'il était à la date du
rapport, pas tel qu'il est aujourd'hui.

---

## 5. Le réflexe arithmétique

Recalcule toujours les ratios qu'on te donne. Un exemple, qui vient de leur propre site : la page TME
cite **404 843 personnes** dépistées en 2022, dont **164 300 femmes enceintes**, « soit 40,0 % ». Le
rapport donne en réalité **40,6 %**. L'écart est sans conséquence, et **tu ne le signales pas** en
entretien : corriger son hôte sur une coquille de site web ne rapporte rien et coûte beaucoup. Mais
c'est exactement le réflexe qu'on attend d'un responsable dont les chiffres vont déclencher des
paiements, et c'est ce réflexe qu'il faut montrer quand on te présentera un chiffre pendant
l'entretien : prendre une seconde, refaire la division, et demander le dénominateur.

---

## 6. La statistique d'une vérification : combien de dossiers tirer ?

C'est la question statistique la plus probable sur ce poste, parce qu'elle touche le paiement.

Reprends le vérificateur du module 01 : il tire **40 dossiers** et en confirme **28**, soit un taux de
confirmation de 70 %. Quelle confiance accorder à ce 70 % ? L'erreur type d'une proportion est la
racine carrée de p multiplié par (1 − p), divisé par n : ici, racine de 0,70 × 0,30 / 40, soit
environ 0,072. L'intervalle de confiance à 95 % vaut 1,96 fois cette erreur, soit **plus ou moins
14 points**. Le vrai taux de confirmation est donc quelque part entre 56 et 84 %, et un paiement
décidé sur ce tirage est décidé sur une fourchette très large.

Pour une précision de **plus ou moins 5 points**, avec un taux attendu de 80 %, la taille
d'échantillon vaut 1,96 au carré, fois 0,80 × 0,20, divisé par 0,05 au carré, soit environ
**246 dossiers**. Si la population ne compte que 400 retours déclarés, la correction pour population
finie (diviser par 1 plus (n − 1)/N) ramène le besoin à environ **153 dossiers**.

Ce qu'il faut en tirer à l'oral, et c'est ce qui impressionne : la **taille de l'échantillon de
vérification est une clause qui se négocie**, et un programme a intérêt à ce qu'elle soit écrite dans
l'accord, avec la méthode de tirage. Un vérificateur qui tire quarante dossiers peut conclure
n'importe quoi dans une fourchette de trente points ; et la pré-vérification interne, elle, peut
tirer plus large chaque mois, parce qu'elle ne coûte que du temps. La méthode générale du calcul de
taille d'échantillon est dans
[`../assitant_pmel/02_statistiques_pmel.md`](../assitant_pmel/02_statistiques_pmel.md).

---

## Angles d'entretien

**« Comment calculez-vous le nombre de patients actuellement sous traitement ? »**

« Un patient est actif à une date si ses derniers ARV couvrent cette date, avec le délai de grâce de
28 jours des définitions MER : on prend sa dernière dispensation, on ajoute les jours de traitement
fournis et les 28 jours, et on regarde si l'on dépasse la date de référence. Le point qui compte est
de savoir sur quelles dispensations on le calcule. Si un site ne regarde que les siennes, les
patients qui prennent leurs ARV ailleurs, ce qui arrive beaucoup avec les déplacements et la
dispensation communautaire, deviennent des perdus de vue alors qu'ils sont sous traitement. Sur un
jeu de données d'exercice que j'ai construit, cela fait treize patients sur près de sept cents,
invisibles pour leur site. C'est pour ça qu'un TX_CURR national n'est jamais la somme des TX_CURR des
sites, et que je ferais toujours le calcul sur l'identifiant national quand il existe. »

**« Comment présenteriez-vous un taux agrégé sur plusieurs sites ? »**

« En rapportant la somme des numérateurs à la somme des dénominateurs, jamais en faisant la moyenne
des taux des sites. Un site qui ramène neuf patients sur dix et un site qui en ramène soixante sur
deux cents ne font pas soixante pour cent en moyenne, ils font trente-trois pour cent ensemble. Dans
Power BI, c'est la différence entre une mesure DAX qui recalcule le rapport à chaque niveau, avec
DIVIDE, et une moyenne de colonne. Et j'affiche toujours le dénominateur à côté du taux, avec la
complétude et la date de l'extraction, parce qu'un taux qui monte pendant que la couverture baisse
n'est pas une amélioration. »

**« Le vérificateur a tiré quarante dossiers et en a confirmé vingt-huit. Qu'en pensez-vous ? »**

« Que soixante-dix pour cent sur quarante dossiers, c'est une fourchette d'environ plus ou moins
quatorze points à 95 % de confiance, donc un vrai taux quelque part entre cinquante-six et
quatre-vingt-quatre pour cent. Je ne contesterais pas le résultat pour autant, je commencerais par
regarder les douze dossiers non confirmés, parce que la cause compte plus que le chiffre : une
dispensation saisie en retard, un faux interrompu, ou un retour déclaré sur une promesse ne
demandent pas la même correction. Et pour la suite, je proposerais que la taille et la méthode de
tirage soient écrites dans l'accord : pour une précision de cinq points, il faut plutôt cent
cinquante à deux cent cinquante dossiers selon la taille de la population. »
