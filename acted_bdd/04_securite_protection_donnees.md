# Sécurité et protection des données de bénéficiaires

*Piste ACTED — Assistant Base de Données (Réf. ASSISTBDD_2607). Base d'exercice : `exercices/acted_bdd.db`. Tous les chiffres de ce module proviennent de requêtes réellement exécutées sur cette base.*

---

## Pourquoi ce module est le plus important de tous

Dans la plupart des métiers de la donnée, une fuite coûte de l'argent et de la réputation. En action humanitaire, en Haïti, en 2026, une fuite peut coûter la vie de quelqu'un.

Une liste de bénéficiaires n'est pas un fichier de clients. C'est la liste nominative, géolocalisée et téléphonée des personnes d'un quartier qui viennent de recevoir de l'argent liquide, avec le montant et la date. Entre les mains de qui il ne faut pas, ce fichier est une liste de cibles. Et cette liste, c'est l'assistant base de données qui la détient, la copie, la sauvegarde et l'exporte.

Le TDR le formule sobrement : « mettre en œuvre des procédures appropriées de sauvegarde, de restauration, de validation des données et de sécurité pour garantir l'intégrité et la disponibilité des données ». Le mot sécurité est là. Un candidat qui l'aborde spontanément, avec le vocabulaire juste, se distingue immédiatement — parce que c'est le sujet dont on parle le moins et qui pèse le plus.

---

## 1. La fuite ordinaire

Personne ne pirate le serveur d'une ONG en Haïti. Voici comment les données sortent réellement.

Le chargé de programme demande la liste des bénéficiaires de Gonaïves pour préparer une visite bailleur. L'assistant base de données exporte `beneficiaires_gonaives.xlsx` avec noms, téléphones, coordonnées GPS et montants reçus, et l'envoie par WhatsApp. Le chargé de programme le transfère à son collègue. Le collègue le montre à un partenaire local. Le fichier existe maintenant sur cinq téléphones, dont deux se feront voler dans l'année, et aucun n'est chiffré. Personne n'a rien fait de malveillant, chaque étape était de bonne foi, et pourtant la liste est dehors.

Retiens la mécanique, parce que c'est elle qu'il faut casser. Il n'y a pas eu d'attaque : il y a eu **un export trop riche, une diffusion sans contrôle et une absence de règle**. Les trois se corrigent par de la procédure, pas par de la technologie.

La règle qui aurait tout évité tient en une phrase, et elle mérite d'être apprise telle quelle : **on n'exporte jamais plus de données que ce que la question posée exige.** Pour préparer une visite, on a besoin d'un nombre de ménages par site et d'une carte. On n'a besoin d'aucun nom.

---

## 2. Le vocabulaire à maîtriser

Une **donnée personnelle** est toute information se rapportant à une personne physique identifiée ou identifiable. Le nom en est une, mais le numéro de téléphone, la coordonnée GPS du domicile et le numéro de pièce d'identité aussi.

On distingue les **identifiants directs**, qui désignent la personne à eux seuls — nom, pièce d'identité, téléphone, photo — des **quasi-identifiants**, qui ne disent rien isolément mais qui, combinés, ne laissent plus qu'une personne possible. La commune, le sexe du chef de ménage, la taille du foyer et le statut de déplacement sont des quasi-identifiants, et c'est là que se trouve le piège que presque tout le monde sous-estime.

Une **donnée sensible** appartient à une catégorie qui expose particulièrement : santé, appartenance ethnique ou politique, situation de handicap, statut de déplacement dans certains contextes, et surtout tout ce qui touche aux violences basées sur le genre ou à l'exploitation et aux abus sexuels. Dans la table `plaintes` de la base d'exercice, 17 plaintes sur 240 sont marquées `sensible = 1`, et elles n'obéissent pas au même régime que les autres : leur accès est restreint à deux personnes nommées, elles ne figurent dans aucun export, et elles suivent le circuit de sauvegarde protégé de l'organisation.

La **minimisation** est le principe selon lequel on ne collecte que ce dont on a réellement besoin pour l'objectif déclaré. Question à se poser devant chaque question d'un formulaire Kobo : *quelle décision cette réponse va-t-elle changer ?* Si personne ne sait répondre, la question sort du formulaire. C'est la mesure de protection la plus efficace qui existe, parce qu'une donnée non collectée ne peut pas fuir.

