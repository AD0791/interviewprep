# XLSForm, de zéro : KoboToolbox et Ona.io

*Module 3 — Préparation Assistant PMEL. Les trois formulaires décrits ici existent réellement dans `xlsform_exercices/` et ont été convertis avec succès par pyxform.*

---

## 1. Le problème avant l'outil

Un coordonnateur part visiter huit écoles dans le Sud. Il emporte des fiches papier. Dans la première école, il note 240 élèves présents sur 220 inscrits — une erreur de report qu'il ne remarque pas. Dans la troisième, il oublie de remplir la ligne des repas. Dans la sixième, il écrit le nom de l'école « Ecole Puits Salé » alors que le référentiel dit « Ecole Puits-Sale ». Trois jours plus tard, quelqu'un ressaisit les huit fiches dans Excel et introduit deux fautes de frappe supplémentaires.

À Port-au-Prince, l'Assistant PMEL reçoit le fichier. Il découvre l'incohérence des 240 présents pour 220 inscrits, mais il est mercredi et le coordonnateur est reparti sur le terrain, injoignable. La ligne des repas manquante, il ne sait pas si elle vaut zéro ou si l'information n'a pas été collectée — et ces deux réponses conduisent à des conclusions opposées. Quant au nom d'école mal orthographié, il fera échouer silencieusement la jointure avec le référentiel, et cette école disparaîtra du rapport régional sans que personne ne s'en aperçoive.

Aucune de ces erreurs n'est due à de l'incompétence. Elles sont dues au fait que **rien, au moment de la saisie, n'a empêché l'erreur d'exister**. C'est exactement le problème que résout la collecte mobile structurée : déplacer le contrôle qualité du bureau vers le terrain, de l'après vers le pendant.

Reformulé pour l'entretien : *une contrainte écrite dans le formulaire vaut trois heures de nettoyage économisées, et surtout elle empêche une erreur qu'aucun nettoyage n'aurait pu rattraper — parce qu'une fois le coordonnateur reparti, la vérité est perdue.*

---

## 2. Ce qu'est XLSForm, et où il se situe

XLSForm n'est pas un logiciel. C'est une **convention d'écriture** : un standard qui permet de décrire un formulaire complexe dans un simple classeur Excel, en respectant des noms de feuilles et de colonnes précis.

La chaîne complète tient en cinq maillons, et il faut savoir la réciter :

1. Tu écris un classeur `.xlsx` respectant le standard XLSForm.
2. Un convertisseur nommé **pyxform** transforme ce classeur en un fichier **XForm**, qui est du XML conforme au standard ODK.
3. Ce XForm est publié sur un **serveur** : KoboToolbox, Ona.io, ODK Central.
4. Un **client** télécharge le formulaire et permet la saisie : ODK Collect ou KoboCollect sur Android, ou **Enketo** dans un navigateur web.
5. Les soumissions remontent au serveur, d'où on les **exporte** en CSV, XLSX, ou via une API.

Pourquoi cette chaîne mérite d'être connue ? Parce qu'elle te permet de **diagnostiquer**. Si le formulaire refuse de se publier, le problème est entre 1 et 2 — une erreur de syntaxe dans ton classeur. S'il se publie mais s'affiche mal sur mobile, le problème est en 4 — une question d'`appearance`. Si les données exportées ont une structure bizarre, le problème est en 5 — probablement un `repeat`. Savoir dire ça en entretien te distingue immédiatement de quelqu'un qui a seulement cliqué dans l'interface graphique de Kobo.

### Kobo et Ona : ce qui est identique, ce qui diffère

Les deux plateformes descendent du même écosystème ODK et consomment **le même standard XLSForm**. Un classeur correct fonctionne sur les deux sans modification. C'est le point rassurant, et c'est la phrase à dire : *« je travaille indifféremment sur Kobo ou Ona, le formulaire est identique, seule la chaîne de déploiement change »*.

