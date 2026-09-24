# Fiche du jour J — vendredi 25 septembre 2026, 13 h, Zoom

*La seule page à relire demain matin, avec [`FICHE_SYNTHESE.md`](FICHE_SYNTHESE.md) si tu as une
heure. Rien de nouveau ici : tout vient des modules.*

---

## Ce soir, avant de dormir : quatre décisions

**Tekkod.** Choisis laquelle des deux réponses du module 05 § 4 est vraie : arrêter ou suspendre,
ou garder une mission réduite déclarée par écrit. Ne dis pas « je verrai ».

**Ton plancher salarial**, fixé seul, en tenant compte de Tekkod, d'un poste de niveau conseiller
principal et d'un contrat de six mois conditionné. Tu ne le dis pas le premier.

**Ta date de disponibilité**, réelle, avec le préavis que tu dois.

**Préviens Davidson Adrien** que l'Institut Panos peut l'appeler : l'annonce prévoit une
vérification rigoureuse des références.

---

## La logistique Zoom : c'est la première preuve de travail hybride

Connecte-toi à **12 h 45**. Vérifie l'heure exacte sur l'invitation. Ordinateur chargé et branché,
batterie ou onduleur prêts si le courant tombe, **partage de connexion du téléphone prêt** en réseau
de secours. Casque ou écouteurs, lumière face à toi, fond neutre, notifications coupées. Ton nom
affiché : **Alexandro Disla**.

Ouverts à côté, mais pas à l'écran partagé : le CV et la lettre envoyés à Panos, l'annonce, cette
fiche, une feuille pour noter **les noms et fonctions du panel dans les trente premières secondes**.

Si la connexion coupe : rejoins aussitôt, excuse-toi en une phrase et reprends où tu en étais.
Si c'est impossible, écris à `contact@institutpanos.org` et appelle le **+509 2942-0321** (numéro
du site).

---

## L'Institut Panos, en six phrases

ONG haïtienne fondée le **29 juin 1986**, née de la communication sociale (Panos Caraïbes),
présente dans les **dix départements** à partir de **Pétion-Ville** (14, rue Borno), du
**Cap-Haïtien** et des **Cayes**. Trois programmes : santé globale, gouvernance, assistance
humanitaire. Dispositif de proximité : **SMS en créole** sans internet (3,6 M+), **ligne 8338**
(1,36 M+ appels, 19 754 assistés, 1 203 références vers les soins), relais communautaires. VIH :
premier **Forum national sur le sida**, campagnes **E=E**, **PrEP**, **TME**, **ARV**, puis
**CHAMPIONS** (USAID, avril 2024, **arrêté au bout de dix mois** en 2025 — au passé, avec respect).
Aujourd'hui **sous-partenaire d'EpiC** (PEPFAR, FHI 360) : éducation des patients, adhérence,
**traçage et retour en soins des patients en interruption**, suppression virale. Une histoire :
**Marie Tania Petit-Frère**, ambassadrice E=E, qui livre aujourd'hui les ARV à domicile à l'HUEH.

---

## AFGHS, en trois phrases

Très probablement l'**America First Global Health Strategy** du Département d'État (18 septembre
2025) : des accords bilatéraux, 100 % des produits et des agents de première ligne en 2026, puis un
co-financement croissant, des **cibles annuelles** et le droit de **retenir le financement**, des
systèmes de données nationaux renforcés. **Haïti n'a pas signé** au 15 septembre 2026 (35 pays
l'ont fait, selon la KFF), d'où, vraisemblablement, l'« accord anticipé de six mois ». **C'est une
déduction : pose-la comme une question.**

---

## Le pitch, en quatre mouvements

