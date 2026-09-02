# Le MEAL appliqué à la santé

*Module 4 — le métier lui-même, décliné sur les composantes que l'annonce cite : RMCNH, WASH,
financement basé sur les résultats, préparation aux catastrophes. La théorie générale n'est pas
recopiée ici : chaîne de résultats, cadre logique, critères du CAD, conception d'indicateurs et
indices composites sont traités dans
[`../assitant_pmel/01_meal_processus.md`](../assitant_pmel/01_meal_processus.md) et
[`../assitant_pmel/05_indicateurs_et_indices.md`](../assitant_pmel/05_indicateurs_et_indices.md).
Relis-les la veille. Ce module traite ce qui change quand l'objet mesuré est un service de santé.*

---

## 1. Ce que le sigle contient, et pourquoi CMMB écrit « M&E » et pas « MEAL »

**MEAL** signifie *monitoring, evaluation, accountability and learning* — suivi, évaluation,
redevabilité et apprentissage. Le **suivi** est continu et interne : il répond à « faisons-nous
ce que nous avions prévu, au rythme prévu ? ». L'**évaluation** est ponctuelle et prend du recul :
elle répond à « cela a-t-il produit l'effet attendu, et pourquoi ? ». La **redevabilité** est
l'obligation de rendre compte, aux bailleurs vers le haut mais aussi aux bénéficiaires et aux
autorités locales vers le bas et vers le côté. L'**apprentissage** est ce qui distingue une
organisation qui produit des rapports d'une organisation qui change de pratique.

L'annonce de CMMB dit « M & E Officer », sans les deux dernières lettres. Ne conclus pas qu'ils
ignorent la redevabilité et l'apprentissage : le vocabulaire du secteur santé américain, celui du
PEPFAR et du CDC, dit « M&E » et dit « **strategic information** » là où le secteur humanitaire
européen dit « MEAL ». D'ailleurs le texte de l'annonce est explicite sur l'apprentissage sans
employer le mot : *« build the data culture at health facilities to improve data demand and data
use »*, construire la culture de la donnée pour accroître la demande et l'usage de
l'information. **La demande de données et l'usage des données** — *data demand and use* — sont
le vocabulaire propre du domaine, et les employer te situe immédiatement.

Retiens donc la traduction : ce que tu appelles apprentissage, ils l'appellent *data use*. Ce que
tu appelles suivi-évaluation, ils l'appellent aussi *strategic information*, abrégé **SI** — et
c'est ce sigle qui apparaît dans leur phrase sur les formations à conduire dans les institutions
sanitaires.

---

## 2. Le suivi de routine en santé : le chemin réel d'un chiffre

Voici la chose la plus importante de ce module. Un officier de suivi-évaluation en santé doit
savoir décrire, de mémoire et en détail, le trajet d'une donnée depuis le patient jusqu'au
bailleur. C'est la question que pose un directeur suivi-évaluation pour savoir si le candidat a
réellement vu un site.

Tout commence par un **registre**, un cahier papier tenu au service : registre de consultation
prénatale, registre de dépistage, registre de dispensation d'antirétroviraux, registre de
vaccination. La donnée y est nominative, écrite à la main, au moment de l'acte. C'est la
**source primaire**, et c'est la seule chose qui existe réellement — tout le reste en est une
transformation.

En fin de journée ou de mois, quelqu'un **agrège** ce registre sur une feuille de comptage, en
comptant les lignes selon les catégories demandées : par sexe, par tranche d'âge, par type de
service. C'est l'étape où naissent la plupart des erreurs, parce que c'est un comptage manuel,
souvent fait vite, souvent par quelqu'un qui n'a pas vu les patients.

Ce comptage alimente le **rapport mensuel de l'institution**, qui remonte à la **direction
sanitaire départementale**, puis au niveau national, où il entre dans le système d'information
sanitaire — en Haïti le **SISNU**, bâti sur DHIS2. En parallèle, si le site dispose d'un dossier
médical électronique, une partie de la donnée est saisie une seconde fois dans ce système, qui
produit ses propres rapports automatiques. Et le partenaire de mise en œuvre — CMMB, en
l'occurrence — construit à partir de tout cela son rapportage bailleur, mensuel, trimestriel,
semestriel et annuel.