Les différences se situent ailleurs. **KoboToolbox** est né dans l'écosystème humanitaire (initiative liée à OCHA et à la Harvard Humanitarian Initiative), propose une instance publique gratuite pour les organisations humanitaires, un constructeur de formulaire graphique, une bibliothèque de questions réutilisables, l'application **KoboCollect**, et un module de gestion des données intégré. C'est le standard de fait dans le secteur en Haïti — si tu ne devais en maîtriser qu'un, c'est celui-là.

**Ona.io** est également bâti sur ODK, met davantage l'accent sur l'**API** et l'intégration avec des outils d'analyse externes, propose des vues de données filtrées et partageables, et une gestion fine des projets et des organisations. On y publie le même XLSForm, on y collecte avec **ODK Collect** ou Enketo.

Dans les deux cas, la démarche pratique est la même : tu prépares ton classeur, tu le téléverses dans un nouveau projet, tu déploies, tu récupères le lien Enketo ou tu configures le client Android avec l'URL du serveur, tu collectes, tu exportes. Les captures d'écran diffèrent, la logique non.

---

## 3. L'anatomie du classeur

Trois feuilles, dont deux obligatoires en pratique.

La feuille **`survey`** contient les questions, dans l'ordre où elles apparaîtront. La feuille **`choices`** contient les listes de réponses des questions à choix. La feuille **`settings`** contient les métadonnées du formulaire.

### Les trois colonnes fondamentales de `survey`

La colonne **`type`** indique la nature de la question. La colonne **`name`** est l'identifiant machine : c'est lui qui deviendra le nom de la variable dans les données exportées. La colonne **`label`** est le texte affiché à la personne qui saisit.

Le nommage mérite une règle stricte, et c'est un argument à faire valoir en entretien. Un `name` doit être en minuscules, sans espace, sans accent, sans caractère spécial, commencer par une lettre, et être court mais explicite. `eleves_presents` est bon ; `Élèves présents (moyenne)` est catastrophique. La raison est simple : **ce `name` devient l'en-tête de colonne dans le fichier exporté, puis le nom du champ dans ta base de données, puis la variable dans ton script d'analyse.** Un nommage propre en amont épargne des heures de renommage en aval. Cette phrase — la donnée bien nommée à la source est de la donnée déjà nettoyée — vaut d'être placée.

### Les types de questions

Les types de saisie courants sont `text` pour du texte libre, `integer` pour un entier, `decimal` pour un nombre à virgule, `date`, `time`, `dateTime`, `select_one <liste>` pour un choix unique, `select_multiple <liste>` pour un choix multiple, `geopoint` pour une position GPS, `image`, `audio`, `video`, `barcode`, `file`.

Deux types ne sont pas des questions mais des instructions. Le type `note` affiche un texte sans rien demander — parfait pour un récapitulatif. Le type `calculate` exécute un calcul invisible dont le résultat est stocké et réutilisable.

Enfin les **métadonnées**, qu'il faut prendre l'habitude de mettre en tête de tout formulaire : `start` et `end` enregistrent l'horodatage de début et de fin de la saisie, `today` la date du jour, `deviceid` l'identifiant de l'appareil, `username` l'utilisateur. Elles sont précieuses pour le contrôle qualité : la différence entre `start` et `end` donne la durée de l'entretien, et un entretien ménage bouclé en quatre minutes alors qu'il en demande vingt-cinq est un signal de fabrication de données. **Savoir mentionner cette technique de détection de fraude est un excellent point d'entretien.**

### La feuille `choices`

Trois colonnes : `list_name` (le nom de la liste, référencé dans le `type` de la question), `name` (le code stocké) et `label` (le texte affiché). Une même liste occupe plusieurs lignes consécutives.

| list_name | name | label |
|---|---|---|
| regions | ouest | Ouest |
| regions | sud | Sud |
| oui_non | oui | Oui |
| oui_non | non | Non |

Le `name` est ce qui finit dans tes données. Utilise des codes stables et signifiants (`oui`, `non`, `ec001`), jamais des numéros arbitraires dont personne ne se souviendra du sens six mois plus tard.

### La feuille `settings`

