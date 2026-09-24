-- Requêtes du module 02 (chaîne MEL de bout en bout), dans l'ordre du texte.
-- Exécution :  sqlite3 panos_iit.db < requetes.sql
-- Données FICTIVES produites par generer_donnees.py.

.headers on
.mode column

-- ---------------------------------------------------------------------------
-- Étape 1 — la cascade telle que les relais la déclarent (naïve).
-- On compte les lignes de visite, sans normaliser les codes ni dédoublonner.
-- ---------------------------------------------------------------------------
SELECT '1. cascade naive' AS etape;
SELECT
    (SELECT COUNT(*) FROM liste_iit)                                  AS listes,
    (SELECT COUNT(*) FROM visites_tracage)                            AS visites,
    (SELECT COUNT(*) FROM visites_tracage WHERE resultat = 'joint')   AS joints,
    (SELECT COUNT(*) FROM visites_tracage WHERE retour_declare = 1)   AS retours_declares;

-- ---------------------------------------------------------------------------
-- Étape 2 — combien de codes saisis ne correspondent à aucun patient listé ?
-- ---------------------------------------------------------------------------
SELECT '2. codes orphelins' AS etape;
SELECT v.code_patient_saisi, v.agent, v.date_visite
FROM visites_tracage v
LEFT JOIN liste_iit l ON l.code_patient = v.code_patient_saisi
WHERE l.code_patient IS NULL;

-- Normalisation : majuscules, espace remplacé par un tiret.
SELECT '2b. orphelins apres normalisation' AS etape;
SELECT v.code_patient_saisi,
       UPPER(REPLACE(TRIM(v.code_patient_saisi), ' ', '-')) AS code_normalise
FROM visites_tracage v
LEFT JOIN liste_iit l
       ON l.code_patient = UPPER(REPLACE(TRIM(v.code_patient_saisi), ' ', '-'))
WHERE l.code_patient IS NULL;

-- ---------------------------------------------------------------------------
-- Étape 3 — les visites en double : un patient, plusieurs lignes.
-- ---------------------------------------------------------------------------
SELECT '3. doublons' AS etape;
WITH v AS (
    SELECT *, UPPER(REPLACE(TRIM(code_patient_saisi), ' ', '-')) AS code
    FROM visites_tracage
)
SELECT code, COUNT(*) AS nb_visites, GROUP_CONCAT(agent, ' + ') AS agents
FROM v
GROUP BY code
HAVING COUNT(*) > 1;

-- ---------------------------------------------------------------------------
-- La vue de travail des étapes 4 à 7 : une visite par patient listé (la plus
-- ancienne), le retour VÉRIFIÉ par une dispensation d'ARV dans les 30 jours
-- qui suivent la visite, sur n'importe quel site, et le drapeau « faux IIT » :
-- le patient était couvert par une dispensation d'un AUTRE site à la date de
-- la liste, donc il n'avait jamais interrompu.
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS tracage_propre;
CREATE TEMP VIEW tracage_propre AS
WITH v AS (
    SELECT *, UPPER(REPLACE(TRIM(code_patient_saisi), ' ', '-')) AS code,
           ROW_NUMBER() OVER (
               PARTITION BY UPPER(REPLACE(TRIM(code_patient_saisi), ' ', '-'))
               ORDER BY date_visite, visite_id) AS rang
    FROM visites_tracage
)
SELECT l.code_patient, l.site, l.date_listage,
       v.visite_id IS NOT NULL                       AS visite,
       COALESCE(v.resultat = 'joint', 0)             AS joint,
       COALESCE(v.retour_declare, 0)                 AS retour_declare,
       COALESCE((
           SELECT 1 FROM dispensations d
           WHERE d.code_patient = l.code_patient
             AND julianday(d.date_dispensation) >  julianday(v.date_visite)
             AND julianday(d.date_dispensation) <= julianday(v.date_visite) + 30
       ), 0)                                         AS retour_verifie,
       EXISTS (
           SELECT 1 FROM dispensations d
           WHERE d.code_patient = l.code_patient
             AND d.site_dispensation <> l.site
             AND d.date_dispensation < l.date_listage
             AND julianday(d.date_dispensation) + d.jours_fournis + 28
                 >= julianday(l.date_listage)
       )                                             AS faux_iit
FROM liste_iit l
LEFT JOIN v ON v.code = l.code_patient AND v.rang = 1;

