# Le VIH vu depuis le mandat de l'Institut Panos

*Module 3. Ce module ne réenseigne pas le VIH : la cascade, la charge virale, les 95-95-95 et
les indicateurs MER sont dans la piste CMMB, et tu les as révisés il y a trois semaines. Relis
[`../cmmb_meal_officer/FICHE_MER_INDICATEURS.md`](../cmmb_meal_officer/FICHE_MER_INDICATEURS.md)
en trente minutes ce soir ; c'est la meilleure fiche que tu possèdes. Ce qui suit, c'est ce qui
change quand l'employeur n'est pas une clinique mais une organisation dont le mandat est
l'éducation des patients, l'adhérence, le traçage et le retour en soins.*

---

## 1. Le problème : réciter la cascade entière à des gens qui en travaillent le bout

La tentation, face à une question VIH, est de dérouler tout ce qu'on sait : le dépistage, le
linkage, les quatre portes, la PTME, la tuberculose. Chez CMMB, qui soigne dans treize hôpitaux,
c'était pertinent. Chez Panos, c'est à côté du sujet. L'Institut ne dépiste pas à grande échelle
et ne soigne pas : il travaille sur les **deux derniers 95**, maintenir les gens sous traitement et
les amener à la suppression virale, et sur la **demande** de services (PrEP, charge virale) et la
**stigmatisation**. Ce sont les étapes qui se jouent hors de la clinique, dans la communauté, là où
sont leurs relais et leur ligne 8338.

La bonne réponse technique, chez eux, part donc toujours de leur mandat et remonte vers les
indicateurs, jamais l'inverse.

---

## 2. Où se situe le mandat de Panos dans la cascade

| Ce que fait l'Institut | Étape de la cascade | Indicateurs MER qui la mesurent | Ce que le programme doit mesurer lui-même |
|---|---|---|---|
| Traçage et retour en soins des patients en interruption | Continuité du traitement | `TX_ML`, `TX_RTT`, `TX_CURR` | Patients listés, visités, joints, revenus (prouvé par dispensation), toujours sous traitement à trois mois |
| Éducation des patients et appui à l'adhérence | Suppression virale | `TX_PVLS` (numérateur et dénominateur) | Patients accompagnés, et leur suppression à la charge virale suivante |
| Création de la demande de charge virale (E=E) | Couverture en charge virale | `TX_PVLS_D` rapporté à `TX_CURR` | Patients orientés vers un test, tests réalisés |
| Campagne PrEP | Prévention | `PrEP_NEW`, `PrEP_CT` | Exposition à la campagne, orientations, et la tendance des nouvelles mises sous PrEP |
| Campagne TME | PTME | `PMTCT_STAT`, `PMTCT_ART` | Connaissance, orientations vers la consultation prénatale |
| Lutte contre la stigmatisation, changement de comportement | En amont de toute la cascade | Aucun | Des indicateurs propres (section 8) |

Deux lectures de ce tableau valent la peine d'être dites. La première : les indicateurs MER de la
troisième colonne sont produits par les **sites cliniques**, pas par l'Institut. Un sous-partenaire
communautaire contribue à `TX_RTT` sans en être le producteur, et son propre suivi doit donc
pouvoir se rattacher aux données cliniques, ce qui ramène à la réconciliation du module 01. La
seconde : la dernière ligne n'a aucun indicateur MER, et c'est pourtant le cœur historique de
l'Institut. Il faut savoir la mesurer autrement.

---

## 3. Interruption et retour : les définitions exactes

C'est le terrain le plus probable des questions techniques, puisque c'est le mandat EpiC de
l'Institut. Les définitions ci-dessous suivent le registre d'indicateurs de l'ONUSIDA, qui reprend
les fiches MER ; l'autorité reste le *MER Indicator Reference Guide* du Département d'État, dans sa
version en vigueur.

**L'interruption de traitement** (IIT, *interruption in treatment*) commence quand un patient n'a eu
**aucun contact clinique ni retrait d'ARV pendant plus de 28 jours** après la date de son dernier
contact attendu, c'est-à-dire après la date où ses ARV devaient s'épuiser. Les 28 jours sont le
seuil de tout le système.