Elle porte le `form_title` (le titre affiché), le `form_id` (l'identifiant unique du formulaire sur le serveur), la `version` (par convention un horodatage `AAAAMMJJNN` — indispensable pour gérer les mises à jour) et la `default_language`.

---

## 4. La logique : le vrai sujet

Tout ce qui précède est de la mise en forme. La valeur ajoutée commence ici.

### `required` — rendre obligatoire

`required` à `yes` interdit de passer à la suite sans réponse. À utiliser avec discernement : rendre tout obligatoire pousse les enquêteurs à inventer des réponses pour avancer. On rend obligatoire ce qui doit exister, et l'on prévoit une modalité « ne sait pas » plutôt que de forcer une réponse fausse.

### `relevant` — l'affichage conditionnel

Une question n'apparaît que si la condition est vraie. C'est le mécanisme des sauts logiques.

```
type                     name           label                                relevant
select_one oui_non       ens_present    Enseignant présent toute la semaine ?
select_one motifs        motif_ens      Motif de l'absence                   ${ens_present}='non'
```

La question du motif n'existe que si l'enseignant a été déclaré absent. Deux conséquences : l'enquêteur ne voit que ce qui le concerne, et surtout **les données sont structurellement cohérentes** — il devient impossible d'avoir un motif d'absence pour un enseignant présent.

La syntaxe `${nom_variable}` référence la réponse d'une question précédente. Les opérateurs sont `=`, `!=`, `>`, `<`, `>=`, `<=`, combinés par `and` et `or`. Pour un choix multiple, on teste avec `selected(${raisons},'autre')`.

### `constraint` — interdire l'impossible

C'est le cœur du contrôle qualité à la saisie. La contrainte porte sur la valeur de la question elle-même, désignée par un point.

```
type       name        label               constraint                        constraint_message
integer    presents    Élèves présents     .>=0 and .<=${inscrits}           Les présents ne peuvent pas dépasser les inscrits
integer    repas       Repas servis        .<=${presents}*${jours_classe}    Impossible : plus de repas que d'élèves-jours
```

Relis ces deux lignes en pensant au module MEAL. **Les règles de cohérence de la triangulation viennent d'être déplacées du nettoyage vers la collecte.** L'incohérence « plus de repas que d'élèves présents » ne pourra plus jamais entrer dans le Data Center, parce que le téléphone refusera l'enregistrement. C'est l'illustration parfaite du principe : *la qualité se construit à la saisie, pas au nettoyage*.

Toujours accompagner une `constraint` d'un `constraint_message` explicite. Un blocage sans explication conduit l'enquêteur à contourner en saisissant n'importe quoi.

### `calculation` — calculer en direct

Le type `calculate` permet de produire une valeur à la volée.

```
type        name            calculation
calculate   taux_presence   if(${inscrits}>0, round(${presents} div ${inscrits}*100,1), 0)
note        affiche         Taux de présence calculé : ${taux_presence} %
```

Deux pièges de syntaxe à mémoriser, ils tombent en examen. La division s'écrit **`div`** et non `/`, parce que la barre oblique désigne un chemin XPath. Et il faut **protéger contre la division par zéro** avec un `if`, sinon le formulaire produit une erreur silencieuse.

L'intérêt du calcul en direct est considérable : combiné à une `note`, il permet de **restituer immédiatement un récapitulatif à l'enquêteur avant validation**, qui peut alors corriger sur place s'il voit un chiffre aberrant. C'est de l'auto-contrôle terrain.

### Les fonctions utiles

Les plus fréquentes sont `if(condition, alors, sinon)`, `selected(${q},'code')`, `count()`, `sum()`, `round(valeur, décimales)`, `today()`, `int()`, `number()`, `string-length()`, `regex(., 'motif')`, `concat()`, `coalesce()`, `position(..)` pour l'index dans une répétition, et `indexed-repeat()` pour aller chercher une valeur précise dans une répétition.

### Groupes et répétitions

`begin_group` / `end_group` regroupent des questions liées ; avec `appearance` valant `field-list`, elles s'affichent toutes sur un même écran, ce qui accélère la saisie.

`begin_repeat` / `end_repeat` répètent un bloc autant de fois que nécessaire — une fois par classe, par membre du ménage, par parcelle. Le nombre de répétitions peut être libre, ou fixé par `repeat_count` à partir d'une question précédente.

**Attention à l'export**, c'est le piège classique dont personne ne parle : un formulaire contenant une répétition ne produit pas un fichier plat mais **plusieurs tables reliées par une clé**. La table principale contient une ligne par soumission ; la table de répétition contient une ligne par classe, avec un identifiant parent. Il faut donc les rejointer à l'analyse. Mentionner ce point spontanément en entretien signale une expérience réelle — c'est le genre de détail qu'on n'apprend qu'en s'y étant cassé les dents.

### `choice_filter` — les listes en cascade

Une cascade fait dépendre une liste du choix précédent : on sélectionne un département, et seules les écoles de ce département apparaissent.

Dans la feuille `choices`, on ajoute une colonne portant le nom du critère :

| list_name | name | label | region |
|---|---|---|---|
| ecoles | ec001 | Ecole Ganthier I | ouest |
| ecoles | ec004 | Ecole Puits-Sale | sud |

Dans la feuille `survey` :

```
type                  name     label         choice_filter
select_one regions    region   Département
select_one ecoles     ecole    École         region=${region}
```

La cascade est une arme de qualité redoutable : elle rend **impossible** d'associer une école à la mauvaise région, et elle supprime la saisie libre des noms d'écoles, donc toutes les variantes orthographiques. Le problème du nom mal écrit décrit au début de ce module disparaît par construction.

### `appearance` — l'ergonomie de terrain

Quelques valeurs à connaître : `minimal` affiche un menu déroulant compact, `horizontal` met les options côte à côte, `field-list` regroupe un groupe sur un écran, `likert` affiche une échelle, `multiline` agrandit une zone de texte, `quick` valide dès la sélection, `no-calendar` simplifie la saisie de date, `compact` économise l'espace. Une ergonomie soignée réduit la fatigue de l'enquêteur, et un enquêteur fatigué produit des données de moindre qualité.

### Le multilingue

En remplaçant `label` par `label::français (fr)` et `label::kreyòl (ht)`, le formulaire devient bilingue et l'enquêteur bascule d'une langue à l'autre. En Haïti, l'argument est décisif : les questions doivent être **posées en créole** pour être comprises, alors que la restitution se fait en français. Proposer spontanément un formulaire bilingue français-créole en entretien est un très bon point — cela montre que tu penses à la personne interrogée, pas seulement à la donnée.

Les colonnes `hint` et `constraint_message` se traduisent de la même manière, et pyxform émet un avertissement si une langue est incomplète.

---

## 5. Les trois formulaires livrés

Ils sont dans `xlsform_exercices/`, tous **convertis avec succès par pyxform**.

### `01_fiche_ecole.xlsx` — le formulaire simple

Fiche d'identification d'une école. Il couvre les fondamentaux : métadonnées, questions de tous types, une contrainte de date empêchant une saisie dans le futur, une contrainte de bornes sur le nombre de salles, une validation par expression régulière sur le numéro de téléphone (`regex(.,'^[0-9]{8}$')`), un `geopoint`, une photo, et une `note` de fin.

*Exercice : ajoute une question sur l'année de construction, avec une contrainte l'obligeant à être comprise entre 1950 et l'année en cours. Puis ajoute une question conditionnelle « type de source d'eau » qui n'apparaît que si l'école a déclaré disposer d'eau potable.*

### `02_presence_hebdomadaire.xlsx` — le formulaire de production

C'est **le formulaire dont Parole et Action a besoin**, et celui à savoir défendre en entretien. Il contient un groupe d'en-tête en `field-list`, une **cascade région → école**, une question sur les jours de classe effectifs avec un `hint` rappelant d'exclure les fermetures (le piège d'indicateur vu au module 5), une question conditionnelle sur le motif de fermeture, puis une **répétition par classe** dont le nombre est piloté par `repeat_count`.

