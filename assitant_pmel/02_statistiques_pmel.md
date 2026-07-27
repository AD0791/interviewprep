# Statistiques pour le suivi-évaluation

*Module 2 — Préparation Assistant PMEL. Tous les résultats chiffrés de ce module ont été calculés sur le jeu de données réel `excel_exercices/data_center_propre_reference.csv` (360 observations, 30 écoles, 12 semaines, 4 départements). Tu peux les reproduire.*

---

## 1. Le problème avant l'outil

Ton rapport mensuel annonce un taux de présence de 75,6 %. Le directeur te demande trois choses : est-ce bon ou mauvais, est-ce que ça baisse, et est-ce que la différence avec le mois dernier est réelle ou due au hasard.

Ces trois questions correspondent exactement aux trois étages de la statistique. La première relève de la **statistique descriptive** : résumer ce que montrent les données. La deuxième relève de l'analyse **bivariée** : mettre une variable en relation avec une autre, ici le temps. La troisième relève de la **statistique inférentielle** : décider si un écart observé sur un échantillon reflète une réalité ou du bruit.

Presque tout le travail d'un assistant PMEL tient dans le premier étage. Mais savoir monter au troisième est ce qui distingue un producteur de tableaux d'un analyste — et c'est ce qu'un examen écrit va tester.

---

## 2. Le vocabulaire de base

Avant les calculs, quelques distinctions qui tombent en examen écrit.

