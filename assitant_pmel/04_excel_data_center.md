# Excel appliqué au Data Center

*Module 4 — Préparation Assistant PMEL. Le fichier d'exercice `excel_exercices/data_center_export_brut.xlsx` contient 356 lignes réelles avec des anomalies volontaires. Le corrigé complet, avec les valeurs exactes, figure en section 7 — ne le lis qu'après avoir cherché.*

---

## 1. Le problème avant l'outil

Tu reçois un export du Data Center : 356 lignes, trente écoles, douze semaines, quatre départements. Ton chef te demande le taux de présence moyen par région pour le rapport mensuel.

La tentation est d'écrire immédiatement un tableau croisé dynamique et de livrer le résultat. C'est l'erreur qui coûte un emploi. Parce que dans ce fichier, trois écoles n'ont pas rapporté toutes leurs semaines, deux lignes sont dupliquées à l'identique, une colonne censée être numérique contient du texte, une école déclare plus d'élèves présents qu'inscrits, et une autre affiche exactement le même nombre de repas pendant douze semaines consécutives. Un tableau croisé calculé sur ces données produira un chiffre. Ce chiffre sera faux, il aura l'air juste, et il partira au bailleur.

Le travail d'un analyste ne commence donc pas par l'analyse. Il commence par **l'interrogatoire du fichier**. Ce module suit cet ordre : d'abord savoir ce qu'on a, ensuite le nettoyer, ensuite seulement le faire parler.

---

## 2. Interroger le fichier avant de le toucher

Quatre questions, dans cet ordre, avant toute formule.

**Quelle est la granularité ?** Une ligne représente quoi, exactement ? Ici : une école, une semaine. La clé métier est donc le couple `code_ecole` + `semaine`. Identifier la clé est le premier geste, parce que tout le reste en découle — les doublons, la complétude, les jointures.

**Combien de lignes devrais-je avoir ?** Trente écoles multipliées par douze semaines égale 360 lignes attendues. Le fichier en contient 356. **L'écart n'est pas anodin : il est composé de lignes manquantes et de lignes en double qui se compensent partiellement.** Un fichier de 356 lignes là où on en attend 360 peut cacher sept absences et trois doublons — c'est exactement le cas ici.

**Quelles colonnes sont-elles vraiment du type annoncé ?** Une colonne « nombre d'élèves » qui contient « N/A » ou « non communiqué » n'est pas numérique, et toute somme la traitera silencieusement comme vide.

**Quelles règles métier doivent tenir ?** Ce sont les règles de triangulation du module 1, transposées en tests : présents ≤ inscrits, parrainés ≤ présents, repas ≤ présents × jours de classe, jours de classe entre 0 et 6, enseignants présents ≤ enseignants prévus.

Formules utiles pour cette phase de reconnaissance :

```excel
=NBVAL(A2:A400)                          ' nombre de valeurs non vides
=NB(H2:H400)                             ' nombre de valeurs NUMÉRIQUES
=NBVAL(H2:H400)-NB(H2:H400)              ' combien de cellules "numériques" sont du texte
=SOMMEPROD(1/NB.SI(A2:A357;A2:A357))     ' nombre de valeurs distinctes
=NB.SI.ENS(A:A;A2;D:D;D2)                ' occurrences de la clé (école, semaine)
```

L'écart entre `NBVAL` et `NB` sur une colonne censée être numérique est le test le plus rapide pour détecter du texte parasite. Retiens-le, il est direct en examen.

---

## 3. Le nettoyage

### 3.1 La complétude

C'est le contrôle qui précède tous les autres, et celui que les candidats oublient. **Une école absente du fichier n'est pas une école à zéro élève.** Si tu calcules une moyenne régionale en ignorant les absences, tu produis un chiffre qui repose sur un dénominateur inconnu.

La méthode : construire la grille théorique complète — trente écoles × douze semaines — et rapprocher l'export de cette grille. En pratique, une matrice écoles en lignes, semaines en colonnes, remplie par `NB.SI.ENS`, révèle instantanément les trous.

