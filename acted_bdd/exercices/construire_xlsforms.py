#!/usr/bin/env python3
# Gist: construire_xlsforms.py
#
# Use Case  : produire les deux formulaires XLSForm du poste ACTED — ciblage de menages
#             et enquete post-distribution (PDM) sur transfert monetaire.
# Purpose   : montrer le codage de formules avancees demande par le TDR : score de
#             vulnerabilite calcule dans le formulaire, Food Consumption Score, rCSI
#             reduit, listes en cascade, controles de coherence et consentement bloquant.
# Key points: les deux classeurs sont valides par pyxform avant ecriture, donc deployables
#             tels quels sur KoboToolbox.
#
# Execution : python3 construire_xlsforms.py
# Sortie    : xlsform_ciblage_menage.xlsx, xlsform_pdm_cash.xlsx

import os

import pandas as pd

RACINE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------------------
# Formulaire 1 — Ciblage des menages
# --------------------------------------------------------------------------------------

CIBLAGE_SURVEY = [
    # type, name, label::Francais (fr), label::Kreyol (ht), autres colonnes
    ("start", "start", "", "", "", "", "", "", ""),
    ("end", "end", "", "", "", "", "", "", ""),
    ("today", "today", "", "", "", "", "", "", ""),
    ("deviceid", "deviceid", "", "", "", "", "", "", ""),
    ("username", "enqueteur", "", "", "", "", "", "", ""),

    ("note", "note_intro",
     "Bonjour. ACTED enregistre les menages pour une possible assistance. "
     "Les informations restent confidentielles, ne sont partagees qu'avec nos equipes, "
     "et sont conservees le temps du projet. Refuser ne retire aucun droit a l'assistance.",
     "Bonjou. ACTED ap anrejistre fanmi yo pou yon asistans posib. "
     "Enfomasyon yo rete konfidansyel.", "", "", "", "", ""),
    ("select_one oui_non", "consentement",
     "Acceptez-vous de repondre a ce questionnaire ?",
     "Eske ou dakò reponn kesyonè sa a ?", "yes", "", "", "", ""),
    ("note", "note_refus", "Merci. L'entretien s'arrete ici.", "Mèsi. Antretyen an fini la.",
     "", "selected(${consentement}, 'non')", "", "", ""),

    ("begin_group", "grp_localisation", "Localisation", "Kote", "", "selected(${consentement}, 'oui')", "", "", ""),
    ("select_one departements", "departement", "Departement", "Depatman", "yes", "", "", "", ""),
    ("select_one communes", "commune", "Commune", "Komin", "yes", "", "", "departement=${departement}", ""),
    ("select_one sites", "code_site", "Site d'intervention", "Sit entèvansyon", "yes", "", "", "commune=${commune}", ""),
    ("geopoint", "gps", "Coordonnees GPS du menage", "Kowòdone GPS fanmi an", "yes", "", "", "", ""),
    ("end_group", "grp_localisation", "", "", "", "", "", "", ""),

    ("begin_group", "grp_chef", "Chef de menage", "Chèf fanmi", "", "selected(${consentement}, 'oui')", "", "", ""),
    ("text", "nom_chef", "Nom de famille", "Siyati", "yes", "", "", "", ""),
    ("text", "prenom_chef", "Prenom", "Prenon", "yes", "", "", "", ""),
    ("select_one sexe", "sexe_chef", "Sexe", "Sèks", "yes", "", "", "", ""),
    ("date", "date_naissance_chef", "Date de naissance", "Dat nesans", "yes", "",
     ". <= today() and . >= date('1920-01-01')", "", ""),
    ("text", "piece_identite", "Numero de piece d'identite (NIF/CIN)", "Nimewo kat idantite", "",
     "", "regex(., '^[0-9]{7}-[0-9]$')", "", ""),
    ("text", "telephone", "Telephone", "Telefòn", "", "", "regex(., '^\\+509[0-9]{8}$')", "", ""),
    ("end_group", "grp_chef", "", "", "", "", "", "", ""),

    ("begin_group", "grp_composition", "Composition du menage", "Konpozisyon fanmi an", "",
     "selected(${consentement}, 'oui')", "", "", ""),
    ("integer", "taille_menage", "Nombre total de personnes vivant dans le menage",
     "Konbyen moun ki abite nan kay la", "yes", "", ". >= 1 and . <= 20", "", ""),
    ("integer", "nb_enfants_moins5", "Dont enfants de moins de 5 ans",
     "Timoun ki poko gen 5 an", "yes", "", ". >= 0 and . <= ${taille_menage}", "", ""),
    ("integer", "nb_femmes_enceintes", "Dont femmes enceintes ou allaitantes",
     "Fanm ansent oswa k ap bay tete", "yes", "", ". >= 0 and . <= ${taille_menage}", "", ""),
    ("integer", "nb_handicap", "Dont personnes en situation de handicap",
     "Moun ki gen andikap", "yes", "", ". >= 0 and . <= ${taille_menage}", "", ""),
    ("select_one statut_deplacement", "statut_deplacement", "Statut de deplacement",
     "Estati deplasman", "yes", "", "", "", ""),
    ("end_group", "grp_composition", "", "", "", "", "", "", ""),

    # --- Score de vulnerabilite calcule dans le formulaire ---------------------------
    ("begin_group", "grp_score", "Score de vulnerabilite", "Nòt vilnerabilite", "",
     "selected(${consentement}, 'oui')", "", "", ""),
    ("calculate", "pts_taille", "", "", "", "", "", "", "min(${taille_menage}, 10) * 4"),
    ("calculate", "pts_enfants", "", "", "", "", "", "", "${nb_enfants_moins5} * 7"),
    ("calculate", "pts_enceintes", "", "", "", "", "", "", "${nb_femmes_enceintes} * 6"),
    ("calculate", "pts_handicap", "", "", "", "", "", "", "${nb_handicap} * 8"),
    ("calculate", "pts_sexe", "", "", "", "", "", "",
     "if(selected(${sexe_chef}, 'F'), 10, 0)"),
    ("calculate", "pts_deplacement", "", "", "", "", "", "",
     "if(selected(${statut_deplacement}, 'deplace'), 15, "
     "if(selected(${statut_deplacement}, 'retourne'), 10, "
     "if(selected(${statut_deplacement}, 'hote'), 8, 0)))"),
    ("calculate", "score_vulnerabilite", "", "", "", "", "", "",
     "min(100, ${pts_taille} + ${pts_enfants} + ${pts_enceintes} + ${pts_handicap} "
     "+ ${pts_sexe} + ${pts_deplacement})"),
    ("note", "note_score", "Score calcule : ${score_vulnerabilite} / 100",
     "Nòt : ${score_vulnerabilite} / 100", "", "", "", "", ""),
    ("calculate", "proposition_selection", "", "", "", "", "", "",
     "if(${score_vulnerabilite} >= 44, 'Selectionne', "
     "if(${score_vulnerabilite} >= 36, 'En attente', 'Non selectionne'))"),
    ("note", "note_proposition",
     "Proposition automatique : ${proposition_selection}. La decision finale appartient "
     "au comite de ciblage communautaire.",
     "Pwopozisyon otomatik : ${proposition_selection}.", "", "", "", "", ""),
    ("end_group", "grp_score", "", "", "", "", "", "", ""),

    ("begin_group", "grp_controle", "Controle de saisie", "Kontwòl", "",
     "selected(${consentement}, 'oui')", "", "", ""),
    ("calculate", "somme_categories", "", "", "", "", "", "",
     "${nb_enfants_moins5} + ${nb_femmes_enceintes} + ${nb_handicap}"),
    ("note", "alerte_coherence",
     "ATTENTION : la somme des categories vulnerables depasse la taille du menage. "
     "Verifiez avant d'envoyer.",
     "ATANSYON : verifye chif yo.", "", "${somme_categories} > ${taille_menage}", "", "", ""),
    ("select_one oui_non", "confirmation_agent",
     "Confirmez-vous avoir verifie les informations avec le chef de menage ?",
     "Eske ou verifye enfòmasyon yo ?", "yes", "", "selected(., 'oui')", "", ""),
    ("end_group", "grp_controle", "", "", "", "", "", "", ""),
]

