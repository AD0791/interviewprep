# Analyse, visualisation et reporting

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Script livré : `exercices/rapport_mensuel.py`, qui produit les graphiques et le classeur de `exercices/sortie_rapport/`. Tous les chiffres de ce module sortent de la base `exercices/acted_bdd.db`.*

*Les fondations statistiques — moyennes pondérées, taux et ratios, dispersion, échantillonnage, pièges d'interprétation — sont traitées dans [Statistiques pour le PMEL](../assitant_pmel/02_statistiques_pmel.md), et la théorie des indicateurs dans [Indicateurs et indices](../assitant_pmel/05_indicateurs_et_indices.md). Le traitement dans Excel est couvert par [Excel appliqué au Data Center](../assitant_pmel/04_excel_data_center.md). Ce module porte sur la chaîne qui va de la base au livrable.*

---

## Ce que le TDR demande

« Extraire des requêtes, des chiffres et des rapports de la base de données ; générer des visualisations de données telles que des diagrammes, des graphiques, des tableaux à inclure dans des outils de communication, des rapports, des évaluations et tout autre document selon les besoins ; en collaboration avec le responsable MEAL, fournir une analyse des données des activités des projets et des données d'évaluation. »

Le mot important est **extraire**. Le rapport ne se fabrique pas à côté de la base, il se fabrique **depuis** la base. C'est toute la différence entre un chiffre qu'on peut refaire et un chiffre qu'on doit croire.

---

## 1. Le problème : deux chiffres pour la même chose

Voici la scène qui se répète dans tous les bureaux terrain. La réunion de coordination commence. Le chargé de programme annonce 1 428 ménages assistés. Le responsable MEAL en compte 600. Le rapport bailleur envoyé la semaine dernière disait 587.

Personne ne ment. Les trois chiffres viennent de trois exports faits à trois dates, retravaillés dans trois classeurs, avec trois définitions implicites de ce qu'est un ménage assisté — l'un compte les lignes d'assistance, l'autre les ménages distincts, le troisième les ménages ayant reçu du cash. La réunion passe quarante minutes à réconcilier des chiffres au lieu de décider quoi que ce soit.

La cause n'est pas l'inattention. C'est que **le chiffre est fabriqué à la main, en dehors de la base**, et qu'une fabrication manuelle n'est jamais reproductible. La solution tient en une phrase : chaque indicateur du rapport correspond à **une requête nommée, écrite une fois, stockée dans le projet, et exécutée à chaque production**. Si deux personnes obtiennent deux chiffres, c'est qu'elles ont utilisé deux requêtes, et on peut les comparer ligne à ligne.

C'est ce que fait `exercices/rapport_mensuel.py` : six requêtes nommées, six tableaux, trois graphiques, un classeur. Aucun copier-coller.

---

## 2. De la question à la requête

Avant d'écrire du SQL, il faut fixer la définition. C'est un travail de dix minutes qui évite des semaines de confusion, et il produit une **fiche d'indicateur** dont le module [Indicateurs et indices](../assitant_pmel/05_indicateurs_et_indices.md) donne le format complet. Trois points suffisent ici.

Le **numérateur** doit être défini sans ambiguïté. « Ménages assistés » veut-il dire les ménages ayant reçu au moins une assistance, ou le nombre d'assistances distribuées ? Ce sont deux chiffres différents — sur notre base, 600 ménages distincts pour 1 428 lignes d'assistance — et c'est exactement l'origine du désaccord de la section 1.

Le **dénominateur** doit être choisi et affiché. Un taux de couverture rapporté aux ménages ciblés ne dit pas la même chose qu'un taux rapporté aux ménages enregistrés, ni qu'un taux rapporté à la population totale de la commune. Le dénominateur est un choix politique déguisé en choix technique, et il doit figurer dans le rapport.

La **période** et la **désagrégation** ferment la définition. Un indicateur bailleur se lit presque toujours désagrégé par sexe, et de plus en plus par âge et par situation de handicap.

Voici l'indicateur de couverture, écrit une fois pour toutes.

