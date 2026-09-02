# Statistiques et analyse de données pour ce poste

*Module 5 — l'annonce demande d'« excellentes compétences analytiques », la connaissance du
quantitatif et du qualitatif, l'expérience de la planification et de la gestion d'enquêtes, et de
coordonner avec les statisticiens l'assistance technique aux institutions. La statistique
générale — position, dispersion, corrélation, tests d'hypothèse, taille d'échantillon,
régression — est traitée dans
[`../assitant_pmel/02_statistiques_pmel.md`](../assitant_pmel/02_statistiques_pmel.md) et il faut
la relire. Ce module traite ce que la santé publique y ajoute et ce qu'un entretien CMMB peut
réellement te demander.*

---

## 1. Les mesures épidémiologiques : la distinction qui tombe toujours

**Prévalence et incidence.** La prévalence est un **stock** : la proportion de personnes qui
vivent avec la maladie à un moment donné. L'incidence est un **flux** : le nombre de nouvelles
infections survenues pendant une période, rapporté à la population exposée. La prévalence du VIH
en Haïti est de 1,8 % selon l'enquête HAPHIA ; l'incidence est le nombre de personnes qui
contractent le virus chaque année.

**Voici le piège, et il est spécifique au VIH, donc il est plausible en entretien.** Quand un
programme réussit, la prévalence **monte**. Elle monte parce que le traitement antirétroviral
empêche les gens de mourir : le stock grossit alors même que le flux diminue. Une prévalence en
hausse peut donc signaler soit une épidémie qui s'aggrave, soit un programme de traitement qui
fonctionne, et **la prévalence seule ne permet pas de trancher**. Ce qui mesure le succès de la
prévention, c'est l'incidence ; ce qui mesure le succès du traitement, c'est la suppression
virale et la mortalité. Un candidat qui dit cela spontanément démontre qu'il comprend
l'épidémiologie et pas seulement l'arithmétique.

**Taux, ratio, proportion.** La distinction générale est traitée dans le module PMEL, mais la
santé maternelle ajoute une confusion célèbre qu'il faut connaître. Le **ratio de mortalité
maternelle** rapporte les décès maternels à 100 000 **naissances vivantes** — c'est un ratio,
parce que le numérateur n'est pas inclus dans le dénominateur. Le **taux de mortalité
maternelle**, plus rarement employé, rapporte ces décès aux femmes en âge de procréer. Les deux
ne sont pas interchangeables, et la valeur qu'on cite habituellement pour Haïti — de l'ordre de
480 pour 100 000 selon les chiffres publiés par CMMB pour la période 2019-2020 — est un **ratio**.

**Le temps-personne.** Quand on suit des patients pendant des durées inégales — ce qui est
toujours le cas d'une cohorte sous traitement, puisque les gens entrent à des dates différentes —
on ne peut pas simplement diviser les événements par le nombre de patients. On divise par la
somme des durées de suivi, en **personnes-années**. C'est la notion qui fonde correctement un
taux d'interruption ou de mortalité sous traitement, et la nommer suffit à montrer que tu sais de
quoi tu parles.

---

## 2. L'analyse de cohorte : le cœur technique du suivi VIH

Une **cohorte** est un groupe défini par un événement d'entrée commun — ici, la mise sous
traitement antirétroviral pendant un trimestre donné — que l'on suit dans le temps. C'est
l'instrument qui répond à la question de la rétention, et il faut savoir en parler.

Le principe est simple : on prend la cohorte des patients mis sous traitement au premier
trimestre d'une année, et on regarde, douze mois plus tard, combien sont encore en soins,
combien sont décédés, combien ont été transférés, combien sont perdus de vue. La somme des
devenirs doit égaler l'effectif de départ. **C'est cette égalité qui est le contrôle qualité le
plus puissant du domaine**, et c'est celle qui se casse en premier quand un site se dégrade,
comme expliqué dans [`03_vih_essentiel.md`](03_vih_essentiel.md).

Deux précisions techniques qui font la différence si on te pousse.

**Les patients transférés sortants doivent être retirés du dénominateur**, pas comptés comme des
échecs. Un patient transféré vers un autre site n'est pas perdu pour le système de santé ; il est
perdu pour ce site. Confondre les deux détruit la comparabilité entre sites : un site situé près
d'une zone de départ affichera une rétention artificiellement mauvaise.

**La censure.** Un patient mis sous traitement il y a huit mois ne peut pas contribuer à un taux
de rétention à douze mois : il n'a pas encore eu l'occasion d'atteindre l'échéance. L'inclure au
dénominateur comme s'il était un succès gonfle le résultat ; l'inclure comme un échec le
détruit. On l'exclut, ou on utilise une méthode qui gère explicitement les durées inégales —
c'est ce que fait l'analyse de survie, dont l'estimateur de Kaplan-Meier est la forme la plus
connue. Tu n'as pas besoin de savoir la calculer ; tu dois savoir que le problème existe et
qu'il porte un nom.

