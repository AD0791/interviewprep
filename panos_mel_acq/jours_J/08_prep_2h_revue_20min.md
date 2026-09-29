# Préparation express — Institut Panos, mardi 29 septembre 2026, 13 h

*Deux heures de préparation, puis vingt minutes de révision avant de te connecter. Ce fichier se
suffit à lui-même : tu n'as rien d'autre à ouvrir. [`FICHE_SYNTHESE.md`](FICHE_SYNTHESE.md) et
[`FICHE_MER_INDICATEURS.md`](FICHE_MER_INDICATEURS.md) restent la profondeur, si une section te
laisse sur ta faim.*

Ils t'ont retenu pour une raison précise : **trois ans sur un programme VIH avec du rapportage
MER**. Tout le reste de l'entretien compte, mais c'est sur cette histoire-là qu'ils vont creuser. La
préparation lui donne donc la première place et le plus de temps.

---

## 0. Le minutage

Chaque bloc se termine **à voix haute**, chronomètre en main. Lire ne prépare pas à parler, et un
entretien se perd plus souvent sur une réponse qui ne s'arrête pas que sur une réponse qu'on
ignore.

| Heure | Durée | Section | Ce que tu dis à voix haute à la fin |
|---|---|---|---|
| 09:00 | 30 min | §1 et §2 — Caris, `AGYW_PREV` | L'histoire de deux minutes, trois fois |
| 09:30 | 25 min | §3 — VIH et MER | Les six définitions de la fin du §3 |
| 09:55 | 25 min | §4 — MEAL et qualité des données | Les trois réponses prêtes du §4 |
| 10:20 | 15 min | §5 — Panos et le poste | « Que savez-vous de nous ? » et « Pourquoi ce poste ? » |
| 10:35 | 25 min | §6 — Questions personnelles | Le pitch, deux fois ; puis écris tes quatre décisions |
| 11:00 | — | Pause | Mange, marche, ne relis rien |
| 12:15 | 20 min | §7 — La révision | Rien de nouveau |
| 12:45 | — | Connexion Zoom | Noms et fonctions du panel notés dans les 30 premières secondes |

Si tu commences plus tard, décale tout, mais **ne rogne ni sur le §2 ni sur le §6** : ce sont les
deux blocs où une hésitation se voit.

---

## 1. Trois choses à savoir avant tout

**Premièrement, ton histoire Caris doit être la réponse la plus précise de l'entretien.** Un panel
qui recrute pour une expérience MER posera des questions de praticien : comment circulait la
donnée, qu'est-ce que tu contrôlais, qu'est-ce qui cassait, ce que tu as amélioré. Le §2 prépare
chacune.

**Deuxièmement, `AGYW_PREV` a une particularité qui peut te piéger ou te servir.** Le guide de
référence MER v2.8.2 (mars 2025, la dernière version publique) précise que cet indicateur est
**saisi dans DATIM par l'équipe du gouvernement américain** (le coordinateur DREAMS), « et non par
les partenaires de mise en œuvre », parce qu'il agrège les services de plusieurs partenaires dans
le temps. Les partenaires produisent les **données de superposition** (*layering*), c'est-à-dire
quelle fille active a terminé quels services du paquet. Si tu dis « je saisissais `AGYW_PREV` dans
DATIM », un panéliste qui connaît le guide tique. Si tu dis « je produisais et contrôlais les données
qui alimentent `AGYW_PREV`, que l'équipe USG consolide et saisit, puisqu'il agrège plusieurs
partenaires », tu montres que tu connais l'indicateur mieux que la plupart des candidats. Le §2.5
te demande de vérifier ce souvenir.

**Troisièmement, les cinq limites de ta lettre ne bougent pas.** Le panel a la lettre sous les yeux.
Pas de master délivré. Cinq ans en ONG dont trois sur le VIH, huit au ministère du Plan, et pas
encore de poste de conseiller technique principal. DATIM : producteur de données, jamais
administrateur de DHIS2. La PTME : la logique, pas le terrain. MESI, SISNU, iSanté Plus : le
paysage, pas l'exploitation. Et aucun indicateur de traitement (`TX_CURR`, `TX_ML`, `TX_PVLS`)
revendiqué comme rapporté.

