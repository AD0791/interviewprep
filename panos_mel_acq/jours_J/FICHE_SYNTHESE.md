# Fiche de synthèse — la passe d'une heure

*À lire ce soir, en entier, avant tout le reste. Chaque fiche condense un module ; le module donne
la profondeur, les sources et les réponses modèles complètes. L'ordre suit celui de l'entretien :
l'organisation, le mécanisme qui explique le poste, la technique, puis toi.*

---

## Fiche 1 — L'Institut Panos, et le passage qu'il est en train de faire

L'Institut Panos est une ONG haïtienne fondée le **29 juin 1986**, née de la communication sociale
dans la filiation de Panos Caraïbes, et devenue une organisation multisectorielle tournée vers les
enfants, les jeunes et les femmes. Elle couvre les **dix départements** depuis un bureau central à
**Pétion-Ville** (14, rue Borno) et deux bureaux régionaux, au **Cap-Haïtien** et aux **Cayes**. Trois
programmes : santé globale, gouvernance, assistance humanitaire.

Son cœur opérationnel est un dispositif de **proximité** : des SMS éducatifs en créole qui passent
sans internet (plus de 3,6 millions), la **ligne gratuite 8338** (plus de 1,36 million d'appels reçus,
19 754 appels assistés, 1 203 références vers les soins), et des relais communautaires dans les zones
enclavées. Sur le VIH, l'Institut revendique le premier **Forum national sur le sida**, les campagnes
**E=E**, **PrEP**, **TME** et **ARV**, puis **CHAMPIONS**, un projet USAID de changement de
comportement lancé en avril 2024 pour cinq ans et **arrêté au bout de dix mois** dans le gel de 2025.
Il est aujourd'hui **sous-partenaire d'EpiC** (PEPFAR, dirigé par FHI 360), avec un mandat précis :
éducation des patients, appui à l'adhérence, **traçage et retour en soins des patients en
interruption de traitement**, suppression virale.

Le point à comprendre, et à dire : une organisation dont le métier était de **toucher les gens**
recrute un responsable de l'information stratégique pour un programme de **prestation de services**
avec le MSPP, payé sur **jalons vérifiés**. Elle passe de la mesure de sa portée à la mesure du service
rendu. Montre que tu as vu ce passage, et cite un fait précis de leur site : la ligne 8338, E=E, ou
l'histoire de **Marie Tania Petit-Frère**, ambassadrice E=E qui livre aujourd'hui les ARV à domicile
à l'HUEH.

Ne parle jamais de CHAMPIONS au présent, ne commente pas leurs chiffres, et ne mentionne sous aucune
forme l'audit financier publié par l'inspecteur général de l'USAID en mai 2025 sur un précédent
accord. Tu le connais seulement pour comprendre pourquoi « la préparation aux vérifications
indépendantes » n'est pas une ligne décorative de l'annonce.

*Pour aller plus loin :* [`00_institut_panos.md`](00_institut_panos.md)

---

## Fiche 2 — AFGHS, et pourquoi les paiements dépendent de jalons

Le sigle du poste n'est expliqué nulle part. Il désigne très probablement l'**America First Global
Health Strategy**, publiée par le Département d'État le **18 septembre 2025**. Elle remplace la
logique des grands partenaires de mise en œuvre par des **accords bilatéraux** pluriannuels avec les
gouvernements. Les États-Unis y paient en 2026 la totalité des produits et des agents de santé de
première ligne, puis exigent un **co-financement** croissant. Les accords fixent des **cibles
annuelles** et permettent de **retenir le financement** si elles ne sont pas tenues, et ils financent
le renforcement des **systèmes de données nationaux**. Au 15 septembre 2026, **35 pays** ont signé
selon la KFF ; **Haïti n'en fait pas partie**, ce qui cadre avec l'« accord anticipé de six mois » de
l'annonce.

Tout cela est une **déduction**. Tu la poses donc comme une question : « Le sigle AFGHS renvoie-t-il à
l'America First Global Health Strategy ? Et comment le paiement est-il construit ? »

Ce que le mécanisme change au métier tient en quatre phrases. L'indicateur devient une clause de
contrat. Les systèmes nationaux deviennent la référence, d'où la réconciliation avec MESI, le SISNU et
iSanté Plus. La vérification fait partie de chaque cycle de paiement. Et six mois obligent à un
système utile dès le premier mois. L'analogie qui tient tout : **un paiement sur jalon est un
décaissement sur pièces justificatives**, et le responsable MEL est celui qui constitue les pièces.

