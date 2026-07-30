# Kobo, ciblage des bénéficiaires et enquêtes PDM

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Formulaires livrés : `exercices/xlsform_ciblage_menage.xlsx` et `exercices/xlsform_pdm_cash.xlsx`, tous deux compilés sans avertissement par pyxform, le moteur qu'utilise KoboToolbox. Chaîne d'import : `exercices/importer_kobo.py`. Les sorties reproduites ici sont réelles.*

*Les bases d'XLSForm — anatomie du classeur, types de questions, `relevant`, `constraint`, `calculation`, listes en cascade, multilingue — sont traitées dans [XLSForm de zéro](../assitant_pmel/03_xlsform_kobo_et_ona.md) et l'automatisation en Python dans [XLSForm avec Python](../assitant_pmel/08_xlsform_avec_python.md). Ce module ne les répète pas : il traite ce que le TDR ACTED demande en plus, c'est-à-dire les formules avancées de ciblage, le codage des enquêtes PDM et endline, la formation des enquêteurs et la chaîne qui va du serveur Kobo jusqu'à la base.*

---

## Ce que le TDR demande exactement

Deux paragraphes du TDR concernent directement ce module. Le premier porte sur le ciblage : « soutenir au codage des questionnaires de ciblage de bénéficiaires en XLS pour la plateforme de collecte KoboToolbox, **y compris l'inclusion de formules avancées sur les indicateurs à mesurer** et pour le choix final dans le processus de sélection de bénéficiaires ». Le second porte sur le suivi : « soutenir au codage des questionnaires de PDM/Endline en XLS ». S'y ajoutent la formation des enquêteurs, l'appui technique pendant les enquêtes, la vérification de la qualité et le stockage.

Le mot qui compte est **formules avancées**. On ne te demande pas de savoir taper une question dans Kobo — n'importe qui l'apprend en une heure. On te demande de savoir coder dans le formulaire un score de vulnérabilité, un score de consommation alimentaire, un contrôle de cohérence qui alerte l'enquêteur avant l'envoi. C'est exactement ce que contiennent les deux classeurs livrés avec ce module.

---

## 1. Le problème : le ciblage sur papier

Voici comment se passe un ciblage sans formulaire intelligent, et pourquoi il finit mal.

L'équipe part avec des fiches papier. Chaque enquêteur note la composition du ménage, coche les critères de vulnérabilité et rapporte les fiches le soir. Deux semaines plus tard, quelqu'un saisit 1 200 fiches dans Excel, applique une grille de pondération dans une colonne de formules, trie par score décroissant, et coupe à la ligne 600.

Quatre choses se sont mal passées, et elles se produisent à chaque fois.

La grille de pondération n'a été appliquée qu'**après** le retour du terrain. Personne n'a pu vérifier sur place qu'un ménage manifestement très vulnérable obtenait bien un score élevé ; les incohérences se découvrent trois semaines trop tard, quand les équipes sont reparties.

Les **erreurs de saisie** ne sont plus rattrapables. Une fiche indiquant huit personnes dont douze enfants de moins de cinq ans est entrée telle quelle dans Excel ; sur le terrain, la question aurait été reposée en dix secondes.

La **formule d'Excel** vit dans un fichier que trois personnes ont modifié. Au moment de justifier le ciblage devant le bailleur, personne ne peut affirmer avec certitude quelle version de la pondération a servi.

Enfin, le **ménage ne sait rien**. Il a répondu à des questions et il attend. Personne n'a pu lui dire, sur place, que sa situation le plaçait a priori dans la liste ou pas, ni qu'un comité tranchera.

Un formulaire XLSForm bien codé règle les quatre. Le score se calcule pendant l'entretien, les incohérences déclenchent une alerte immédiate, la pondération est versionnée dans le formulaire déployé, et l'enquêteur peut annoncer la proposition automatique en précisant que la décision revient au comité.

---