*S'il s'agit d'un deuxième entretien* plutôt que d'un premier reporté : ouvre sur une phrase qui
reprend un point du premier (« Depuis notre échange, j'ai réfléchi à… »), attends-toi à plus de mises
en situation et à la question du salaire, et prépare-toi à rencontrer le Chief of Party.

---

## 2. Ton expérience VIH-MER à Caris — le cœur de l'entretien

### 2.1 L'histoire en deux minutes

Elle suit le CV déposé, mot pour mot sur les faits. Retiens l'ordre des idées, pas les phrases.

> « D'octobre 2021 à août 2024, j'ai été officier de suivi-évaluation sur le projet Impact Youth de
> la Caris Foundation, un programme VIH. Mon travail couvrait tout le cycle de rapportage : la
> collecte numérique sur les sites avec CommCare et HIVHaiti, la consolidation dans une base MySQL
> que j'administrais, les contrôles, la désagrégation, et la remontée des indicateurs MER à l'USAID
> via DATIM, comme producteur de données. Je n'administrais pas la plateforme ; je préparais,
> validais et soumettais.
>
> Sur les indicateurs, l'exemple le plus direct est `AGYW_PREV`, sous DREAMS : je produisais et
> contrôlais les données de superposition des services, qui alimentent l'indicateur que l'équipe du
> gouvernement américain consolide dans DATIM.
>
> Ce dont je suis le plus fier, c'est la qualité. J'avais établi et je supervisais les protocoles de
> DQA : remonter les chiffres rapportés jusqu'aux registres sources, et suivre chaque action
> corrective jusqu'à sa clôture, pas seulement jusqu'à sa consignation. Et j'ai réécrit une partie du
> rapportage manuel en Python et SQL, avec les contrôles intégrés, ce qui a réduit le temps de
> traitement d'environ 40 % et libéré du temps pour la vérification.
>
> C'est exactement ce que demande votre annonce : des chiffres qui tiennent devant un vérificateur,
> parce que les paiements en dépendent. »

Environ cent vingt secondes. Si on t'arrête avant la fin, c'est bon signe : ils veulent creuser.

### 2.2 `AGYW_PREV`, à connaître parfaitement

Tout ce qui suit vient du guide de référence **MER v2.8.2**, section *AGYW_PREV* (pages 33 à 38).

**Ce qu'il mesure.** Le pourcentage des **participantes DREAMS actives** qui ont terminé **au moins
le paquet primaire** de services fondés sur des données probantes. DREAMS vise les adolescentes et
jeunes femmes de 10 à 24 ans. Le guide insiste : l'indicateur ne mesure **pas l'impact** de DREAMS,
il mesure la **fidélité de la superposition**, c'est-à-dire si chaque fille reçoit bien le paquet
complet prévu pour son âge.

**Qui compte.** Une fille est *inscrite* quand elle répond aux critères de vulnérabilité du pays et
accepte le programme. L'inscription ou le dépistage de vulnérabilité ne comptent pas comme un
service. Elle est *participante* dès qu'elle a commencé ou terminé un service. Elle est **active** si
elle a commencé ou terminé un service **dans les 6 derniers mois au T2, ou les 12 derniers mois au
T4**. Seules les actives comptent. Les autres sont *inactives* : perdues de vue, ou ayant terminé le
programme lors d'une période précédente.

**Le calcul.** Les participantes actives se répartissent en quatre groupes :

| Groupe | Numérateur | Dénominateur |
|---|---|---|
| 1. Paquet primaire terminé, rien de plus | oui | oui |
| 2. Paquet primaire terminé **et** au moins un service secondaire | oui | oui |
| 3. Au moins un service terminé, mais pas tout le paquet primaire | non | oui |
| 4. Un service commencé, aucun encore terminé | non | oui |

Le numérateur est donc la somme des groupes 1 et 2, et le dénominateur la somme des quatre. C'est
un indicateur **instantané** (*snapshot*) : il décrit l'état de superposition de chaque fille depuis
son entrée dans DREAMS, à la fin de la période.

**Les désagrégations**, toutes obligatoires : l'état de superposition, croisé avec le **temps passé
dans DREAMS** (0-6 mois, 7-12, 13-24, 25 mois et plus), croisé avec l'**âge** (10-14, 15-19, 20-24,
et 25-29 pour celles qui ont vieilli depuis leur inscription). L'âge retenu est l'âge **à la fin de
la période**, pas à l'inscription. S'y ajoute un **type de service** : prévention des violences,
soutien à la scolarité, renforcement économique.