**Trois conséquences pratiques découlent de ce trajet, et il faut les avoir prêtes.**

D'abord, **la donnée est saisie plusieurs fois**, dans des systèmes qui ne se parlent pas
toujours, et les totaux divergent presque toujours. Un écart entre le registre, le rapport
mensuel du site et ce qui apparaît dans le système national n'est pas un scandale, c'est le
fonctionnement normal ; le travail consiste à connaître l'ampleur habituelle de l'écart et à
réagir quand elle change.

Ensuite, **la vérification consiste à remonter le chemin en sens inverse**. C'est exactement ce
que dit ton CV : la remontée du chiffre rapporté jusqu'au registre source. On ne vérifie jamais
un rapport en le comparant à un autre rapport ; on le vérifie en recomptant la source.

Enfin, **tout ce qui casse ce chemin casse l'indicateur** : une rupture de registres papier, une
panne du système informatique, un agent formé qui part et n'est pas remplacé, une définition
d'indicateur modifiée en cours d'année sans que les sites en soient informés.

---

## 3. La qualité des données en santé : le vocabulaire exact

Les cinq dimensions générales de la qualité sont traitées dans
[`../assitant_pmel/01_meal_processus.md`](../assitant_pmel/01_meal_processus.md). Ce qui suit
est ce que le secteur santé y ajoute, avec son vocabulaire propre.

**Le DQA — *data quality assessment*.** C'est l'exercice formel de vérification, généralement
conduit sur site. Sa mécanique tient en une opération : on choisit un indicateur et une période,
on recompte la source primaire, et on compare au chiffre rapporté. Le rapport du recompte au
rapporté s'appelle le **facteur de vérification** — *verification factor*. Un facteur de 1,00
signifie que le rapporté correspond exactement à la source. Un facteur de 0,85 signifie que le
site a sur-rapporté de quinze pour cent ; un facteur de 1,20 qu'il a sous-rapporté. **Un facteur
supérieur à 1 n'est pas une bonne nouvelle** : sous-rapporter, c'est perdre des patients dans les
chiffres, donc perdre des médicaments commandés et du financement.

**Le DQR de l'OMS — *data quality review*.** C'est le cadre méthodologique de référence pour la
qualité des données de routine, et il structure l'analyse en quatre familles. La **complétude et
la ponctualité** : quelle proportion des sites attendus ont rapporté, et dans les délais. La
**cohérence interne** : les valeurs aberrantes, les ruptures de tendance inexpliquées, et les
relations logiques entre indicateurs qui doivent être respectées — par exemple, le nombre de
femmes ayant reçu une quatrième consultation prénatale ne peut pas dépasser celles qui en ont eu
une première. La **cohérence externe** : la comparaison des données de routine avec une source
indépendante, typiquement une enquête en population. Et la **cohérence des dénominateurs** : la
comparaison des populations cibles utilisées, qui sont souvent la source d'erreur la plus grave et
la moins visible.

Cette dernière famille mérite une phrase de plus, parce qu'elle est spécifique à la santé. Un
taux de couverture vaccinale, un taux de consultation prénatale, un taux d'accouchement assisté
ont tous pour dénominateur une **population cible estimée** : le nombre de femmes enceintes
attendues dans l'aire de desserte, le nombre d'enfants de moins d'un an. Ce dénominateur ne se
compte pas, il se calcule en appliquant un coefficient démographique à une projection de
population. En Haïti, avec des déplacements massifs de population liés à l'insécurité, ces
projections sont fragiles, et un dénominateur faux produit des couvertures supérieures à cent
pour cent ou ridiculement basses sans que le service ait changé. Savoir dire cela est un marqueur
fort de professionnalisme.

**Le SIMS**, enfin — *site improvement through monitoring system* — est l'outil du PEPFAR pour
évaluer sur site, au moyen d'éléments d'évaluation standardisés, la qualité des services et des
systèmes de données. Si tu l'as croisé chez Caris, tu peux le nommer ; sinon, sache simplement ce
que c'est.

---

## 4. Les composantes citées dans l'annonce