## 2. Coder le score de vulnérabilité dans le formulaire

Voici le cœur du formulaire de ciblage livré. Le principe est de décomposer le score en points partiels nommés plutôt que de tout écrire dans une seule formule illisible.

| type | name | calculation |
|---|---|---|
| `calculate` | `pts_taille` | `min(${taille_menage}, 10) * 4` |
| `calculate` | `pts_enfants` | `${nb_enfants_moins5} * 7` |
| `calculate` | `pts_enceintes` | `${nb_femmes_enceintes} * 6` |
| `calculate` | `pts_handicap` | `${nb_handicap} * 8` |
| `calculate` | `pts_sexe` | `if(selected(${sexe_chef}, 'F'), 10, 0)` |
| `calculate` | `pts_deplacement` | `if(selected(${statut_deplacement}, 'deplace'), 15, if(selected(${statut_deplacement}, 'retourne'), 10, if(selected(${statut_deplacement}, 'hote'), 8, 0)))` |
| `calculate` | `score_vulnerabilite` | `min(100, ${pts_taille} + ${pts_enfants} + ${pts_enceintes} + ${pts_handicap} + ${pts_sexe} + ${pts_deplacement})` |

Trois décisions de conception se lisent dans ce tableau, et ce sont elles qu'un jury sondera.

**La décomposition en points nommés.** On pourrait écrire une seule formule de six lignes. On ne le fait pas, pour trois raisons : le débogage devient possible puisqu'on peut afficher chaque composante séparément, la relecture par le responsable MEAL devient praticable puisqu'il voit que le handicap pèse huit points et le déplacement quinze, et la modification devient sûre puisque changer une pondération touche une ligne au lieu d'en réécrire une longue.

**Le plafonnement.** `min(${taille_menage}, 10) * 4` empêche qu'un ménage de dix-huit personnes accapare le score à lui seul. Sans plafond, une seule variable écrase toutes les autres et le score cesse de mesurer la vulnérabilité pour mesurer la taille. Le `min(100, ...)` final borne le total, ce qui rend les scores comparables entre projets.

**L'imbrication des conditions.** XLSForm n'a pas de `switch` : on imbrique des `if`. La lisibilité impose d'ordonner du cas le plus lourd au cas le plus léger, et de terminer par la valeur par défaut. C'est un détail de style, mais c'est le genre de détail qu'un formateur remarque.

Le formulaire affiche ensuite le résultat et sa conséquence.

| type | name | label |
|---|---|---|
| `note` | `note_score` | `Score calcule : ${score_vulnerabilite} / 100` |
| `calculate` | `proposition_selection` | `if(${score_vulnerabilite} >= 44, 'Selectionne', if(${score_vulnerabilite} >= 36, 'En attente', 'Non selectionne'))` |
| `note` | `note_proposition` | `Proposition automatique : ${proposition_selection}. La decision finale appartient au comite de ciblage communautaire.` |

La dernière phrase n'est pas de la politesse. Elle est le garde-fou éthique du dispositif : **un algorithme ne sélectionne pas des bénéficiaires, il propose un classement qu'un comité communautaire valide ou corrige.** Le score ne voit pas la veuve dont la maison vient de brûler et qui a refusé de le mentionner. Savoir dire cela en entretien montre qu'on ne confond pas l'outil et la décision.

### Le contrôle de cohérence qui parle à l'enquêteur

```
type      : note
name      : alerte_coherence
label     : ATTENTION : la somme des categories vulnerables depasse la taille du menage.
            Verifiez avant d'envoyer.
relevant  : ${somme_categories} > ${taille_menage}
```

Cette note n'apparaît que si l'incohérence existe. Remarque la nuance de conception : c'est une **alerte** et non une contrainte bloquante. Une contrainte `constraint` empêcherait d'avancer, ce qui est le bon choix quand la valeur est nécessairement fausse — un âge de 200 ans — mais le mauvais choix ici, parce que le cas peut être réel dans des configurations familiales inhabituelles. On alerte, on fait vérifier, on laisse passer si l'enquêteur confirme.