```excel
=NB.SI.ENS($A:$A;$A2;$D:$D;E$1)
```

Une cellule à 0 signale une absence, une cellule à 2 signale un doublon. La même formule détecte les deux problèmes.

Et surtout : **le taux de complétude est lui-même un indicateur à publier**. Écrire « taux de présence moyen : 76 % » est incomplet ; écrire « taux de présence moyen : 76 %, calculé sur 353 des 360 remontées attendues, soit 98,1 % de complétude » est du travail professionnel. C'est une phrase à placer telle quelle en entretien.

### 3.2 Les doublons

Il faut distinguer deux natures de doublons, et cette distinction est un très bon point d'examen.

Le **doublon exact** est une ligne strictement identique à une autre, généralement due à une double synchronisation. On le repère avec `Données > Supprimer les doublons` ou avec une mise en forme conditionnelle sur la ligne concaténée.

Le **quasi-doublon** est plus dangereux : même clé métier, valeurs légèrement différentes. Il résulte d'une correction saisie deux fois, ou de deux personnes ayant rapporté la même école. Ici, une école a deux lignes pour la même semaine avec 247 et 249 élèves présents. Lequel garder ?

**La règle : on ne tranche pas seul.** On documente, on conserve provisoirement la ligne la plus récente selon la date de saisie, on signale au coordonnateur, et on corrige après confirmation. Dire cela en entretien vaut mieux que n'importe quelle formule, parce que cela montre que tu comprends que la donnée appartient au terrain, pas à l'analyste.

```excel
=A2&"_"&D2                                     ' clé de contrôle
=SI(NB.SI.ENS($A:$A;A2;$D:$D;D2)>1;"DOUBLON";"")
```

### 3.3 L'harmonisation des libellés

Quatre pathologies typiques, toutes présentes dans le fichier.

Les **espaces parasites** en début, en fin ou en double à l'intérieur : `=SUPPRESPACE(B2)` (en anglais `TRIM`) les élimine tous, y compris les espaces multiples internes.

La **casse incohérente** : `=NOMPROPRE(B2)` (`PROPER`) normalise, `=MAJUSCULE()` et `=MINUSCULE()` aussi. Attention, `NOMPROPRE` transforme « Ecole Ganthier II » en « Ecole Ganthier Ii » — les chiffres romains y résistent mal. Mieux vaut souvent aligner sur le référentiel plutôt que reformater.

Les **caractères invisibles** venant de copier-coller : `=EPURAGE()` (`CLEAN`), et `=SUBSTITUE(B2;CAR(160);" ")` pour l'espace insécable, qui est le poison le plus courant des exports web.

Le **libellé qui contredit le code**, et c'est le plus grave : dans ce fichier, l'école `EC009` porte le nom « Ecole Gonaives » alors que le référentiel dit « Ecole Puits-Sale ». Le code et le nom ne désignent pas la même école. **La règle absolue : le code fait foi, jamais le libellé.** On ne joint jamais deux tables sur un nom ; on joint sur un identifiant. Le libellé de l'export est écrasé par celui du référentiel via une recherche.

```excel
=RECHERCHEX(A2;referentiel!$A:$A;referentiel!$B:$B;"CODE INCONNU")
```

`RECHERCHEX` (`XLOOKUP`) est à préférer à `RECHERCHEV` : elle gère la valeur manquante nativement, cherche dans les deux sens, et ne casse pas si l'on insère une colonne. Si la version d'Excel est ancienne, la combinaison `INDEX` + `EQUIV` (`INDEX`/`MATCH`) fait la même chose.

De la même manière, la région ne doit jamais être lue depuis l'export — où l'on trouve ici « ouest » en minuscules pour certaines semaines d'une école du Sud — mais toujours recalculée depuis le référentiel à partir du code.

### 3.4 Les colonnes numériques polluées