La **limitation de finalité** interdit de réutiliser pour un usage B des données collectées pour un usage A. Les données de ciblage WASH ne servent pas à constituer la liste de diffusion d'un autre projet, même si c'est pratique.

---

## 3. Le piège de la réidentification, démontré

Beaucoup de gens croient qu'il suffit de retirer les noms pour anonymiser un fichier. Mesurons ce que cela vaut réellement sur notre base.

Le concept de référence est le **k-anonymat** : un jeu de données est k-anonyme si chaque combinaison de quasi-identifiants est partagée par au moins *k* personnes. Quand *k* vaut 1, une seule personne correspond à la combinaison, et retirer le nom n'a servi à rien.

```sql
WITH classes AS (
  SELECT c.nom_commune, m.sexe_chef, m.taille_menage, m.statut_deplacement,
         COUNT(*) AS k
  FROM menages m
  JOIN sites    s ON s.code_site  = m.code_site
  JOIN communes c ON c.id_commune = s.id_commune
  GROUP BY 1, 2, 3, 4
)
SELECT CASE WHEN k = 1 THEN 'k=1 (reidentifiable)'
            WHEN k < 5 THEN 'k entre 2 et 4'
            ELSE 'k>=5' END AS niveau,
       COUNT(*) AS classes,
       SUM(k)   AS menages
FROM classes
GROUP BY 1
ORDER BY 1;
```

| niveau | classes | menages |
|---|---|---|
| k entre 2 et 4 | 261 | 673 |
| k=1 (reidentifiable) | 245 | 245 |
| k>=5 | 48 | 300 |

Lis bien ce tableau. **Deux cent quarante-cinq ménages sur 1 218, soit un sur cinq, sont identifiables de manière unique** à partir de quatre informations banales : la commune, le sexe du chef de ménage, le nombre de personnes au foyer et le statut de déplacement. Aucun nom, aucun téléphone, aucune coordonnée GPS n'est nécessaire. N'importe qui connaissant un peu le quartier retrouve la personne.

Voici quelques-unes de ces combinaisons uniques.

| nom_commune | sexe_chef | taille_menage | statut_deplacement | k |
|---|---|---|---|---|
| Cap-Haitien | F | 2 | Hote | 1 |
| Cap-Haitien | F | 3 | Hote | 1 |
| Cap-Haitien | F | 4 | Retourne | 1 |

C'est **la** démonstration à savoir refaire en examen pratique, et à savoir raconter en entretien. Elle prouve qu'on comprend la protection des données au-delà du slogan « on a enlevé les noms ».

Les remèdes se combinent. On **généralise** : la taille du ménage devient une tranche, « 1 à 3 », « 4 à 6 », « 7 et plus », et le nombre de combinaisons possibles s'effondre. On **agrège** : on ne publie pas la ligne, on publie le comptage par commune. On **supprime** les classes trop petites, en appliquant un seuil — la pratique courante dans les clusters humanitaires est de ne rien publier en dessous de cinq à dix unités. Et on **restreint** : le fichier ligne à ligne reste interne, seul l'agrégé circule.

---

## 4. Anonymiser ou pseudonymiser

Les deux mots sont souvent confondus, et la différence est exactement ce qu'un jury veut entendre.

La **pseudonymisation** remplace les identifiants directs par un code, mais conserve quelque part une table de correspondance qui permet de revenir à la personne. C'est **réversible**, donc les données restent des données personnelles au sens juridique, et elles restent soumises à toutes les protections. C'est ce qu'on utilise en interne, parce qu'on a besoin de pouvoir recontacter le ménage — pour l'enquête post-distribution, pour traiter sa plainte, pour vérifier un doublon.

L'**anonymisation** est irréversible : plus aucun chemin ne mène à la personne, ni par la table de correspondance, ni par recoupement de quasi-identifiants. C'est ce qu'on vise pour tout ce qui sort de l'organisation.

Le point qui trompe : **un fichier pseudonymisé mais réidentifiable par recoupement n'est pas anonyme**, et la section précédente montre à quel point c'est facile.

Voici la vue d'export sûr, telle qu'on peut la poser dans la base.

