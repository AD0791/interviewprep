# Le système d'information sanitaire : la moitié que personne ne prépare

*Module 6 — c'est ton avantage décisif. La moitié des puces de l'annonce décrit un métier
d'exploitation de système d'information, et presque aucun candidat en suivi-évaluation ne peut le
traiter. Ce module te donne le paysage haïtien, le vocabulaire, et la limite exacte de ce que tu
peux revendiquer.*

---

## 1. La limite à énoncer toi-même

Commençons par là, parce que c'est une règle absolue et que tout le reste du module en dépend.

Chez la Caris Foundation, ton rôle vis-à-vis de DATIM et de DHIS2 était celui d'un **producteur
de données**. Tu préparais, validais et soumettais les indicateurs MER : consolider les données
des sites, appliquer les définitions, construire les désagrégations, faire valider, respecter
l'échéance, corriger les retours. **Tu n'administrais pas la plateforme DHIS2** — pas de
configuration de métadonnées, pas de gestion d'utilisateurs à l'échelle du système, pas de
paramétrage d'ensembles de données.

Cette distinction n'est pas une faiblesse à dissimuler : c'est **exactement le rôle d'un officier
de suivi-évaluation chez un partenaire de mise en œuvre**, et c'est précisément le poste que
CMMB propose. L'énoncer de toi-même, avant qu'on ne creuse, produit un effet inverse de celui que
tu crains : cela te fait passer pour quelqu'un qui sait de quoi il parle et qui ne surjoue pas.

La formulation, à connaître par cœur :

> « Soyons précis sur DATIM, parce que la nuance compte. J'étais du côté producteur de données :
> je préparais, je validais et je soumettais les indicateurs MER dans DATIM, avec les
> désagrégations exigées et les échéances de soumission du PEPFAR. Je n'étais pas administrateur
> de la plateforme DHIS2 elle-même — la configuration des métadonnées et la gestion des
> utilisateurs à l'échelle du système ne relevaient pas de moi. En revanche, l'administration de
> bases de données, je la fais tous les jours par ailleurs, sur MySQL et PostgreSQL, et c'est de
> là que je tire ce que je peux apporter sur le volet système d'information de votre poste. »

**Ce que tu peux revendiquer sans réserve**, parce que c'est dans ton CV : la mise en place et
l'administration des systèmes de collecte alimentant le rapportage — CommCare, HIVHaiti, une base
MySQL intégrée chez Caris ; l'administration de la base mWater chez HANWASH, avec nettoyage et
fusion de doublons ; l'administration du panneau ODK chez Anseye Pou Ayiti ; et, côté ingénierie,
l'administration de bases relationnelles en accès concurrent, les pipelines ETL, les services
d'API sécurisés et le contrôle d'accès par rôle.

---

## 2. Le paysage des systèmes d'information sanitaire haïtiens

Connaître ces quatre noms et savoir ce qui les distingue te met immédiatement au niveau de la
conversation. Peu de candidats les maîtrisent.

**Le SISNU** — Système d'Information Sanitaire National Unique — est le système d'information
sanitaire de routine du pays. Il est bâti sur **DHIS2** et a été lancé par le ministère de la
santé publique et de la population en **2013**, avec l'appui financier et technique de l'USAID.
Depuis 2017, le ministère travaille avec ses partenaires internationaux à en faire un système
unique et interopérable. Il est déployé dans les **dix départements** et couvre plus de
**800 institutions sanitaires**. C'est là que remontent les rapports mensuels agrégés des
institutions, tous programmes confondus. C'est le système national de rapportage : **agrégé, pas
nominatif**.

**iSanté** est le dossier médical électronique du pays pour le VIH. Il a été lancé en **2005** par
le ministère avec le **CDC** et l'**I-TECH**, l'International Training and Education Center for
Health. Il est utilisé dans plus de **150 hôpitaux et cliniques**, contient de l'ordre de
**1,3 million de dossiers patients**, et couvre selon les sources entre 63 et 70 % des personnes
sous traitement antirétroviral en Haïti. Il est **nominatif** et sert le soin : résumés de prise
en charge, résultats de laboratoire, rapports automatiques pour le ministère, alertes cliniques.

**MESI** — *Monitoring, Evaluation and Surveillance Interface* — est l'interface de rapportage du
ministère qui reçoit les rapports de cas VIH depuis les sites de dépistage et de conseil. iSanté
et MESI fonctionnent **en parallèle** dans la plupart des cliniques du ministère : iSanté envoie
des rapports de cas automatiques mensuels et génère le rapport que chaque institution doit
soumettre à la base nationale de suivi et de surveillance du VIH et de la tuberculose. C'est de
la base MESI que sont tirés les chiffres haïtiens du *Global AIDS Monitoring*.