Trois cellules de la colonne des élèves présents contiennent du texte : un tiret, la mention « non communiqué », et une valeur « N/A » — cette dernière étant particulièrement sournoise parce qu'**Excel et la plupart des outils la convertissent silencieusement en cellule vide**, ce qui la rend invisible au contrôle visuel tout en faussant les calculs.

```excel
=SI(ESTNUM(H2);H2;"")                     ' isole les valeurs réellement numériques
=NBVAL(H:H)-NB(H:H)                        ' compte les intrus
```

La décision de traitement doit être explicite et documentée : ces valeurs sont-elles des zéros, ou des données manquantes ? **Ce ne sont pas des zéros.** « Non communiqué » signifie que l'information n'a pas été collectée. Les traiter comme des zéros écraserait la moyenne de l'école. On les laisse vides, on les exclut des calculs, et on les compte dans le taux de complétude.

### 3.5 Les dates hétérogènes

Deux écoles ont leurs dates au format jour/mois/année alors que le reste du fichier est en année-mois-jour. Excel interprète différemment selon les paramètres régionaux, et une date mal interprétée fait basculer une ligne dans le mauvais mois.

```excel
=DATE(DROITE(E2;4);STXT(E2;4;2);GAUCHE(E2;2))    ' reconstruction depuis jj/mm/aaaa
=SI(ESTNUM(E2);"date valide";"texte à convertir")
```

En pratique, Power Query gère cela plus proprement en imposant un format à la colonne à l'import et en isolant les lignes en erreur.

### 3.6 Les bornes et les valeurs aberrantes

Chaque variable a un domaine de validité. Les jours de classe doivent être compris entre 0 et 6 — le fichier contient une valeur de −5. Les effectifs inscrits doivent rester dans une plage plausible — une école affiche 3 200 inscrits là où les autres se situent entre 80 et 320.

Pour les aberrations statistiques moins évidentes, la méthode de l'écart interquartile est le standard : on calcule le premier et le troisième quartile, l'écart interquartile est leur différence, et l'on signale toute valeur en dehors de l'intervalle allant du premier quartile moins 1,5 fois l'écart au troisième quartile plus 1,5 fois l'écart.

```excel
=QUARTILE.INCLURE(G:G;1)
=QUARTILE.INCLURE(G:G;3)
=SI(OU(G2<$Q$1-1,5*($Q$3-$Q$1);G2>$Q$3+1,5*($Q$3-$Q$1));"ABERRANT";"")
```

Une valeur aberrante ne se supprime pas automatiquement : elle se **vérifie**. Une école peut légitimement être bien plus grande que les autres.

---

## 4. La triangulation dans Excel

C'est ici que le module 1 devient opérationnel. Chaque règle de cohérence devient une colonne de test, et le résultat alimente le journal des anomalies.

```excel
' Règle 1 — les présents ne dépassent pas les inscrits
=SI(H2>G2;"R1 : presents > inscrits";"")

' Règle 2 — les parrainés présents ne dépassent pas les présents
=SI(I2>H2;"R2 : parraines > presents";"")

' Règle 3 — les repas ne dépassent pas le maximum théorique
=SI(J2>H2*F2;"R3 : repas > presents x jours";"")

' Règle 4 — des élèves présents sans aucun enseignant
=SI(ET(L2=0;H2>0);"R4 : eleves sans enseignant";"")

' Règle 5 — bornes des jours de classe
=SI(OU(F2<0;F2>6);"R5 : jours de classe hors bornes";"")

' Agrégation des tests
=TEXTEJOINDRE(" | ";VRAI;N2:R2)
```

### Le piège du faux positif

Une sixième règle consiste à détecter les valeurs constantes, symptôme d'une donnée recopiée d'une semaine sur l'autre plutôt que relevée.

```excel
=SI(NB.SI.ENS($A:$A;A2)=NB.SI.ENS($A:$A;A2;$J:$J;J2);"R6 : repas constants";"")
```