```sql
-- Gist: vue_export_partenaire.sql
-- Export destine a un partenaire ou a un bailleur : aucune donnee nominative,
-- quasi-identifiants generalises, classes de moins de 5 menages ecartees.
CREATE VIEW v_export_partenaire AS
SELECT c.nom_commune,
       CASE WHEN m.taille_menage <= 3 THEN '1-3'
            WHEN m.taille_menage <= 6 THEN '4-6'
            ELSE '7+' END                       AS tranche_taille,
       m.sexe_chef,
       m.statut_selection,
       COUNT(*)                                 AS nb_menages,
       ROUND(AVG(m.score_vulnerabilite), 1)     AS score_moyen
FROM menages m
JOIN sites    s ON s.code_site  = m.code_site
JOIN communes c ON c.id_commune = s.id_commune
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) >= 5;
```

Trois protections coexistent dans ces quelques lignes. Aucune colonne nominative n'est sélectionnée. La taille du ménage est généralisée en tranches. Le `HAVING COUNT(*) >= 5` écarte automatiquement toute combinaison qui désignerait moins de cinq foyers. Et comme c'est une vue, on peut donner au compte bailleur un droit de lecture **sur la vue seulement**, jamais sur la table `menages` : la protection devient structurelle, elle ne dépend plus de la vigilance de celui qui exporte.

Pour la pseudonymisation interne, on remplace le code du ménage par une empreinte salée plutôt que par un simple numéro d'ordre, parce qu'un numéro d'ordre se reconstitue trivialement quand on possède la base source.

```sql
-- PostgreSQL : le sel doit etre stocke separement, jamais dans le meme fichier
-- que les donnees exportees, sinon la pseudonymisation ne protege plus rien.
SELECT encode(digest(m.code_menage || :sel, 'sha256'), 'hex') AS pseudo_id,
       c.nom_commune, m.sexe_chef, m.statut_selection
FROM menages m ...
```

---

## 5. Protéger le support

### 5.1 Le chiffrement

Le chiffrement **au repos** protège les données quand le support est volé ou perdu. Concrètement, cela veut dire FileVault activé sur le portable, BitLocker sur Windows, une archive chiffrée pour le disque externe de sauvegarde, et pour la base elle-même l'extension SQLCipher si l'on reste sur SQLite ou le chiffrement des tablespaces sur PostgreSQL.

Le chiffrement **en transit** protège les données pendant qu'elles circulent. KoboToolbox utilise HTTPS, donc le trajet tablette-serveur est couvert, mais tout ce qui suit est à ta charge : un export téléchargé puis envoyé par WhatsApp ou déposé sur une clé USB sort de la zone protégée.

Le maillon faible est presque toujours le même, et il faut savoir le nommer : **le fichier exporté**. La base est correctement gérée, le serveur Kobo est correctement configuré, et il traîne quinze exports Excel dans le dossier Téléchargements d'un portable non chiffré. La règle pratique consiste à traiter les exports comme des objets périssables : un dossier unique, un nommage daté, une purge hebdomadaire, et jamais d'export nominatif hors du poste de travail.

### 5.2 Les mots de passe et les comptes

Un compte nominatif par personne, jamais de compte partagé. C'est la condition sans laquelle le journal d'audit ne sert à rien : si trois personnes utilisent `saisie01`, la traçabilité est nulle et personne ne peut répondre à la question de savoir qui a modifié un montant.

Un gestionnaire de mots de passe pour l'équipe, l'authentification à deux facteurs sur le serveur Kobo et sur la messagerie, et surtout une **procédure de départ** : le jour où quelqu'un quitte le projet, son compte est désactivé le jour même, pas trois mois plus tard. La revue trimestrielle des comptes décrite dans le module [Administration](03_administration_bdd.md) est le filet de sécurité de cette procédure.

---

## 6. Tracer : le journal d'audit

Le bailleur demande, dix-huit mois après la distribution, pourquoi le ménage MEN-00003, initialement non sélectionné, apparaît finalement parmi les bénéficiaires. Sans traçabilité, la seule réponse possible est un haussement d'épaules — et c'est précisément le genre de trou qui déclenche un audit approfondi.

Voici le mécanisme qui répond à la question. Il s'agit d'un **déclencheur**, ou *trigger* : une instruction que la base exécute automatiquement à chaque modification d'une colonne sensible.