```sql
SELECT d.nom_departement AS departement,
       COUNT(DISTINCT CASE WHEN m.statut_selection = 'Selectionne'
                           THEN m.id_menage END) AS cibles,
       COUNT(DISTINCT a.id_menage)               AS atteints
FROM menages m
JOIN sites        s ON s.code_site      = m.code_site
JOIN communes     c ON c.id_commune     = s.id_commune
JOIN departements d ON d.id_departement = c.id_departement
LEFT JOIN assistances a ON a.id_menage  = m.id_menage
GROUP BY 1
ORDER BY cibles DESC;
```

| departement | cibles | atteints | taux |
|---|---|---|---|
| Artibonite | 267 | 266 | 99,6 % |
| Ouest | 167 | 167 | 100,0 % |
| Centre | 86 | 86 | 100,0 % |
| Nord | 81 | 81 | 100,0 % |

Deux détails techniques portent toute la fiabilité de ce tableau. Le `COUNT(DISTINCT a.id_menage)` compte les **ménages** et non les lignes d'assistance ; sans le `DISTINCT`, on compterait les 1 428 lignes d'assistance et le taux dépasserait 200 %. Et le `LEFT JOIN` conserve les ménages ciblés qui n'ont rien reçu ; avec un `INNER JOIN`, ils disparaîtraient et les deux colonnes seraient toujours égales — le rapport afficherait 100 % partout et serait faux.

---

## 3. Choisir la bonne représentation

La question à se poser n'est jamais « quel graphique est joli » mais **« qu'est-ce que le lecteur doit voir en trois secondes »**. Chaque forme répond à une intention.

Pour **comparer des catégories**, un graphique en barres, horizontales si les libellés sont longs, triées par valeur sauf si un ordre naturel existe. C'est la forme la plus lisible qui existe et on l'utilise dans huit cas sur dix.

Pour montrer une **évolution dans le temps**, une courbe, avec l'axe des temps régulier. Une courbe sur des catégories non ordonnées est une faute : elle suggère une continuité qui n'existe pas.

Pour une **composition**, des barres empilées plutôt qu'un camembert. Le camembert n'est acceptable que pour deux ou trois parts, parce que l'œil compare mal des angles. Au-delà, il est illisible, et le camembert en trois dimensions ajoute une distorsion de perspective qui fausse la lecture.

Pour une **distribution**, un histogramme ou une boîte à moustaches, qui montrent l'étalement que la moyenne cache.

Pour une **relation entre deux variables**, un nuage de points.

Et souvent, pour **un seul chiffre**, une phrase. « Sept pour cent des ménages déclarent avoir reçu moins que le montant enregistré » se lit mieux que n'importe quel graphique.

### Les règles d'honnêteté

Elles sont peu nombreuses et un jury peut les tester.

L'axe des ordonnées d'un graphique en barres **part de zéro**, sans exception. Tronquer l'axe multiplie visuellement un écart de deux points jusqu'à le faire paraître énorme. Sur une courbe, la troncature est parfois acceptable, à condition de la signaler.

Les **effectifs accompagnent les pourcentages**. « 60 % des ménages » n'a pas le même poids selon que la base est de 500 ou de 5 ménages. Le script livré affiche systématiquement le nombre et le pourcentage l'un sous l'autre, et rappelle l'effectif total dans le titre.

Les **catégories ordonnées gardent leur ordre**. Sur le score de consommation alimentaire, on affiche Pauvre, Limite, Acceptable dans cet ordre, jamais trié par fréquence, parce que l'ordre porte du sens.

La **couleur signifie quelque chose**. Une couleur d'accent pour ce qui compte, du gris pour le contexte, du rouge réservé à l'alerte. Un graphique arc-en-ciel ne dit rien de plus qu'un graphique sobre, il fatigue simplement le lecteur.

Enfin, un graphique porte **un titre qui énonce le constat**, pas l'objet. « Neuf pour cent des ménages enquêtés sont en consommation alimentaire pauvre » vaut mieux que « Répartition FCS ».

---

## 4. Le rapport mensuel, produit depuis la base

Voici les cinq blocs du rapport que produit le script, avec les chiffres réels.

### 4.1 La couverture