CIBLAGE_COLONNES = ["type", "name", "label::Francais (fr)", "label::Kreyol (ht)",
                    "required", "relevant", "constraint", "choice_filter", "calculation"]

CHOIX_COMMUNS = [
    # list_name, name, label fr, label ht, filtres
    ("oui_non", "oui", "Oui", "Wi", "", ""),
    ("oui_non", "non", "Non", "Non", "", ""),
    ("sexe", "F", "Feminin", "Fi", "", ""),
    ("sexe", "M", "Masculin", "Gason", "", ""),
    ("statut_deplacement", "deplace", "Deplace", "Deplase", "", ""),
    ("statut_deplacement", "hote", "Famille hote", "Fanmi ki resevwa", "", ""),
    ("statut_deplacement", "residant", "Residant", "Rezidan", "", ""),
    ("statut_deplacement", "retourne", "Retourne", "Retounen", "", ""),
    ("departements", "HT03", "Artibonite", "Latibonit", "", ""),
    ("departements", "HT01", "Ouest", "Lwès", "", ""),
    ("departements", "HT02", "Centre", "Sant", "", ""),
    ("departements", "HT04", "Nord", "Nò", "", ""),
    ("communes", "HT0311", "Gonaives", "Gonayiv", "HT03", ""),
    ("communes", "HT0321", "Saint-Marc", "Sen Mak", "HT03", ""),
    ("communes", "HT0331", "Dessalines", "Desalin", "HT03", ""),
    ("communes", "HT0111", "Port-au-Prince", "Pòtoprens", "HT01", ""),
    ("communes", "HT0121", "Croix-des-Bouquets", "Kwadèboukè", "HT01", ""),
    ("communes", "HT0211", "Mirebalais", "Mibalè", "HT02", ""),
    ("communes", "HT0411", "Cap-Haitien", "Okap", "HT04", ""),
    ("sites", "S001", "Gonaives - Site 1", "Gonayiv - Sit 1", "", "HT0311"),
    ("sites", "S002", "Gonaives - Site 2", "Gonayiv - Sit 2", "", "HT0311"),
    ("sites", "S005", "Saint-Marc - Site 1", "Sen Mak - Sit 1", "", "HT0321"),
    ("sites", "S009", "Dessalines - Site 1", "Desalin - Sit 1", "", "HT0331"),
    ("sites", "S014", "Port-au-Prince - Site 1", "Pòtoprens - Sit 1", "", "HT0111"),
    ("sites", "S019", "Croix-des-Bouquets - Site 1", "Kwadèboukè - Sit 1", "", "HT0121"),
    ("sites", "S027", "Mirebalais - Site 1", "Mibalè - Sit 1", "", "HT0211"),
    ("sites", "S034", "Cap-Haitien - Site 1", "Okap - Sit 1", "", "HT0411"),
]

