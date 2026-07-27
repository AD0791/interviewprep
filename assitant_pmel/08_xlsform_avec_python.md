# Manipuler les XLSForm avec Python

*Module 8 — Préparation Assistant PMEL. Les cinq scripts décrits ici sont dans `python_xlsform/` et **ont tous été exécutés** : les sorties affichées sont réelles.*

---

## 1. Le problème avant l'outil

Tu gères vingt formulaires de collecte. Le référentiel des écoles change : trois nouvelles ouvrent, une ferme. Il faut mettre à jour la feuille `choices` de chacun des vingt classeurs, incrémenter vingt numéros de version, vérifier que rien n'est cassé, et redéployer.

À la main, cela représente une matinée, et une matinée pendant laquelle on introduit des erreurs — un classeur oublié, une version non incrémentée, une liste mal recopiée. Le pire est que ces erreurs sont silencieuses : le formulaire se déploie quand même, et l'on ne découvre le problème que trois semaines plus tard, quand une école n'apparaît dans aucune remontée.

Le même raisonnement vaut pour la relecture. Comment vérifier que dans un formulaire de quarante questions, chaque `constraint` a bien son `constraint_message`, qu'aucune variable n'est référencée avant d'être définie, qu'aucun `name` ne comporte d'accent, et qu'aucune liste de choix n'est appelée sans exister ? À l'œil, c'est fastidieux et faillible. En Python, c'est trente lignes et deux secondes.

**L'argument à faire valoir en entretien** : *un XLSForm est un fichier Excel, donc un objet manipulable par programme. Traiter les formulaires comme du code — génération, audit automatique, validation avant déploiement, versionnement — supprime toute une classe d'erreurs et rend les mises à jour instantanées.*

---

## 2. La boîte à outils

Quatre bibliothèques suffisent, toutes standard.

**pyxform** est le convertisseur officiel du projet ODK. C'est exactement le moteur qu'utilisent KoboToolbox et Ona côté serveur : si pyxform accepte ton formulaire en local, le serveur l'acceptera. C'est pourquoi la validation locale est fiable.

**openpyxl** lit et écrit les classeurs `.xlsx`. C'est avec elle qu'on génère ou modifie la structure d'un XLSForm.

**pandas** sert au traitement des données collectées : lecture des exports, jointures, contrôles.

**requests** permet d'appeler les API de Kobo et Ona pour automatiser publication et récupération des soumissions.

```bash
pip install pyxform openpyxl pandas requests
```

À citer si l'on te demande d'aller plus loin : **pyodk**, le client Python officiel d'ODK Central, qui encapsule proprement l'authentification et la récupération des soumissions.

---

## 3. Valider avant de déployer

C'est le script le plus rentable, et celui à mettre en place en premier. Un formulaire déployé sans conversion préalable réussie, c'est une journée de collecte perdue.

Le cœur tient en trois lignes :

```python
from pyxform.xls2xform import xls2xform_convert

avertissements = xls2xform_convert("mon_formulaire.xlsx", "sortie.xml", validate=False)
```

Si la conversion échoue, une exception est levée avec la cause exacte : liste de choix manquante, `name` dupliqué, `end_group` oublié, expression mal formée. Si elle réussit, la fonction renvoie la liste des avertissements — moins graves, mais qu'il faut lire.

Le script `xlsform_valider.py` industrialise cela sur un dossier entier :

```bash
$ python3 xlsform_valider.py ../xlsform_exercices

[OK]    01_fiche_ecole.xlsx
        [row : 18] Use the max-pixels parameter to speed up submission sending...
[OK]    02_presence_hebdomadaire.xlsx
        [row : 41] Use the max-pixels parameter to speed up submission sending...
[OK]    03_enquete_menage_impact.xlsx
        Language 'kreyol (ht)' is missing the survey columns constraint_message, hint.

3/3 formulaire(s) valide(s).
```