À l'intérieur de la répétition, quatre contraintes de triangulation opèrent : les présents ne peuvent excéder les inscrits, les parrainés présents ne peuvent excéder les présents, les repas servis ne peuvent excéder le produit des présents par les jours de classe, et les jours d'absence de l'enseignant ne peuvent excéder les jours de classe. Le motif d'absence de l'enseignant n'apparaît que si celui-ci a été déclaré absent.

Après la répétition, six calculs agrègent les totaux, le taux de l'école et le ratio repas par élève-jour, restitués dans une `note` récapitulative. Puis un mécanisme d'alerte : si le taux de l'école tombe sous 60 %, une question de confirmation apparaît, suivie d'une demande d'explication obligatoire. C'est de l'auto-contrôle intégré, et cela reprend exactement le seuil d'alerte défini dans la fiche d'indicateur du module 5.

*Exercice : ajoute la désagrégation par sexe à l'intérieur de la répétition, avec une contrainte garantissant que filles plus garçons égale le total des présents.*

### `03_enquete_menage_impact.xlsx` — l'enquête d'effet

Questionnaire ménage **bilingue français-créole**, structuré en quatre sections. Il illustre les sauts logiques en cascade (le nombre d'enfants scolarisés n'est demandé que s'il y a des enfants de 6 à 14 ans ; les raisons de non-scolarisation ne sont demandées que si des enfants ne sont pas scolarisés ; la précision « autre raison » n'apparaît que si « autre » a été coché), le choix multiple avec `selected()`, une échelle de Likert, un score de consommation alimentaire calculé en direct, et une variable `groupe` distinguant **traitement et comparaison** — le dispositif d'évaluation d'effet du module 1.