CHOIX_COLONNES = ["list_name", "name", "label::Francais (fr)", "label::Kreyol (ht)",
                  "departement", "commune"]

# --------------------------------------------------------------------------------------
# Formulaire 2 — PDM sur transfert monetaire
# --------------------------------------------------------------------------------------

# Les huit groupes alimentaires du Food Consumption Score et leur ponderation
# nutritionnelle standard (PAM). La ponderation est la partie que les enqueteurs
# ne doivent jamais avoir a calculer de tete : le formulaire s'en charge.
GROUPES_FCS = [
    ("cereales", "Cereales, tubercules (riz, mais, banane, patate)", "Sereyal, tibèkil", 2),
    ("legumineuses", "Legumineuses (pois, haricots, arachide)", "Pwa", 3),
    ("legumes", "Legumes et feuilles", "Legim ak fèy", 1),
    ("fruits", "Fruits", "Fwi", 1),
    ("proteines", "Viande, poisson, oeufs", "Vyann, pwason, ze", 4),
    ("lait", "Lait et produits laitiers", "Lèt", 4),
    ("sucre", "Sucre et produits sucres", "Sik", 0.5),
    ("huile", "Huile, graisses, beurre", "Lwil, grès", 0.5),
]

# Les cinq strategies de survie du rCSI et leur severite standard.
STRATEGIES_RCSI = [
    ("aliments_moins_chers", "Consommer des aliments moins preferes ou moins chers",
     "Manje manje ki mwen chè", 1),
    ("emprunter", "Emprunter de la nourriture ou compter sur l'aide de proches",
     "Prete manje", 2),
    ("reduire_portions", "Reduire la taille des portions", "Diminye pòsyon", 1),
    ("restreindre_adultes", "Restreindre la consommation des adultes au profit des enfants",
     "Granmoun manje mwens", 3),
    ("reduire_repas", "Reduire le nombre de repas par jour", "Diminye kantite repa", 1),
]