Il renvoie un code de sortie non nul en cas d'échec, ce qui permet de le brancher dans un enchaînement automatique : aucun formulaire ne part si un seul échoue.

Remarque le troisième avertissement : pyxform signale que la version créole est incomplète. C'est précisément le genre de défaut invisible à l'œil qu'un contrôle automatique attrape systématiquement.

---

## 4. Auditer un formulaire

pyxform vérifie que le formulaire est **techniquement convertible**. Il ne vérifie pas qu'il est **bien conçu**. Un formulaire peut se convertir parfaitement tout en ayant des contraintes sans message d'erreur, des listes de choix orphelines, ou des divisions non protégées contre le zéro.

Le script `xlsform_audit.py` comble cet écart. Il lit les trois feuilles avec openpyxl et applique une série de contrôles métier : validité des noms de variables selon la convention (minuscules, chiffres, souligné, commençant par une lettre), détection des noms dupliqués, vérification que toute liste utilisée dans `survey` existe dans `choices` et inversement, résolution de chaque référence `${variable}` contre les variables réellement définies, présence d'un `constraint_message` pour chaque `constraint`, détection des divisions écrites avec `/` au lieu de `div` et des divisions non protégées par un `if`, complétude des traductions, et présence des champs obligatoires de `settings`.

Exécution réelle sur le formulaire de production :

```bash
$ python3 xlsform_audit.py ../xlsform_exercices/02_presence_hebdomadaire.xlsx

  Questions : 41
  Listes de choix definies : 6 | utilisees : 6
  Types : select_one=9, integer=8, calculate=7, text=3, note=3, begin_group=1,
          date=1, begin_repeat=1, geopoint=1, image=1, ...
  Obligatoires : 21
  Contraintes : 9
  Conditions (relevant) : 6
  Calculs : 7

  Aucun probleme detecte.
```

Et sur le questionnaire bilingue :

```bash
$ python3 xlsform_audit.py ../xlsform_exercices/03_enquete_menage_impact.xlsx

  Questions : 37
  Langues : francais (fr), kreyol (ht)

  2 point(s) d'attention :
   - TRADUCTION INCOMPLETE : la langue 'kreyol (ht)' n'a pas de colonne 'constraint_message'
   - TRADUCTION INCOMPLETE : la langue 'kreyol (ht)' n'a pas de colonne 'hint'
```

L'audit retrouve exactement ce que pyxform avait signalé, plus tout ce que pyxform ne regarde pas.

**Le point le plus intéressant à raconter en entretien** est le contrôle de **résolution des références**. Dans un formulaire, une expression comme `relevant="${ens_present}='non'"` renvoie à une variable définie ailleurs. Si cette variable a été renommée ou supprimée, ODK ne plante pas nécessairement : la condition devient simplement toujours fausse, et **la question n'apparaît jamais**. On collecte alors pendant des semaines sans s'apercevoir qu'un champ entier est systématiquement vide. Un contrôle automatique des références élimine cette catégorie de bug silencieux — et c'est le type de bug qui coûte le plus cher, parce qu'il ne se voit qu'au moment de l'analyse, quand il est trop tard.

Le cœur du contrôle, en résumé :

```python
import re
REF = re.compile(r"\$\{([^}]+)\}")

noms_definis = {r["name"] for r in survey if r.get("name")} | METADONNEES
for i, ligne in enumerate(survey, start=2):
    for colonne in ("relevant", "constraint", "calculation", "choice_filter", "repeat_count"):
        for reference in REF.findall(ligne.get(colonne, "")):
            if reference not in noms_definis:
                print(f"REFERENCE INCONNUE ligne {i} ({colonne}) : ${{{reference}}}")
```

---

## 5. Générer un formulaire par programme

Le script `xlsform_builder.py` expose une petite classe `XLSForm` qui permet d'écrire un formulaire en Python plutôt que dans Excel.