**SALVH** — Suivi Actif Longitudinal du VIH en Haïti — est la base nationale de **surveillance
des cas VIH**, longitudinale et nominative. Elle reçoit des extractions automatiques mensuelles
depuis les **trois dossiers médicaux électroniques** du pays, dont iSanté, ainsi que depuis MESI,
et contient des données **dédupliquées** sur toutes les personnes diagnostiquées depuis 2004.
Elle utilise l'**empreinte digitale comme identifiant unique**. Les systèmes qui l'alimentent
couvrent plus de 95 % des patients sous traitement.

**Et par-dessus, DATIM**, la plateforme du PEPFAR, également bâtie sur DHIS2, où les partenaires
de mise en œuvre — Caris, CMMB — soumettent leurs indicateurs MER pour le bailleur américain.

**La carte mentale à retenir**, et à savoir dire en une phrase : le soin est saisi dans un dossier
médical électronique nominatif comme iSanté ; la surveillance épidémiologique nominative va dans
SALVH, dédupliquée, sous l'autorité du ministère ; le rapportage de routine agrégé va dans le
SISNU ; le rapportage bailleur va dans DATIM. **Quatre systèmes, quatre finalités, et un même
patient qui les traverse.** Quand un chiffre diverge entre deux d'entre eux, la question n'est
pas « lequel a raison » mais « à quelle étape la définition ou le périmètre change ».

**Un exemple de valeur pour l'entretien : le programme PLR**, *patient linkage to and retention in
care*. Il exploite les données des dossiers médicaux électroniques pour repérer les patients qui
manquent leurs rendez-vous, notifie les praticiens, et déclenche la visite à domicile d'agents de
santé communautaires équipés de tablettes. Le CDC rapporte que ce dispositif a ramené en soins
près de **17 000 patients perdus de vue** dans plus de 80 institutions. C'est l'illustration
parfaite de ce que l'annonce appelle *data use* : une donnée de routine transformée en action
opérationnelle, et un indicateur — la rétention — amélioré par le système d'information plutôt que
par un discours sur la qualité.

---

## 3. Les puces HMIS de l'annonce, traduites en pratique

Reprenons ce que l'annonce demande et disons ce que cela signifie concrètement, parce que c'est
sur ce terrain que tu gagnes.

### « Appuyer l'infrastructure informatique et la gestion des outils de données »

Cela veut dire : maintenir les postes, les tablettes, les connexions et les serveurs qui font
tourner la collecte, et être l'interlocuteur qui comprend à la fois le problème technique et sa
conséquence sur le rapportage. En Haïti, les contraintes réelles sont l'électricité, la
connectivité, et le vol ou la perte de matériel. D'où la primauté du **fonctionnement hors
ligne** — ce que ton CV appelle la fiabilité hors ligne sur le programme de modernisation mobile
chez Tekkod. Un outil de collecte qui exige une connexion permanente ne fonctionne pas dans une
institution rurale haïtienne, et c'est pour cela qu'ODK, KoboToolbox et CommCare sont construits
autour d'une saisie locale suivie d'une synchronisation.

### « Appuyer le déploiement de la dernière version sur tous les sites »

C'est une opération que l'on sait mal faire, et que tu sais faire. Les principes se disent en
quelques phrases.

On **ne déploie jamais partout d'un coup** : on pilote sur un ou deux sites représentatifs, on
observe un cycle, puis on étend. On **ne déploie jamais en milieu de période de rapportage** : on
attend la clôture, parce qu'une modification de formulaire au milieu d'un mois produit deux jeux
de données incompatibles pour la même période. On **prépare toujours un retour arrière** : si la
nouvelle version casse quelque chose, on doit pouvoir revenir à la précédente sans perdre les
données saisies entre-temps. Et on **versionne les formulaires**, parce que la donnée collectée
avec la version 3 d'un formulaire n'a pas la même structure que celle collectée avec la
version 2 — c'est le piège classique de la collecte mobile, et il se règle en conservant le
numéro de version dans chaque soumission.

Une phrase à avoir prête, parce qu'elle démontre l'expérience : « le problème d'un déploiement,
ce n'est pas d'installer la nouvelle version, c'est de savoir ce qu'on fait des données saisies
avec l'ancienne et des sites qui n'ont pas encore été mis à jour ».

### « Signaler les bogues » et « documenter toute communication d'incident technique »