La règle générale à formuler : **on bloque ce qui est impossible, on alerte sur ce qui est improbable.** Bloquer l'improbable pousse les enquêteurs à saisir n'importe quoi pour pouvoir avancer, ce qui dégrade la qualité au lieu de l'améliorer.

### Le consentement qui arrête le formulaire

```
type            : select_one oui_non
name            : consentement
label           : Acceptez-vous de repondre a ce questionnaire ?
required        : yes

type            : note
name            : note_refus
label           : Merci. L'entretien s'arrete ici.
relevant        : selected(${consentement}, 'non')
```

Tous les groupes suivants portent `relevant = selected(${consentement}, 'oui')`. Un refus fait donc disparaître l'intégralité du questionnaire, et aucune donnée personnelle n'est enregistrée. C'est la traduction technique du principe développé dans [Sécurité et protection des données](04_securite_protection_donnees.md), et c'est un excellent point à montrer parce qu'il prouve que la protection des données n'est pas une intention mais une implémentation.

---

## 3. Coder l'enquête post-distribution

Le formulaire PDM livré mesure quatre choses : la réception effective du transfert, la sécurité alimentaire par deux indices standards, la redevabilité, et l'intégrité du processus.

### 3.1 Le Food Consumption Score

Le FCS est l'indicateur de sécurité alimentaire le plus utilisé par le PAM. On demande, pour huit groupes alimentaires, combien de jours sur les sept derniers le ménage en a consommé, puis on pondère chaque groupe par sa valeur nutritionnelle.

| Groupe | Pondération |
|---|---|
| Céréales et tubercules | 2 |
| Légumineuses | 3 |
| Légumes et feuilles | 1 |
| Fruits | 1 |
| Viande, poisson, œufs | 4 |
| Lait et produits laitiers | 4 |
| Sucre | 0,5 |
| Huile et graisses | 0,5 |

La formule tient en une ligne de `calculation`, générée automatiquement par le script de construction.

```
${fcs_cereales} * 2 + ${fcs_legumineuses} * 3 + ${fcs_legumes} * 1 + ${fcs_fruits} * 1
+ ${fcs_proteines} * 4 + ${fcs_lait} * 4 + ${fcs_sucre} * 0.5 + ${fcs_huile} * 0.5
```

La classification suit les seuils standards, et le formulaire l'affiche immédiatement à l'enquêteur.

```
classe_fcs : if(${score_fcs} <= 21, 'Pauvre',
              if(${score_fcs} <= 35, 'Limite', 'Acceptable'))
```

Le point qui compte pour l'assistant base de données : **la pondération est dans le formulaire, pas dans un fichier Excel d'analyse.** Le score arrive déjà calculé dans la base, identique pour toutes les soumissions, sans risque qu'un analyste applique une grille différente d'un mois à l'autre. Sur les 567 enquêtes de la base d'exercice, la distribution est la suivante.

| Classe FCS | Ménages | Part |
|---|---|---|
| Acceptable | 325 | 57,3 % |
| Limite | 186 | 32,8 % |
| Pauvre | 56 | 9,9 % |

### 3.2 L'indice réduit des stratégies de survie

Le rCSI mesure ce que le ménage a dû faire pour manger malgré tout. Cinq stratégies, chacune pondérée par sa sévérité : consommer des aliments moins chers pèse 1, emprunter de la nourriture pèse 2, réduire les portions pèse 1, restreindre la consommation des adultes au profit des enfants pèse 3, réduire le nombre de repas pèse 1. Le score va de 0 à 56.