```sql
-- Gist: trigger_audit_menages.sql
-- La table session_courante porte l'identite de l'utilisateur applicatif et le motif
-- de l'operation ; elle est renseignee par l'application a l'ouverture de la session.
CREATE TABLE session_courante (cle TEXT PRIMARY KEY, valeur TEXT);

CREATE TRIGGER trg_audit_menages_update
AFTER UPDATE OF statut_selection, telephone, score_vulnerabilite ON menages
FOR EACH ROW
BEGIN
  INSERT INTO journal_audit (table_cible, cle_cible, action, champ,
                             ancienne_valeur, nouvelle_valeur,
                             identifiant_util, horodatage, motif)
  SELECT 'menages', OLD.code_menage, 'UPDATE', champ, ancien, nouveau,
         COALESCE((SELECT valeur FROM session_courante WHERE cle = 'utilisateur'), 'inconnu'),
         datetime('now'),
         (SELECT valeur FROM session_courante WHERE cle = 'motif')
  FROM (
    SELECT 'statut_selection'    AS champ, OLD.statut_selection    AS ancien, NEW.statut_selection    AS nouveau
    UNION ALL SELECT 'telephone',           OLD.telephone,           NEW.telephone
    UNION ALL SELECT 'score_vulnerabilite', CAST(OLD.score_vulnerabilite AS TEXT),
                                            CAST(NEW.score_vulnerabilite AS TEXT)
  )
  WHERE ancien IS NOT nouveau;
END;
```

Testons-le pour de vrai. On déclare qui agit et pourquoi, puis on applique la décision du comité de recours.

```sql
INSERT INTO session_courante VALUES
  ('utilisateur', 'adisla'),
  ('motif', 'Recours accepte par le comite du 12/05');

UPDATE menages
SET statut_selection = 'Selectionne', score_vulnerabilite = 48
WHERE code_menage = 'MEN-00003';

SELECT table_cible, cle_cible, champ, ancienne_valeur, nouvelle_valeur,
       identifiant_util, motif
FROM journal_audit;
```

| table_cible | cle_cible | champ | ancienne_valeur | nouvelle_valeur | identifiant_util | motif |
|---|---|---|---|---|---|---|
| menages | MEN-00003 | statut_selection | Non selectionne | Selectionne | adisla | Recours accepte par le comite du 12/05 |
| menages | MEN-00003 | score_vulnerabilite | 35 | 48 | adisla | Recours accepte par le comite du 12/05 |

Deux lignes, écrites automatiquement, que personne n'a eu à penser à créer. La question du bailleur trouve désormais une réponse en une requête : le ménage est passé de non sélectionné à sélectionné le tel jour, par tel utilisateur, sur décision du comité de recours du 12 mai.

Trois détails du déclencheur méritent d'être remarqués. La clause `WHERE ancien IS NOT nouveau` évite de journaliser les mises à jour qui ne changent rien, ce qui garderait le journal illisible. L'opérateur `IS NOT` plutôt que `<>` gère correctement les valeurs nulles, puisque `NULL <> 'x'` ne vaut pas vrai en SQL ternaire. Et le motif est **obligatoire dans la procédure**, même s'il n'est pas techniquement contraint : une modification sans motif est une modification qu'on ne saura pas défendre.

La table `journal_audit` elle-même doit être protégée. Personne n'y a le droit d'écriture directe ni de suppression, y compris l'administrateur applicatif : seuls les déclencheurs y écrivent. Un journal que l'on peut modifier n'est pas un journal.

---

## 7. Le cadre : consentement, partage, conservation

### 7.1 Informer et recueillir le consentement

Avant la première question du formulaire, l'enquêteur doit lire une note d'information et enregistrer une réponse. Cette note dit qui collecte, pour quoi faire, avec qui les données seront partagées, combien de temps elles seront conservées, et comment la personne peut demander à les consulter, les corriger ou les retirer. Le refus doit être possible sans conséquence sur l'accès à l'assistance, et cette phrase-là doit être dite à voix haute.

En pratique, cela se code dans le formulaire XLSForm comme une question obligatoire de type `select_one oui_non` avec une contrainte de saut : si la réponse est non, le formulaire s'arrête. Le module [Kobo et enquêtes](05_kobo_ciblage_et_pdm.md) montre l'implémentation.

Il faut connaître la limite honnête de ce dispositif, et savoir la formuler : dans un contexte de crise, le consentement d'une personne qui a faim et qui pense que refuser la privera d'aide n'est pas pleinement libre. C'est pourquoi les cadres humanitaires — le manuel du CICR sur la protection des données dans l'action humanitaire est la référence — ne s'appuient pas seulement sur le consentement, mais sur l'intérêt vital et la mission humanitaire comme bases de traitement, avec en contrepartie une obligation renforcée de minimisation.