Relis la formulation de l'annonce : ils veulent que soient documentés les incidents qui privent
une institution de son système informatique, **parce que cela crée un arriéré et empêche le
personnel clinique d'accéder à l'information et de rapporter**. Ils décrivent donc une procédure
de gestion d'incidents, et ils en donnent la justification en termes de rapportage.

Ce qu'un journal d'incidents doit contenir : la date et l'heure de détection, le site touché, la
nature du problème, les services empêchés, qui a été prévenu et quand, les actions entreprises,
la date de rétablissement, et — la colonne que personne ne met et qui fait toute la différence —
**l'impact sur les données de la période**.

### Et voici l'idée qui vaut l'entretien

Une panne informatique n'est pas un incident technique. C'est un **événement de qualité des
données**.

Le raisonnement se déroule ainsi. Un site perd son système pendant trois semaines. Le soin
continue — on ne cesse pas de traiter les patients parce que l'ordinateur est en panne — mais
l'enregistrement bascule sur le papier. Quand le système revient, quelqu'un doit saisir trois
semaines d'arriéré, souvent en quelques jours, souvent quelqu'un qui n'était pas présent lors des
consultations. Cette saisie rétrospective de masse est **structurellement moins fiable** que la
saisie au fil de l'eau : les dates se tassent sur les jours de saisie, les champs facultatifs
sont sautés, les désagrégations se dégradent, et certains actes ne sont jamais saisis du tout.

Conclusion opérationnelle : **le journal des incidents techniques doit être lu à côté des
indicateurs du mois**, et un indicateur d'un site ayant subi une interruption prolongée doit être
publié avec cette réserve. C'est la jonction exacte des deux moitiés de leur annonce, et c'est
une chose qu'un profil purement suivi-évaluation ne verra pas et qu'un profil purement
informatique ne dira pas.

### « Assurer le déploiement continu, l'amélioration et le fonctionnement de la base »

Le vocabulaire d'exploitation à savoir mobiliser : les **sauvegardes**, et surtout leur
**restauration testée** — une sauvegarde jamais restaurée n'est pas une sauvegarde, c'est une
hypothèse ; le **contrôle d'accès par rôle**, que tu as implémenté ; la **journalisation des
accès**, indispensable quand la donnée est un statut sérologique ; la surveillance des
performances, parce qu'un système lent finit par ne plus être utilisé, ce dont ton exemple des
trente-six secondes ramenées à moins d'une demi-seconde est l'illustration ; et la gestion des
**conflits de synchronisation**, qui est le problème propre aux systèmes hors ligne — deux
appareils modifiant le même enregistrement pendant qu'ils sont déconnectés.

### « Construire la culture de la donnée » et « former à l'analyse »

C'est le versant humain, traité dans
[`04_meal_sante.md`](04_meal_sante.md) sous l'angle de la restitution et de la formation. Le point
à retenir ici : la demande de données ne se décrète pas, elle se crée en rendant aux gens quelque
chose d'utile. Un site qui reçoit chaque mois une page comparative qui l'aide à piloter finit par
réclamer ses chiffres quand ils sont en retard. C'est à ce moment-là, et pas avant, que la culture
de la donnée existe.

---

## 4. La collecte mobile, telle que l'annonce la demande

L'annonce cite « Open Data Tools kit », qui est **ODK — Open Data Kit**. C'est ton terrain : ton
CV mentionne le codage de formulaires XLSForm pour ODK et KoboToolbox avec logiques de saut et
contraintes de validation, chez Anseye Pou Ayiti, ainsi que l'administration du panneau ODK.

Le principe à savoir défendre est celui du **déplacement du contrôle vers l'amont**. Beaucoup des
incohérences qu'on passe du temps à traquer au nettoyage peuvent être rendues **structurellement
impossibles au moment de la saisie**. Une contrainte qui refuse un âge supérieur à cent vingt ans
supprime définitivement cette erreur. Une liste de sites en cascade, dépendante du département
sélectionné, supprime les fautes d'orthographe et les erreurs de rattachement. Une règle qui
interdit de saisir plus de tests positifs que de tests réalisés supprime une famille entière
d'incohérences. Et un récapitulatif calculé affiché avant validation permet à l'agent de repérer
lui-même une saisie aberrante **sur place, quand l'information est encore vérifiable** — parce
qu'une fois qu'il est reparti, la vérité est perdue et on ne peut plus que deviner.