Les deux indices se lisent ensemble, et c'est la lecture croisée qui est intéressante. Un ménage peut afficher un FCS acceptable **parce qu'**il applique des stratégies de survie sévères : il mange, mais les adultes se privent. Un FCS acceptable avec un rCSI élevé décrit une situation fragile qu'un seul indicateur masquerait. Savoir raconter cela montre qu'on comprend les indicateurs et pas seulement les formules — la théorie complète est dans [Indicateurs et indices](../assitant_pmel/05_indicateurs_et_indices.md).

### 3.3 La question qui protège

```
type      : select_one oui_non
name      : a_paye
label     : Avez-vous du payer quoi que ce soit pour recevoir l'aide ?

type      : note
name      : note_alerte_paiement
label     : ALERTE : signalez immediatement au responsable MEAL a la fin de la journee.
            Ne discutez de ce cas avec personne d'autre.
relevant  : selected(${a_paye}, 'oui')
```

Cette question détecte les détournements et les demandes de contrepartie. Sa présence dans le formulaire n'est pas anodine : elle transforme l'enquête PDM en dispositif de contrôle interne. La note d'alerte donne à l'enquêteur une consigne claire, y compris l'instruction de ne pas en parler autour de lui, parce qu'une rumeur mal gérée met en danger la personne qui a répondu.

### 3.4 La durée d'entretien

```
duree_entretien_min :
  int((decimal-date-time(${end}) - decimal-date-time(${start})) * 1440)
```

Cette ligne est probablement le meilleur détecteur de fraude d'enquêteur qui existe, et elle ne coûte rien. Un entretien PDM complet demande vingt à quarante minutes. Une soumission de trois minutes signifie presque toujours que le formulaire a été rempli sans que les questions soient posées. Le calcul en minutes vient du fait que `decimal-date-time` renvoie un nombre de jours : on multiplie par 1 440 minutes.

Le contrôle qui l'accompagne se fait à l'import, et on verra plus bas qu'il remonte vingt soumissions suspectes sur 589.

---

## 4. Former les enquêteurs

Le TDR mentionne deux fois la formation. C'est une responsabilité réelle, et elle a une méthode.

La formation ne commence pas par le formulaire, elle commence par **le sens des questions**. Un enquêteur qui ne comprend pas ce que mesure le FCS traduira « légumineuses » de travers en créole et le score sera faux partout de la même manière — un biais systématique, bien plus grave qu'une erreur aléatoire. Une demi-journée sur le pourquoi vaut mieux que deux jours sur le comment.

Le deuxième temps est la **traduction validée collectivement**. Les formulaires livrés portent une colonne `label::Kreyol (ht)` à côté du français, mais une traduction écrite par une seule personne au bureau ne suffit pas : on la fait relire par les enquêteurs, parce que ce sont eux qui savent comment on dit réellement les choses à Gonaïves. Une question comprise différemment par deux enquêteurs produit deux variables différentes portant le même nom.

Le troisième temps est le **jeu de rôle**, par binômes, avec des cas préparés : le ménage qui n'a pas sa carte, celui qui répond à côté, celui qui répond ce qu'il croit qu'on veut entendre, celui qui refuse. C'est là qu'on apprend à ne pas suggérer la réponse.

Le quatrième est le **pilote réel** sur cinq à dix ménages hors zone d'enquête, suivi d'un débriefing immédiat. Le pilote révèle systématiquement des choses que la relecture au bureau ne montre pas : une question ambiguë, un saut de logique qui ne se déclenche pas, une liste de choix incomplète.

Le cinquième est la **supervision du premier jour**. Le superviseur accompagne, observe sans intervenir, et corrige le soir. Ne jamais corriger devant le ménage.

Enfin, le **contrôle qualité quotidien** : chaque soir, on télécharge les soumissions du jour et on regarde quatre indicateurs — la durée médiane d'entretien par enquêteur, le taux de valeurs manquantes par enquêteur, la dispersion géographique des points GPS, et le taux de refus. Un enquêteur dont la durée médiane est deux fois plus courte que celle de ses collègues n'est pas forcément malhonnête, mais il faut aller voir. Cette boucle quotidienne, appliquée dès le premier jour, change complètement la qualité d'une collecte.