-- ---------------------------------------------------------------------------
-- Étape 4 — la cascade vérifiée, avant le contrôle d'identité nationale.
-- ---------------------------------------------------------------------------
SELECT '4. cascade verifiee' AS etape;
SELECT COUNT(*)                                   AS listes,
       SUM(visite)                                AS visites_uniques,
       SUM(joint)                                 AS joints,
       SUM(retour_declare)                        AS retours_declares,
       SUM(retour_verifie)                        AS retours_verifies,
       SUM(retour_declare AND retour_verifie)     AS declares_et_verifies,
       ROUND(1.0 * SUM(retour_declare AND retour_verifie)
             / SUM(retour_declare), 2)            AS facteur_verification
FROM tracage_propre;

-- ---------------------------------------------------------------------------
-- Étape 5 — les faux IIT : listés par leur site, mais servis ailleurs.
-- Combien, et combien d'entre eux passent pour des « retours vérifiés » ?
-- ---------------------------------------------------------------------------
SELECT '5. faux IIT' AS etape;
SELECT SUM(faux_iit)                              AS faux_iit,
       COUNT(*)                                   AS listes,
       ROUND(100.0 * SUM(faux_iit) / COUNT(*), 1) AS pct_liste,
       SUM(faux_iit AND retour_verifie)           AS faux_retours_verifies,
       SUM(faux_iit AND retour_declare)           AS faux_retours_declares
FROM tracage_propre;

-- ---------------------------------------------------------------------------
-- Étape 6 — la cascade propre : les faux IIT sortent du dénominateur ET du
-- numérateur. C'est le chiffre qu'on peut présenter à un vérificateur.
-- ---------------------------------------------------------------------------
SELECT '6. cascade propre' AS etape;
SELECT COUNT(*)                                   AS vrais_iit,
       SUM(visite)                                AS visites,
       SUM(joint)                                 AS joints,
       SUM(retour_declare)                        AS retours_declares,
       SUM(retour_verifie)                        AS retours_verifies,
       ROUND(1.0 * SUM(retour_declare AND retour_verifie)
             / SUM(retour_declare), 2)            AS facteur_verification,
       ROUND(100.0 * SUM(retour_verifie) / COUNT(*), 1) AS pct_revenus
FROM tracage_propre
WHERE NOT faux_iit;

-- ---------------------------------------------------------------------------
-- Étape 7 — le tableau par site qui alimente le tableau de bord.
-- ---------------------------------------------------------------------------
SELECT '7. par site' AS etape;
SELECT site,
       COUNT(*)                                   AS listes,
       SUM(faux_iit)                              AS faux_iit,
       SUM(NOT faux_iit)                          AS vrais_iit,
       SUM(visite AND NOT faux_iit)               AS visites,
       SUM(retour_declare AND NOT faux_iit)       AS declares,
       SUM(retour_verifie AND NOT faux_iit)       AS verifies,
       ROUND(100.0 * SUM(retour_verifie AND NOT faux_iit)
             / SUM(NOT faux_iit), 1)              AS pct_revenus
FROM tracage_propre
GROUP BY site
ORDER BY site;

-- ---------------------------------------------------------------------------
-- Étape 8 (module 04) — la file active au 31 mai 2026, vue par chaque site
-- (ses seules dispensations) puis au niveau national (toutes les
-- dispensations du patient). Actif = ARV couvrant la date, délai de grâce
-- de 28 jours compris.
-- ---------------------------------------------------------------------------
SELECT '8. file active site / national' AS etape;
WITH ref AS (SELECT '2026-05-31' AS d),
actif AS (
    SELECT p.code_patient, p.site_rattache,
           EXISTS (SELECT 1 FROM dispensations x, ref
                   WHERE x.code_patient = p.code_patient
                     AND x.site_dispensation = p.site_rattache
                     AND x.date_dispensation <= ref.d
                     AND julianday(x.date_dispensation) + x.jours_fournis + 28
                         >= julianday(ref.d))                AS actif_vu_du_site,
           EXISTS (SELECT 1 FROM dispensations x, ref
                   WHERE x.code_patient = p.code_patient
                     AND x.date_dispensation <= ref.d
                     AND julianday(x.date_dispensation) + x.jours_fournis + 28
                         >= julianday(ref.d))                AS actif_national
    FROM patients p
)
SELECT site_rattache AS site,
       SUM(actif_vu_du_site)                           AS tx_curr_site,
       SUM(actif_national)                             AS tx_curr_national,
       SUM(actif_national) - SUM(actif_vu_du_site)     AS ecart
FROM actif
GROUP BY site_rattache
UNION ALL
SELECT 'TOTAL', SUM(actif_vu_du_site), SUM(actif_national),
       SUM(actif_national) - SUM(actif_vu_du_site)
FROM actif;