def construire_pdm_survey():
    lignes = [
        ("start", "start", "", "", "", "", "", ""),
        ("end", "end", "", "", "", "", "", ""),
        ("today", "today", "", "", "", "", "", ""),
        ("username", "enqueteur", "", "", "", "", "", ""),
        ("note", "note_intro",
         "Enquete post-distribution ACTED. Vos reponses n'ont aucune consequence sur "
         "une assistance future et restent confidentielles.",
         "Ankèt apre distribisyon ACTED.", "", "", "", ""),
        ("select_one oui_non", "consentement", "Acceptez-vous de repondre ?",
         "Eske ou dakò reponn ?", "yes", "", "", ""),

        ("begin_group", "grp_identification", "Identification", "Idantifikasyon", "",
         "selected(${consentement}, 'oui')", "", ""),
        ("text", "code_menage", "Code menage (sur la carte du beneficiaire)",
         "Kòd fanmi", "yes", "", "regex(., '^MEN-[0-9]{5}$')", ""),
        ("select_one oui_non", "carte_presentee", "La carte a-t-elle ete presentee ?",
         "Eske kat la prezante ?", "yes", "", "", ""),
        ("geopoint", "gps", "Coordonnees GPS", "Kowòdone GPS", "yes", "", "", ""),
        ("end_group", "grp_identification", "", "", "", "", "", ""),

        ("begin_group", "grp_transfert", "Reception du transfert", "Resepsyon lajan an", "",
         "selected(${consentement}, 'oui')", "", ""),
        ("select_one oui_non", "a_recu", "Avez-vous recu le transfert monetaire ?",
         "Eske ou resevwa lajan an ?", "yes", "", "", ""),
        ("integer", "montant_recu_htg", "Montant recu en gourdes",
         "Konbyen goud ou resevwa", "yes", "selected(${a_recu}, 'oui')",
         ". >= 0 and . <= 50000", ""),
        ("integer", "delai_reception_jours",
         "Combien de jours entre l'annonce et la reception ?",
         "Konbyen jou ant anons la ak resepsyon an", "yes",
         "selected(${a_recu}, 'oui')", ". >= 0 and . <= 180", ""),
        ("select_one usages", "utilisation_principale", "Usage principal du transfert",
         "Kisa ou fè ak lajan an", "yes", "selected(${a_recu}, 'oui')", "", ""),
        ("select_one raisons_non", "raison_non_reception", "Pourquoi n'avez-vous rien recu ?",
         "Poukisa ou pa resevwa anyen ?", "yes", "selected(${a_recu}, 'non')", "", ""),
        ("end_group", "grp_transfert", "", "", "", "", "", ""),
    ]

    # --- Module FCS -------------------------------------------------------------------
    lignes.append(("begin_group", "grp_fcs",
                   "Consommation alimentaire des 7 derniers jours",
                   "Konsomasyon manje 7 dènye jou yo", "",
                   "selected(${consentement}, 'oui')", "", ""))
    lignes.append(("note", "note_fcs",
                   "Pour chaque groupe, indiquez le nombre de jours de consommation "
                   "sur les 7 derniers jours (0 a 7).",
                   "Pou chak gwoup, di konbyen jou sou 7 jou yo.", "", "", "", ""))
    for nom, label_fr, label_ht, _poids in GROUPES_FCS:
        lignes.append(("integer", f"fcs_{nom}", label_fr, label_ht, "yes", "",
                       ". >= 0 and . <= 7", ""))
    formule_fcs = " + ".join(f"${{fcs_{nom}}} * {poids}" for nom, _f, _h, poids in GROUPES_FCS)
    lignes.append(("calculate", "score_fcs", "", "", "", "", "", formule_fcs))
    lignes.append(("calculate", "classe_fcs", "", "", "", "", "",
                   "if(${score_fcs} <= 21, 'Pauvre', "
                   "if(${score_fcs} <= 35, 'Limite', 'Acceptable'))"))
    lignes.append(("note", "note_fcs_resultat",
                   "Score de consommation alimentaire : ${score_fcs} — ${classe_fcs}",
                   "Nòt konsomasyon : ${score_fcs} — ${classe_fcs}", "", "", "", ""))
    lignes.append(("end_group", "grp_fcs", "", "", "", "", "", ""))

    # --- Module rCSI ------------------------------------------------------------------
    lignes.append(("begin_group", "grp_rcsi",
                   "Strategies de survie alimentaire (7 derniers jours)",
                   "Estrateji siviv (7 dènye jou)", "",
                   "selected(${consentement}, 'oui')", "", ""))
    for nom, label_fr, label_ht, _sev in STRATEGIES_RCSI:
        lignes.append(("integer", f"rcsi_{nom}", label_fr, label_ht, "yes", "",
                       ". >= 0 and . <= 7", ""))
    formule_rcsi = " + ".join(f"${{rcsi_{nom}}} * {sev}" for nom, _f, _h, sev in STRATEGIES_RCSI)
    lignes.append(("calculate", "score_rcsi", "", "", "", "", "", formule_rcsi))
    lignes.append(("note", "note_rcsi",
                   "Indice reduit des strategies de survie : ${score_rcsi} (0 a 56)",
                   "Endis rCSI : ${score_rcsi}", "", "", "", ""))
    lignes.append(("end_group", "grp_rcsi", "", "", "", "", "", ""))

    # --- Redevabilite -----------------------------------------------------------------
    lignes += [
        ("begin_group", "grp_redevabilite", "Redevabilite", "Redevabilite", "",
         "selected(${consentement}, 'oui')", "", ""),
        ("select_one satisfaction", "satisfaction",
         "Globalement, etes-vous satisfait de l'assistance recue ?",
         "Èske ou satisfè ?", "yes", "", "", ""),
        ("select_one oui_non", "connait_mecanisme_plainte",
         "Savez-vous comment deposer une plainte aupres d'ACTED ?",
         "Eske ou konnen kijan pou pote plent ?", "yes", "", "", ""),
        ("select_multiple canaux", "canaux_connus", "Par quels canaux ?", "Ki jan ?", "",
         "selected(${connait_mecanisme_plainte}, 'oui')", "", ""),
        ("select_one oui_non", "a_paye", "Avez-vous du payer quoi que ce soit pour recevoir l'aide ?",
         "Eske ou te oblije peye yon bagay ?", "yes", "", "", ""),
        ("text", "precision_paiement", "Precisez", "Presize", "yes",
         "selected(${a_paye}, 'oui')", "", ""),
        ("note", "note_alerte_paiement",
         "ALERTE : signalez immediatement au responsable MEAL a la fin de la journee. "
         "Ne discutez de ce cas avec personne d'autre.",
         "ALÈT : rapòte bay responsab MEAL la.", "",
         "selected(${a_paye}, 'oui')", "", ""),
        ("end_group", "grp_redevabilite", "", "", "", "", "", ""),

        ("calculate", "duree_entretien_min", "", "", "", "", "",
         "int((decimal-date-time(${end}) - decimal-date-time(${start})) * 1440)"),
    ]
    return lignes