**`TX_ML`** compte les patients sortis de la file active pendant la période, ventilés par devenir :
décédés, transférés sortants, ayant refusé ou arrêté le traitement, et en interruption. Les
interruptions sont elles-mêmes ventilées selon la **durée passée sous traitement avant
l'interruption** : moins de trois mois, ou davantage (les versions récentes du guide découpent plus
finement, vérifie la version en vigueur). **Une précision qui corrige la fiche CMMB** : sa formule
« perdus de vue depuis moins de trois mois » doit se lire « interrompus après moins de trois mois
de traitement ». La ventilation ne porte pas sur la durée de l'absence, mais sur l'ancienneté sous
traitement au moment où le patient décroche, parce que les patients qui interrompent dans les
premiers mois forment un groupe à part, avec des causes et des réponses différentes.

**`TX_RTT`** compte les patients qui étaient en interruption depuis **plus de 28 jours** et qui ont
**repris leurs ARV** pendant la période. Ils sont réintégrés dans `TX_CURR`. Et la conséquence
qu'il faut savoir énoncer : **un patient tracé et ramené avant le 28e jour n'est pas un `TX_RTT`**.
Il n'a jamais quitté `TX_CURR`, et il n'apparaît dans aucun indicateur de retour. Le module 01 § 5
montre pourquoi un jalon écrit sur `TX_RTT` seul punit alors le meilleur travail de traçage.

**L'équation de cohorte** relie tout : `TX_CURR` final égale `TX_CURR` initial, plus `TX_NEW`,
plus `TX_RTT`, moins `TX_ML`. Quand elle ne tombe pas juste, il manque presque toujours des sorties
documentées ; le mécanisme est raconté dans la fiche MER CMMB, section 4.

---

## 4. Adhérence, charge virale et le message E=E

La distinction entre **couverture en charge virale** et **taux de suppression** est le point que tu
dois pouvoir dire en une phrase, parce qu'il touche directement le mandat E=E de l'Institut. La
couverture rapporte les patients qui ont un résultat de charge virale récent à tous les patients
sous traitement ; la suppression rapporte les patients supprimés aux seuls patients testés. Un
taux de suppression ne se commente jamais sans sa couverture, parce qu'un site qui ne teste que ses
meilleurs patients affiche une suppression magnifique sur un dénominateur minuscule.

Le chiffre haïtien récent le montre bien : l'étude publiée en 2025 dans le *Journal of Infectious
Diseases* rapporte qu'en avril 2024, **86 % des personnes sous traitement qui avaient eu un test de
charge virale étaient supprimées**. La phrase contient sa propre limite, « qui avaient eu un test »,
et c'est exactement ce qu'il faut remarquer à voix haute si on te donne ce chiffre.

C'est là que la campagne E=E prend un sens de suivi-évaluation. Quand l'Institut écrit qu'il veut
« créer la demande pour l'utilisation des tests de charge virale », il agit sur la **couverture**,
et donc sur la fiabilité même du taux de suppression national. Un bon indicateur de son effet n'est
pas le taux de suppression, mais le nombre de patients orientés vers un test et réellement testés.

Les seuils (moins de 1 000 copies par millilitre pour la suppression, l'indétectabilité plus bas,
qui porte le message U=U) sont expliqués dans
[`../cmmb_meal_officer/03_vih_essentiel.md`](../cmmb_meal_officer/03_vih_essentiel.md) § 3.

---

## 5. La dispensation différenciée et l'insécurité : ce qu'elles font aux données

Le traitement ne se distribue plus seulement à la clinique. Les **points de distribution**
communautaires (plus de cinquante points fixes dans les dix départements selon *HPN* en septembre
2025), la **dispensation multi-mois**, la **livraison à domicile**, que fait aujourd'hui Marie Tania
Petit-Frère à l'HUEH, rapprochent les ARV des patients, et ils sont d'autant plus nécessaires que
l'OIM comptait **1 466 862 personnes déplacées** à l'intérieur du pays sur sa collecte de mars à mai
2026.