### RMCNH — santé reproductive, maternelle, néonatale et infantile

L'annonce écrit *RMCNH* ; l'usage international est **RMNCH**, et en français haïtien on dit
souvent **SRMNIA**, santé de la reproduction, maternelle, néonatale, infantile et des
adolescents. Ne relève pas la coquille en entretien.

Les indicateurs à connaître se répartissent en quelques familles. Sur la grossesse : la
**première consultation prénatale**, CPN1, et la **quatrième**, CPN4 — le rapport des deux
mesure la fidélisation, et l'écart entre les deux est l'un des indicateurs les plus révélateurs
d'un système de santé. Sur l'accouchement : la proportion d'**accouchements assistés par du
personnel qualifié**, et la proportion d'accouchements en institution. Sur le post-partum : la
consultation postnatale dans les deux jours. Sur l'enfant : la couverture vaccinale, dont
l'indicateur de référence est le **Penta3**, troisième dose de vaccin pentavalent, et surtout le
**taux d'abandon** entre la première et la troisième dose, qui mesure la capacité du système à
faire revenir les gens. Sur la nutrition : l'allaitement exclusif, le retard de croissance, la
malnutrition aiguë. Sur la planification familiale : la prévalence contraceptive et les
**années-couples de protection**.

Et l'articulation avec le VIH est directe, ce qui te sert : la **PTME** vit à l'intersection
exacte de la consultation prénatale et du programme VIH. L'indicateur PMTCT_STAT a pour
dénominateur les nouvelles consultantes prénatales — c'est-à-dire l'indicateur CPN1 du programme
de santé maternelle. **Les deux systèmes doivent donner le même nombre**, et quand ils divergent,
c'est un des tests de cohérence les plus utiles à mettre en place.

### WASH — eau, assainissement et hygiène

C'est le domaine que tu as pratiqué deux ans chez HANWASH, et ton CV mentionne l'alignement sur
les normes **JMP**. Le JMP est le programme commun de surveillance OMS-UNICEF, et il fournit
l'**échelle de service** qui structure tous les indicateurs du domaine : pour l'eau de boisson,
on gradue de l'eau de surface à la source non améliorée, puis au service limité, au service de
base, et au service géré en toute sécurité ; l'assainissement suit une échelle parallèle, de la
défécation à l'air libre au service géré en toute sécurité. La distinction déterminante entre le
service limité et le service de base tient au **temps d'accès** : trente minutes aller-retour,
file d'attente comprise.

Le piège du domaine, celui que tu as rencontré, est la différence entre un point d'eau
**construit** et un point d'eau **fonctionnel**. Compter des ouvrages construits est un
indicateur d'extrant qui ne dit rien du service rendu ; la fonctionnalité doit être vérifiée
périodiquement, et c'est ce qui justifie les enquêtes géospatiales et le suivi de la
maintenance.

### RBF — le financement basé sur les résultats

C'est la composante la plus intéressante pour un professionnel du suivi-évaluation, et sans doute
celle sur laquelle on te testera le plus volontiers, parce qu'elle transforme la donnée en argent.

Le principe : au lieu de financer une institution sanitaire sur la base de ses intrants — un
budget, des salaires, des équipements — on la paie sur la base de ses **résultats vérifiés**,
c'est-à-dire un montant par acte produit, pondéré par un **score de qualité**. Haïti n'est pas
novice : le ministère de la santé publique et de la population utilise cette approche depuis
**1999**, et l'a formellement adoptée dans sa stratégie de financement de la santé en **2012**.
Le ministère maintient un portail dédié au FBR — financement basé sur les résultats.

L'architecture haïtienne du dispositif est ce qu'il faut connaître, parce qu'elle est
entièrement construite autour d'un problème de suivi-évaluation. Les fonctions sont
**délibérément séparées** — financeur, régulateur, acheteur sont des entités distinctes au sein
du ministère — et une **agence de vérification externe** contrôle l'exactitude de tous les
résultats déclarés par les institutions, avec une périodicité **trimestrielle**.