---

## 3. Le dénominateur en santé publique : la source d'erreur numéro un

Un indicateur de couverture est une fraction, et en santé le numérateur vient du registre pendant
que le **dénominateur vient d'ailleurs**. C'est cette asymétrie qui produit les erreurs les plus
graves et les plus difficiles à voir.

Une couverture vaccinale a pour dénominateur le nombre d'enfants de moins d'un an dans l'aire de
desserte. Ce nombre n'est pas compté : il est obtenu en appliquant un coefficient démographique —
la proportion attendue de nourrissons dans la population — à une projection de population fondée
sur un recensement souvent ancien. En Haïti, le dernier recensement général remonte à 2003, et
les déplacements de population liés à l'insécurité ont vidé et rempli des quartiers entiers en
quelques mois.

Les symptômes d'un dénominateur faux sont reconnaissables et il faut savoir les nommer. Une
**couverture supérieure à cent pour cent** signale presque toujours un dénominateur trop petit,
ou un numérateur qui inclut des personnes venues d'ailleurs — un centre de référence qui dessert
au-delà de son aire théorique. Une **couverture anormalement basse et stable** sur un site par
ailleurs actif signale un dénominateur trop grand. Et un **saut brutal de la couverture au
1er janvier**, sans qu'aucune activité ait changé, signale simplement la mise à jour annuelle des
projections de population.

La conduite à tenir se résume en une phrase que tu peux dire telle quelle : « quand une couverture
bouge, je vérifie le dénominateur avant d'interpréter le numérateur, parce qu'un dénominateur qui
change ressemble exactement à un programme qui change ».

---

## 4. Les enquêtes : ce que « planifier et gérer une enquête » veut dire

L'annonce demande explicitement l'expérience de la planification et de la gestion d'enquêtes. Il
faut pouvoir décrire la séquence complète sans hésiter, parce que c'est une question de
vérification d'expérience.

On part de la **question à laquelle l'enquête doit répondre**, et non de l'inverse — une enquête
qui commence par un questionnaire produit un questionnaire de quatre-vingts questions dont
personne n'exploitera la moitié. On choisit ensuite le **type** : enquête de base, à mi-parcours,
finale, enquête de satisfaction, enquête post-distribution. On définit la **population cible** et
la **base de sondage** — la liste à partir de laquelle on tire, et c'est souvent le point faible,
parce qu'une liste incomplète produit un biais qu'aucun traitement statistique ne rattrape. On
détermine le **plan de sondage** et la **taille d'échantillon**. On conçoit le **questionnaire**,
on le traduit en créole, et on le **teste sur le terrain** avant de le déployer. On le code en
**XLSForm** avec ses contraintes et ses logiques de saut, ce que tu sais faire. On forme les
enquêteurs et on organise leur supervision. On collecte avec un **contrôle qualité en cours de
collecte** et non seulement à la fin. Puis on nettoie, on analyse, on rédige, et on restitue.

**Les plans de sondage à savoir nommer.** L'**aléatoire simple** suppose une base de sondage
complète, ce qui est rare. Le **stratifié** découpe la population en groupes homogènes — par
département, par milieu urbain et rural — et tire dans chacun ; il garantit la représentation de
chaque strate et améliore la précision. Le **grappes** tire d'abord des zones puis enquête
plusieurs ménages dans chacune ; c'est le plan des grandes enquêtes de terrain parce qu'il réduit
massivement les coûts de déplacement, au prix d'une perte de précision qu'on appelle l'**effet de
grappe** et qu'on compense en augmentant la taille d'échantillon. Le **systématique** prend un
individu tous les *n* dans une liste ordonnée.

**Et un plan qu'il faut connaître spécifiquement parce qu'il est propre à la santé : le LQAS**,
*lot quality assurance sampling*, échantillonnage pour l'assurance qualité par lots. Importé du
contrôle qualité industriel, il ne vise pas à estimer un taux avec précision mais à **classer une
zone** — atteint-elle ou non un seuil de performance ? Il permet de conclure sur de très petits
échantillons, typiquement dix-neuf observations par zone, ce qui le rend utilisable pour une
supervision de routine sur de nombreux sites. C'est exactement le genre d'outil qu'un officier de
suivi-évaluation propose quand on lui demande de vérifier trente institutions avec les moyens du
bord, et le citer te distingue immédiatement.

---

## 5. Détecter les anomalies dans des données de routine

C'est la compétence pratique la plus directement utile du poste, et c'est là que ton expérience
d'automatisation devient concrète. Voici la batterie de contrôles qu'on applique à un jeu de
rapports mensuels d'institutions sanitaires.