Pour les données, chacun de ces progrès crée le même risque : **le patient est servi ailleurs que
là où il est suivi.** Un patient déplacé qui prend ses ARV sur un autre site disparaît de la file
active de son site d'origine et y apparaît comme une interruption. Sans identifiant national, il est
tracé pour rien, compté en `TX_ML` à un endroit et parfois en `TX_NEW` à un autre, et l'indicateur
national de rétention se dégrade sans qu'un seul patient ait réellement arrêté.

C'est le problème que la base nationale **SALVH** traite. Selon la même étude de 2025, elle
comptait **308 500 personnes** diagnostiquées en janvier 2024, relie les dossiers entre sites par
un identifiant maître fondé sur l'**empreinte digitale** (disponible pour environ **60 %** des
personnes sous traitement), et complète cet identifiant par un algorithme de rapprochement en
cascade : même empreinte, puis même nom, prénom et date de naissance, puis même nom et téléphone,
et ainsi de suite, jusqu'à une revue manuelle des cas douteux. Résultat : la déduplication réduit
d'environ **14 %** le nombre de patients qui passeraient sinon pour perdus de vue, et de **41,5 %**
pour la cohorte diagnostiquée en 2021-2022, la plus mobile.

C'est l'argument technique le plus fort que tu puisses porter demain, parce qu'il relie ton métier
d'ingénieur de données à leur mandat : **avant de tracer un patient, il faut savoir s'il est
réellement perdu.** Le module 02 le démontre sur le jeu d'exercice, avec la requête.

Le dispositif de retour en soins le plus connu en Haïti mérite aussi un nom : le programme **PLR**
(*patient linkage and retention*), qui exploite les dossiers électroniques pour repérer les
rendez-vous manqués et déclencher les visites d'agents communautaires, et dont le CDC rapportait
qu'il avait ramené près de 17 000 patients perdus de vue dans plus de 80 institutions (voir
[`../cmmb_meal_officer/06_hmis_et_qualite_donnees.md`](../cmmb_meal_officer/06_hmis_et_qualite_donnees.md)
§ 2). L'annonce de FHI 360 pour EpiC Haïti cite PLR et **Radar** comme les plateformes de suivi des
interruptions. Tu ne connais pas Radar : c'est une question à poser, pas un outil à revendiquer.

---

## 6. La PrEP

La PrEP (prophylaxie pré-exposition) est un traitement antirétroviral pris par une personne
séronégative pour réduire son risque d'infection. L'Institut a mené la campagne nationale pour le
compte du MSPP. Les deux indicateurs MER sont **`PrEP_NEW`**, les personnes nouvellement mises sous
PrEP pendant la période, et **`PrEP_CT`**, celles qui, déjà sous PrEP, sont revenues la poursuivre.
Le second est celui qu'on oublie, et c'est le plus parlant : une PrEP qu'on arrête au bout d'un
mois ne protège personne.

**Le problème de mesure d'une campagne PrEP est celui de l'attribution.** Les mises sous PrEP
augmentent après la campagne ; est-ce la campagne ? La réponse honnête est qu'on ne peut presque
jamais le prouver seul, et qu'on construit plutôt une **analyse de contribution** avec plusieurs
indices qui convergent : la tendance des mises sous PrEP publiée par MESI par département, une
question simple posée aux nouveaux patients sur les sites (« comment avez-vous entendu parler de la
PrEP ? »), les orientations passées par la ligne 8338, et la chronologie (la hausse suit-elle les
vagues de la campagne, département par département ?). Aucun de ces indices ne suffit ; leur
convergence est ce qu'un évaluateur accepte.

---

## 7. La PTME : ce que tu sais, et la limite

L'Institut a une campagne TME, l'annonce cite la PTME dans les qualifications requises, et ta lettre
l'**exclut explicitement** de ton périmètre. La position est donc simple : tu connais la logique, tu
ne revendiques aucune expérience.