*Exercice : ajoute une section sur les revenus avec des indicateurs proxy (type de toiture, possession de biens), et calcule un score de richesse simplifié.*

### Vérifier un formulaire avant de le déployer

```bash
pip install pyxform --break-system-packages
python3 -c "from pyxform.xls2xform import xls2xform_convert; print(xls2xform_convert('mon_form.xlsx','sortie.xml',validate=False))"
```

Un formulaire déployé sans conversion préalable réussie est une collecte perdue. Les erreurs les plus fréquentes sont un `name` dupliqué, une liste référencée dans `type` mais absente de `choices`, une variable référencée avant d'être définie, un `end_group` ou `end_repeat` manquant, un espace ou un accent dans un `name`, l'usage de `/` au lieu de `div`, et les guillemets typographiques copiés depuis Word qui cassent les expressions.

---

## 6. Traçons une collecte complète

Le lundi matin, tu mets à jour la liste des écoles dans la feuille `choices` et tu incrémentes la `version` dans `settings`. Tu convertis le classeur en local pour vérifier qu'il n'y a pas d'erreur, puis tu redéployes sur KoboToolbox ou Ona.

Le coordonnateur ouvre KoboCollect sur son téléphone et récupère la nouvelle version. Il part dans une zone sans réseau — **la collecte fonctionne entièrement hors ligne**, c'est un point à souligner en entretien pour le contexte rural haïtien. Il choisit « Sud », et la liste ne lui propose que les écoles du Sud. Il indique quatre jours de classe parce que le lundi a été perdu, et coche « intempérie ». Il saisit six classes.

Dans la troisième, il tape 195 présents pour 180 inscrits. **Le téléphone refuse** et affiche « Les présents ne peuvent pas dépasser les inscrits ». Il vérifie sa fiche papier, constate qu'il a lu la ligne du dessus, et corrige en 175. Cette erreur, qui aurait coûté un aller-retour de trois jours depuis Port-au-Prince, vient d'être réglée en dix secondes sur place.

À la fin, l'écran récapitulatif affiche les totaux et un taux d'école de 58 %. L'alerte se déclenche, il confirme et explique : « inondation, deux classes inaccessibles ». Cette explication qualitative, capturée au moment exact où l'information existe, est ce qui te permettra d'interpréter correctement la chute dans ton rapport mensuel — au lieu de conclure à tort à un désengagement des familles.