Le tableau de la section 2, accompagné d'un graphique en barres horizontales où les ménages ciblés apparaissent en gris et les ménages atteints en couleur d'accent, avec le taux inscrit en bout de barre. La lecture est immédiate : la couverture est quasi complète partout, et l'unique ménage manquant de l'Artibonite est identifiable en une requête.

### 4.2 La sécurité alimentaire

```sql
SELECT CASE WHEN score_fcs <= 21 THEN 'Pauvre'
            WHEN score_fcs <= 35 THEN 'Limite'
            ELSE 'Acceptable' END AS classe,
       COUNT(*) AS menages
FROM pdm_reponses
GROUP BY 1;
```

| Classe | Ménages | Part |
|---|---|---|
| Pauvre | 56 | 9,9 % |
| Limite | 186 | 32,8 % |
| Acceptable | 325 | 57,3 % |

Le graphique correspondant respecte l'ordre de sévérité et code la classe « Pauvre » en rouge. La phrase de commentaire qui l'accompagne est celle qui compte : un ménage sur dix reste en consommation alimentaire pauvre après le transfert, ce qui pose la question du montant du transfert ou de la durée de l'assistance, et c'est le genre de constat qui alimente une décision programmatique.

### 4.3 La satisfaction et la redevabilité

| Satisfaction | Ménages |
|---|---|
| 1 — Très insatisfait | 18 |
| 2 — Insatisfait | 48 |
| 3 — Neutre | 132 |
| 4 — Satisfait | 262 |
| 5 — Très satisfait | 107 |

Deux pièges méritent d'être signalés. D'abord, calculer une moyenne sur cette échelle est discutable : une échelle de Likert est **ordinale**, l'écart entre 1 et 2 n'est pas nécessairement le même qu'entre 4 et 5, et la pratique la plus honnête consiste à publier la répartition, ou au minimum la part des satisfaits — ici 369 ménages sur 567, soit 65,1 %. Ensuite, une enquête de satisfaction menée par l'organisation qui distribue souffre d'un **biais de désirabilité** : les gens disent du bien à celui qui donne. Le mentionner dans le rapport n'affaiblit pas l'analyse, cela la crédibilise.

### 4.4 L'écart entre le déclaré et l'enregistré

| Enquêtes | Écarts | Part | Montant manquant |
|---|---|---|---|
| 567 | 39 | 6,9 % | 95 500 HTG |

C'est le chiffre le plus utile du rapport, parce qu'il déclenche une action plutôt qu'il ne décrit. La formulation doit rester prudente : trente-neuf ménages déclarent avoir reçu moins que le montant enregistré, pour un total de 95 500 gourdes, ce qui peut relever de frais prélevés par l'opérateur de paiement, d'une confusion du répondant ou d'un problème réel — et une vérification ciblée sur ces trente-neuf cas est recommandée. On expose l'écart, on liste les hypothèses, on propose l'action. On n'accuse personne dans un rapport.

### 4.5 Les plaintes

| Catégorie | Reçues | Clôturées | Taux de traitement |
|---|---|---|---|
| Ciblage | 86 | 61 | 70,9 % |
| Délai | 47 | 27 | 57,4 % |
| Montant | 44 | 29 | 65,9 % |
| Information | 36 | 20 | 55,6 % |
| Comportement staff | 16 | 10 | 62,5 % |
| Autre | 11 | 5 | 45,5 % |

Le graphique empile les clôturées et les non clôturées, ce qui rend visible d'un coup d'œil le reste à traiter. La lecture qui intéresse le responsable MEAL : les plaintes de ciblage dominent en volume, ce qui est normal et sain — cela signifie que le mécanisme est connu — mais le taux de traitement des plaintes d'information, à 55,6 %, est le plus bas et mérite qu'on regarde pourquoi.

Les 17 plaintes marquées sensibles n'apparaissent **dans aucun de ces tableaux**. Elles suivent le circuit protégé décrit dans [Sécurité et protection des données](04_securite_protection_donnees.md), et le rapport se contente de mentionner qu'un circuit distinct existe et fonctionne.

### 4.6 La désagrégation