*Pour aller plus loin :* [`01_afghs_et_jalons.md`](01_afghs_et_jalons.md) §§ 1-3

---

## Fiche 3 — Le jalon qui tient, et les façons dont il échoue

Il y a deux familles de jalons. Les **jalons de processus** (cadre validé, outil déployé, relais
formés, premier rapport de réconciliation) se prouvent par un document et protègent le démarrage. Les
**cibles de performance** (retour en soins, charge virale) se prouvent par des données et se
contestent.

La fiche d'un indicateur payant s'écrit comme une clause. Pour le retour en soins, l'interruption se
définit comme dans les MER, **plus de 28 jours sans ARV** après le dernier contact attendu, mais
**vérifiée au niveau national** ; la reprise se prouve par une **dispensation** dans les 30 jours
suivant le contact, jamais par la déclaration du relais ; les décès et transferts ne sortent du
dénominateur qu'avec une **pièce** ; et la fiche écrit **ses propres limites**, parce qu'une limite
déclarée est une réserve et une limite découverte est une faute.

Le jalon échoue de quatre façons : la **dérive de définition** (une promesse comptée comme un retour),
le **faux dénominateur** (des patients qui prenaient leurs ARV ailleurs), le **double comptage**, et la
**période décalée**. Et une cinquième, qui montre que tu connais les indicateurs : **le piège des
28 jours**. Un patient ramené avant le 28e jour n'est jamais un `TX_RTT` ; un jalon écrit sur les seuls
retours après interruption paie donc pour laisser les gens décrocher. Il faut suivre aussi les
rendez-vous manqués rattrapés à temps.

*Pour aller plus loin :* [`01_afghs_et_jalons.md`](01_afghs_et_jalons.md) §§ 4-5

---

## Fiche 4 — Se vérifier avant d'être vérifié

Le vérificateur tire un échantillon de patients déclarés, cherche pour chacun la fiche de traçage, la
dispensation et la preuve de l'interruption, et calcule le **facteur de vérification** : ce qu'il
retrouve dans les sources, divisé par ce qui a été rapporté. En dessous de 1, sur-déclaration ;
au-dessus, sous-déclaration. La tolérance est une clause de l'accord, à demander.

La règle est de faire la même chose soi-même, **chaque mois**, avant l'échéance, et de tenir pour
chaque jalon un **dossier de preuve** : la version de la fiche, l'extraction, le calcul, le résultat de
la pré-vérification et les actions correctives. C'est la discipline que tu pratiquais chez Caris en
DQA, remonter du chiffre au registre source et suivre les actions correctives jusqu'à clôture, et
c'est l'argument central de ta lettre.

Un point de statistique qui impressionne : quarante dossiers et vingt-huit confirmés, soit 70 %, c'est
une fourchette de **plus ou moins 14 points** à 95 %. Pour plus ou moins 5 points autour de 80 %, il
faut environ **246 dossiers**, ou **153** si la population ne compte que 400 retours déclarés. La
taille de l'échantillon se négocie dans l'accord.

Les incitations à surveiller sont la sur-déclaration, la mauvaise classification (« transféré » pour
les introuvables), l'écrémage (tracer d'abord les patients faciles) et l'éviction de ce qui n'est pas
payé. Les contrôles : la triangulation avec les ARV dispensés, la contre-vérification par une autre
personne que le relais, le suivi des indicateurs non payés, une piste d'audit. Et une idée propre à
Panos, à présenter avec sa contrainte de confidentialité : utiliser la ligne 8338 pour rappeler un
échantillon de patients déclarés revenus.

*Pour aller plus loin :* [`01_afghs_et_jalons.md`](01_afghs_et_jalons.md) §§ 6-7 et
[`04_analyse_et_tableaux_de_bord.md`](04_analyse_et_tableaux_de_bord.md) § 6

---

## Fiche 5 — La réconciliation avec les systèmes nationaux

**iSanté Plus** est le dossier médical électronique nominatif des sites ; **SALVH** la base nationale
longitudinale et dédupliquée, qui comptait 308 500 personnes diagnostiquées en janvier 2024 et relie
les dossiers par l'empreinte digitale (disponible pour environ 60 % des personnes sous traitement) ;
**MESI** l'interface de rapportage VIH du ministère ; le **SISNU** le rapportage agrégé national, sur
DHIS2 ; **DATIM** la plateforme du PEPFAR.