### 7.2 Partager sans exposer

Le partage se décide par niveau, et le tableau suivant est le genre de livrable qu'on peut proposer dès la première semaine de poste.

| Destinataire | Ce qu'il reçoit | Ce qu'il ne reçoit jamais |
|---|---|---|
| Bailleur | Indicateurs agrégés par commune, taux de couverture, budget consommé | Noms, téléphones, GPS de ménages, plaintes sensibles |
| Cluster / OCHA | Comptages par site avec seuil minimal de 5 unités | Toute ligne individuelle |
| Partenaire de mise en œuvre | Liste des ménages de sa zone, sous accord écrit de partage | Ménages hors de sa zone, données de plainte |
| Autorité locale | Nombre de bénéficiaires par section communale | Toute donnée nominative, sauf obligation légale documentée |
| Équipe interne MEAL | Accès nominatif complet, comptes nominatifs, journalisé | Rien de restreint, hors plaintes sensibles |

La ligne « autorité locale » est celle qui demande le plus de fermeté et de tact. Une demande de liste nominative par une autorité doit remonter au coordonnateur et au responsable protection, jamais être traitée par l'assistant base de données seul. Savoir dire cela en entretien montre qu'on connaît sa place dans la chaîne de décision.

Tout partage externe passe par un **accord de partage de données** écrit, qui précise la finalité, les champs transmis, la durée de conservation par le destinataire et l'interdiction de retransmission.

### 7.3 Conserver, puis détruire

Une donnée conservée sans raison est un risque conservé sans raison. La politique de conservation fixe une durée par catégorie, et le tableau tient en quelques lignes : les données de ciblage vivent le temps du projet plus la période d'audit exigée par le bailleur, souvent cinq à sept ans ; les coordonnées de contact n'ont plus d'utilité une fois le suivi post-distribution terminé et peuvent être effacées bien avant ; les données de plainte sensible suivent la politique de protection de l'organisation et ne sont accessibles qu'aux personnes désignées.

La destruction est une opération technique qui doit être réelle. Effacer un fichier ne l'efface pas : il faut un écrasement sécurisé pour les supports, et pour la base une mise à `NULL` des colonnes concernées suivie d'un `VACUUM`, faute de quoi les valeurs restent lisibles dans les pages libérées du fichier. Cette dernière remarque est technique et précise, et elle impressionne parce qu'elle est presque toujours ignorée.

### 7.4 Réagir à un incident

Un portable est volé, un export a été envoyé au mauvais destinataire, un compte a été compromis. La séquence à connaître comporte cinq temps : contenir en coupant l'accès et en changeant les mots de passe, évaluer ce qui est réellement sorti et pour combien de personnes, notifier immédiatement le responsable MEAL et le coordonnateur qui décideront de l'information des personnes concernées, corriger la cause, et documenter l'incident dans un registre.

Le point sur lequel il faut être catégorique : **on ne dissimule jamais un incident.** Le réflexe de cacher est humain et il transforme un incident gérable en faute grave. Le dire spontanément en entretien est un signal de maturité professionnelle.

---

## 8. Sept exercices de protection

Refais la mesure de k-anonymat de la section 3 sur la base, puis recommence en généralisant la taille du ménage en tranches et vérifie de combien le nombre de ménages réidentifiables diminue.

Crée la vue `v_export_partenaire`, exporte-la en CSV, et vérifie qu'aucune ligne du fichier ne correspond à moins de cinq ménages.

Installe le déclencheur d'audit sur `assistances` pour journaliser toute modification de `montant_htg`, puis démontre son fonctionnement en corrigeant un montant avec un motif.

Écris la requête qui liste toutes les modifications faites par un utilisateur donné entre deux dates, telle qu'on la fournirait à un auditeur.

Rédige la note d'information et de consentement à lire avant l'enquête de ciblage, en cinq phrases maximum, dans un français simple traduisible en créole.

Construis le tableau de partage de la section 7.2 pour un projet WASH réel, en ajoutant la colonne du responsable qui autorise chaque partage.

Enfin, rédige la procédure d'incident sur une page, avec les cinq temps, les noms des personnes à prévenir et le modèle de fiche de registre. C'est, là encore, un livrable que tu peux poser sur la table.

---

## Angles d'entretien

**« Comment protégez-vous les données personnelles des bénéficiaires ? »**