Une **population** est l'ensemble complet des unités qui t'intéressent : les 3 148 élèves du réseau. Un **échantillon** en est un sous-ensemble observé. Un **paramètre** décrit la population (on le note avec des lettres grecques : μ pour la moyenne, σ pour l'écart-type) ; une **statistique** décrit l'échantillon et sert à estimer le paramètre (x̄, s).

Une **variable qualitative nominale** classe sans ordre : la région, le sexe. Une **variable qualitative ordinale** classe avec un ordre mais sans distance mesurable : une échelle de satisfaction. Une **variable quantitative discrète** compte : le nombre d'élèves. Une **variable quantitative continue** mesure : le taux de présence.

Cette typologie n'est pas décorative : **elle détermine quel test et quel graphique sont légitimes.** On ne calcule pas une moyenne de régions, on ne fait pas de corrélation de Pearson sur une variable ordinale. Si un examinateur te demande « quel test utiliseriez-vous ? », la première chose à faire est d'identifier la nature des variables.

---

## 3. Statistique descriptive et analyse univariée

L'analyse univariée décrit une variable à la fois. On la résume par trois familles d'indicateurs : la position, la dispersion, et la forme.

### 3.1 Les indicateurs de position

La **moyenne arithmétique** est la somme divisée par l'effectif. Sur nos données, le taux de présence moyen est de **75,56 %**.

La **médiane** est la valeur qui partage la série en deux moitiés égales. Ici : **75,22 %**.

Le **mode** est la valeur la plus fréquente. C'est le seul indicateur de position calculable sur une variable nominale.

Les **quantiles** découpent la série. Ici, le premier quartile vaut **66,0 %** et le troisième **86,1 %** : un quart des observations école-semaine sont sous 66 %, un quart au-dessus de 86 %.

**Quand préférer la médiane à la moyenne ?** Quand la distribution est asymétrique ou contient des valeurs extrêmes, parce que la moyenne y est sensible et la médiane non. L'exemple canonique est le revenu : dans un village où dix ménages gagnent 500 gourdes et un ménage en gagne 50 000, la moyenne dit 5 000 et ne décrit personne, tandis que la médiane dit 500 et décrit la réalité. C'est une question d'examen quasi certaine — retiens l'exemple, pas seulement la règle.

Ici, moyenne et médiane sont presque confondues (75,56 contre 75,22), ce qui indique une distribution à peu près symétrique.

### 3.2 La moyenne pondérée, le piège du métier

Le taux de présence moyen non pondéré est de 75,56 %. Le taux pondéré — la somme des présents divisée par la somme des inscrits — vaut **75,77 %**.

L'écart est faible ici, mais le principe est capital. La moyenne simple donne le même poids à une école de 80 élèves et à une école de 320. La moyenne pondérée reflète la réalité du terrain. **Pour un indicateur de taux agrégé, c'est toujours la version pondérée qui est correcte.**

$$\text{Taux régional} = \frac{\sum \text{présents}}{\sum \text{inscrits}} \quad \text{et non} \quad \frac{1}{n}\sum \text{taux}_i$$

L'écart entre les deux versions est lui-même informatif : s'il est important, c'est que la taille des écoles est liée à leur performance, ce qui mérite une analyse.

### 3.3 Les indicateurs de dispersion

L'**étendue** est la différence entre le maximum et le minimum : ici de 47,2 % à 98,9 %, soit 51,7 points. Elle est très sensible aux extrêmes.

La **variance** est la moyenne des carrés des écarts à la moyenne. L'**écart-type** en est la racine carrée, et il a l'avantage de s'exprimer dans la même unité que la variable : ici **12,51 points**. Interprétation courante : environ deux tiers des observations se situent à moins d'un écart-type de la moyenne, soit entre 63 et 88 %.

Attention à une subtilité d'examen : on divise par *n* pour la variance d'une population et par *n − 1* pour celle d'un échantillon (correction de Bessel). Dans Excel, `ECARTYPE.PEARSON` divise par *n*, `ECARTYPE.STANDARD` par *n − 1*. En pratique, on utilise presque toujours la seconde.

L'**écart interquartile** est la différence entre le troisième et le premier quartile : ici **20,0 points**. Il est robuste aux valeurs extrêmes et sert à la détection des aberrations selon la règle des 1,5 écart interquartile vue au [module Excel](04_excel_data_center.md).

Le **coefficient de variation** est l'écart-type rapporté à la moyenne, exprimé en pourcentage : ici **16,6 %**. Son intérêt est de permettre de comparer la dispersion de variables d'unités différentes. On considère généralement qu'au-delà de 30 %, la moyenne devient peu représentative.

### 3.4 La forme de la distribution

L'**asymétrie** (*skewness*) indique de quel côté la distribution s'étire. Positive, la queue s'étend vers la droite et la moyenne dépasse la médiane. L'**aplatissement** (*kurtosis*) mesure l'épaisseur des queues.

Le repère pratique : si la moyenne dépasse nettement la médiane, la distribution est étirée à droite ; si c'est l'inverse, elle est étirée à gauche. Ici l'écart est de 0,34 point, donc la distribution est quasi symétrique.

### 3.5 Représenter une variable seule

Un **histogramme** pour une variable continue, un **diagramme en barres** pour une variable qualitative, une **boîte à moustaches** pour visualiser médiane, quartiles et valeurs extrêmes simultanément. La boîte à moustaches est particulièrement efficace pour comparer plusieurs groupes d'un coup d'œil — quatre régions côte à côte, par exemple.

> **Épreuve écrite.** Sache calculer à la main moyenne, médiane, mode, étendue, variance, écart-type et coefficient de variation sur une petite série. Sache expliquer quand la médiane est préférable. Sache reconnaître une distribution asymétrique à partir de la position relative de la moyenne et de la médiane.

---

## 4. L'analyse bivariée

L'analyse bivariée met deux variables en relation. La méthode dépend entièrement de leur nature — c'est le tableau à connaître par cœur.

| Variable 1 | Variable 2 | Méthode descriptive | Test associé |
|---|---|---|---|
| Qualitative | Qualitative | Tableau croisé, profils en pourcentage | Khi-deux d'indépendance |
| Qualitative (2 groupes) | Quantitative | Moyennes par groupe, boîtes à moustaches | Test t de Student |
| Qualitative (3 groupes ou plus) | Quantitative | Moyennes par groupe | ANOVA |
| Quantitative | Quantitative | Nuage de points, covariance | Corrélation, régression |

### 4.1 Deux variables qualitatives : le tableau croisé

Croisons la région avec le fait d'être une observation « faible » (taux inférieur à 70 %).

| Région | Taux ≥ 70 % | Taux < 70 % | Total | % faible |
|---|---|---|---|---|
| Artibonite | 52 | 56 | 108 | 51,9 % |
| Centre | 51 | 21 | 72 | 29,2 % |
| Ouest | 66 | 30 | 96 | 31,3 % |
| Sud | 65 | 19 | 84 | 22,6 % |

Le point de méthode qui compte : **un tableau croisé ne se lit jamais en effectifs bruts, toujours en pourcentages en ligne ou en colonne**, parce que les groupes n'ont pas la même taille. Ici, l'Artibonite compte 56 observations faibles et l'Ouest 30, mais l'écart réel est de 51,9 % contre 31,3 %.

### 4.2 Deux variables quantitatives : la corrélation

Le **coefficient de corrélation de Pearson** mesure l'intensité et le sens d'une relation **linéaire**. Il varie de −1 à +1. Zéro signifie absence de relation linéaire — pas absence de relation, la nuance est importante.

Sur nos données, la corrélation entre l'effectif inscrit et le taux de présence vaut **0,051** : autrement dit, la taille de l'école n'a aucun lien linéaire avec sa performance de présence. La corrélation entre les jours de classe et le taux vaut **−0,040**, également nulle.

Le **coefficient de Spearman** travaille sur les rangs plutôt que sur les valeurs. On l'utilise quand la relation est monotone mais non linéaire, quand il y a des valeurs extrêmes, ou quand une variable est ordinale. La corrélation de Spearman entre la semaine et le taux vaut **−0,076**, soit une très légère tendance à la baisse au fil du temps, mais trop faible pour être exploitable.

Ordres de grandeur d'interprétation : en deçà de 0,3 en valeur absolue la relation est faible, entre 0,3 et 0,7 elle est modérée, au-delà de 0,7 elle est forte. Ces seuils sont indicatifs et dépendent du domaine.

**La phrase à ne jamais oublier : corrélation n'est pas causalité.** Trois explications concurrentes existent toujours devant une corrélation. Le lien peut être causal dans un sens, causal dans l'autre sens, ou dû à une troisième variable qui influence les deux — on parle de variable confondante. L'exemple pédagogique classique : les ventes de glaces et les noyades sont fortement corrélées, parce que la chaleur cause les deux. Savoir énoncer cela avec un exemple est attendu.

### 4.3 Une qualitative et une quantitative : comparer des groupes

Comparons le taux de présence entre les quatre départements.

| Région | n | Moyenne | Écart-type |
|---|---|---|---|
| Sud | 84 | 79,24 | 12,28 |
| Centre | 72 | 77,97 | 12,93 |
| Ouest | 96 | 74,56 | 11,35 |
| Artibonite | 108 | 71,98 | 12,41 |

L'écart entre le Sud et l'Artibonite est de **7,26 points**. Est-il réel ou dû au hasard de l'échantillonnage ? C'est la question inférentielle, traitée à la section suivante.

---

## 5. La statistique inférentielle

### 5.1 L'idée générale

Tu observes un échantillon et tu veux conclure sur la population. L'inférence fournit le cadre : jusqu'où puis-je généraliser, et avec quelle marge d'erreur ?

Deux outils : l'intervalle de confiance, qui donne une fourchette pour une valeur inconnue, et le test d'hypothèse, qui tranche entre deux propositions.

### 5.2 L'intervalle de confiance

L'**erreur type** de la moyenne est l'écart-type divisé par la racine carrée de l'effectif. Elle mesure la précision de ton estimation. L'intervalle de confiance à 95 % s'obtient en ajoutant et retranchant environ 1,96 erreur type.

$$IC_{95\%} = \bar{x} \pm 1{,}96 \times \frac{s}{\sqrt{n}}$$

Sur nos données : moyenne 75,56, écart-type 12,51, effectif 360. L'erreur type vaut 0,659 et l'intervalle **[74,27 ; 76,85]**.

**L'interprétation correcte**, celle qu'un examinateur attend : si l'on répétait l'échantillonnage un grand nombre de fois, 95 % des intervalles ainsi construits contiendraient la vraie valeur. La formulation relâchée « il y a 95 % de chances que la vraie valeur soit dans l'intervalle » est techniquement fausse mais universellement employée — sache la nuance sans en faire un débat.

Point pratique décisif : **l'intervalle rétrécit comme la racine carrée de l'effectif**. Pour diviser la marge d'erreur par deux, il faut quadrupler l'échantillon. C'est ce qui rend les grandes enquêtes coûteuses, et c'est l'argument à donner quand on te demande pourquoi on n'enquête pas plus de monde.

### 5.3 Le test d'hypothèse

On formule une **hypothèse nulle** (H₀), qui est toujours l'hypothèse d'absence d'effet : « il n'y a pas de différence entre les régions ». Et une **hypothèse alternative** (H₁) : « il y a une différence ». On calcule ensuite une statistique de test et la **p-value** associée.

**La p-value est la probabilité d'observer un écart au moins aussi grand que celui constaté, si l'hypothèse nulle était vraie.** Cette définition doit être sue mot pour mot : c'est la question piège la plus fréquente en entretien d'analyste.

Si la p-value est inférieure au seuil retenu — conventionnellement 0,05 — on rejette l'hypothèse nulle et l'on parle de résultat statistiquement significatif. Sinon, on ne rejette pas : ce qui n'est **pas** la même chose que prouver l'absence de différence. L'absence de preuve n'est pas la preuve de l'absence.

Deux erreurs sont possibles. L'**erreur de type I** consiste à rejeter H₀ alors qu'elle est vraie — un faux positif, dont la probabilité est le seuil α. L'**erreur de type II** consiste à ne pas rejeter H₀ alors qu'elle est fausse — un faux négatif, dont la probabilité est notée β. La **puissance** du test vaut 1 − β : c'est la capacité à détecter un effet réel, et elle augmente avec la taille de l'échantillon.

### 5.4 Les tests à connaître

Le **test t de Student** compare les moyennes de deux groupes. Sur nos données, comparons le Sud et l'Artibonite. La différence est de 7,26 points, l'erreur type de la différence de 1,795, ce qui donne une statistique **t = 4,04**. Avec une valeur de t supérieure à 2 en valeur absolue et des effectifs de cette taille, la p-value est très inférieure à 0,05 : **la différence est statistiquement significative**. On utilise la variante de Welch, qui ne suppose pas l'égalité des variances — c'est le choix par défaut prudent.

L'**ANOVA** compare les moyennes de trois groupes ou plus simultanément. Elle répond à « au moins un groupe diffère-t-il des autres ? ». Si le résultat est significatif, des tests post-hoc identifient quels groupes diffèrent.

Le **test du khi-deux** teste l'indépendance de deux variables qualitatives. Sur notre tableau croisé région × observation faible, on obtient **khi-deux = 20,81 à 3 degrés de liberté**. La valeur critique à 5 % pour 3 degrés de liberté étant de 7,81, on rejette l'hypothèse d'indépendance : **la proportion d'observations faibles dépend bien de la région**. Condition d'application à connaître : chaque effectif théorique doit être d'au moins 5.

Les **tests non paramétriques** — Mann-Whitney en remplacement du test t, Kruskal-Wallis en remplacement de l'ANOVA, Wilcoxon pour des échantillons appariés — s'emploient quand les conditions de normalité ne sont pas réunies ou sur des variables ordinales.

### 5.5 La significativité statistique n'est pas la significativité pratique

C'est le point de maturité qui distingue un bon candidat. Avec un échantillon très grand, un écart minuscule et sans intérêt opérationnel devient statistiquement significatif. Inversement, un écart important peut ne pas atteindre la significativité sur un petit échantillon.

D'où l'importance de la **taille d'effet**. Le *d* de Cohen rapporte la différence des moyennes à l'écart-type commun. Sur notre comparaison Sud–Artibonite, **d = 0,59**, ce qui correspond à un effet moyen selon les repères usuels (0,2 faible, 0,5 moyen, 0,8 fort). Un écart de 7,26 points de taux de présence entre deux départements est à la fois statistiquement significatif et opérationnellement important : il justifie une action.

Formuler cette double lecture — « c'est significatif, et l'ampleur de l'effet est moyenne, donc cela mérite une intervention » — est exactement le registre d'un analyste confirmé.

### 5.6 Calculer une taille d'échantillon

Pour une proportion, la formule de base pour une population infinie est :

$$n = \frac{z^2 \times p(1-p)}{e^2}$$

où *z* vaut 1,96 pour un niveau de confiance de 95 %, *p* est la proportion attendue (on prend 0,5 en l'absence d'information, car c'est le cas le plus défavorable) et *e* la marge d'erreur acceptée.

Avec p = 0,5 et une marge de 5 %, on obtient environ **385 personnes**. C'est le nombre magique à connaître : toute enquête sérieuse tourne autour de 400 répondants pour une marge de 5 %.

Pour une population finie, on applique une correction :

$$n_{ajusté} = \frac{n}{1 + \frac{n-1}{N}}$$

Sur nos 3 148 élèves, l'échantillon ajusté descend à environ 343. Et si l'on procède par grappes — en tirant des écoles entières plutôt que des élèves individuels — il faut multiplier par un **effet de grappe** généralement compris entre 1,5 et 2, parce que les élèves d'une même école se ressemblent davantage entre eux qu'avec ceux d'une autre école.

---

## 6. Analyse multivariée et modélisation

### 6.1 La régression linéaire

La régression explique une variable quantitative par une ou plusieurs autres. Sa forme générale :

$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \dots + \varepsilon$$

Chaque coefficient s'interprète comme l'effet d'une unité supplémentaire de la variable correspondante, **toutes choses égales par ailleurs**. Cette dernière expression est l'apport essentiel de la régression multiple par rapport à une simple corrélation : elle isole l'effet propre de chaque variable en neutralisant les autres.

Sur nos données, en expliquant le taux de présence par la semaine et le nombre de jours de classe, on obtient une constante de 80,69, un coefficient de −0,295 pour la semaine et de −0,666 pour les jours de classe, avec un **R² de 0,008**.

Ce résultat mérite d'être commenté honnêtement, parce que c'est ce qu'un examinateur veut voir : **le modèle n'explique rien**. Un R² de 0,008 signifie que moins de 1 % de la variance du taux de présence est expliquée par ces deux variables. La conclusion correcte n'est pas de forcer une interprétation des coefficients, mais de dire que la variabilité du taux de présence tient à des facteurs absents du modèle — l'école elle-même, la qualité de l'enseignement, le contexte local, la sécurité. Savoir dire « mon modèle n'explique pas grand-chose et voici pourquoi » vaut mieux que sur-interpréter trois décimales.

Le **R²** mesure la part de variance expliquée, entre 0 et 1. Il augmente mécaniquement quand on ajoute des variables, d'où le **R² ajusté** qui pénalise la complexité.

Les conditions d'application à citer : relation linéaire, indépendance des observations, homoscédasticité (variance des résidus constante), normalité approximative des résidus, et absence de multicolinéarité forte entre variables explicatives.

### 6.2 La régression logistique

Quand la variable à expliquer est binaire — l'élève abandonne ou non, le ménage est en insécurité alimentaire ou non — on utilise la régression logistique, qui modélise une probabilité. Ses coefficients s'interprètent en **rapports de cotes** (*odds ratios*) : un rapport de cotes de 2 signifie que la cote de l'événement double quand la variable augmente d'une unité.

C'est le modèle le plus utile en pratique dans le secteur, parce que beaucoup de questions de suivi-évaluation sont binaires.

### 6.3 Les méthodes descriptives multivariées

L'**analyse en composantes principales** réduit un grand nombre de variables quantitatives corrélées à quelques axes synthétiques. Elle sert notamment à construire des indices composites en dérivant les pondérations des données elles-mêmes — cela fait le lien avec le [module 5](05_indicateurs_et_indices.md).

L'**analyse factorielle des correspondances** fait l'équivalent pour des variables qualitatives. La **classification** (*clustering*) regroupe les unités similaires : elle permet par exemple de dégager des profils d'écoles selon leur combinaison de présence, d'encadrement et d'équipement, ce qui est très parlant dans un rapport.

### 6.4 Séries temporelles et évaluation d'impact

Sur une série chronologique, on distingue la **tendance**, la **saisonnalité** et le **résidu**. La saisonnalité est capitale en milieu scolaire : la présence baisse structurellement en période de récolte ou de saison des pluies, et interpréter cette baisse comme un échec du programme serait une erreur d'analyse grossière. **On compare toujours une période à la même période de l'année précédente, jamais au mois précédent.**

Pour l'évaluation d'impact, trois approches par ordre de rigueur croissante. La comparaison **avant-après** est la plus faible : elle attribue au programme tout ce qui a changé, y compris ce qui aurait changé de toute façon. La comparaison **avec un groupe témoin** est meilleure, mais suppose que les deux groupes soient comparables. La **double différence** (*difference-in-differences*) combine les deux : elle compare l'évolution du groupe bénéficiaire à l'évolution du groupe témoin, ce qui neutralise à la fois les différences initiales entre groupes et les tendances communes.

$$\text{Impact} = (Y^{trait}_{après} - Y^{trait}_{avant}) - (Y^{témoin}_{après} - Y^{témoin}_{avant})$$

C'est la raison pour laquelle le formulaire d'enquête ménage du [module XLSForm](03_xlsform_kobo_et_ona.md) contient une variable distinguant groupe de traitement et groupe de comparaison. Toute la chaîne se tient.

Le **biais de sélection** est la menace principale : les élèves parrainés ne sont pas tirés au sort, ils sont sélectionnés selon des critères de vulnérabilité. Comparer naïvement parrainés et non parrainés mesure donc autant l'effet de la sélection que celui du programme. Savoir énoncer cette limite spontanément — surtout chez une organisation dont le parrainage est le cœur de métier — démontre une vraie honnêteté méthodologique.

---

## 7. Les pièges classiques

Le **paradoxe de Simpson** : une tendance observée dans chaque sous-groupe peut s'inverser quand on agrège. C'est l'argument le plus fort en faveur de la désagrégation systématique.

Le **biais de survie** : n'analyser que les unités encore présentes surestime la performance, puisque les cas difficiles ont disparu de l'échantillon.

La **régression vers la moyenne** : les unités extrêmes tendent naturellement à se rapprocher de la moyenne à la mesure suivante. Si l'on cible les écoles les plus faibles et qu'elles s'améliorent, une partie de cette amélioration serait survenue sans intervention. C'est pourquoi un groupe témoin est indispensable.

La **confusion entre absence et zéro**, déjà vue au module Excel, qui reste l'erreur la plus coûteuse.

Le **choix de la période de comparaison** : comparer au mois précédent en présence de saisonnalité produit des conclusions fausses.

---

## Angles d'entretien

**« Quelle est la différence entre moyenne et médiane, et quand utilisez-vous l'une plutôt que l'autre ? »**

La moyenne est la somme des valeurs divisée par leur nombre, la médiane est la valeur qui coupe la série en deux moitiés égales. La différence pratique tient à leur sensibilité aux valeurs extrêmes : la moyenne est tirée par les valeurs atypiques, la médiane non. J'utilise donc la médiane dès que la distribution est asymétrique ou contient des valeurs extrêmes, et l'exemple qui parle le mieux est le revenu : dans un village où dix ménages gagnent cinq cents gourdes et un ménage en gagne cinquante mille, la moyenne annonce cinq mille gourdes et ne décrit la situation d'aucun des onze ménages, tandis que la médiane annonce cinq cents et décrit la réalité de la grande majorité. En pratique je publie souvent les deux, parce que l'écart entre elles est lui-même une information : quand la moyenne dépasse nettement la médiane, cela signale une distribution étirée vers le haut, donc une forte inégalité. Et pour les indicateurs de taux agrégés, j'ajoute une vigilance particulière : le taux d'une région n'est pas la moyenne des taux de ses écoles mais le rapport de la somme des présents à la somme des inscrits, sinon on donne le même poids à une école de quatre-vingts élèves et à une école de trois cent vingt.

**« Qu'est-ce qu'une p-value ? »**

La p-value est la probabilité d'observer un écart au moins aussi grand que celui que j'ai constaté, sous l'hypothèse que l'hypothèse nulle soit vraie, c'est-à-dire sous l'hypothèse qu'il n'y ait en réalité aucune différence. Si cette probabilité est très faible, généralement en dessous de cinq pour cent, je considère que l'hypothèse d'absence de différence est difficile à maintenir, et je conclus que l'écart est statistiquement significatif. Il y a deux erreurs d'interprétation que je fais attention à éviter. La première est de croire que la p-value donne la probabilité que l'hypothèse nulle soit vraie : ce n'est pas le cas, elle raisonne dans l'autre sens, en supposant l'hypothèse nulle vraie. La seconde est de confondre significativité statistique et importance pratique : avec un échantillon très grand, une différence négligeable devient significative. C'est pourquoi je regarde toujours la taille d'effet en complément. Par exemple, sur des données de présence scolaire, j'ai comparé deux départements dont les moyennes différaient de sept points ; le test donnait une statistique t de quatre, donc largement significative, mais ce qui m'a convaincu qu'il fallait agir, c'est le d de Cohen à zéro virgule cinquante-neuf, qui correspond à un effet d'ampleur moyenne, et surtout le fait que sept points de taux de présence représentent concrètement plusieurs centaines d'élèves-jours perdus.

**« Comment détermineriez-vous la taille d'un échantillon pour une enquête ? »**

Je pars de la formule classique pour l'estimation d'une proportion : n égale z au carré multiplié par p fois un moins p, le tout divisé par la marge d'erreur au carré. Le z vaut un virgule quatre-vingt-seize pour un niveau de confiance de quatre-vingt-quinze pour cent, et pour p je retiens zéro virgule cinq quand je n'ai pas d'estimation préalable, parce que c'est la valeur qui maximise la variance et donc le cas le plus défavorable. Avec une marge d'erreur de cinq pour cent, cela donne environ trois cent quatre-vingt-cinq répondants. J'applique ensuite deux ajustements. D'abord la correction pour population finie, parce que si ma population totale ne compte que trois mille personnes, l'échantillon nécessaire descend autour de trois cent quarante. Ensuite l'effet de grappe : si je tire des écoles entières plutôt que des élèves individuels, ce qui est presque toujours le cas pour des raisons de coût et de sécurité d'accès, je dois multiplier ma taille par un facteur généralement compris entre un et demi et deux, parce que les élèves d'une même école se ressemblent plus entre eux qu'avec ceux d'une autre école, et cette redondance d'information me fait perdre en précision. Enfin, je réfléchis toujours à la désagrégation voulue en amont : si je dois pouvoir conclure séparément sur quatre départements, ce n'est pas trois cent quatre-vingt-cinq personnes au total qu'il me faut, mais trois cent quatre-vingt-cinq par département, ce qui change complètement le budget de l'enquête. C'est une discussion à avoir avant la collecte, jamais après.

---

*Modules liés : [MEAL](01_meal_processus.md) · [Indicateurs et indices](05_indicateurs_et_indices.md) · [Excel](04_excel_data_center.md) · [XLSForm](03_xlsform_kobo_et_ona.md)*