```sql
SELECT d.nom_departement AS departement, m.sexe_chef AS sexe,
       COUNT(DISTINCT a.id_menage) AS menages_assistes,
       SUM(m.taille_menage)        AS personnes_couvertes
FROM assistances a
JOIN menages      m ON m.id_menage      = a.id_menage
JOIN sites        s ON s.code_site      = m.code_site
JOIN communes     c ON c.id_commune     = s.id_commune
JOIN departements d ON d.id_departement = c.id_departement
GROUP BY 1, 2;
```

| departement | sexe | menages_assistes | personnes_couvertes |
|---|---|---|---|
| Artibonite | F | 193 | 2 953 |
| Artibonite | M | 73 | 1 369 |
| Centre | F | 67 | 1 165 |
| Centre | M | 19 | 363 |
| Nord | F | 53 | 890 |
| Nord | M | 28 | 560 |
| Ouest | F | 115 | 1 880 |
| Ouest | M | 52 | 966 |

Presque tous les cadres logiques exigent cette désagrégation, et il faut savoir énoncer sa limite : ce tableau compte les ménages **dirigés par une femme**, ce qui n'est pas la même chose que le nombre de femmes bénéficiaires. Pour ce dernier, il faut passer par la table `individus`. Confondre les deux est l'erreur la plus fréquente des rapports de distribution, et la signaler en entretien montre qu'on lit les indicateurs plutôt qu'on ne les produit.

---

## 5. Industrialiser la production

### 5.1 Les vues de reporting

Une vue est une requête enregistrée sous un nom. Elle sert deux objectifs à la fois : elle fige la définition de l'indicateur, et elle permet de donner un accès en lecture à quelqu'un sans lui ouvrir les tables nominatives.

```sql
CREATE VIEW v_couverture_par_departement AS
SELECT d.nom_departement,
       COUNT(DISTINCT CASE WHEN m.statut_selection = 'Selectionne'
                           THEN m.id_menage END) AS cibles,
       COUNT(DISTINCT a.id_menage)               AS atteints
FROM menages m
JOIN sites        s ON s.code_site      = m.code_site
JOIN communes     c ON c.id_commune     = s.id_commune
JOIN departements d ON d.id_departement = c.id_departement
LEFT JOIN assistances a ON a.id_menage  = m.id_menage
GROUP BY 1;
```

Le jour où la définition de « ciblé » change, on modifie la vue et **tous** les rapports suivent. Sans vue, il faut retrouver la formule dans quinze classeurs.

Quand la requête devient lourde et que le tableau de bord est consulté cent fois par jour sur des données qui bougent une fois par semaine, on passe à une **vue matérialisée** en PostgreSQL, ou à une table de synthèse rafraîchie par tâche planifiée ailleurs. Le principe reste celui du module [Modélisation](02_modelisation_et_conception.md) : la table de synthèse est dérivée, jamais saisie.

### 5.2 Le script plutôt que le clic

`exercices/rapport_mensuel.py` produit en une commande les trois graphiques et le classeur Excel à six feuilles, une par requête. L'intérêt n'est pas le gain de temps du premier mois, il est ailleurs.

La production est **reproductible** : le même script sur la même base donne exactement le même rapport, ce qui rend la discussion possible quand un chiffre surprend. Elle est **traçable** : le script est un fichier versionné, donc on sait quelle définition a servi en mars et quelle définition a servi en juin. Elle est **transmissible** : un collègue peut produire le rapport en ton absence, ce qui est précisément ce qu'on attend d'une procédure opérationnelle.

Et elle laisse une porte ouverte à ceux qui veulent creuser : le classeur Excel produit contient les tableaux sources, donc le chargé de programme peut faire son propre tableau croisé sans redemander un export.

### 5.3 Excel, Power BI, ou script

Le choix se fait sur trois critères, et il vaut mieux le formuler ainsi qu'affirmer qu'un outil est meilleur.

**Excel** reste le bon outil pour l'exploration rapide et pour tout ce que le destinataire doit pouvoir manipuler lui-même. Un tableau croisé dynamique branché sur un export propre répond à quatre-vingts pour cent des demandes internes. Sa limite est la reproductibilité : dès qu'un chiffre doit être refait chaque mois à l'identique, Excel devient le problème plutôt que la solution.

**Power BI** convient au tableau de bord consulté par plusieurs personnes, avec des filtres interactifs, connecté directement à la base. Sa limite est la dépendance à une licence et à une connexion, ce qui n'est pas neutre dans un bureau terrain haïtien.