Je raisonne à trois niveaux, parce que la technique seule ne suffit jamais. Le premier niveau est la collecte, et c'est celui qui protège le plus : je pratique la minimisation, c'est-à-dire que pour chaque question du formulaire je demande quelle décision la réponse va changer, et si personne ne sait répondre, la question sort du formulaire. Une donnée non collectée ne peut pas fuir. Le deuxième niveau est le stockage et l'accès : chiffrement du poste et du disque de sauvegarde, comptes nominatifs et jamais de compte partagé, droits accordés selon le principe du moindre privilège, et journalisation automatique par déclencheur de toute modification d'un champ sensible, avec l'utilisateur et le motif. Le troisième niveau est la diffusion, et c'est là que se produisent les vraies fuites : elles ne viennent presque jamais d'une attaque, elles viennent d'un export trop riche envoyé par messagerie. Ma règle est qu'on n'exporte jamais plus que ce que la question exige, et que ce qui sort de l'organisation passe par une vue agrégée avec un seuil minimal. Sur ce point je fais toujours une démonstration qui frappe : sur ma base d'exercice, si je retire les noms mais que je garde la commune, le sexe du chef de ménage, la taille du foyer et le statut de déplacement, un ménage sur cinq reste identifiable de façon unique. Retirer les noms n'anonymise pas. Il faut généraliser les quasi-identifiants et écarter les groupes trop petits, et c'est exactement ce que fait ma vue d'export.

**« Quelle est la différence entre anonymisation et pseudonymisation ? »**

La pseudonymisation remplace les identifiants directs par un code, mais une table de correspondance existe quelque part et permet de revenir à la personne. C'est donc réversible, et les données restent juridiquement des données personnelles, soumises à toutes les protections. On l'utilise en interne parce qu'on a besoin de ce retour : pour recontacter le ménage lors de l'enquête post-distribution, pour traiter sa plainte, pour vérifier qu'il n'est pas enregistré deux fois. L'anonymisation est irréversible : aucun chemin ne mène plus à la personne, ni par une table de correspondance, ni par recoupement. C'est ce qu'on vise pour tout ce qui sort. Le piège que je vérifie systématiquement, c'est qu'un fichier pseudonymisé reste très souvent réidentifiable par recoupement des quasi-identifiants, donc n'est pas anonyme même si tout le monde le croit. Concrètement, quand je prépare un export externe, je fais trois choses : je ne sélectionne aucune colonne nominative, je généralise les variables trop précises comme la taille du ménage ou la date de naissance, et je pose un seuil qui écarte automatiquement toute combinaison correspondant à moins de cinq personnes. Et je préfère implémenter cela dans une vue plutôt que dans un script, parce que je peux alors donner au destinataire un droit de lecture sur la vue seulement : la protection devient structurelle au lieu de dépendre de la vigilance de celui qui fait l'export ce jour-là.

**« Une autorité locale vous demande la liste nominative des bénéficiaires. Que faites-vous ? »**

Je ne la fournis pas, et je ne refuse pas non plus de mon propre chef, parce que ce n'est pas ma décision. Je remonte immédiatement la demande au responsable MEAL et au coordonnateur de la zone, et je documente par écrit qui a demandé quoi, quand et sous quelle forme. Ce que je peux proposer de moi-même, c'est l'alternative qui répond au besoin légitime sans exposer personne : un comptage agrégé par section communale, le nombre de ménages assistés et la nature de l'assistance, ce qui satisfait presque toujours l'objectif réel de la demande, qui est de savoir ce qui se passe sur le territoire. Si une obligation légale est invoquée, elle doit être vérifiée et documentée, et la décision revient à la coordination, éventuellement au siège. Le raisonnement de fond que j'applique est celui du principe humanitaire de ne pas nuire : une liste nominative de personnes ayant reçu du cash, avec leurs coordonnées et leur localisation, est une liste de cibles potentielles dans un contexte où des groupes armés contrôlent des quartiers. Ce n'est pas une hypothèse théorique en Haïti. Donc ma position par défaut est l'agrégat, et toute exception passe par une décision écrite, prise plus haut que moi.

---

*Suite du parcours : [Administration de base de données](03_administration_bdd.md) · [Kobo, ciblage et PDM](05_kobo_ciblage_et_pdm.md) · [Gestion de l'information et archivage](06_gestion_information_archivage.md) · [Fiche de révision](00_fiche_revision_examen.md)*