Les chiffres divergent pour cinq raisons, toujours les mêmes : la **définition**, le **périmètre**, la
**période**, l'**identité** et la **latence**. Le rapport mensuel de réconciliation met côte à côte la
valeur du programme et celle de chaque système, l'écart, sa cause et l'action. La phrase à dire : **un
écart expliqué est une information ; un écart inexpliqué est un risque de paiement.**

La limite, à dire toi-même : « Je connais ces systèmes comme paysage, je ne les ai pas exploités. J'ai
produit des données pour DATIM et construit des pipelines et des déduplications entre des sources qui
ne se parlaient pas ; je commencerais par comprendre les définitions et les identifiants de chaque
système avant de comparer un seul chiffre. »

Et l'objectif final, qui est celui de la stratégie américaine : renforcer le MSPP plutôt que
construire à côté. Définitions et identifiants nationaux, outils du ministère quand ils suffisent,
responsables départementaux associés à chaque rapport, tout documenté. **Le meilleur système d'un
programme de transition est celui qu'on peut arrêter au sixième mois sans que le ministère perde ses
données.**

*Pour aller plus loin :* [`01_afghs_et_jalons.md`](01_afghs_et_jalons.md) §§ 8-9

---

## Fiche 6 — La chaîne MEL en sept étapes, sur un exemple réel

C'est la démonstration à faire si l'on te demande « comment feriez-vous ». Le module 02 la construit
pour le mandat EpiC de l'Institut, le traçage des patients en interruption, avec un jeu de données
d'exercice et des requêtes SQL qui tournent.

La **théorie du changement** écrit ses hypothèses (ARV disponibles, patient joignable, accès
possible). Le **cadre de résultats** est court : la suppression virale des patients revenus avec sa
couverture, la reprise prouvée par dispensation, les rendez-vous manqués rattrapés avant 28 jours, la
rétention à trois mois, les visites et contacts, et une ligne de qualité des données. Le **chemin de la
donnée** part du dossier électronique, passe par une liste vérifiée au niveau national, arrive sur la
tablette du relais hors ligne, et revient dans une base où la visite est rapprochée de la dispensation.
Le **formulaire** fait choisir le patient dans la liste du relais au lieu de taper son code, fait
confirmer le code de la carte, et **ne demande jamais si le patient est revenu** : il demande le
rendez-vous. Pas de GPS, pas de nom dans les soumissions, formulaire chiffré. Les **requêtes**
normalisent les codes, dédoublonnent avec `ROW_NUMBER`, vérifient les retours par la dispensation et
écartent les faux interrompus. Le **tableau de bord** a une page par public. Et l'**apprentissage**
tient en trois questions, une revue mensuelle et une pause au troisième mois, avec des cycles PDSA
adossés au programme national **HEALTHQUAL** du MSPP.

Le résultat à retenir : sur le jeu d'exercice, **41 retours déclarés sur 105 listés (39 %)** deviennent
**27 retours vérifiés sur 92 vrais interrompus (29,3 %)**, après une visite au code irrécupérable, trois
doublons, un facteur de vérification de 0,75 et **13 faux interrompus (12,4 %)**, dont sept passaient
pour des retours vérifiés. En entretien, dis « sur un jeu de données d'exercice », jamais « dans un
programme ».

Le plan de six mois se dit en une minute : deux semaines d'écoute qui livrent le premier jet du cadre ;
cadre validé et formulaire testé à la fin du premier mois ; déploiement et tableau de bord au
deuxième ; première réconciliation et pré-vérification au troisième ; amélioration et co-production
avec les directions départementales aux quatrième et cinquième ; vérification finale et transfert au
MSPP au sixième.

*Pour aller plus loin :* [`02_chaine_mel_bout_en_bout.md`](02_chaine_mel_bout_en_bout.md)

---

## Fiche 7 — Le VIH, vu depuis le mandat de Panos

Panos travaille sur les **deux derniers 95** (maintien sous traitement, suppression virale), sur la
**demande** de services (PrEP, charge virale) et sur la **stigmatisation**. Pars de ce mandat, pas de
la cascade entière.