PDM_COLONNES = ["type", "name", "label::Francais (fr)", "label::Kreyol (ht)",
                "required", "relevant", "constraint", "calculation"]

PDM_CHOIX = [
    ("oui_non", "oui", "Oui", "Wi"),
    ("oui_non", "non", "Non", "Non"),
    ("usages", "nourriture", "Nourriture", "Manje"),
    ("usages", "sante", "Sante", "Sante"),
    ("usages", "education", "Education (frais scolaires)", "Lekòl"),
    ("usages", "dette", "Remboursement de dette", "Peye dèt"),
    ("usages", "agriculture", "Intrants agricoles", "Semans, zouti"),
    ("usages", "logement", "Logement, reparation", "Kay"),
    ("usages", "autre", "Autre", "Lòt"),
    ("raisons_non", "pas_informe", "Je n'ai pas ete informe", "Yo pa t di m"),
    ("raisons_non", "absent", "J'etais absent le jour de la distribution", "M pa t la"),
    ("raisons_non", "probleme_carte", "Probleme de carte ou d'identification", "Pwoblèm kat"),
    ("raisons_non", "probleme_operateur", "Probleme avec l'operateur de paiement", "Pwoblèm ak konpayi an"),
    ("raisons_non", "autre", "Autre", "Lòt"),
    ("satisfaction", "1", "Tres insatisfait", "Pa satisfè ditou"),
    ("satisfaction", "2", "Insatisfait", "Pa satisfè"),
    ("satisfaction", "3", "Neutre", "Nan mitan"),
    ("satisfaction", "4", "Satisfait", "Satisfè"),
    ("satisfaction", "5", "Tres satisfait", "Trè satisfè"),
    ("canaux", "ligne_verte", "Ligne telephonique gratuite", "Liy telefòn gratis"),
    ("canaux", "boite", "Boite a suggestions", "Bwat sijesyon"),
    ("canaux", "agent", "Agent de terrain", "Ajan sou teren an"),
    ("canaux", "comite", "Comite communautaire", "Komite kominotè"),
]