---

## 5. La chaîne du serveur Kobo à la base

C'est ici que le poste d'assistant base de données se distingue d'un poste d'enquêteur senior. L'export Kobo n'est pas une base : c'est un fichier plat, avec des colonnes de métadonnées, des libellés non harmonisés, des soumissions dupliquées et des valeurs textuelles dans des colonnes numériques. Le transformer en données chargées, tracées et réconciliées est un travail à part entière.

Voici la sortie réelle de `exercices/importer_kobo.py` sur l'export brut de 589 lignes.

```
Lignes lues dans l'export         : 589
  rejetees (motif documente)      : 56
  doublons ecartes (meme cle)     : 18
  retenues apres deduplication    : 515
  effectivement inserees          : 515
  deja presentes (import rejoue)  : 0
Controle : lues - rejets - doublons - retenues = 0 (doit valoir 0)

Motifs de rejet par frequence :
    28  satisfaction hors echelle 1-5 ou non numerique
    20  duree d entretien inferieure a 8 minutes
     8  score_fcs absent ou hors bornes 0-112
     5  montant_recu_htg non numerique

Harmonisation des libelles de commune : 19 graphies distinctes ramenees a 10 communes.
```

Six propriétés de cette chaîne méritent d'être expliquées, parce que chacune répond à une question qu'on te posera.

**La réconciliation qui boucle.** La dernière ligne du rapport vérifie que les lignes lues se répartissent exactement entre rejets, doublons et retenues, sans perte. Un import qui ne boucle pas est un import qui perd des données sans le dire. C'est la première chose que je vérifie et la première chose que montre le rapport.

**Le rejet documenté plutôt que la suppression silencieuse.** Les 56 lignes rejetées ne disparaissent pas : elles partent dans la table `rejets` avec leur contenu intégral en JSON et le motif exact. On peut donc les rouvrir, appeler l'enquêteur, corriger et réimporter. Sans cette table, la donnée est perdue et personne ne sait qu'elle a existé.

**L'harmonisation explicite plutôt que floue.** Les dix-neuf graphies de commune — « Gonaives », « GONAIVES », « Gonaïves », « Gonaive », « gonaives » — sont ramenées à dix communes par une table de correspondance écrite dans le code, versionnée, relisible. Un rapprochement flou automatique serait plus court à écrire et impossible à auditer. La règle héritée du module qualité s'applique : **le flou produit des candidats, jamais des décisions.**

**La déduplication par règle de conservation.** Dix-huit soumissions portent le même couple ménage-date, parce que l'enquêteur a renvoyé le formulaire après une coupure réseau. On ne garde pas la première arrivée au hasard : on garde **la plus complète**, mesurée par le nombre de champs renseignés. La règle est écrite, donc défendable.

**L'idempotence.** Relancer exactement le même import ne crée aucune ligne supplémentaire : le rapport affiche alors 0 insertion et 515 déjà présentes. Cela tient à deux choses, la contrainte `UNIQUE (id_menage, date_enquete)` dans le schéma et la clause `ON CONFLICT ... DO NOTHING` dans la requête. C'est une propriété essentielle en bureau terrain, où l'on relance un import parce qu'on ne sait plus s'il a fonctionné.

**La séparation entre le brut et le propre.** Le CSV d'origine n'est jamais modifié. Il est archivé tel quel, daté, et tout le nettoyage se fait dans le script. On peut donc rejouer toute la chaîne après correction d'une règle, ce qui serait impossible si l'on avait « nettoyé le fichier » à la main.

### Le contrôle qui suit l'import

Charger n'est pas terminer. Une fois les données en base, on rapproche ce que le ménage déclare de ce que l'équipe distribution a enregistré.