**Les contrôles de complétude et de ponctualité** d'abord : quels sites attendus n'ont pas
rapporté, et lesquels ont rapporté hors délai. C'est le contrôle le plus simple et le plus
important, parce que **tout indicateur doit être publié avec son taux de complétude**. Un taux de
suppression virale calculé sur 60 % des sites n'a pas la même valeur que le même chiffre calculé
sur la totalité, et ne pas le dire est une faute.

**Les valeurs aberrantes** ensuite. La méthode standard du cadre DQR de l'OMS consiste à comparer
la valeur du mois à la moyenne des mois précédents du même site, et à signaler tout écart
supérieur à un nombre donné d'écarts-types. La médiane et l'écart interquartile sont plus robustes
que la moyenne et l'écart-type quand les données sont sales, ce qui est le cas général. On
signale, on ne corrige pas : une valeur aberrante peut parfaitement être vraie — une campagne de
dépistage, une épidémie, l'ouverture d'un service.

**Les contrôles de cohérence logique**, qui sont les plus productifs. Ils encodent des relations
qui ne peuvent pas être violées : le nombre de quatrièmes consultations prénatales ne peut pas
dépasser le nombre de premières ; le nombre de tests positifs ne peut pas dépasser le nombre de
tests réalisés ; le nombre de patients mis sous traitement ne peut pas dépasser le nombre de
diagnostics ; la somme des désagrégations par sexe doit égaler le total. Chacune de ces règles
est une ligne de SQL, et chacune attrape une famille entière d'erreurs de saisie.

**Les contrôles de cohérence temporelle** : une série strictement identique d'un mois sur
l'autre est presque toujours une donnée recopiée plutôt que relevée. C'est un signal fort et
facile à automatiser.

**Les contrôles inter-systèmes**, enfin : le même indicateur produit par deux sources doit
concorder. Les nouvelles consultantes prénatales du programme de santé maternelle et le
dénominateur de l'indicateur de statut VIH en consultation prénatale décrivent les mêmes femmes.
S'ils divergent, l'une des deux chaînes a un problème.

**Et la règle qui accompagne tout cela.** Une alerte n'a de valeur que si elle est vraie assez
souvent pour qu'on continue à la lire. Un jeu de règles qui produit six alertes dont cinq sont
des faux positifs fait perdre du temps aux équipes, et à la troisième fois plus personne
n'ouvre le fichier. On croise donc systématiquement les règles avec le **référentiel des sites** —
un site qui n'offre pas un service déclarera légitimement zéro tous les mois — et on ajuste les
seuils jusqu'à ce que le taux de faux positifs soit supportable.

---

## 6. Interpréter sans se tromper

Trois pièges d'interprétation, tous plausibles en entretien.

**La moyenne non pondérée.** C'est le piège classique du métier, traité en détail dans
[`../assitant_pmel/02_statistiques_pmel.md`](../assitant_pmel/02_statistiques_pmel.md), et il
faut savoir le formuler en une phrase : la moyenne des taux des sites n'est pas le taux global.
Faire la moyenne des taux de suppression virale de vingt sites donne un poids égal à un site de
quarante patients et à un site de quatre mille. **Le taux global se calcule en additionnant les
numérateurs et en additionnant les dénominateurs**, jamais en moyennant des pourcentages. Les
deux chiffres ont chacun leur usage — la moyenne non pondérée décrit la performance typique d'un
site, le taux global décrit la performance du programme — mais on ne les confond pas et on dit
lequel on présente.

**Le paradoxe de Simpson.** Une tendance visible dans chaque sous-groupe peut s'inverser dans
l'agrégat, quand la composition des groupes change. Un programme peut voir son taux global de
suppression virale baisser alors qu'il s'améliore dans chaque tranche d'âge, simplement parce
qu'il a récemment recruté beaucoup d'adolescents, dont la suppression est structurellement plus
basse. La leçon : **avant de conclure qu'un indicateur s'est dégradé, vérifie si la population
qu'il décrit a changé.** C'est un argument de désagrégation, et il impressionne.

**Corrélation et causalité.** Le fait que les sites ayant reçu une formation affichent de
meilleurs résultats ne prouve pas que la formation les a produits : peut-être a-t-on formé en
priorité les sites déjà les mieux organisés. La réponse honnête consiste à nommer le **biais de
sélection** et à dire ce qu'il faudrait pour conclure — une comparaison avant-après sur les deux
groupes, ce qu'on appelle la **différence de différences**, ou un plan d'attribution qui ne soit
pas fondé sur la performance préalable.

---

## 7. Les outils, tels que l'annonce les demande

L'annonce cite nommément Word, **Excel**, **Access**, PowerPoint et GSuite. La mention d'Access
est révélatrice : elle signale des bases de données locales, sur poste, dans des institutions
sanitaires — ce qui est cohérent avec la réalité du terrain haïtien.