Pourquoi cette séparation ? Parce que le financement basé sur les résultats crée un **conflit
d'intérêts structurel** : l'institution qui déclare ses actes est celle qui sera payée pour ces
actes. La tentation de sur-déclarer n'est pas une hypothèse morale, c'est une propriété du
dispositif. D'où trois couches de contrôle : la **vérification quantitative**, qui recompte les
actes dans les registres ; la **vérification qualitative**, qui note la qualité des soins selon
une grille ; et la **contre-vérification communautaire**, qui va retrouver dans la communauté un
échantillon de patients déclarés pour confirmer qu'ils existent et qu'ils ont bien reçu le
service.

C'est ce dernier point qui fait la différence en entretien : **la contre-vérification
communautaire est une réponse à la fabrication de patients fantômes**. Sans elle, un registre
bien tenu et entièrement inventé passe toutes les vérifications documentaires.

Le second effet pervers à connaître s'appelle l'**effet d'éviction** : quand certains actes sont
payés et d'autres non, l'institution déplace son effort vers les actes rémunérés au détriment des
autres. C'est pour cela qu'un dispositif de financement basé sur les résultats doit suivre aussi
les indicateurs **non rémunérés**, pour vérifier qu'ils ne se dégradent pas.

### Préparation et réponse aux catastrophes

Haïti cumule séismes, cyclones, inondations et déplacements liés à l'insécurité. CMMB a répondu
au séisme de 2010 et à celui de 2021. Le suivi-évaluation change de nature en urgence : les
cycles se raccourcissent — on rapporte parfois quotidiennement —, on accepte une précision
moindre en échange de la rapidité, et l'unité de compte devient souvent le ménage plutôt que
l'individu.

Deux notions à nommer. Le **cadre de redevabilité envers les populations affectées**, et
notamment les **mécanismes de plainte et de retour d'information** — comment une personne
assistée peut signaler un problème et obtenir une réponse. Et la **préparation** proprement dite,
qui se mesure autrement que la réponse : existence et mise à jour des plans de contingence,
stocks prépositionnés, personnel formé, exercices de simulation réalisés. Un indicateur de
préparation mesure une **capacité en attente**, pas un service rendu, et c'est une catégorie que
beaucoup de candidats ne savent pas construire.

---

## 5. La restitution : la partie du poste que personne ne prépare

L'annonce demande de *« provide routine feedback on key outcome indicators to health facilities
and senior management team »*. C'est-à-dire de **rendre aux institutions sanitaires leurs propres
chiffres**. C'est la tâche la plus sous-estimée du métier, et celle où un bon officier de
suivi-évaluation se distingue immédiatement d'un compilateur de rapports.

Le problème est simple à énoncer. Un site remplit des rapports tous les mois et ne voit jamais
rien revenir. Au bout de quelques mois, il remplit pour se débarrasser, non pour savoir. La
qualité s'effondre, et aucune formation n'y changera quoi que ce soit, parce que le problème
n'est pas la compétence, c'est l'absence de contrepartie.

Une bonne restitution obéit à quelques règles. **Elle est comparative** : un site ne comprend son
chiffre que confronté à son propre passé et à ses pairs, donc on montre la série du site et sa
position parmi les sites comparables. **Elle est courte** : une page, trois ou quatre indicateurs
choisis, pas trente. **Elle est visuelle** : une courbe se lit, un tableau de quarante lignes ne
se lit pas. **Elle nomme une action**, pas un jugement — non pas « votre taux d'abandon est
mauvais » mais « votre écart entre première et troisième dose s'est creusé sur deux trimestres ;
la question à instruire est le rappel des rendez-vous ». Et surtout, **elle revient au cycle
suivant sur ce qui avait été dit au cycle précédent**, sinon elle n'est qu'un bulletin de plus.

Une pratique à proposer si l'occasion se présente, parce qu'elle est standard dans le domaine et
qu'elle a un nom : la **revue de performance** périodique, une réunion courte et régulière où le
site lit lui-même ses chiffres devant son équipe. L'objectif n'est pas que l'officier de
suivi-évaluation explique les données au site ; c'est que le site les explique. C'est exactement
ce que l'annonce appelle *data demand and use*, et c'est ce qui distingue une culture de la
donnée d'une obligation de rapportage.

---

## 6. La formation et l'appui aux institutions