```sql
SELECT COUNT(*) AS enquetes,
       SUM(CASE WHEN p.montant_recu_htg <> a.montant_htg THEN 1 ELSE 0 END) AS ecarts,
       ROUND(100.0 * SUM(CASE WHEN p.montant_recu_htg <> a.montant_htg THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS pct,
       CAST(SUM(a.montant_htg - p.montant_recu_htg) AS INTEGER) AS manquant_htg
FROM pdm_reponses p
JOIN assistances a ON a.id_menage = p.id_menage AND a.id_activite = 3;
```

| enquetes | ecarts | pct | manquant_htg |
|---|---|---|---|
| 567 | 39 | 6,9 | 95 500 |

Trente-neuf ménages sur 567, soit près de sept pour cent, déclarent avoir reçu moins que le montant enregistré, pour un total de 95 500 gourdes. Ce chiffre n'est pas une preuve de détournement : il peut refléter des frais prélevés par l'opérateur de paiement, une confusion du répondant, ou une erreur de saisie. Mais c'est **exactement le genre de chiffre qui déclenche une investigation**, et le produire spontanément après chaque PDM est ce qu'on attend d'un assistant base de données. Le module [Analyse et visualisation](07_analyse_visualisation_reporting.md) montre comment l'inscrire dans le rapport.

---

## 6. Sept exercices

Ouvre `exercices/xlsform_ciblage_menage.xlsx`, modifie la pondération du handicap de huit à douze points, recompile avec pyxform et vérifie qu'aucune erreur n'apparaît.

Ajoute au formulaire de ciblage un groupe répété qui liste les membres du ménage, avec calcul automatique de la taille à partir du nombre de répétitions, puis explique pourquoi ce calcul est plus fiable qu'une question directe.

Ajoute au formulaire PDM une question filtrée qui ne s'affiche que pour les ménages ayant déclaré n'avoir rien reçu, et code le saut correspondant.

Exécute `importer_kobo.py` sur l'export brut, puis ouvre la table `rejets` et écris la requête qui produit la liste de rappel destinée au superviseur, avec le code ménage, l'enquêteur et le motif.

Modifie la règle de durée minimale d'entretien de huit à quinze minutes, relance l'import, et commente l'effet sur le nombre de rejets — puis décide si cette règle est justifiable et pourquoi.

Écris la requête qui compare, par enquêteur, la durée médiane d'entretien, le taux de valeurs manquantes et le score de satisfaction moyen, et interprète les écarts.

Enfin, rédige le plan de formation d'une journée pour six enquêteurs sur le formulaire PDM, minute par minute. C'est un livrable que tu peux montrer en entretien.

---

## Angles d'entretien

**« Comment coderiez-vous un questionnaire de ciblage avec un score de vulnérabilité ? »**

Je commence par la grille de pondération, qui n'est pas une décision technique : elle vient du responsable programme et du comité de ciblage, et je la fais valider par écrit avant d'écrire une ligne, parce que c'est elle qui décide qui reçoit de l'aide. Ensuite je la code dans le formulaire lui-même plutôt que dans un fichier d'analyse en aval, pour trois raisons. Le score est calculé pendant l'entretien, donc l'enquêteur peut vérifier sur place qu'un ménage manifestement très vulnérable obtient bien un score élevé, ce qui révèle immédiatement une pondération mal calibrée. La pondération est versionnée avec le formulaire déployé, donc au moment de justifier le ciblage devant le bailleur, je peux dire exactement quelle grille a servi. Et le score arrive déjà calculé dans la base, identique pour toutes les soumissions. Techniquement, je décompose en points partiels nommés — points pour la taille, pour les enfants de moins de cinq ans, pour le handicap, pour le statut de déplacement — plutôt que d'écrire une formule unique, parce que c'est débogable et relisible par un non-informaticien. Je plafonne les composantes, par exemple la taille du ménage comptée au maximum pour dix personnes, sinon une seule variable écrase toutes les autres et le score cesse de mesurer la vulnérabilité. J'ajoute des contrôles de cohérence, en distinguant ce que je bloque de ce sur quoi j'alerte : je bloque l'impossible, comme un nombre d'enfants supérieur à la taille du ménage, et j'alerte sur l'improbable, parce que bloquer l'improbable pousse les enquêteurs à saisir n'importe quoi pour pouvoir avancer. Et le formulaire affiche toujours que la proposition est automatique mais que la décision appartient au comité communautaire : un algorithme classe, il ne sélectionne pas.