Le **script Python** convient à la production régulière, versionnée, automatisable. Sa limite est qu'il faut savoir le lire pour le modifier, donc il doit être documenté et simple.

En pratique on combine : la base est la source unique, le script produit le rapport officiel, le classeur exporté permet l'exploration, et le tableau de bord Power BI existe si l'organisation en dispose déjà.

---

## 6. Écrire l'analyse

Produire les chiffres est la moitié du travail. Le TDR demande « une analyse des données », et l'analyse est ce qui transforme un tableau en décision.

La structure qui fonctionne pour chaque bloc du rapport tient en quatre temps. **Le constat**, une phrase avec le chiffre et son effectif. **La comparaison**, qui donne l'échelle — par rapport au mois dernier, à la cible, à l'autre département. **L'hypothèse**, formulée comme une hypothèse et non comme une conclusion. **La recommandation**, adressée à quelqu'un de précis avec une action précise.

Appliqué à l'écart de montants, cela donne : « Trente-neuf ménages sur 567 enquêtés, soit 6,9 %, déclarent avoir reçu moins que le montant enregistré, pour un écart cumulé de 95 500 gourdes. Cette proportion était de 4 % lors du PDM précédent. Trois explications sont possibles : des frais prélevés par l'opérateur de paiement, une confusion du répondant sur le montant, ou un problème dans la chaîne de distribution. Il est recommandé au chargé de distribution de vérifier les trente-neuf cas listés en annexe avant le prochain cycle, en priorité les douze cas où l'écart dépasse 2 000 gourdes. »

Trois interdits terminent ce module. **Ne jamais présenter un pourcentage sans son effectif.** **Ne jamais conclure à une causalité à partir d'une corrélation** : les ménages ayant reçu un kit hygiène ont un meilleur score alimentaire, mais c'est peut-être parce qu'ils ont aussi reçu du cash. Et **ne jamais taire une limite** : la taille d'échantillon, le biais de désirabilité, les données manquantes se disent en une phrase, et cette phrase augmente la crédibilité du reste au lieu de la diminuer.

---

## 7. Sept exercices

Exécute `rapport_mensuel.py` sur la base, ouvre les trois graphiques et critique-les : que verrait un lecteur en trois secondes, et que manque-t-il ?

Ajoute une septième requête qui calcule le délai médian de réception par département, et le graphique correspondant.

Reprends le graphique de satisfaction et propose deux représentations différentes, puis justifie laquelle tu retiendrais pour un rapport bailleur et laquelle pour une réunion interne.

Écris la vue `v_couverture_par_departement`, accorde un droit de lecture dessus à un compte fictif de bailleur, et vérifie qu'il ne peut pas lire la table `menages`.

Produis le tableau désagrégé par sexe **au niveau des individus** plutôt que des ménages, et explique en deux phrases la différence avec le tableau de la section 4.6.

Rédige le commentaire d'analyse en quatre temps pour le bloc « sécurité alimentaire », en respectant la structure constat, comparaison, hypothèse, recommandation.

Enfin, construis la maquette d'une page de tableau de bord mensuel : quels cinq indicateurs, dans quel ordre, avec quelle forme visuelle, et pourquoi.

---

## Angles d'entretien

**« Comment produisez-vous le rapport mensuel d'un projet ? »**