Appliquée à ce fichier, cette règle signale **six écoles**. Mais seule une est réellement suspecte. Les cinq autres sont des écoles **sans cantine** : elles déclarent légitimement zéro repas chaque semaine, et leur constance est normale.

C'est la leçon la plus importante de ce module. **Une règle de détection produit des candidats, pas des verdicts.** Il faut toujours croiser l'anomalie détectée avec le référentiel — ici, la colonne « cantine » — avant de conclure. Un analyste qui envoie six alertes dont cinq fausses perd la confiance de ses coordonnateurs, et à la troisième fois plus personne ne lit ses alertes.

Savoir raconter cet exemple précis en entretien — « j'ai écrit une règle de détection, elle a produit six alertes, j'ai croisé avec le référentiel, cinq étaient des faux positifs dus aux écoles sans cantine » — est infiniment plus convaincant que réciter une liste de fonctions.

### Le journal des anomalies

C'est le livrable attendu. Un onglet dédié, une ligne par anomalie, avec ces colonnes : code de l'école, semaine, nature de l'anomalie, valeur observée, valeur attendue ou plausible, gravité, action proposée, personne à contacter, statut, date de résolution.

Ce journal n'est pas de la paperasse : c'est ce qui alimente le plan d'action mensuel exigé par la fiche de poste, et c'est ce qui permet de constater le mois suivant si les faiblesses ont été corrigées.

---

## 5. Les fonctions à maîtriser

**Recherche et jointure.** `RECHERCHEX` (`XLOOKUP`) pour ramener une information d'une autre table ; `INDEX` + `EQUIV` en repli sur les versions anciennes ; `RECHERCHEV` (`VLOOKUP`) à connaître mais à éviter.