```python
f = XLSForm("Suivi quotidien de la cantine", "pa_cantine_jour")
f.metadonnees()

f.liste("regions", [("ouest", "Ouest"), ("sud", "Sud"),
                    ("centre", "Centre"), ("artibonite", "Artibonite")])
f.liste("ecoles", [("ec001", "Ecole Ganthier I", "ouest"),
                   ("ec004", "Ecole Puits-Sale", "sud")], colonne_filtre="region")

f.groupe("entete", "Identification")
f.q("date", "date_jour", "Date du service", required="yes",
    constraint=".<=today()", constraint_message="Date future impossible")
f.q("select_one regions", "region", "Departement", required="yes")
f.q("select_one ecoles", "ecole", "Ecole", required="yes",
    choice_filter="region=${region}")
f.fin_groupe("entete")

f.q("integer", "presents", "Eleves presents aujourd'hui", required="yes",
    constraint=".>=0 and .<=500", constraint_message="Valeur attendue entre 0 et 500")
f.q("integer", "repas", "Nombre de repas servis", required="yes",
    relevant="${service_assure}='oui'",
    constraint=".<=${presents}",
    constraint_message="Impossible : plus de repas que d'eleves presents")
f.calcul("couverture", "if(${presents}>0, round(${repas} div ${presents}*100,1), 0)")
f.q("note", "recap", "Couverture du jour : ${couverture} % des eleves presents")

f.ecrire("exemple_genere.xlsx")
```

Le classeur produit passe la conversion pyxform et l'audit sans aucun problème détecté. La version est générée automatiquement à partir de la date du jour, au format `AAAAMMJJNN` — ce qui supprime l'oubli d'incrémentation, une erreur classique qui empêche les appareils de récupérer la nouvelle version.

**Quand cette approche vaut-elle le détour ?** Pas pour un formulaire unique — Excel est plus rapide. Elle devient rentable dans trois cas. Le premier est la génération de familles de formulaires qui partagent une structure mais diffèrent par leurs listes : un formulaire par département, par exemple. Le deuxième est la mise à jour de masse des listes de choix depuis une source de vérité — la base de données des écoles — qui garantit que les vingt formulaires portent exactement le même référentiel. Le troisième est la génération d'un formulaire depuis un plan MEAL : si la matrice de suivi des indicateurs est dans un classeur, on peut en dériver automatiquement les questions correspondantes, ce qui garantit que **rien de ce qui doit être mesuré n'est oublié dans le formulaire** — c'est l'argument le plus fort, parce qu'il relie directement l'outil à la méthode du [module 1](01_meal_processus.md).

Voici l'idée du troisième cas, en quelques lignes :

```python
import pandas as pd

itt = pd.read_excel("plan_meal.xlsx", sheet_name="indicateurs")
f = XLSForm("Collecte derivee du plan MEAL", "pa_itt")
f.metadonnees()

for _, ind in itt.iterrows():
    f.q(ind["type_question"], ind["nom_variable"], ind["libelle"],
        required="yes",
        constraint=ind.get("borne", ""),
        constraint_message=ind.get("message", ""))

f.ecrire("formulaire_depuis_itt.xlsx")
```

---

## 6. Gérer le multilingue

Le script `xlsform_traduire.py` convertit un formulaire monolingue en formulaire multilingue et prépare le travail du traducteur. Il renomme les colonnes traduisibles — `label`, `hint`, `constraint_message` — au format `colonne::langue`, crée les colonnes de la nouvelle langue, et les préremplit avec le texte source préfixé d'un marqueur.