Sur **Excel**, sache dire ce que tu fais réellement : tableaux croisés dynamiques, recherches et
correspondances entre tables, sommes et comptages conditionnels, mise en forme conditionnelle
pour signaler visuellement les anomalies, et surtout **Power Query** pour enregistrer une fois la
chaîne de nettoyage et la rejouer chaque mois. L'argument à donner sur Power Query est celui du
coût : la première mise en place coûte une journée, les onze cycles suivants coûtent deux
minutes, et le temps libéré va à l'analyse.

Sur **Access**, sois exact : ce n'est pas ton outil principal, mais le modèle relationnel l'est
entièrement — tables, clés, relations, jointures, requêtes. Une phrase honnête et forte : « Access
est une base relationnelle avec une interface ; je travaille quotidiennement en SQL sur MySQL et
PostgreSQL, donc l'objet m'est familier même si ce n'est pas l'outil que j'utilise le plus. Ce que
j'apporterais surtout sur ce point, c'est la vigilance sur les fichiers Access locaux : ils vivent
sur un poste, ils sont rarement sauvegardés, et ils sont une cause classique de perte de données
dans les institutions. »

Sur le reste, tu es en terrain solide et ton CV le porte : SQL, Python et Pandas, R et Quarto,
Power BI, Looker Studio, Stata. Ne noie pas l'interlocuteur sous les outils. La phrase qui
fonctionne est celle qui relie l'outil au problème : « j'automatise les contrôles qui doivent
tourner à chaque cycle, parce qu'un contrôle manuel est un contrôle qu'on saute le mois où l'on
est débordé ».

---

## Angles d'entretien

**« Nous vous donnons l'export brut du rapportage mensuel de trente institutions. Par où
commencez-vous ? »**

C'est l'exercice le plus probable si l'entretien devient pratique.

« Je ne commence pas par l'analyse, je commence par le décompte de ce qui manque. Combien de
sites attendus, combien ont rapporté, à quelle date — parce que le taux de complétude conditionne
la lecture de tout le reste et qu'il doit accompagner chaque chiffre que je publierai ensuite.

Ensuite je conserve le brut intact. Je ne modifie jamais l'onglet ou la table d'origine : c'est
la trace de ce qui a été reçu, et c'est ce qui permet de refaire le travail si une décision de
nettoyage se révèle mauvaise. Le nettoyage se fait dans une copie, et chaque décision est tracée.

Puis j'applique les contrôles dans l'ordre du plus grossier au plus fin : les doublons d'abord,
puis les types et les formats — dates impossibles, âges négatifs, codes de site inconnus au
référentiel —, puis les règles de cohérence logique entre indicateurs, puis les valeurs aberrantes
par rapport à l'historique de chaque site, puis les séries figées d'un mois sur l'autre.

Chaque anomalie va dans un journal : site, période, indicateur, valeur observée, valeur attendue,
gravité, action, responsable. Je ne corrige pas moi-même une donnée de site ; je remonte au site,
parce que l'anomalie m'apprend souvent quelque chose sur le processus de collecte lui-même, et
qu'une anomalie qui se répète devient une ligne du plan d'action du cycle suivant plutôt qu'une
correction de plus.

Et enfin seulement, je calcule les indicateurs, avec leurs désagrégations, en additionnant les
numérateurs et les dénominateurs plutôt qu'en moyennant des taux, et je publie chaque indicateur
avec son taux de complétude et les réserves qui s'imposent. »

**« Un indicateur chute de trente pour cent d'un mois sur l'autre. Que faites-vous ? »**

« Quatre hypothèses, dans cet ordre, parce qu'elles vont de la plus fréquente à la plus rare.

Premièrement, un problème de complétude : un ou plusieurs sites n'ont pas rapporté ce mois-là.
C'est de loin la cause la plus courante d'une chute brutale, et elle se vérifie en trente
secondes en comparant la liste des sites rapporteurs.

Deuxièmement, un problème de dénominateur ou de définition : la population cible a été mise à
jour, ou la règle de comptage a changé sans que tout le monde l'applique en même temps.

Troisièmement, un événement opérationnel réel : une rupture de stock de tests ou
d'antirétroviraux, une panne du système informatique du site qui a créé un arriéré de saisie, une
fermeture liée à l'insécurité, le départ d'un agent non remplacé. C'est pour cela que je tiens un
journal des incidents à côté des indicateurs : un chiffre s'interprète avec le contexte
opérationnel du mois, pas contre lui.

Et quatrièmement seulement, une vraie dégradation de la performance du programme. C'est
l'hypothèse la plus grave, donc c'est la dernière que je retiens, une fois les trois autres
écartées — et à ce moment-là je la documente et je la remonte immédiatement, parce qu'une
dégradation réelle ne s'améliore pas en attendant le cycle suivant. »