**« Vous recevez un export Kobo de 600 lignes. Décrivez ce que vous en faites. »**

Je ne l'ouvre pas dans Excel pour le corriger à la main, parce que ce travail ne serait ni reproductible ni auditable. J'archive d'abord le fichier brut tel quel, daté, et je ne le modifie plus jamais : tout le nettoyage se fait dans un script, ce qui me permet de rejouer la chaîne complète si je corrige une règle. Le script fait quatre choses dans cet ordre. Il normalise, c'est-à-dire qu'il ramène les dates à un format unique alors que le terrain en produit trois, qu'il retire les séparateurs de milliers et les unités collées dans les colonnes numériques, et qu'il harmonise les libellés par une table de correspondance explicite — sur mon export d'exercice, dix-neuf graphies de commune se ramènent à dix communes réelles. Il valide ensuite chaque ligne contre des règles métier, et une ligne qui échoue part dans une table de rejets avec son contenu intégral et le motif exact, jamais à la poubelle : je peux rappeler l'enquêteur, corriger et réimporter. Il déduplique sur la clé métier, ici le couple ménage et date d'enquête, en conservant la soumission la plus complète, parce que les renvois après coupure réseau sont systématiques. Et il charge de façon idempotente, avec une contrainte d'unicité en base et une clause de conflit, de sorte que relancer l'import ne crée aucun doublon. À la fin, le script imprime une réconciliation qui doit boucler : lignes lues moins rejets moins doublons moins retenues égale zéro. Sur mon exercice, 589 lignes lues donnent 56 rejets documentés, 18 doublons écartés et 515 lignes chargées. Un import qui ne boucle pas perd des données sans le dire, et c'est la première chose que je vérifie.

**« Comment détectez-vous qu'un enquêteur remplit ses questionnaires sans poser les questions ? »**

Je regarde d'abord la durée d'entretien, que je calcule dans le formulaire à partir des métadonnées de début et de fin, ce qui ne coûte rien à mettre en place. Un PDM complet demande vingt à quarante minutes ; une soumission de trois minutes est presque toujours un formulaire rempli sans entretien. Sur mon export d'exercice, ce seul contrôle remonte vingt soumissions suspectes sur 589. Je regarde ensuite trois autres signaux, parce qu'aucun ne suffit isolément. La dispersion géographique des points GPS : des soumissions censées venir de ménages différents et enregistrées au même endroit à quelques minutes d'intervalle sont un signal fort. La variance des réponses : un enquêteur dont toutes les enquêtes donnent des scores très proches produit probablement des réponses inventées, parce que le vrai terrain est bruyant. Et le taux de valeurs manquantes, qui est souvent anormalement bas chez celui qui invente, puisqu'il ne rencontre jamais de refus ni d'hésitation. Ce que je fais de ces signaux compte autant que la façon de les produire. Je ne les traite pas comme des preuves, je les traite comme des questions, et je les remonte au superviseur de collecte, pas à l'enquêteur directement. La bonne pratique est de faire tourner ces contrôles chaque soir pendant la collecte, pas à la fin : détectés le premier jour, ils se corrigent par un accompagnement ; détectés à la fin, ils obligent à refaire l'enquête.

---

*Suite du parcours : [Sécurité et protection des données](04_securite_protection_donnees.md) · [Gestion de l'information et archivage](06_gestion_information_archivage.md) · [Analyse et visualisation](07_analyse_visualisation_reporting.md) · [Fiche de révision](00_fiche_revision_examen.md)*