Je pars d'un principe : le rapport se fabrique depuis la base, jamais à côté. Concrètement, chaque indicateur du rapport correspond à une requête nommée, écrite une fois, stockée dans le dossier du projet et exécutée à chaque production. C'est ce qui règle le problème que je rencontre partout, où trois personnes annoncent trois chiffres différents pour la même chose parce que chacune a fait son propre export à sa propre date avec sa propre définition. Avec des requêtes nommées, si deux chiffres divergent, on compare les deux requêtes et on voit immédiatement laquelle compte les lignes d'assistance et laquelle compte les ménages distincts. Avant d'écrire le SQL, je fige la définition avec le responsable MEAL : le numérateur, le dénominateur, la période et la désagrégation. Le dénominateur en particulier est un choix qui doit apparaître dans le rapport, parce qu'un taux de couverture rapporté aux ménages ciblés ne raconte pas la même histoire que le même taux rapporté à la population de la commune. Ensuite j'automatise : un script produit les tableaux, les graphiques et un classeur Excel qui contient les données sources, pour que le chargé de programme puisse creuser sans me redemander un export. L'automatisation ne me fait pas gagner du temps le premier mois, elle me le fait gagner à partir du deuxième, et surtout elle rend la production reproductible, traçable et transmissible — un collègue peut sortir le rapport en mon absence, ce qui est exactement ce qu'on attend d'une procédure opérationnelle. Enfin je fige les définitions dans des vues en base, de sorte que le jour où la définition change, tous les rapports suivent au lieu qu'il faille retrouver la formule dans quinze classeurs.

**« Comment choisissez-vous un type de graphique ? »**

Je pars de ce que le lecteur doit comprendre en trois secondes, pas de ce qui est joli. Pour comparer des catégories, des barres, horizontales si les libellés sont longs, et c'est le cas dans huit situations sur dix. Pour une évolution dans le temps, une courbe, et jamais une courbe sur des catégories non ordonnées, parce que cela suggère une continuité qui n'existe pas. Pour une composition, des barres empilées plutôt qu'un camembert, que je réserve à deux ou trois parts au maximum puisque l'œil compare très mal des angles ; et jamais de camembert en trois dimensions, dont la perspective fausse les proportions. Pour une distribution, un histogramme, parce que la moyenne cache l'étalement. Et souvent, pour un seul chiffre, une phrase vaut mieux qu'un graphique. À cela j'ajoute quelques règles d'honnêteté que je considère comme non négociables : l'axe des barres part de zéro, sinon on exagère visuellement un écart de deux points ; le pourcentage est toujours accompagné de son effectif, parce que soixante pour cent de cinq ménages n'est pas soixante pour cent de cinq cents ; les catégories ordonnées gardent leur ordre naturel, donc je n'affiche jamais l'échelle de consommation alimentaire triée par fréquence ; et la couleur signifie quelque chose, une couleur d'accent pour l'essentiel, du gris pour le contexte, du rouge réservé à l'alerte. Enfin, je titre mes graphiques par le constat plutôt que par l'objet : « un ménage sur dix reste en consommation alimentaire pauvre » plutôt que « répartition du FCS ».

**« Le chargé de programme veut afficher un chiffre que vos données ne soutiennent pas. Que faites-vous ? »**

Je commence par comprendre ce qu'il veut dire, parce que souvent le désaccord porte sur la définition et non sur le chiffre. S'il annonce mille cinq cents ménages assistés et que j'en compte mille quatre cent quarante, il compte peut-être les lignes de distribution là où je compte les ménages distincts, et dans ce cas nous avons tous les deux raison sur des choses différentes : je propose de nommer les deux indicateurs séparément dans le rapport, ce qui clôt le débat. Si le désaccord persiste après clarification, je montre la requête. Pas le résultat, la requête : elle est lisible, elle dit exactement ce qui est compté, et elle déplace la discussion du terrain de l'autorité vers celui de la définition. Si finalement le chiffre demandé n'est pas soutenu par les données, je le dis clairement, une fois, sans dramatiser, et je propose ce que les données permettent d'affirmer honnêtement — il y a presque toujours une formulation exacte qui sert le même objectif de communication. Si la demande est maintenue malgré tout, je remonte au responsable MEAL, qui est mon superviseur direct et le garant de la qualité des données, et je documente par écrit ce que j'ai transmis et pourquoi. Ce n'est pas une question de rapport de force : un chiffre faux dans un rapport bailleur se retourne toujours contre l'organisation lors d'un audit, et mon rôle est précisément d'éviter cela. Ce que je ne fais jamais, c'est produire le chiffre en silence en me disant que ce n'est pas mon problème.

---

*Suite du parcours : [Kobo, ciblage et PDM](05_kobo_ciblage_et_pdm.md) · [Gestion de l'information](06_gestion_information_archivage.md) · [Examen blanc corrigé](08_examen_blanc_corrige.md) · [Fiche de révision](00_fiche_revision_examen.md)*