```bash
$ python3 xlsform_traduire.py ../xlsform_exercices/02_presence_hebdomadaire.xlsx \
                              02_bilingue.xlsx "kreyol (ht)"

Ecrit : 02_bilingue.xlsx
Chaines a traduire : 72
  survey ligne 6  [label::kreyol (ht)] [A TRADUIRE] Identification
  survey ligne 7  [label::kreyol (ht)] [A TRADUIRE] Nom du coordonnateur
  survey ligne 8  [label::kreyol (ht)] [A TRADUIRE] Date de la collecte
  survey ligne 9  [label::kreyol (ht)] [A TRADUIRE] Numero de la semaine (1-52)
  ...
```

Le fichier produit **passe la validation pyxform** immédiatement, avant même d'être traduit. On peut donc l'envoyer au traducteur en sachant qu'il est structurellement correct, et la fonction `rapport_traduction()` permet de vérifier à tout moment ce qu'il reste à traiter.

En contexte haïtien, l'argument est concret : les questions doivent être **posées en créole** pour être comprises par les personnes interrogées, alors que la restitution et les rapports se font en français. Un formulaire bilingue supprime la traduction improvisée par l'enquêteur, qui est une source majeure d'incohérence — deux enquêteurs traduisant différemment la même question ne mesurent pas la même chose, ce qui est un problème de **fiabilité** au sens du [module 1](01_meal_processus.md).

---

## 7. Traiter les données collectées

C'est le script le plus utile au quotidien, parce qu'il traite le piège dont personne ne parle avant de s'y être cassé les dents.

**Un formulaire contenant un `begin_repeat` ne produit pas un fichier plat.** L'export génère une table principale, avec une ligne par soumission, et une table séparée par répétition, avec une ligne par occurrence, reliée à la première par une clé — `_parent_index` ou `_submission__uuid` selon la plateforme. Pour analyser, il faut les rejointer.

Le script `aplatir_soumissions.py` prend un export contenant des répétitions et enchaîne quatre opérations : la jointure avec détection automatique de la clé, les contrôles de triangulation, l'analyse des durées de saisie, et la vérification des totaux calculés dans le formulaire.

Exécution réelle sur un export simulé de vingt-quatre soumissions :

```bash
$ python3 aplatir_soumissions.py export_kobo_simule.xlsx

Table principale 'pa_presence_hebdo' : 24 soumissions, 15 colonnes
Repetition 'classe' : 105 lignes -> 105 apres jointure sur _parent_index = _index

Controles de coherence :
  R1 presents > inscrits                     :   1 ligne(s)
  R2 parraines > presents                    :   0 ligne(s)
  R3 repas > presents x jours                :   0 ligne(s)
  R4 enseignant absent, eleves presents      :  29 ligne(s)

Duree de saisie (minutes) :
  mediane 15.0 | min 2.0 | max 20.0
  soumissions anormalement rapides : 2

Verification des totaux calcules dans le formulaire :
  ecart total sur les presents : 10
  ecart total sur les repas    : 150

Ecrit : donnees_aplaties.xlsx (105 lignes)
```

Quatre choses méritent d'être commentées, et chacune est un argument d'entretien.

**La jointure a un piège.** Les deux tables contiennent une colonne `_index`, et une fusion naïve les rend indistinguables — ce qui casse ensuite la détection des lignes orphelines. Le script renomme donc la clé parente avant de joindre. C'est un détail technique, mais c'est le genre de détail dont la connaissance prouve qu'on a réellement manipulé ces exports.

**La durée de saisie détecte les données fabriquées.** Les métadonnées `start` et `end` donnent le temps passé sur chaque soumission. Ici, la médiane est de quinze minutes, et deux soumissions ont été bouclées en deux minutes — soit moins de 30 % du temps médian. Ce n'est pas une preuve de fraude, mais c'est un signal à vérifier. **Mentionner spontanément cette technique en entretien est très efficace**, parce que peu de candidats savent que l'outil de collecte fournit gratuitement un indicateur de qualité de ce type.