La logique tient en une phrase, et la chaîne complète est dans la fiche MER CMMB, section 6 : on
connaît le statut des femmes enceintes (`PMTCT_STAT`), on met les positives sous traitement
(`PMTCT_ART`, qui est en réalité un indicateur de linkage), on teste les nourrissons exposés par PCR
dans les deux premiers mois (`PMTCT_EID`), et on établit leur statut final vers dix-huit mois
(`PMTCT_FO`).

> « Sur la PTME, je veux être aussi précis que dans ma lettre : je connais la chaîne et ses
> indicateurs, du statut connu en consultation prénatale jusqu'au statut final de l'enfant, mais je
> ne l'ai pas suivie sur le terrain. Mon expérience VIH porte sur le système d'information et le
> rapportage d'un programme de prévention chez les jeunes. »

---

## 8. Mesurer le changement de comportement

C'est le métier historique de l'Institut, et c'est celui que les indicateurs MER ne mesurent pas.
CHAMPIONS en donne un exemple : le site annonce **« 1 M de jeunes adultes potentiellement
atteints »** par dix influenceurs. Le mot important est « potentiellement ». C'est une **portée
potentielle**, la somme des abonnés, pas un nombre de personnes qui ont vu le message, encore moins
de personnes qui ont changé quoi que ce soit.