**Agrégation conditionnelle.** `SOMME.SI.ENS`, `NB.SI.ENS`, `MOYENNE.SI.ENS` (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`) sont le socle de tout tableau d'indicateurs. Elles acceptent plusieurs critères simultanés, ce qui permet de calculer directement un indicateur désagrégé.

```excel
' Élèves présents dans le Sud en semaine 5
=SOMME.SI.ENS(H:H;C:C;"Sud";D:D;5)

' Taux de présence d'une région, calculé correctement
=SOMME.SI.ENS(H:H;C:C;"Sud")/SOMME.SI.ENS(G:G;C:C;"Sud")
```

**Attention à un piège méthodologique majeur** : le taux de présence régional n'est pas la moyenne des taux des écoles, c'est le rapport des sommes. Une moyenne de taux donne le même poids à une école de 80 élèves et à une école de 320 — c'est une moyenne non pondérée, et elle est fausse pour cet usage. La distinction entre moyenne simple et moyenne pondérée est un classique d'examen écrit ; on la retrouve en détail dans le [module de statistiques](02_statistiques_pmel.md).

**Logique et gestion d'erreur.** `SI`, `SI.CONDITIONS` (`IFS`), `ET`, `OU`, `SIERREUR` (`IFERROR`), `SI.NON.DISP` (`IFNA`), `ESTNUM`, `ESTVIDE`, `ESTNA`.

**Texte.** `SUPPRESPACE`, `EPURAGE`, `NOMPROPRE`, `MAJUSCULE`, `MINUSCULE`, `GAUCHE`, `DROITE`, `STXT`, `CHERCHE`, `TROUVE`, `SUBSTITUE`, `TEXTEJOINDRE`, `CONCAT`, `NBCAR`.

**Dates.** `DATE`, `ANNEE`, `MOIS`, `JOUR`, `AUJOURDHUI`, `NO.SEMAINE`, `DATEDIF`, `FIN.MOIS`, `NB.JOURS.OUVRES`.

**Statistiques.** `MOYENNE`, `MEDIANE`, `MODE.SIMPLE`, `ECARTYPE.STANDARD`, `QUARTILE.INCLURE`, `CENTILE.INCLURE`, `MIN`, `MAX`, `GRANDE.VALEUR`, `PETITE.VALEUR`, `RANG`, `SOMMEPROD` (indispensable pour les moyennes pondérées et les comptages multicritères complexes).

```excel
' Moyenne pondérée du taux de présence par les effectifs
=SOMMEPROD(H2:H357;G2:G357)/SOMME(G2:G357)
```

---

## 6. Tableaux croisés, Power Query et restitution

### Le tableau croisé dynamique

C'est l'outil de restitution central. Pour ce fichier : régions en lignes, semaines en colonnes, et en valeurs la somme des présents et la somme des inscrits — puis un **champ calculé** faisant leur rapport, ce qui donne le taux pondéré correct.

Deux réglages à connaître par cœur, parce qu'ils sont sources d'erreurs silencieuses. D'abord, dans les options du tableau, cocher « pour les cellules vides, afficher » et y mettre un tiret plutôt que zéro — pour ne pas confondre absence et valeur nulle, encore une fois. Ensuite, penser à actualiser après toute modification de la source : un tableau croisé ne se met pas à jour tout seul, et livrer un rapport calculé sur des données périmées est une faute classique.

Les **segments** (*slicers*) permettent de filtrer plusieurs tableaux simultanément — pratique pour un tableau de bord d'une page.

### Power Query

C'est le bon outil dès que la même opération doit être répétée chaque mois. Power Query enregistre les étapes de transformation et les rejoue sur un nouveau fichier d'un simple clic. Concrètement, pour le Data Center : importer l'export, supprimer les colonnes inutiles, imposer les types, remplacer les valeurs textuelles par du vide, supprimer les doublons, joindre le référentiel sur le code d'école, ajouter les colonnes calculées, puis charger.

L'argument à faire valoir en entretien est celui du temps : *le premier mois, la mise en place prend une journée ; les onze mois suivants, le nettoyage prend deux minutes.* C'est exactement le type de proposition d'amélioration continue que demande la fiche de poste.

Power Query gère aussi la **consolidation de plusieurs fichiers** — si chaque coordonnateur envoie son propre classeur, l'import depuis un dossier assemble tout automatiquement.

### La mise en forme conditionnelle

Elle transforme un tableau en outil de pilotage : rouge sous 60 %, orange entre 60 et 75 %, vert au-dessus ; jeux d'icônes pour l'évolution ; barres de données pour comparer les effectifs. Le seuil de 60 % est celui défini dans la fiche d'indicateur du [module 5](05_indicateurs_et_indices.md) — la cohérence entre les documents compte.

### Les graphiques

Une courbe pour une évolution dans le temps, un histogramme pour comparer des catégories, un nuage de points pour une relation entre deux variables. Trois règles : un titre qui énonce le message et non le sujet (« La présence chute dans l'Artibonite depuis la semaine 8 » plutôt que « Taux de présence »), un axe des ordonnées qui part de zéro pour ne pas exagérer les écarts, et pas de camembert au-delà de trois catégories.

---

## 7. Le corrigé de l'exercice

Ne lis cette section qu'après avoir fait le travail. Les valeurs ci-dessous sont celles réellement présentes dans le fichier.

**Volumétrie.** 356 lignes pour 360 attendues. Après dédoublonnage, 353 couples école-semaine uniques, soit un **taux de complétude de 98,1 %**.

**Complétude.** Trois écoles incomplètes : `EC018` n'a pas rapporté les semaines 9 à 12 (quatre absences, la plus préoccupante car elle suggère un arrêt de remontée), `EC022` manque les semaines 5 et 6, `EC030` manque la semaine 12.

**Doublons.** Deux doublons exacts sur `EC005` aux semaines 3 et 4. Un quasi-doublon sur `EC012` semaine 7, avec 247 et 249 élèves présents pour un nombre de repas identique — à arbitrer avec le coordonnateur, pas seul.

**Libellés.** `EC001` alterne entre « Ecole Ganthier I » et « ecole ganthier i ». `EC002` présente « Ecole  Ganthier II » avec espaces parasites en début, en fin et à l'intérieur. `EC014` porte la région « ouest » en minuscules pour certaines semaines alors que le référentiel la situe dans le Sud. Et surtout, `EC009` porte le nom « Ecole Gonaives » quand le référentiel dit « Ecole Puits-Sale » : **contradiction entre code et libellé, à corriger en faisant foi du code.**

**Texte en colonne numérique.** Trois occurrences : `EC013` semaine 2 contient un tiret, `EC026` semaine 10 contient « non communiqué », `EC006` semaine 5 contenait « N/A » et apparaît désormais comme cellule vide après conversion — c'est le cas le plus insidieux.

**Cellules vides sur les repas.** Trois : `EC024` semaine 8, `EC008` semaine 7, `EC019` semaine 4.

**Violations de règles métier.** Présents supérieurs aux inscrits sur `EC028` semaine 9 et `EC016` semaine 6. Parrainés supérieurs aux présents sur `EC020` semaine 3. Repas supérieurs au maximum théorique sur `EC003` semaine 4, `EC007` semaine 11, `EC011` semaine 8, `EC025` semaine 2, et `EC015` aux semaines 8 et 10. Jours de classe négatifs (−5) sur `EC027` semaine 10, ce qui entraîne mécaniquement une seconde alerte sur les repas de cette ligne — **une anomalie en cause une autre, il faut traiter la cause et non le symptôme**. Élèves présents sans aucun enseignant sur `EC017` semaine 3 et `EC004` semaine 9. Effectif aberrant de 3 200 inscrits sur `EC023` semaine 6.

**Repas constants.** La règle signale `EC001`, `EC009`, `EC015`, `EC021`, `EC023` et `EC028`. Croisement avec le référentiel : seule `EC015` dispose d'une cantine et déclare pourtant 900 repas identiques douze semaines de suite — c'est la vraie anomalie. Les cinq autres écoles n'ont pas de cantine et déclarent légitimement zéro. **Cinq faux positifs sur six alertes.**

**Dates.** `EC010` et `EC021` utilisent le format jour/mois/année.

**Résultats après nettoyage**, à titre de vérification : le taux de présence global pondéré s'établit à **75,8 %**. Par région : Sud 79,2 %, Centre 78,0 %, Ouest 74,6 %, Artibonite 72,0 %. Le fichier `data_center_propre_reference.csv` contient les données propres si tu veux contrôler tes calculs.

---

## 8. Le rapport mensuel

Le livrable demandé par la fiche de poste est double : un classeur Excel d'indicateurs et une note narrative.

Le **classeur** s'organise en onglets : les données brutes conservées intactes, les données nettoyées, le journal des anomalies, le tableau des indicateurs, les tableaux croisés, et une page de synthèse. Règle d'or : **on ne modifie jamais l'onglet brut.** Il est la trace de ce qui a été reçu, et c'est ce qui permet de refaire le travail si une décision de nettoyage se révèle mauvaise.

La **note narrative** suit une structure simple : le contexte du mois et le taux de complétude, les résultats des indicateurs avec leur évolution, les tendances observées avec leur interprétation prudente, les points forts, les points faibles, les défis rencontrés, les recommandations, et le plan d'action avec responsables et échéances. Elle doit aussi reprendre le suivi des actions décidées le mois précédent.

Un paragraphe bien écrit vaut mieux qu'un tableau de plus. Par exemple : *« Le taux de présence de l'Artibonite recule de 4,2 points par rapport au mois précédent, pour s'établir à 72,0 %, soit le plus faible des quatre départements. Ce recul se concentre sur trois écoles, et coïncide avec les remontées d'incidents sécuritaires signalées en semaines 9 et 10. Il ne peut donc être interprété comme un désengagement des familles sans vérification complémentaire ; une mission de terrain est recommandée avant toute conclusion. »* Ce paragraphe montre la mesure, l'écart, la localisation, l'hypothèse explicative, la prudence interprétative, et l'action recommandée. C'est le modèle à reproduire.

---

## Angles d'entretien

**« On vous remet un export de données terrain. Que faites-vous en premier ? »**

Je ne calcule rien avant d'avoir interrogé le fichier. Ma première question est celle de la granularité : que représente une ligne, et quelle est la clé métier ? Sur un suivi scolaire hebdomadaire, c'est le couple école-semaine. Je calcule ensuite le nombre de lignes que je devrais avoir — trente écoles fois douze semaines égale trois cent soixante — et je le compare au nombre réel, parce qu'un écart révèle simultanément des absences de remontée et des doublons, qui peuvent d'ailleurs se compenser et masquer les deux problèmes. Je vérifie ensuite que les colonnes annoncées comme numériques le sont vraiment, en comparant le nombre de valeurs non vides au nombre de valeurs numériques : l'écart me donne immédiatement les cellules polluées par du texte. Et seulement après, j'applique mes règles métier de cohérence. Le principe que je m'applique est qu'une absence de donnée n'est jamais un zéro : je publie donc toujours mes indicateurs accompagnés du taux de complétude sur lequel ils reposent, parce qu'un taux de présence de soixante-seize pour cent calculé sur quatre-vingts pour cent des écoles n'a pas la même valeur que le même chiffre calculé sur la totalité.

**« Comment calculez-vous un taux de présence par région ? »**

Attention au piège, et c'est une erreur que je vois souvent : le taux régional n'est pas la moyenne des taux des écoles, c'est le rapport de la somme des présents à la somme des inscrits. La différence n'est pas théorique. Une moyenne des taux donne le même poids à une école de quatre-vingts élèves et à une école de trois cent vingt, alors que la seconde pèse quatre fois plus dans la réalité de la région. On obtient donc une moyenne non pondérée, qui peut s'écarter sensiblement de la vérité, surtout si les petites écoles ont des comportements atypiques. En pratique, j'utilise deux sommes conditionnelles et je fais leur rapport, ou dans un tableau croisé dynamique je crée un champ calculé plutôt que d'agréger une colonne de taux déjà calculée ligne à ligne. Je garde par ailleurs la moyenne non pondérée comme information complémentaire, parce que l'écart entre les deux est lui-même instructif : s'il est important, cela signifie que la taille des écoles et leur performance sont liées, ce qui mérite une analyse.

**« Vous détectez une anomalie dans les données. Comment procédez-vous ? »**

Je ne corrige jamais directement, pour deux raisons. La première est que je peux me tromper sur la nature de l'anomalie. J'ai un exemple précis en tête : j'avais écrit une règle signalant les écoles dont le nombre de repas restait rigoureusement constant sur toute la période, en partant du principe qu'une donnée recopiée est une donnée non relevée. La règle a produit six alertes. En croisant avec le référentiel des écoles, j'ai constaté que cinq de ces écoles n'avaient tout simplement pas de cantine et déclaraient légitimement zéro repas chaque semaine. Une seule alerte était fondée. Si j'avais envoyé les six, j'aurais fait perdre du temps à cinq coordonnateurs et perdu leur confiance pour les alertes suivantes. La seconde raison est que l'anomalie m'apprend souvent quelque chose sur le processus de collecte lui-même, et cette information disparaît si je me contente de corriger la cellule. Ma procédure est donc de consigner chaque anomalie dans un journal avec sa nature, la valeur observée, la valeur attendue et la gravité ; de croiser avec le référentiel pour éliminer les faux positifs ; de remonter au coordonnateur concerné pour les cas restants ; puis de corriger seulement après confirmation, en conservant intacte la donnée brute d'origine. Et j'inscris les anomalies récurrentes dans le plan d'action du mois suivant, parce que corriger un chiffre sans corriger le processus qui l'a produit garantit de retrouver la même erreur.

---

*Modules liés : [Le processus MEAL](01_meal_processus.md) · [XLSForm](03_xlsform_kobo_et_ona.md) · [Statistiques](02_statistiques_pmel.md) · [Indicateurs](05_indicateurs_et_indices.md)*