PDM_CHOIX_COLONNES = ["list_name", "name", "label::Francais (fr)", "label::Kreyol (ht)"]


def ecrire(chemin, survey, colonnes_survey, choices, colonnes_choices, settings):
    with pd.ExcelWriter(chemin, engine="openpyxl") as writer:
        pd.DataFrame(survey, columns=colonnes_survey).to_excel(
            writer, sheet_name="survey", index=False)
        pd.DataFrame(choices, columns=colonnes_choices).to_excel(
            writer, sheet_name="choices", index=False)
        pd.DataFrame([settings]).to_excel(writer, sheet_name="settings", index=False)
    print(f"Ecrit : {os.path.basename(chemin)}  ({len(survey)} lignes de survey)")


def valider(chemin):
    """Compile le classeur avec pyxform : c'est le meme moteur que KoboToolbox."""
    from pyxform.xls2xform import convert
    resultat = convert(chemin)
    avertissements = getattr(resultat, "warnings", []) or []
    print(f"  pyxform : compilation reussie, {len(avertissements)} avertissement(s)")
    for a in avertissements[:5]:
        print(f"    - {a}")


if __name__ == "__main__":
    chemin_ciblage = os.path.join(RACINE, "xlsform_ciblage_menage.xlsx")
    ecrire(chemin_ciblage, CIBLAGE_SURVEY, CIBLAGE_COLONNES,
           CHOIX_COMMUNS, CHOIX_COLONNES,
           {"form_title": "ACTED Haiti - Ciblage des menages",
            "form_id": "acted_ciblage_menage_v1",
            "default_language": "Francais (fr)",
            "version": "2026072901"})
    valider(chemin_ciblage)

    chemin_pdm = os.path.join(RACINE, "xlsform_pdm_cash.xlsx")
    ecrire(chemin_pdm, construire_pdm_survey(), PDM_COLONNES,
           PDM_CHOIX, PDM_CHOIX_COLONNES,
           {"form_title": "ACTED Haiti - PDM transfert monetaire",
            "form_id": "acted_pdm_cash_v1",
            "default_language": "Francais (fr)",
            "version": "2026072901"})
    valider(chemin_pdm)