L'**interruption** commence au-delà de **28 jours** sans ARV après le dernier contact attendu.
**`TX_ML`** compte les sorties par devenir : décès, transfert, refus ou arrêt, interruption, cette
dernière ventilée selon le **temps passé sous traitement avant de décrocher**, et non selon la durée de
l'absence (c'est la lecture exacte de la formule ambiguë de la fiche CMMB). **`TX_RTT`** compte les
retours après plus de 28 jours d'interruption. L'équation de cohorte relie tout : `TX_CURR` de fin
égale début plus `TX_NEW` plus `TX_RTT` moins `TX_ML`.

La **couverture** en charge virale et le **taux de suppression** se donnent toujours ensemble : l'étude
de 2025 rapporte 86 % de suppression **chez les personnes testées**, et E=E, qui veut « créer la demande
de tests de charge virale », agit sur la couverture.

La **dispensation différenciée** (plus de cinquante points de distribution, multi-mois, livraison à
domicile) et près de **1,5 million de déplacés internes** selon l'OIM font qu'un patient est souvent
servi ailleurs que là où il est suivi, d'où les faux perdus de vue : la déduplication nationale dans
SALVH réduit d'environ **14 %** les perdus de vue apparents, et de 41,5 % pour la cohorte 2021-2022.

Pour la PrEP, `PrEP_NEW` et `PrEP_CT`, et l'effet d'une campagne se démontre par une **analyse de
contribution**, jamais par une attribution. Pour le changement de comportement, sépare la **portée**,
l'**exposition** et le **changement** : « 1 M de jeunes potentiellement atteints » est une portée
potentielle.