Le soir, de retour en zone couverte, il synchronise. Le mardi, tu exportes en XLSX : une table principale avec une ligne par école-semaine, une table de répétition avec une ligne par classe. Tu les rejoins sur l'identifiant parent, et tu attaques l'analyse. Ton nettoyage se limite à la complétude et aux doublons de synchronisation, parce que **toutes les incohérences internes ont été bloquées à la source**.

---

## Angles d'entretien

**« Quelle est votre expérience de la collecte de données mobile ? »**

Je conçois les formulaires directement en XLSForm plutôt que par le constructeur graphique, parce que le classeur me donne accès à toute la logique conditionnelle et se versionne proprement. Concrètement, je structure les trois feuilles `survey`, `choices` et `settings`, je nomme les variables en pensant à l'aval — le `name` que j'écris devient l'en-tête de colonne à l'export, puis le champ en base, donc un nommage propre en amont m'épargne des heures de renommage. Ensuite j'investis surtout dans la logique : les questions conditionnelles avec `relevant` pour que l'enquêteur ne voie que ce qui le concerne, les contraintes avec `constraint` pour rendre les valeurs impossibles réellement impossibles, les calculs en direct pour afficher un récapitulatif que l'enquêteur peut vérifier avant de valider, et les listes en cascade pour supprimer la saisie libre des noms de lieux. Je valide toujours le formulaire avec pyxform avant de le déployer, parce qu'un formulaire qui échoue en production est une journée de collecte perdue. Je publie indifféremment sur KoboToolbox ou Ona — le classeur est le même, seule la chaîne de déploiement change — et je collecte avec KoboCollect ou ODK Collect, qui fonctionnent entièrement hors ligne, ce qui est déterminant dans les zones rurales sans couverture.

**« Comment utilisez-vous le formulaire pour améliorer la qualité des données ? »**

Ma conviction est que la qualité se construit à la saisie et non au nettoyage, parce qu'une fois l'enquêteur reparti du terrain, l'information juste est définitivement perdue — on ne peut plus que deviner. Je traduis donc les règles de cohérence de la triangulation directement en contraintes dans le formulaire. Sur un suivi scolaire, cela donne trois règles : les élèves présents ne peuvent pas dépasser les inscrits, les élèves parrainés présents ne peuvent pas dépasser le total des présents, et les repas servis ne peuvent pas dépasser le nombre d'élèves présents multiplié par le nombre de jours de classe. Ces trois incohérences deviennent structurellement impossibles à enregistrer. J'ajoute une note récapitulative en fin de formulaire, alimentée par des calculs, pour que l'enquêteur voie lui-même ses totaux et son taux de présence avant de valider, avec une alerte s'il passe sous un seuil critique — et dans ce cas je lui demande une explication écrite, ce qui me donne l'information qualitative indispensable pour interpréter le chiffre plus tard. Enfin j'utilise les métadonnées : l'écart entre l'horodatage de début et de fin me donne la durée de chaque entretien, et un questionnaire de vingt-cinq minutes bouclé en quatre minutes est un signal que je vais vérifier.

**« Que se passe-t-il quand un formulaire contient une répétition ? »**

Une répétition permet de saisir un bloc de questions autant de fois que nécessaire, par exemple une fois par classe dans une école ou une fois par membre du ménage. Mais elle a une conséquence qu'on oublie souvent : les données exportées ne sont plus un fichier plat. Le serveur produit une table principale avec une ligne par soumission, et une table séparée pour la répétition avec une ligne par occurrence et un identifiant qui pointe vers la soumission parente. Pour analyser, il faut donc rejointer les deux tables sur cet identifiant, et faire attention en agrégeant à ne pas compter plusieurs fois les valeurs de la table principale. C'est aussi pour cette raison que je place systématiquement des variables de type `calculate` après la répétition, avec des fonctions comme `sum()`, pour disposer des totaux déjà agrégés au niveau de l'école directement dans la table principale : cela me donne un contrôle immédiat sans avoir à refaire la jointure, et cela me sert de vérification croisée si la jointure devait mal se passer.

---

*Modules liés : [Le processus MEAL](01_meal_processus.md) · [Théorie des indicateurs](05_indicateurs_et_indices.md) · [Excel et le Data Center](04_excel_data_center.md)*