**La vérification des totaux croise deux sources qui devraient concorder.** Le formulaire calcule des totaux par `sum()` au moment de la saisie ; le script les recalcule depuis les lignes répétées. Un écart signifie soit une modification des données après soumission, soit un problème dans l'expression du formulaire. Ici, l'écart de 150 repas sur une soumission signale une valeur altérée. C'est une **triangulation interne** — la donnée confrontée à elle-même — et c'est une application directe du [module 1](01_meal_processus.md).

**Les contrôles de cohérence sont les mêmes que partout ailleurs.** Les quatre règles R1 à R4 sont identiques à celles du formulaire XLSForm, du classeur Excel et des requêtes SQL. La règle R4 remonte vingt-neuf lignes, ce qui est normal : un enseignant absent une partie de la semaine n'est pas une anomalie, seulement un fait à suivre. C'est un rappel du principe des faux positifs du [module 4](04_excel_data_center.md) — **une règle produit des candidats, pas des verdicts**.

Le cœur du script, réduit à l'essentiel :

```python
import pandas as pd

feuilles = pd.read_excel("export.xlsx", sheet_name=None)
principale = feuilles["pa_presence_hebdo"]
repetition = feuilles["classe"]

# _index existe dans les DEUX tables : on isole la cle parente
parent = principale.rename(columns={"_index": "_cle_parent"})
parent["_parent_trouve"] = True

plat = repetition.merge(parent, left_on="_parent_index",
                        right_on="_cle_parent", how="left")

orphelines = plat[plat["_parent_trouve"].isna()]
print(f"{len(orphelines)} ligne(s) sans soumission parente")
```

---

## 8. Automatiser publication et récupération

Kobo et Ona exposent tous deux une API REST. Le principe est identique : un jeton d'authentification dans l'en-tête, puis des appels sur les points d'accès de l'API.

```python
import requests

TOKEN = "votre_jeton_api"
entetes = {"Authorization": f"Token {TOKEN}"}

# Lister les projets (KoboToolbox)
r = requests.get("https://kf.kobotoolbox.org/api/v2/assets.json", headers=entetes)
for actif in r.json()["results"]:
    print(actif["uid"], actif["name"])

# Récupérer les soumissions d'un formulaire
uid = "aXXXXXXXXXXXXXXXXX"
r = requests.get(f"https://kf.kobotoolbox.org/api/v2/assets/{uid}/data.json",
                 headers=entetes)
donnees = pd.json_normalize(r.json()["results"])
```

Sur Ona, la logique est la même avec `https://api.ona.io/api/v1/data/<form_id>`. Sur ODK Central, la bibliothèque **pyodk** encapsule tout cela proprement.

> Cette section est du **code de référence** : elle n'a pas pu être exécutée ici, faute d'identifiants sur une instance réelle. Le reste du module l'a été.

Ce que l'automatisation apporte concrètement : la récupération quotidienne des soumissions sans intervention humaine, l'exécution automatique des contrôles de cohérence sur les nouvelles données, l'envoi d'une alerte lorsqu'une école n'a pas rapporté, et la mise à jour d'un tableau de bord. Autrement dit, **le suivi de complétude devient continu au lieu d'être mensuel** — et repérer une remontée manquante le jour même plutôt qu'en fin de mois change complètement les chances de récupérer la donnée juste.

---

## 9. La chaîne complète

Les scripts s'enchaînent en un flux mensuel.

```bash
# 1. Mettre à jour les listes de choix depuis le référentiel
python3 xlsform_builder.py

# 2. Auditer la conception
python3 xlsform_audit.py *.xlsx

# 3. Valider techniquement — bloque si un formulaire échoue
python3 xlsform_valider.py . || exit 1

# 4. (Publier via l'API)

# 5. Après collecte : aplatir, contrôler, produire
python3 aplatir_soumissions.py export_kobo.xlsx
```

Chaque étape échoue bruyamment plutôt que silencieusement, ce qui est exactement ce qu'on veut : mieux vaut un script qui refuse de continuer qu'un formulaire déployé avec une référence cassée.