Un responsable MEL range ce type de résultat sur une **échelle** et sait dire à quel barreau
s'arrête chaque chiffre. La portée potentielle, d'abord ; puis l'**exposition** (les personnes qui
ont effectivement vu ou entendu) ; le **rappel** (celles qui s'en souviennent) ; les
**connaissances et attitudes** ; l'**intention** ; le **comportement** déclaré ; et enfin
l'**utilisation des services**, la seule mesurée dans des données de service et non dans une
déclaration. Chaque barreau demande son outil : les statistiques des plateformes et des médias pour
la portée, une enquête avec questions de rappel spontané et assisté pour l'exposition, une enquête
CAP (connaissances, attitudes, pratiques) pour les barreaux du milieu, et les données des sites pour
le dernier.

Ce n'est pas une critique de CHAMPIONS, et ne le présente jamais ainsi : c'est la raison pour
laquelle un programme de prestation de services exige un autre système de mesure qu'une campagne,
et c'est exactement le passage que fait l'Institut avec AFGHS. La phrase à avoir :

> « Pour une campagne, je sépare toujours la portée, l'exposition et le changement. La portée se lit
> dans les statistiques des médias, l'exposition se mesure par enquête, et le changement ne se prouve
> vraiment que dans les données de service : des tests de charge virale demandés, des mises sous
> PrEP, des patients revenus. C'est le dernier barreau qui intéresse un programme payé sur jalons. »

---

## 9. La confidentialité

Le sujet est développé dans
[`../cmmb_meal_officer/03_vih_essentiel.md`](../cmmb_meal_officer/03_vih_essentiel.md) § 9 et, pour
le versant technique, dans le module HMIS CMMB § 5. Chez Panos, il prend une forme particulière,
parce qu'une organisation de proximité **se déplace chez les gens et les appelle**. Un relais qu'on
voit entrer régulièrement dans la même cour, un appel pris par un membre de la famille, une liste
oubliée sur une tablette : chacun de ces incidents peut révéler un statut. Les règles qui en
découlent sont celles du module 02 § 5 (liste propre à chaque relais, formulaire chiffré, ni nom ni
GPS dans les soumissions) et celles du module 01 § 7 pour les rappels téléphoniques (consentement
préalable, identité vérifiée avant toute mention du VIH).

---

## 10. Ce que tu dis de ton expérience VIH

La règle est inchangée depuis CMMB, et le dossier Panos l'a rendue plus stricte à l'écrit. Voici ce
que tu peux dire, dans cet ordre.

Tu as été **officier de suivi-évaluation sur un programme VIH**, le projet **Impact Youth** de la
Caris Foundation International, d'octobre 2021 à août 2024. Tu conduisais le rapportage de routine
de cliniques multi-sites et tu **remontais les indicateurs MER à l'USAID via DATIM**, la plateforme
du PEPFAR bâtie sur DHIS2, **comme producteur de données** : préparer, valider, soumettre, jamais
administrer la plateforme. Si l'on te demande quels indicateurs, l'exemple confirmé est
**`AGYW_PREV`**, l'indicateur de prévention chez les adolescentes et jeunes femmes du programme
**DREAMS**, et tu ajoutes la phrase de périmètre :

> « Mon expérience directe porte sur le périmètre de mon projet, `AGYW_PREV` sous DREAMS par
> exemple. Je ne prétends pas avoir rapporté les indicateurs de traitement ; je connais leur logique
> pour l'avoir étudiée, pas pour les avoir produits. Ce que je maîtrise, c'est le processus :
> consolider, appliquer la définition, désagréger, contrôler, soumettre, et corriger ce qui revient.
> Ce processus est le même quel que soit l'indicateur. »

Ce que tu ne dis pas : que tu as rapporté `TX_CURR`, `TX_ML` ou `TX_PVLS` ; que tu as travaillé
sur la PTME ; que tu as administré DHIS2 ou DATIM ; que tu as exploité MESI, le SISNU ou iSanté
Plus ; que tu as travaillé sur le Projet Santé de Caris.

---

## Angles d'entretien

**« Comment mesureriez-vous l'efficacité de notre travail de traçage des patients en
interruption ? »**

« Je la mesurerais en trois temps, et je commencerais par le dénominateur. Avant de compter les
retours, je vérifierais que les patients listés sont réellement en interruption, c'est-à-dire
qu'aucun autre site ne leur a dispensé d'ARV. Avec la dispensation différenciée et les
déplacements, une partie des patients qui semblent perdus prennent leur traitement ailleurs ; l'étude
publiée l'an dernier sur SALVH montre que la déduplication nationale réduit d'environ 14 % le nombre
de perdus de vue apparents. Ensuite je mesurerais le retour par la dispensation dans le dossier
électronique, pas par la déclaration du relais. Et enfin je regarderais si le retour dure : la
proportion des patients revenus qui sont toujours sous traitement trois mois après. J'ajouterais un
indicateur que TX_RTT ne voit pas : les rendez-vous manqués rattrapés avant le 28e jour, parce que
c'est le meilleur travail de traçage et qu'il n'apparaît dans aucun indicateur de retour. »

**« Quelle différence faites-vous entre TX_ML et TX_RTT ? »**

« TX_ML compte les sorties de la file active pendant la période, ventilées par devenir : décès,
transferts, arrêts et interruptions, les interruptions étant elles-mêmes ventilées selon le temps
passé sous traitement avant de décrocher. TX_RTT compte les retours : des patients en interruption
depuis plus de 28 jours qui ont repris leurs ARV pendant la période, et qu'on réintègre dans
TX_CURR. Les deux se lisent ensemble dans l'équation de cohorte : le TX_CURR de fin de période, c'est
celui du début plus les nouveaux, plus les retours, moins les sorties. Et une précision qui compte
pour un programme de traçage : un patient ramené avant le 28e jour n'est jamais sorti, donc il
n'apparaît ni dans TX_ML ni dans TX_RTT. Je le dis franchement : ces indicateurs de traitement, je
les connais pour les avoir étudiés ; ceux que j'ai rapportés à Caris portaient sur la prévention
chez les jeunes, AGYW_PREV sous DREAMS. »

**« Comment prouveriez-vous qu'une campagne a eu un effet ? »**

« Le plus souvent, on ne le prouve pas seul, et je préfère le dire plutôt que de promettre une
attribution. On construit une analyse de contribution : plusieurs indices indépendants qui
convergent. Pour une campagne PrEP par exemple, la tendance des mises sous PrEP dans MESI par
département et sa chronologie par rapport aux vagues de la campagne, une question posée aux nouveaux
patients sur la façon dont ils en ont entendu parler, et les orientations passées par votre ligne
8338. Et je sépare toujours la portée, l'exposition et le changement : la portée se lit dans les
statistiques des médias, l'exposition se mesure par enquête, et le changement se voit dans les
données de service. C'est seulement ce dernier niveau qu'un bailleur qui paie sur résultats
acceptera. »