L'annonce demande de planifier et conduire toutes les formations liées à l'information
stratégique, dans les institutions sanitaires et auprès des directions départementales, puis de
recueillir en visite les besoins d'appui.

Le principe qui doit guider ta réponse : **une formation ne corrige pas un problème de
processus**. Si un site se trompe systématiquement sur une désagrégation d'âge, la cause est
généralement que le registre papier n'a pas de colonne pour cette tranche, ou que la définition a
changé sans que la fiche d'indicateur ait été rediffusée. Former les gens à mieux compter sur un
outil qui ne le permet pas produit de la frustration et aucun résultat.

La séquence correcte se dit en trois temps. On **diagnostique** d'abord : on regarde où l'erreur
naît réellement en remontant le chemin de la donnée. On **corrige l'outil** ensuite quand c'est
l'outil — le registre, le formulaire, la fiche d'indicateur, la contrainte de validation. Et on
**forme** enfin, sur ce qui reste, avec du matériel écrit qui survit au départ de la personne
formée. Cette dernière précision compte en Haïti, où la rotation du personnel est forte : une
formation dont il ne reste rien à l'écrit est un investissement perdu à la première démission.
Ton CV mentionne la production de guides techniques chez HANWASH ; c'est exactement ce point.

Sur la forme, la **supervision formative** — accompagner un agent pendant qu'il fait le travail,
plutôt que de le convoquer à un atelier — est la modalité qui fonctionne le mieux sur les
compétences de saisie et de comptage. Elle a aussi l'avantage de faire d'une pierre deux coups
avec la visite de site que l'annonce demande.

---

## Angles d'entretien

**« Comment organiseriez-vous vos quatre-vingt-dix premiers jours ? »**

« Je diviserais en trois temps. Le premier mois, comprendre et ne rien changer : cartographier
les flux de données existants, site par site — quels registres, quels systèmes, qui saisit, qui
agrège, à quelle date, vers qui — et lire les trois ou quatre derniers cycles de rapportage pour
repérer où les chiffres bougent de façon inexpliquée. Je demanderais aussi les définitions
d'indicateurs en vigueur et le calendrier de rapportage bailleur, parce que tout le reste s'y
accroche.

Le deuxième mois, sortir. Visiter les institutions les plus représentatives et les plus
problématiques, faire un recompte de vérification sur un ou deux indicateurs, et surtout écouter
ce que les sites disent de leurs propres difficultés — c'est là qu'on apprend qu'un site rapporte
mal parce qu'il n'a plus de registres depuis six semaines, ce qu'aucune analyse de bureau ne
révélera.

Le troisième mois, poser deux ou trois choses durables plutôt que dix éphémères : un jeu de
contrôles automatiques exécutés à la réception des données, un format de restitution court
renvoyé à chaque site, et un journal d'anomalies partagé. Et je livrerais évidemment les cycles
de rapportage dans les délais dès le premier mois — la découverte ne suspend pas les échéances. »

**« Un site vous rapporte des chiffres que vous savez faux, et son directeur départemental les a
déjà validés. Que faites-vous ? »**

« Je ne les corrige pas unilatéralement et je ne les rapporte pas non plus en silence. Je fais
trois choses. D'abord, j'objective : je remonte au registre source et je constitue un écart
documenté, avec la période, l'indicateur, le chiffre rapporté, le chiffre recompté et le facteur
de vérification. Une conviction ne se discute pas, un écart chiffré se discute. Ensuite, je vais
voir le site avant d'aller voir quiconque d'autre, parce que dans la majorité des cas
l'explication est un problème de processus ou de définition, pas une intention — et si c'est une
définition mal partagée, c'est mon problème avant d'être le sien. Enfin, si l'écart est confirmé
et significatif, je remonte à mon directeur suivi-évaluation avec le dossier et une
recommandation, parce que la relation avec la direction départementale n'est pas la mienne à
arbitrer seul.

Ce que je ne ferais jamais, c'est soumettre un chiffre que je sais faux au bailleur en me
disant qu'il a été validé plus haut. Le rapportage engage l'organisation, et une donnée fausse
découverte en audit coûte infiniment plus cher que la même donnée corrigée à temps avec sa note
explicative. »