**Formation** (économiste appliqué, CTPEA ; jamais « diplômé »). **Le VIH au centre** (Caris, Impact
Youth, 2021-2024, MER via DATIM comme producteur, DQA jusqu'au registre source). **Les deux
compétences et le ministère** (collecte numérique et MEAL, dont Anseye : trois programmes en trois
mois ; ingénierie de données ; huit ans au ministère du Plan). **Leur annonce** (jalons vérifiables,
réconciliation MESI / SISNU / iSanté Plus, chaîne complète en quelques semaines, hybride).

---

## Les cinq limites, dans les mots de la lettre

Pas de master délivré (DES en attente de la soutenance du mémoire). Cinq ans en ONG dont trois sur le
VIH, huit au ministère du Plan, et pas encore de poste de conseiller technique principal. DATIM :
producteur de données, jamais administrateur. PTME : la logique, pas le terrain. MESI, SISNU, iSanté
Plus : le paysage, pas l'exploitation.

---

## Les quatre idées qui te distinguent

**Le faux dénominateur.** Avant de tracer un patient, vérifier qu'il est réellement perdu. La
déduplication nationale dans SALVH réduit d'environ **14 %** les perdus de vue apparents (*Journal
of Infectious Diseases*, 2025) ; sur ton jeu d'exercice, **12,4 %** de la liste n'avaient jamais
interrompu, et sept d'entre eux passaient même pour des « retours vérifiés ».

**Le formulaire ne demande pas le retour.** Le relais note le rendez-vous ; le retour, c'est la
dispensation qui le prouve. Sur le jeu d'exercice : **39 % déclarés, 29,3 % vérifiés.**

**Le piège des 28 jours.** Un patient ramené avant le 28e jour n'est jamais un `TX_RTT`. Un jalon
écrit sur les seuls retours après interruption paie pour laisser les gens décrocher : suivre aussi
les rendez-vous manqués rattrapés.

**Se vérifier avant d'être vérifié.** Pré-vérification mensuelle, facteur de vérification, dossier
de preuve par jalon. Quarante dossiers, c'est **± 14 points** : la taille de l'échantillon se
négocie dans l'accord.

---

## Les définitions à avoir sur le bout de la langue

**Interruption** : plus de 28 jours sans ARV après le dernier contact attendu. **`TX_ML`** : les
sorties, par devenir (décès, transfert, refus ou arrêt, interruption ventilée selon le temps passé
sous traitement avant de décrocher). **`TX_RTT`** : les retours après plus de 28 jours
d'interruption. **Équation de cohorte** : `TX_CURR` fin = début + `TX_NEW` + `TX_RTT` − `TX_ML`.
**Couverture en charge virale** = testés ÷ `TX_CURR` ; **suppression** = supprimés ÷ testés ; jamais
l'une sans l'autre. **Facteur de vérification** = retrouvé dans les sources ÷ rapporté. **Taux
agrégé** = somme des numérateurs ÷ somme des dénominateurs, jamais une moyenne de taux.

---

## Tes trois questions

Le mécanisme : « AFGHS renvoie-t-il à l'America First Global Health Strategy, et comment le paiement
est-il construit, jalons de processus, cibles de résultats, et qui vérifie ? » La référence :
« Quand la ligne 8338 réfère quelqu'un, comment savez-vous si la référence a abouti ? » Les outils :
« Pour le traçage dans EpiC, quels outils utilisez-vous, PLR, Radar, autre chose ? »

---

## Les pièges

Ne dis pas « diplômé », « master », « lauréat ». Ne dis pas que tu as rapporté `TX_CURR`, `TX_ML`
ou `TX_PVLS` (ton exemple confirmé est `AGYW_PREV` sous DREAMS). Ne revendique ni la PTME, ni
l'administration de DHIS2, ni l'exploitation de MESI, ni le Projet Santé. Ne parle pas de CHAMPIONS
au présent, ni de l'audit de l'USAID sous aucune forme. Ne relève aucune coquille de leur site. Ne
donne jamais un taux sans son dénominateur. Ne donne pas le premier chiffre de salaire. Et dans une
mise en situation, dis d'abord **ce que tu vérifies**, puis ce que tu fais, puis à qui tu le dis.