---

## Angles d'entretien

**« Comment gérez-vous plusieurs formulaires de collecte qui évoluent ? »**

Je les traite comme du code plutôt que comme des documents. Concrètement, cela veut dire trois choses. D'abord, la source de vérité des listes de choix n'est pas dans les classeurs mais dans le référentiel — la base des écoles — et je régénère les feuilles `choices` depuis cette source, ce qui garantit que tous les formulaires portent exactement les mêmes codes et supprime les divergences. Ensuite, je valide systématiquement avant de déployer, avec pyxform en local : c'est le même moteur que celui qu'utilisent Kobo et Ona côté serveur, donc si la conversion passe chez moi, elle passera chez eux, et je ne perds jamais une journée de collecte à cause d'un formulaire cassé. Enfin, j'incrémente la version automatiquement à partir de la date, parce que l'oubli d'incrémentation est une erreur classique qui empêche les appareils de récupérer la nouvelle version — et c'est le genre de problème qu'on met trois semaines à diagnostiquer.

**« Qu'est-ce qu'un script d'audit apporte de plus que la validation ? »**

La validation vérifie que le formulaire est techniquement convertible ; l'audit vérifie qu'il est bien conçu. Ce sont deux choses différentes, et un formulaire peut parfaitement passer la première en échouant sur la seconde. Le contrôle auquel je tiens le plus est la résolution des références. Dans un XLSForm, une expression comme `relevant` renvoie à une variable définie ailleurs par la syntaxe dollar-accolades. Si cette variable a été renommée au fil des versions, le formulaire se convertit toujours, mais la condition devient systématiquement fausse et la question n'apparaît plus jamais à l'écran. On collecte alors pendant des semaines avec un champ entièrement vide, et on ne le découvre qu'au moment de l'analyse, quand la donnée est définitivement perdue. Une expression régulière qui extrait toutes les références et les confronte à la liste des variables réellement définies élimine cette catégorie entière de bugs silencieux, en deux secondes. Je vérifie de la même manière que chaque contrainte a bien son message d'explication — parce qu'un blocage sans message pousse l'enquêteur à saisir n'importe quoi pour avancer — et que les divisions sont protégées contre le zéro.

**« Vous récupérez un export contenant des groupes répétés. Que faites-vous ? »**

Je commence par vérifier que je comprends la structure, parce qu'un export avec répétition n'est pas un fichier plat : il y a une table principale avec une ligne par soumission, et une table séparée par répétition avec une ligne par occurrence, reliées par une clé parente. Je les rejoins, avec une précaution qui a son importance : les deux tables contiennent une colonne `_index`, donc une fusion naïve les rend indistinguables et casse ensuite la détection des lignes orphelines — je renomme la clé parente avant de joindre. Une fois la table aplatie, j'applique trois contrôles. Le premier, ce sont les règles de cohérence métier, les mêmes que celles que j'ai codées dans le formulaire. Le deuxième, c'est la vérification des totaux : le formulaire calcule des sommes au moment de la saisie, et je les recalcule depuis les lignes détaillées ; un écart signale soit une modification après soumission, soit une erreur dans l'expression de calcul. Le troisième, c'est la durée de saisie, que j'obtiens en soustrayant les métadonnées de début et de fin. Sur un exemple récent, la médiane était de quinze minutes et deux soumissions avaient été bouclées en deux minutes : ce n'est pas une preuve de fraude, mais c'est un signal que je vérifie avant d'intégrer les données. Ces métadonnées sont fournies gratuitement par l'outil de collecte, et c'est dommage de ne pas s'en servir.

---

*Modules liés : [XLSForm sur Kobo et Ona](03_xlsform_kobo_et_ona.md) · [Excel et le Data Center](04_excel_data_center.md) · [SQL pour l'analyse](07_sql_analyse_pmel.md) · [MEAL](01_meal_processus.md)*