**Les règles opérationnelles.** Fréquence **semestrielle**. Un service ne compte que s'il est
**terminé** selon la définition du pays (par exemple 80 % des séances d'un curriculum). Le paquet
primaire est fixé **par chaque pays** pour chaque tranche d'âge. La collecte exige un **identifiant
unique** par fille pour suivre ses services entre partenaires sans double comptage : carte ou
« passeport » DREAMS, base DHIS2. Les services eux-mêmes restent comptés dans leurs propres
indicateurs, comme `HTS_TST`, `PrEP_NEW` ou `OVC_SERV` (qui a une désagrégation DREAMS pour les
10-17 ans). Le guide fixe un repère : **90 % des actives devraient avoir terminé au moins le paquet
primaire après 13 mois ou plus dans DREAMS**. Et depuis la v2.8.2, l'indicateur est devenu
**optionnel**.

**Les contrôles de qualité prévus par le guide.** Le numérateur ne peut pas dépasser le
dénominateur. Toute baisse du total d'une période à l'autre s'explique dans le récit narratif, par
les inactives (perdues ou programme terminé).

**Les pièges de qualité propres à cet indicateur.** C'est ta meilleure matière pour montrer que tu
as pratiqué, et ils découlent directement des règles. Le **double comptage**, quand une fille servie
par deux partenaires n'a pas d'identifiant commun. Un **service commencé compté comme terminé**. Un
**mauvais âge**, quand on garde l'âge d'inscription au lieu de l'âge en fin de période. Une **fenêtre
d'activité mal appliquée**, qui compte une inactive comme active. Et une inscription enregistrée
comme un service.

La phrase à placer : « `AGYW_PREV` ne dit pas si DREAMS marche, il dit si chaque fille reçoit bien
tout son paquet. C'est un indicateur de fidélité, et c'est pour ça que l'identifiant unique décide
de tout. »

### 2.3 Le circuit de la donnée, à décrire si on te le demande

Décris-le comme une chaîne dont tu tenais chaque maillon, dans l'ordre du CV. La collecte se faisait
sur les sites avec CommCare et HIVHaiti, sur des formulaires standardisés entre sites, pour que la
donnée soit juste à la saisie plutôt que réparée ensuite. Tu supervisais les agents de collecte. Les
données arrivaient dans une base MySQL que tu administrais. Là, les contrôles tournaient :
doublons, champs manquants, incohérences de dates et d'âges, valeurs hors plage. Puis venait la
consolidation par période et la désagrégation selon les exigences MER, et enfin la validation avant
soumission. Les retours et corrections étaient suivis jusqu'à leur clôture. En parallèle, des
tableaux de bord Power BI et Quarto sur AWS donnaient chaque semaine les indicateurs clés.

### 2.4 Les relances probables

**« Quels indicateurs rapportiez-vous ? »**
« Le périmètre de mon projet, qui était la prévention chez les jeunes : `AGYW_PREV` sous DREAMS en
est l'exemple le plus direct. Je ne prétends pas avoir rapporté les indicateurs de traitement comme
`TX_CURR` ou `TX_PVLS` ; je connais leur logique pour l'avoir étudiée, pas pour les avoir produits.
Ce que je maîtrise, c'est le processus : consolider, appliquer la définition exacte, désagréger,
contrôler, soumettre, corriger ce qui revient. Il est le même quel que soit l'indicateur. »

**« Comment prépariez-vous une soumission ? »**
« En partant de la fiche de l'indicateur, pas de la base : définition, numérateur, dénominateur,
désagrégations requises. Puis l'extraction pour la période, les contrôles automatiques, une revue
des écarts avec la période précédente, et, pour les écarts qui ne s'expliquent pas, un retour au
registre source avant de soumettre. Rien ne partait sans avoir été comparé à la période d'avant. »

**« Qu'est-ce qu'un DQA, concrètement ? »**
« On tire un échantillon de sites et de dossiers, on recompte à partir des registres sources, et on
compare au chiffre rapporté : c'est le facteur de vérification, retrouvé divisé par rapporté. En
dessous de 1, on a sur-déclaré ; au-dessus, sous-déclaré. Puis on regarde le système qui a produit
l'écart (formulaires, circuits, formation), et on ouvre des actions correctives avec un responsable
et une date. Le point qui distingue un DQA utile d'un DQA décoratif, c'est de suivre ces actions
jusqu'à leur clôture et de vérifier au cycle suivant qu'elles ont marché. »

**« Quels problèmes de qualité avez-vous rencontrés ? »**
Réponds par ce que tes contrôles visaient, puis donne **un cas réel** si tu en as un en tête :
« Les contrôles que j'avais mis en place visaient surtout les doublons, les données incomplètes ou
tardives des sites, et les incohérences entre ce que disait le formulaire et ce que disait le
registre. Sur un indicateur de superposition comme `AGYW_PREV`, le risque principal est de compter
la même fille deux fois, ou de compter un service commencé comme terminé. » Ne fabrique pas
d'incident : un exemple vague mais vrai vaut mieux qu'un récit précis inventé.

**« Qu'avez-vous amélioré ? »**
« La chaîne de rapportage manuelle, réécrite en Python et SQL avec les contrôles intégrés : environ
40 % de temps de traitement en moins. Le plus important n'était pas le temps gagné, c'était que les
contrôles tournaient à chaque fois, y compris le mois où tout le monde était débordé. »

**« Pourquoi avez-vous quitté Caris ? »**
Le contexte du secteur (fin d'un cycle de projet, resserrement des financements), puis une
transition vers des missions de conseil où tu as continué le même métier. Jamais un mot négatif sur
Caris.

### 2.5 À vérifier dans ta mémoire avant 13 h

Prends cinq minutes, sans écran, pour répondre à trois questions. **Qui saisissait réellement
`AGYW_PREV` dans DATIM ?** Si c'était toi, rien ne t'interdit de le dire, mais sache que le guide
confie la saisie à l'équipe USG, et sois prêt à expliquer l'arrangement (base de coordination DHIS2,
envoi au point focal DREAMS de l'USAID). **Quels autres indicateurs passaient par tes mains ?**
N'en cite aucun que tu ne pourrais pas définir. Et **as-tu un cas réel de problème de qualité et de
sa correction ?** Un seul suffit. Il remplacera l'exemple générique du §2.4.

---

## 3. VIH et indicateurs MER — l'essentiel

**Le cadre.** L'objectif 95-95-95 : 95 % des personnes vivant avec le VIH connaissent leur statut,
95 % de celles-ci sont sous traitement, 95 % de celles-ci ont une charge virale supprimée. Le
**mandat de Panos dans EpiC** porte sur les deux derniers 95 : éducation des patients, adhérence,
**traçage et retour en soins des patients en interruption**, suppression virale. Pars toujours de
ce mandat.

**Les indicateurs à connaître**, par famille :

| Indicateur | Ce qu'il compte | Fréquence |
|---|---|---|
| `HTS_TST` / `HTS_TST_POS` | Personnes testées / testées positives ; rendement = POS ÷ TST | trimestrielle |
| `TX_NEW` | Nouvelles mises sous ARV | trimestrielle |
| `TX_CURR` | Personnes sous ARV en fin de période (ARV reçus dans les 28 jours après le dernier retrait manqué) | trimestrielle |
| `TX_ML` | Sorties de la file active : décès, interruption, transfert, refus ou arrêt | trimestrielle |
| `TX_RTT` | Retours sous ARV après une interruption de plus de 28 jours | trimestrielle |
| `TX_PVLS` | Charge virale supprimée (moins de 1 000 copies/ml) chez les testés des 12 derniers mois | trimestrielle |
| `PrEP_NEW` / `PrEP_CT` | Nouvelles mises sous PrEP / poursuites de PrEP | trimestrielle |
| `PMTCT_STAT`, `PMTCT_ART` | Statut connu en CPN, ARV chez les femmes enceintes positives | trimestrielle |
| `AGYW_PREV` | Superposition DREAMS (§2.2) | semestrielle |
| `OVC_SERV` | Enfants vulnérables et leurs familles servis | semestrielle |

Pour la PTME, tu connais la chaîne et ces deux indicateurs, et tu le dis sans rien revendiquer de
plus. Toutes les fréquences de ce tableau sont celles du tableau récapitulatif du guide v2.8.2.

**Les règles qui font la différence.** Elles viennent toutes du guide v2.8.2.

L'**interruption de traitement** (IIT) : aucun contact clinique pendant **plus de 28 jours** après le
dernier rendez-vous ou contact attendu.

L'**équation de cohorte** : `TX_CURR` de fin égale `TX_CURR` de début, plus `TX_NEW`, plus `TX_RTT`,
moins `TX_ML`.

La **désagrégation IIT n'a pas le même sens dans les deux indicateurs**. Dans `TX_ML`, elle porte
sur le **temps passé sous traitement avant** l'interruption (moins de 3 mois, 3 à 5, 6 et plus).
Dans `TX_RTT`, elle porte sur la **durée de l'interruption** avant le retour. Et un patient ne peut
pas figurer dans `TX_ML` et `TX_RTT` **la même période**.

Le **piège des 28 jours** : un patient ramené avant le 28e jour n'est jamais sorti, donc il
n'apparaît ni dans `TX_ML` ni dans `TX_RTT`. Le meilleur travail de traçage, rattraper un rendez-vous
manqué à temps, est invisible dans ces deux indicateurs, et un jalon payé sur les seuls `TX_RTT`
paierait pour laisser les gens décrocher.

La **couverture** en charge virale (testés ÷ `TX_CURR` éligibles) et la **suppression** (supprimés ÷
testés) se donnent toujours ensemble : une suppression de 90 % sur 30 % de couverture ne dit presque
rien.

Les **indicateurs pays hôte**, saisis par le personnel USG, couvrent tout le pays : un `TX_CURR`
national n'égale jamais la somme des partenaires. C'est une différence de périmètre, pas une erreur.

Les **faux perdus de vue** : avec la dispensation différenciée et près de 1,5 million de déplacés
internes (OIM), un patient « perdu » prend souvent ses ARV ailleurs. La déduplication nationale dans
SALVH réduit d'environ **14 %** les perdus de vue apparents (*Journal of Infectious Diseases*, 2025).
Avant de tracer un patient, on vérifie qu'il est vraiment perdu.

**Face à un code que tu ne connais pas**, ne bluffe jamais un numérateur. « Celui-là, je ne l'ai pas
rapporté, donc je préfère ne pas vous donner sa définition exacte de mémoire. Je peux vous dire où
il se situe : le préfixe dit le domaine, le suffixe ce qu'on compte. Et en arrivant, je vérifierais
sa fiche dans le guide de référence, parce que la définition du dénominateur décide de tout le
reste. »

**Les six définitions à dire à voix haute** en fin de bloc : l'IIT à 28 jours ; l'équation de
cohorte ; la différence entre `TX_ML` et `TX_RTT` ; couverture et suppression ; le numérateur et le
dénominateur d'`AGYW_PREV` ; pourquoi un `TX_CURR` national n'est pas une somme.

---

## 4. MEAL et qualité des données

**Les quatre lettres, sans jargon.** Le **suivi** regarde en continu si les activités se font et si
les produits sortent comme prévu. L'**évaluation** juge, à des moments choisis, si les résultats
sont atteints et pourquoi. La **redevabilité** rend des comptes au bailleur, au ministère et aux
personnes servies. L'**apprentissage** transforme tout cela en décisions : on change ce qui ne
marche pas, pendant le programme et pas après. Dans ce poste, il faut ajouter l'**ACQ**,
l'amélioration continue de la qualité : de petits cycles PDSA (planifier, faire, étudier, agir) sur
un problème précis d'un site, adossés au programme national **HEALTHQUAL** du MSPP.

**Un bon indicateur** est d'abord une **fiche** avant d'être un chiffre : la définition exacte, le
numérateur, le dénominateur, la source, la méthode de calcul, la fréquence, les désagrégations, le
responsable, et ses **limites connues**. Dans un mécanisme payé sur jalons, cette fiche est une
**clause de contrat** : chaque mot ambigu devient un litige de paiement. D'où la phrase à placer :
**un paiement sur jalon est un décaissement sur pièces justificatives, et le responsable MEL est
celui qui constitue les pièces.**

**Les critères de qualité des données.** Ce sont les cinq critères classiques de l'USAID (ADS 201),
plus la complétude :
- **Validité** : l'indicateur mesure bien ce qu'il prétend mesurer.
- **Intégrité** : la donnée est protégée contre les erreurs et les manipulations.
- **Précision** : elle est assez fine pour la décision à prendre.
- **Fiabilité** : même méthode, même résultat, d'une période et d'une personne à l'autre.
- **Ponctualité** : elle est disponible à temps pour servir.
- **Complétude** : la part des sites qui ont rapporté.

Un chiffre se donne toujours avec sa complétude, jamais complété par une estimation présentée comme
une donnée.

**Se vérifier avant d'être vérifié.** Chaque mois, avant l'échéance, refaire soi-même ce que fera le
vérificateur : échantillon, retour aux sources, facteur de vérification, et un **dossier de preuve**
par jalon (version de la fiche, extraction, calcul, résultat de la pré-vérification, actions
correctives). Un point de statistique qui marque : quarante dossiers dont vingt-huit confirmés, soit
70 %, c'est une fourchette de **plus ou moins 14 points** à 95 %. La taille de l'échantillon se
négocie donc dans l'accord.

**La réconciliation avec les systèmes nationaux.** Les chiffres d'un programme et ceux de MESI, du
SISNU ou d'iSanté Plus divergent pour cinq raisons, toujours les mêmes : la **définition**, le
**périmètre**, la **période**, l'**identité** (le même patient compté deux fois) et la **latence**
(la saisie tardive). Le rapport mensuel met côte à côte les valeurs, l'écart, sa cause et l'action.
**Un écart expliqué est une information ; un écart inexpliqué est un risque de paiement.**

**La règle de calcul qui trahit les amateurs.** Un taux agrégé est une somme de numérateurs sur une
somme de dénominateurs, **jamais une moyenne de taux**. Neuf sur dix et soixante sur deux cents ne
font pas 60 % en moyenne ; ils font 69 sur 210, soit 32,9 %. Un taux ne s'affiche jamais sans son
numérateur et son dénominateur.

### Trois réponses prêtes

**« Comment assurez-vous la qualité des données ? »**
« À trois moments. À la saisie d'abord, parce que c'est là que c'est le moins cher : formulaires
numériques avec contraintes, listes au lieu de texte libre, identifiants uniques. Ensuite en continu,
avec des contrôles automatiques à chaque extraction : doublons, champs manquants, numérateurs
supérieurs aux dénominateurs, variations anormales, complétude et ponctualité par site. Et
périodiquement par le DQA : retour aux registres sources sur un échantillon, facteur de
vérification, actions correctives suivies jusqu'à clôture. C'est ce que j'avais mis en place à
Caris. Dans un programme payé sur jalons, j'ajouterais une pré-vérification mensuelle, pour
connaître notre facteur de vérification avant le vérificateur. »

**« Nos chiffres ne concordent pas avec ceux de MESI. Que faites-vous ? »**
« Je ne corrige rien avant de comprendre. Je compare d'abord les définitions et les périodes,
parce que c'est la cause la plus fréquente et la moins grave. Puis le périmètre : les mêmes sites,
les mêmes patients ? Puis l'identité, les doublons entre systèmes, et enfin la latence des saisies.
Chaque écart reçoit une cause et une action, dans un rapport de réconciliation mensuel partagé avec
le MSPP. Et je le dis franchement : je connais MESI comme paysage, je ne l'ai pas exploité ; je
commencerais par comprendre ses définitions et ses identifiants avant de comparer un seul chiffre. »

**« La vérification indépendante a lieu dans cinq jours et votre pré-vérification donne 0,6 sur un
site. Que faites-vous ? »**
Dis toujours **ce que tu vérifies, puis ce que tu fais, puis à qui tu le dis**. « Je vérifie d'abord
que le 0,6 est réel et pas une erreur de ma propre extraction. S'il l'est, je cherche la cause sur
les dossiers non retrouvés : définition mal appliquée, pièces manquantes, doublons. Je corrige ce
qui est une erreur de documentation avec des pièces réelles, jamais en fabriquant quoi que ce soit.
Je retire du rapport ce qui ne peut pas être prouvé. Et je préviens le Chief of Party le jour même,
avec l'analyse et une recommandation, parce qu'il vaut mieux déclarer un écart que se le faire
découvrir. »

---

## 5. L'Institut Panos et le poste

**Panos en six phrases.** ONG haïtienne fondée le **29 juin 1986**, née de la communication sociale
dans la filiation de Panos Caraïbes. Elle est présente dans les **dix départements** depuis
**Pétion-Ville**, le **Cap-Haïtien** et **les Cayes**, avec trois programmes : santé globale,
gouvernance, assistance humanitaire. Son dispositif de proximité comprend des **SMS en créole** qui
passent sans internet (plus de 3,6 millions), la **ligne gratuite 8338** (plus de 1,36 million
d'appels, 1 203 références vers les soins) et des relais communautaires dans les zones enclavées.
Sur le VIH, elle revendique le premier **Forum national sur le sida** et les campagnes **E=E**,
**PrEP** et **TME**. Elle est aujourd'hui **sous-partenaire d'EpiC** (PEPFAR, dirigé par FHI 360) pour
l'éducation des patients, l'adhérence, le traçage des patients en interruption et la suppression
virale. Une histoire à citer si l'occasion se présente : **Marie Tania Petit-Frère**, ambassadrice
E=E, qui livre aujourd'hui les ARV à domicile à l'HUEH.

**Le poste.** Responsable MEL/ACQ, aussi appelé Conseiller Technique Principal en Information
Stratégique, rattaché au **Chief of Party**, sur un programme AFGHS-PANOS de **six mois**
renouvelables avec le MSPP, conditionné au financement, hybride possible. Il a six fonctions : le
cadre MEL ; les **indicateurs et jalons dont dépendent les paiements** ; la **réconciliation avec
MESI, le SISNU et iSanté Plus** ; la préparation aux **vérifications indépendantes** ; le
renforcement des capacités du MSPP ; l'agenda d'apprentissage.

**AFGHS est une question, pas un fait.** Le sigle désigne très probablement l'*America First Global
Health Strategy* du Département d'État (18 septembre 2025), qui passe par des accords bilatéraux
avec des cibles annuelles et le droit de retenir le financement. Haïti n'avait pas signé au 15
septembre 2026, ce qui cadre avec l'« accord anticipé de six mois ». Pose-la comme une question.

**Ce qu'on ne dit jamais.** CHAMPIONS, le projet USAID arrêté au bout de dix mois en 2025, ne se
cite qu'au passé et avec respect, seulement s'ils en parlent. L'audit de l'USAID sur un précédent
accord ne se mentionne sous aucune forme. Et on ne corrige ni leurs chiffres ni leur site.

**« Que savez-vous de nous ? »**
« Que vous êtes l'une des organisations qui ont façonné la riposte au VIH en Haïti, depuis le
premier Forum national sur le sida jusqu'aux campagnes E=E, et que votre force est la proximité :
les SMS en créole, la ligne 8338, les relais dans les zones que l'État n'atteint plus. Aujourd'hui,
au sein d'EpiC, vous travaillez sur le maintien en soins et la suppression virale. Et ce que je lis
dans cette annonce, c'est un passage : d'une organisation qui mesurait sa portée à un programme de
prestation de services avec le MSPP, payé sur des jalons vérifiés. C'est précisément ce passage que
le poste doit rendre solide. »

**« Pourquoi ce poste ? »**
« Parce qu'il réunit les deux moitiés de mon parcours. Le VIH et le rapportage MER, que j'ai
pratiqués trois ans à Caris. Et les systèmes, parce que réconcilier MESI, le SISNU et iSanté Plus
est d'abord un problème d'ingénierie des données : des définitions qui divergent, des périodes qui
ne se recouvrent pas, des patients comptés deux fois. Des postes où les deux comptent autant, il y en
a peu. Et c'est un programme où la qualité de la donnée décide directement des paiements, ce qui
donne au travail que j'aime le plus, la vérification, une importance réelle. »

**« Que feriez-vous le premier mois ? »**
« Deux semaines d'écoute, avec le Chief of Party, les équipes, le MSPP et les directions
départementales, pour comprendre les définitions, les systèmes et les attentes du bailleur. À la fin
de ces deux semaines, un premier jet du cadre MEL et des fiches d'indicateurs payants. À la fin du
mois, le cadre validé et l'outil de collecte testé. Au troisième mois, la première réconciliation et
la première pré-vérification. Au sixième, un système que le ministère peut faire tourner sans nous. »

---

## 6. Les questions personnelles

### Le pitch de quatre-vingt-dix secondes

Quatre mouvements : ta formation, le VIH au centre, tes deux compétences et le ministère, leur
annonce.

> « Je suis économiste appliqué, formé au CTPEA, et je travaille depuis plus de dix ans entre le
> suivi-évaluation et les systèmes d'information, en Haïti. Le cœur de mon expérience, c'est trois
> ans comme officier de suivi-évaluation sur un programme VIH, le projet Impact Youth de la Caris
> Foundation : rapportage de routine multi-sites, indicateurs MER remontés à l'USAID via DATIM comme
> producteur de données, et les protocoles de DQA que j'avais établis. Autour de ça, deux
> compétences. La collecte numérique et le MEAL, dont, début 2026, les indicateurs et la collecte de
> trois programmes chez Anseye Pou Ayiti, en trois mois. Et l'ingénierie de données : bases,
> pipelines, réconciliation entre systèmes qui ne se parlent pas. Avant cela, huit ans au ministère
> du Plan, où j'ai appris qu'un chiffre public engage l'institution qui le publie. Votre annonce
> demande des indicateurs qui tiennent devant un vérificateur, la réconciliation avec les systèmes
> nationaux, et une chaîne montée vite. C'est exactement ce que je sais faire. »

Dis « formé au CTPEA », jamais « diplômé », « master » ni « lauréat ».

### Les questions qui reviennent

**« Il vous manque le master et les dix ans de conseil de haut niveau. »**
Ne t'excuse pas. « C'est exact, et je l'ai écrit dans ma lettre : pas de master délivré, le DES reste
en attente de la soutenance de mon mémoire, et pas encore de poste de conseiller technique
principal. Ce que j'apporte, c'est ce que ce programme demande dès le premier mois : écrire les
fiches d'indicateurs comme des clauses, construire l'outil, faire la réconciliation et préparer la
vérification, sans attendre qu'une équipe soit recrutée. Avoir rapporté dans DATIM et savoir
construire le système qui l'alimente, c'est plus rare que les années. »

**« Quelles sont vos forces ? »**
Deux, avec une preuve chacune : la rigueur sur la qualité des données (les DQA suivis jusqu'à
clôture à Caris), et la capacité à construire le système moi-même (le rapportage réécrit en Python
et SQL, environ 40 % de temps en moins).

**« Et votre point faible ? »**
Un vrai, avec ce que tu fais pour le compenser : « Je suis un homme de données et de systèmes, pas
un clinicien. Sur les questions cliniques, je m'appuie sur les équipes médicales et sur les
définitions du guide, et je ne tranche jamais seul une question qui relève d'elles. » Ou, si tu la
reconnais mieux : « J'ai tendance à vouloir tout automatiser tôt ; j'ai appris à valider d'abord le
processus à la main avec l'équipe, puis à automatiser. »

**« Vous êtes actuellement chez Tekkod. Qu'en ferez-vous ? »**
Choisis maintenant la réponse vraie. Soit « j'y mettrais fin, ou je suspendrais la mission, avant de
commencer : un poste de ce niveau ne se fait pas à côté d'autre chose ». Soit « je garderais une
mission réduite, hors de mes heures, déclarée noir sur blanc dans le contrat, sans conflit
d'intérêts ». Jamais « je verrai ».

**« Vos expériences se chevauchent. »**
Dis la vérité de ton arrangement : le régime réel de chaque poste, ceux qui se faisaient à distance
(le CV porte « Télétravail » pour Tekkod et HANWASH), et le fait que les employeurs le savaient. Puis
referme : « Pour votre poste, c'est un temps plein, et il aura la priorité. »

**« Six mois, conditionnés au financement : cela vous convient ? »**
« Oui. C'est un accord anticipé, et le secteur a appris l'an dernier qu'un financement peut s'arrêter
du jour au lendemain. J'aimerais connaître le calendrier attendu pour la signature et le démarrage.
Et un programme de six mois se juge sur ce qu'il laisse : je construirais un système utile dès le
premier mois, qui reste au ministère à la fin. »

**« Comment travaillez-vous sous pression ? »**
Un récit d'une minute, terminé par un résultat : l'échéance de rapportage à Caris et la chaîne
réécrite pour que les contrôles tournent même le mois où tout le monde est débordé. Ou Anseye :
trois programmes en trois mois, de la définition des indicateurs à la restitution.

**« Comment travailleriez-vous avec le Chief of Party ? »**
« Sans surprise, dans les deux sens. Je lui dis ce que disent les données dès que je le sais,
surtout quand c'est une mauvaise nouvelle, avec l'analyse et une recommandation. Une page par mois
sur l'état des jalons et le facteur de vérification. Et je lui demande de trancher vite quand une
définition doit être négociée avec le bailleur, parce que c'est une décision de direction. »

**« Et l'hybride ? »**
« Je le pratique depuis des années : tout ce qui compte s'écrit, une seule source de vérité, des
heures de disponibilité explicites, des outils qui marchent sans connexion. En personne : le MSPP,
les sites, les formations. À distance : l'analyse, les rapports, les tableaux de bord. En Haïti,
l'hybride est aussi une assurance de continuité, comme vos trois bureaux. »

**« Quand seriez-vous disponible ? »**
Une date réelle, préavis compris, et rien ne se quitte avant une offre signée.

**« Vos prétentions salariales ? »**
Ne donne pas le premier chiffre. « J'aimerais d'abord connaître la fourchette prévue pour le poste ;
je suis sûr que nous trouverons un accord cohérent avec un poste de conseiller principal sur six
mois. » Si l'on insiste, donne **une fourchette mensuelle** dont le bas est au-dessus de ton
plancher, en précisant la devise. Une indemnité de connexion et d'énergie se discute *après* le
montant.

**« Code de conduite, PSEA ? »**
Oui, sans hésiter, et tu connais l'obligation de signaler immédiatement toute préoccupation par les
canaux établis.

**« Où vous voyez-vous dans cinq ans ? »**
« À la tête de l'information stratégique d'un programme de santé, idéalement en ayant contribué à ce
que les données du programme vivent dans les systèmes du ministère plutôt qu'à côté. »

### Tes quatre décisions, à écrire avant 11 h

1. **Tekkod** : arrêt ou suspension, ou mission réduite déclarée.
2. **Ton plancher salarial** mensuel, en devise, fixé seul.
3. **Ta date de disponibilité** réelle.
4. **Préviens Davidson Adrien**, (+509) 4460-6638, que l'Institut peut l'appeler : l'annonce prévoit
   une vérification rigoureuse des références.

### Si une partie se fait en anglais

> "For three years I was the M&E officer on Caris Foundation's Impact Youth HIV project. I ran
> routine multi-site reporting and submitted PEPFAR MER indicators to USAID through DATIM, as a data
> producer, not a platform administrator. My most direct indicator was AGYW_PREV under DREAMS: I
> produced and checked the layering data behind it. What I'm proudest of is data quality: I set up
> the DQA protocols, tracing reported figures back to source registers and following every
> corrective action to closure."

### Tes trois questions, à la fin

Sur le mécanisme : « AFGHS renvoie-t-il à l'America First Global Health Strategy, et comment le
paiement est-il construit : jalons de processus, cibles de résultats, et qui vérifie ? » Sur la
proximité : « Quand la ligne 8338 réfère quelqu'un vers les soins, comment savez-vous si la
référence a abouti ? » Sur les outils : « Pour le traçage dans EpiC, quels outils utilisez-vous ? »

---

## 7. La révision de vingt minutes — à 12 h 15

**Cinq minutes : les phrases.** Lis-les à voix haute, une fois.

Ils me veulent pour Caris : producteur de données MER dans DATIM, jamais administrateur ; DQA
jusqu'au registre source, actions suivies jusqu'à clôture ; 40 % de temps en moins en Python et SQL.
`AGYW_PREV` mesure la fidélité de la superposition, pas l'impact : groupes 1 et 2 sur les quatre
groupes, participantes actives seulement, 6 mois au T2 et 12 mois au T4, semestriel, saisi par
l'équipe USG, optionnel depuis la v2.8.2. L'IIT, c'est plus de 28 jours. La cohorte : début plus
`TX_NEW` plus `TX_RTT` moins `TX_ML`. Un patient ramené avant 28 jours n'est jamais un `TX_RTT`.
Couverture et suppression toujours ensemble. Un paiement sur jalon est un décaissement sur pièces. On
se vérifie avant d'être vérifié. Un écart expliqué est une information, un écart inexpliqué est un
risque de paiement. Chaque taux avec son dénominateur.

**Cinq minutes : le pitch et l'histoire Caris**, une fois chacun, chronométrés.

**Cinq minutes : les limites et les pièges.** Pas de master délivré, jamais « diplômé ». Pas de poste
de conseiller principal. Pas d'administration DHIS2. Pas de PTME pratiquée. MESI, SISNU, iSanté
Plus : le paysage. Aucun `TX_*` revendiqué. Pas de Projet Santé, pas de Stata. CHAMPIONS au passé,
l'audit jamais. Pas le premier chiffre de salaire. Dans une mise en situation : ce que je vérifie,
ce que je fais, à qui je le dis.

**Cinq minutes : la logistique.** Ordinateur branché, onduleur ou batterie prêts, partage de
connexion du téléphone prêt, casque, lumière face à toi, notifications coupées, nom affiché
« Alexandro Disla ». À côté de l'écran, sans les partager : le CV et la lettre envoyés, l'annonce, une
feuille pour les noms du panel. Si la connexion coupe : rejoins aussitôt, une phrase d'excuse, et
reprends. Si c'est impossible : `contact@institutpanos.org` et le **+509 2942-0321**. Connexion à
**12 h 45**.