Les notions XLSForm à savoir nommer : les types de questions, les **contraintes** et leur message
d'erreur, la **pertinence** qui gouverne les logiques de saut, les **calculs**, les **groupes
répétés** pour les listes de longueur variable comme les membres d'un ménage, les **choix en
cascade**, les champs **obligatoires**, et les **métadonnées** automatiques — horodatage,
identifiant d'appareil, position GPS — qui servent au contrôle qualité de la collecte elle-même.
Ce dernier point mérite une phrase : les métadonnées permettent de détecter un questionnaire
rempli en trois minutes quand la moyenne est de vingt-cinq, ou dix questionnaires enregistrés au
même point GPS, ce qui est le contrôle antifraude standard sur une enquête.

---

## 5. La protection des données, quand la donnée est un statut VIH

Le sujet est traité sous l'angle éthique dans [`03_vih_essentiel.md`](03_vih_essentiel.md), et
sous l'angle général dans
[`../acted_bdd/04_securite_protection_donnees.md`](../acted_bdd/04_securite_protection_donnees.md).
Ce qu'il faut savoir dire ici est le versant technique, parce que c'est ta valeur ajoutée.

L'accès à la donnée nominative se **restreint par rôle** et se **journalise** : qui a consulté
quoi, quand. Les analyses travaillent sur des extractions **dépersonnalisées**, avec des
identifiants techniques. Les transferts de données sont **chiffrés**, et les extractions ne
circulent pas par courriel personnel ni par clé USB non protégée. Les appareils de collecte sont
protégés par code, avec chiffrement du stockage et effacement à distance quand la plateforme le
permet — parce que la perte d'une tablette est l'incident de terrain le plus banal. Les
sauvegardes sont chiffrées elles aussi, ce que l'on oublie systématiquement. Et l'on applique un
**seuil de petits effectifs** à toute publication : une cellule contenant un ou deux patients dans
une désagrégation fine identifie une personne dans une petite commune.

---

## Angles d'entretien

**« Comment vous y prendriez-vous pour déployer une nouvelle version de notre outil de collecte
sur l'ensemble des sites ? »**

« Je commencerais par ne pas la déployer tout de suite. Trois questions d'abord : qu'est-ce qui
change exactement dans la structure des données, où en est-on dans le cycle de rapportage, et
qu'est-ce qui se passe si ça se passe mal.

Sur la structure, si des champs sont ajoutés, renommés ou supprimés, les données de l'ancienne
version et de la nouvelle ne s'empilent plus directement, et il faut décider avant le déploiement
comment on les réconcilie pour la période en cours. C'est le point qu'on découvre trop tard en
général.

Sur le calendrier, je déploierais après une clôture de période, jamais au milieu, pour ne pas
avoir deux structures de données sur un même mois.

Sur le risque, je piloterais sur un ou deux sites représentatifs — pas les meilleurs, plutôt un
site correct et un site en difficulté — sur un cycle complet, en gardant la possibilité de revenir
en arrière. Ensuite j'étendrais par vagues, avec une note d'une page pour les agents, un canal
clair pour signaler les problèmes, et un suivi des sites effectivement passés à la nouvelle
version, parce que le vrai risque d'un déploiement progressif est d'oublier qui n'a pas encore
migré.

Et je documenterais l'opération dans le journal, avec les dates de bascule par site — parce que
ces dates expliqueront des ruptures dans les séries pendant les mois suivants, et que sans elles
quelqu'un finira par interpréter une discontinuité technique comme un changement de performance. »

**« Un site n'a pas remonté ses données depuis trois semaines. Que faites-vous ? »**

« Je ne commence pas par relancer, je commence par distinguer. Un site silencieux, c'est soit un
problème technique, soit un problème humain, soit un problème d'accès, et les trois n'appellent
pas la même réponse.

Le premier appel sert à savoir si l'équipe est en place et si le système fonctionne. Si c'est
technique — la tablette est cassée, la connexion est coupée, le logiciel refuse de synchroniser —
je le traite comme un incident : je le consigne, j'organise la solution de contournement, qui est
presque toujours le retour au papier avec saisie différée, et je note que les données de la
période arriveront en saisie rétrospective, donc avec une fiabilité moindre à signaler dans le
rapport.

Si c'est humain — l'agent formé est parti, il n'a pas été remplacé, personne ne sait faire — c'est
un problème de continuité de compétence, et la réponse est un appui rapproché plus une note
écrite qui survit à la prochaine rotation, pas un rappel à l'ordre.

Si c'est l'accès — insécurité, route coupée — il n'y a rien à corriger et tout à documenter,
parce que la conséquence est un trou de données assumé et déclaré, pas un chiffre inventé.

Dans tous les cas, ce site apparaît dans le taux de complétude que je publie avec l'indicateur du
mois. Un site silencieux qu'on ne signale pas devient un chiffre faussement rassurant. »