Ton expérience : officier S&E sur le programme VIH **Impact Youth** de Caris, MER via DATIM comme
**producteur**, exemple confirmé **`AGYW_PREV`** sous DREAMS, et la phrase de périmètre (« je connais
la logique des indicateurs de traitement pour l'avoir étudiée, pas pour les avoir produits »). Pas de
PTME, pas de `TX_*` rapportés, pas d'administration DHIS2.

*Pour aller plus loin :* [`03_vih_pour_panos.md`](03_vih_pour_panos.md) et, ce soir,
[`../cmmb_meal_officer/FICHE_MER_INDICATEURS.md`](../cmmb_meal_officer/FICHE_MER_INDICATEURS.md)

---

## Fiche 8 — Analyse et tableaux de bord

La règle unique : **un taux ne s'affiche jamais sans son numérateur et son dénominateur, et un taux
agrégé est une somme de numérateurs sur une somme de dénominateurs.** Neuf sur dix et soixante sur
deux cents ne font pas 60 % en moyenne, ils font 32,9 % ensemble ; dans Power BI, c'est
`DIVIDE([Retours vérifiés], [Vrais IIT])` et non `AVERAGE` d'une colonne de taux.

La **file active** se calcule par la couverture d'ARV, jours fournis plus 28 jours de grâce ; vue du
site, elle perd les patients servis ailleurs (666 contre 679 sur le jeu d'exercice), et c'est pourquoi
un `TX_CURR` national n'est jamais la somme des sites. La **complétude** et la **promptitude**
accompagnent chaque indicateur. Les **anomalies** s'automatisent dès le premier mois : numérateur
supérieur au dénominateur, variation au-delà d'un seuil, valeurs répétées, dates de saisie concentrées
après une panne.

Un tableau de bord est une collection de réponses : une page pour le Chief of Party (jalons,
trajectoire, facteur de vérification, sites à risque), une pour le MSPP (sites, complétude,
réconciliation), des listes pour les superviseurs, en créole et sans pourcentages ; la sécurité au
niveau des lignes pour les directions départementales ; un PDF daté chaque mois. Et le réflexe :
**recalcule chaque ratio qu'on te donne**, sans jamais corriger ton hôte.

*Pour aller plus loin :* [`04_analyse_et_tableaux_de_bord.md`](04_analyse_et_tableaux_de_bord.md)

---

## Fiche 9 — Le pitch et les limites

Le pitch suit quatre mouvements : la **formation** (économiste appliqué, formé au CTPEA, jamais
« diplômé ») ; le **VIH au centre** (Caris, Impact Youth, MER via DATIM, DQA) ; les **deux compétences
et le ministère** (collecte numérique et MEAL, dont trois programmes en trois mois chez Anseye ;
ingénierie de données ; huit ans au ministère du Plan) ; **leur annonce** (jalons vérifiables,
réconciliation, chaîne complète en quelques semaines, hybride). Quatre-vingt-dix secondes.

Les cinq limites, dans les mots de la lettre : pas de master délivré ; cinq ans en ONG dont trois sur
le VIH et huit au ministère, sans poste de conseiller technique principal ; producteur de données dans
DATIM, pas administrateur ; la PTME connue, pas pratiquée ; MESI, SISNU et iSanté Plus connus comme
paysage, pas exploités. Énonce-en au moins une toi-même.

À la question « il vous manque le master et les dix ans », ne t'excuse pas : confirme, puis dis ce que
le programme demande dès le premier mois, et que ce profil (avoir rapporté dans DATIM et savoir
construire le système qui l'alimente) est plus rare que les années.

*Pour aller plus loin :* [`05_parcours_pression_hybride.md`](05_parcours_pression_hybride.md) §§ 2-4

---

## Fiche 10 — La pression et l'hybride

Quatre récits, une minute chacun, terminés par un résultat et par une phrase qui les relie au poste.
**Caris** : la chaîne manuelle de rapportage réécrite en Python et SQL, contrôles intégrés, environ
**40 %** de temps de traitement en moins, et un contrôle exécuté même le mois où tout le monde est
débordé. **Anseye** : trois programmes en trois mois, de la définition des indicateurs à la
restitution, la version réduite de ce que demande AFGHS. **Tekkod** : une connexion de **36 secondes
ramenée sous la demi-seconde** en éliminant des requêtes en boucle, et des index composites contre les
verrous. **HANWASH** : régler à distance les problèmes de collecte de terrain, et écrire les guides pour
qu'ils ne reviennent pas.

Dans une mise en situation, dis toujours **ce que tu vérifies, puis ce que tu fais, puis à qui tu le
dis**. Un chiffre incomplet se donne avec sa complétude, jamais rempli avec une estimation présentée
comme une donnée ; une mauvaise nouvelle va au Chief of Party le jour même.

L'hybride se démontre : Tekkod et HANWASH en télétravail sur le CV déposé ; tout ce qui compte s'écrit ;
une seule source de vérité ; des heures de disponibilité explicites ; des systèmes qui marchent sans
connexion. En personne : le MSPP, les sites, les formations, l'équipe. À distance : l'analyse, les
rapports, les tableaux de bord. En Haïti, l'hybride est une assurance de continuité, exactement ce que
leurs trois bureaux revendiquent. Et l'entretien sur Zoom est ta première preuve.

*Pour aller plus loin :* [`05_parcours_pression_hybride.md`](05_parcours_pression_hybride.md) §§ 5-6 et
[`06_simulation_entretien.md`](06_simulation_entretien.md) bloc 5

---

## Fiche 11 — Salaire, disponibilité, références, sauvegarde

Ne donne pas le premier chiffre : demande la fourchette budgétée. C'est un poste de **niveau
conseiller principal**, sur **six mois conditionnés** : fixe ce soir ton plancher en tenant compte de
Tekkod, pense en mensuel, en devise et en conditions, et place une indemnité de connexion et d'énergie
**après** le montant. Donne une date de disponibilité réelle, préavis compris, et ne quitte rien avant
une offre signée. **Préviens Davidson Adrien**, ta référence, parce que l'annonce prévoit une
vérification rigoureuse des références. Sur la PSEA et le Code de conduite : oui, sans hésiter, et tu
connais l'obligation de signaler.

*Pour aller plus loin :* [`05_parcours_pression_hybride.md`](05_parcours_pression_hybride.md) §§ 7-8

---

## Fiche 12 — Les cinq minutes qui restent

Si tu n'as que cinq minutes demain, relis ces phrases.

L'Institut passe de la mesure de sa portée à la mesure du service rendu, sous un mécanisme où
l'argent suit des jalons vérifiés. **Un paiement sur jalon est un décaissement sur pièces.** Avant de
tracer un patient, vérifier qu'il est réellement perdu. Le retour se prouve par la dispensation, pas
par le relais. Un patient ramené avant 28 jours n'est jamais un `TX_RTT`. On se vérifie avant d'être
vérifié. Un écart expliqué est une information, un écart inexpliqué est un risque de paiement. Le
meilleur système d'un programme de transition est celui que le ministère sait faire tourner sans nous.
Et chaque taux se donne avec son dénominateur.

Tes questions : AFGHS et la construction du paiement ; comment savoir si une référence de la 8338 a
abouti ; les outils de traçage utilisés dans EpiC.
