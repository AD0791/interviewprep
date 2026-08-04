#!/usr/bin/env python3
# Gist: build_dataset.py
#
# Use Case  : practice dataset for the Remote Leverage Data Analyst interview (3 Aug 2026).
# Purpose   : reproduce the business a VA-placement agency actually runs on — leads and
#             marketing spend on the way in, vacancies and a candidate submittal funnel in
#             the middle, placements and fees on the way out — so every metric named in the
#             job description can be computed for real.
# Key points: deterministic (fixed seed); CSV output that Tableau Public reads directly;
#             a DuckDB file for SQL practice in a dialect close to BigQuery; and seven
#             deliberate data-quality defects so the "validation and reconciliation"
#             responsibility can be demonstrated rather than described.
#
# Run: python3 build_dataset.py
# Out: csv/*.csv  and  agency.duckdb

import csv
import os
import random
from datetime import date, timedelta

RACINE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(RACINE, "csv")

random.seed(20260803)  # interview date

DEBUT = date(2025, 1, 1)
FIN = date(2026, 7, 26)          # last full week before the interview
JOURS = (FIN - DEBUT).days

# --------------------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------------------

CHANNELS = ["Paid Search", "Paid Social", "Organic", "Referral", "Outbound"]
CHANNEL_WEIGHTS = [30, 22, 20, 16, 12]

CAMPAIGNS = {
    "Paid Search": ["gs_va_hire", "gs_latam_talent", "gs_competitor"],
    "Paid Social": ["fb_founders", "li_agency_owners", "fb_retarget"],
    "Organic": ["blog", "seo_landing"],
    "Referral": ["client_referral", "partner"],
    "Outbound": ["cold_email_q1", "cold_email_q2", "linkedin_dm"],
}

INDUSTRIES = ["Real Estate", "E-commerce", "Marketing Agency", "Insurance",
              "Healthcare", "Construction", "SaaS", "Legal", "Logistics"]
SIZES = ["1-10", "11-50", "51-200", "200+"]

ROLE_FAMILIES = {
    "Sales VA":        ["Sales Development Rep", "Appointment Setter", "Cold Caller"],
    "Executive VA":    ["Executive Assistant", "Operations Assistant"],
    "Marketing VA":    ["Social Media Manager", "Content Writer", "Email Marketer"],
    "Bookkeeping":     ["Bookkeeper", "Accounts Payable Clerk"],
    "Customer Support": ["Customer Support Agent", "Helpdesk Agent"],
    "Technical":       ["Data Analyst", "Web Developer", "Automation Specialist"],
}

COUNTRIES = ["Colombia", "Mexico", "Argentina", "Philippines", "Peru",
             "Venezuela", "Dominican Republic", "Haiti", "Brazil", "Guatemala"]
COUNTRY_WEIGHTS = [22, 16, 12, 20, 8, 7, 5, 3, 4, 3]

ENGLISH = ["B1", "B2", "C1", "C2"]
ENGLISH_WEIGHTS = [18, 42, 30, 10]

CANDIDATE_SOURCES = ["Job Board", "Referral", "LinkedIn", "Facebook Group", "Website"]

REJECT_REASONS = ["English level", "Rate expectation", "Availability",
                  "Skill mismatch", "Client cancelled", "Candidate withdrew",
                  "Client chose other candidate"]

PIPELINES = ["ats_submittals", "ats_vacancies", "stripe_invoices",
             "ga4_sessions", "ads_spend", "hubspot_leads"]

# Les commerciaux : nom, facteur de reussite, quota mensuel de clients signes,
# date d'entree. Les facteurs different volontairement pour que le classement par
# taux de conversion soit exploitable — et le piege est que le meilleur taux
# n'appartient pas au commercial qui signe le plus de clients.
SALES_REPS = [
    dict(rep="Dana Whitfield",  skill=1.35, quota=8, hired="2025-01-01"),
    dict(rep="Marcus Lee",      skill=1.10, quota=8, hired="2025-01-01"),
    dict(rep="Priya Raman",     skill=0.95, quota=8, hired="2025-03-01"),
    dict(rep="Tomas Ferreira",  skill=0.80, quota=6, hired="2025-06-01"),
    dict(rep="Alicia Moreno",   skill=1.05, quota=6, hired="2025-09-15"),
]

LOST_REASONS = ["Price", "Went with competitor", "No budget", "Timing",
                "No response", "Not a fit"]

PRENOMS = ["Maria", "Juan", "Camila", "Andres", "Sofia", "Diego", "Valentina",
           "Carlos", "Ana", "Luis", "Isabella", "Miguel", "Daniela", "Jose",
           "Angelica", "Ricardo", "Paula", "Jorge", "Laura", "Fernando"]
NOMS = ["Gomez", "Rodriguez", "Martinez", "Santos", "Reyes", "Cruz", "Torres",
        "Ramirez", "Flores", "Castillo", "Mendoza", "Vargas", "Delgado", "Rojas"]

ENTREPRISES = ["Summit", "Blue Harbor", "Northgate", "Ironwood", "Clearview",
               "Redstone", "Pinnacle", "Silverline", "Oakfield", "Brightpath",
               "Cedar Creek", "Vantage", "Kingsley", "Westbrook", "Lakeshore"]
SUFFIXES = ["Group", "Partners", "LLC", "Realty", "Media", "Solutions", "Capital"]


def jour(offset):
    return DEBUT + timedelta(days=offset)


def choisir(options, poids):
    return random.choices(options, weights=poids)[0]


def saisonnalite(d):
    """Le volume d'affaires respire : creux en decembre, pic au printemps."""
    facteur = {12: 0.6, 1: 0.85, 7: 0.9, 8: 0.95}.get(d.month, 1.0)
    if d.weekday() >= 5:
        facteur *= 0.25
    return facteur


# --------------------------------------------------------------------------------------
# 1. Marketing spend and leads
# --------------------------------------------------------------------------------------

def construire_marketing():
    spend, leads = [], []
    id_lead = 1
    # Cout par clic et taux de conversion propres a chaque canal : c'est ce qui fera
    # diverger le CPL et le CAC entre canaux, donc ce qui rend l'analyse interessante.
    profil = {
        "Paid Search": dict(cpc=3.10, ctr=0.042, lead_rate=0.085, budget=420),
        "Paid Social": dict(cpc=1.35, ctr=0.019, lead_rate=0.045, budget=310),
        "Organic":     dict(cpc=0.00, ctr=0.000, lead_rate=0.000, budget=0),
        "Referral":    dict(cpc=0.00, ctr=0.000, lead_rate=0.000, budget=0),
        "Outbound":    dict(cpc=0.00, ctr=0.000, lead_rate=0.000, budget=95),
    }

    for offset in range(JOURS + 1):
        d = jour(offset)
        f = saisonnalite(d)
        for canal in CHANNELS:
            p = profil[canal]
            if p["budget"] == 0:
                continue
            depense = round(p["budget"] * f * random.uniform(0.7, 1.3), 2)
            clics = int(depense / p["cpc"]) if p["cpc"] else 0
            impressions = int(clics / p["ctr"]) if p["ctr"] else 0
            campagne = random.choice(CAMPAIGNS[canal])
            # Defaut qualite n°1 : 2 % des lignes de depense arrivent sans campagne,
            # ce qui casse toute attribution si on ne le detecte pas.
            if random.random() < 0.02:
                campagne = ""
            spend.append(dict(spend_date=d.isoformat(), channel=canal, campaign=campagne,
                              spend_usd=depense, impressions=impressions, clicks=clics))

        # Volume de leads du jour, par canal
        volumes = {
            "Paid Search": int(random.gauss(4.2, 1.6) * f),
            "Paid Social": int(random.gauss(2.8, 1.4) * f),
            "Organic":     int(random.gauss(2.1, 1.1) * f),
            "Referral":    int(random.gauss(1.3, 0.9) * f),
            "Outbound":    int(random.gauss(1.7, 1.0) * f),
        }
        for canal, n in volumes.items():
            for _ in range(max(0, n)):
                # Le lead est attribue a un commercial deja en poste ce jour-la.
                disponibles = [r for r in SALES_REPS if date.fromisoformat(r["hired"]) <= d]
                proprietaire = random.choice(disponibles) if disponibles else SALES_REPS[0]
                leads.append(dict(lead_id=f"L{id_lead:05d}", created_date=d.isoformat(),
                                  channel=canal, campaign=random.choice(CAMPAIGNS[canal]),
                                  company_size=random.choice(SIZES),
                                  industry=random.choice(INDUSTRIES),
                                  owner=proprietaire["rep"],
                                  stage="new", first_contact_date="", demo_date="",
                                  closed_date="", lost_reason="",
                                  converted=0, converted_date="", client_id=""))
                id_lead += 1
    return spend, leads


# --------------------------------------------------------------------------------------
# 2. Clients (converted leads)
# --------------------------------------------------------------------------------------

def construire_clients(leads):
    """Les canaux ne convertissent pas au meme rythme : le referral est rare mais
    excellent, le paid social abondant mais faible. C'est exactement l'arbitrage
    qu'un dashboard d'acquisition doit rendre visible."""
    taux = {"Paid Search": 0.085, "Paid Social": 0.042, "Organic": 0.075,
            "Referral": 0.230, "Outbound": 0.055}
    competence = {r["rep"]: r["skill"] for r in SALES_REPS}
    clients = []
    id_client = 1
    for lead in leads:
        # Le canal fixe la qualite du lead, le commercial module la conversion.
        if random.random() > taux[lead["channel"]] * competence[lead["owner"]]:
            continue
        cree = date.fromisoformat(lead["created_date"])
        delai = max(1, int(random.gauss(11, 6)))
        signup = cree + timedelta(days=delai)
        if signup > FIN:
            continue
        code = f"C{id_client:04d}"
        lead["converted"] = 1
        lead["converted_date"] = signup.isoformat()
        lead["client_id"] = code

        # Churn : plus le client est ancien, plus il a eu d'occasions de partir.
        anciennete = (FIN - signup).days
        churned, churn_date = 0, ""
        if anciennete > 60 and random.random() < 0.18:
            jour_churn = signup + timedelta(days=random.randint(60, max(61, anciennete)))
            if jour_churn <= FIN:
                churned, churn_date = 1, jour_churn.isoformat()

        clients.append(dict(
            client_id=code,
            company_name=f"{random.choice(ENTREPRISES)} {random.choice(SUFFIXES)}",
            industry=lead["industry"], company_size=lead["company_size"],
            signup_date=signup.isoformat(), acquisition_channel=lead["channel"],
            acquisition_campaign=lead["campaign"], lead_id=lead["lead_id"],
            status="churned" if churned else "active", churn_date=churn_date))
        id_client += 1
    return clients


# --------------------------------------------------------------------------------------
# 2b. Sales pipeline — stage progression and rep activity
# --------------------------------------------------------------------------------------

def construire_pipeline_ventes(leads):
    """Fait progresser chaque lead dans les etapes commerciales et journalise l'activite.

    Le modele est celui d'un CRM ordinaire : new -> contacted -> demo -> won ou lost.
    Un lead recent et non conclu reste 'open', ce qui est indispensable pour que la
    notion de pipeline ouvert ait un sens — et pour que le calcul du taux de reussite
    pose la meme question de censure que le taux de pourvoi des postes.
    """
    activites = []
    id_act = 1
    for lead in leads:
        cree = date.fromisoformat(lead["created_date"])

        # 8 % des leads ne sont jamais travailles : c'est un vrai chiffre de gestion.
        if random.random() < 0.08 and lead["converted"] == 0:
            lead["stage"] = "new"
            continue

        contact = cree + timedelta(days=max(0, int(random.gauss(1.6, 1.2))))
        if contact > FIN:
            lead["stage"] = "new"
            continue
        lead["first_contact_date"] = contact.isoformat()
        lead["stage"] = "contacted"

        n_appels = max(1, int(random.gauss(3.2, 1.6)))
        n_emails = max(1, int(random.gauss(4.5, 2.0)))
        for i in range(n_appels + n_emails):
            quand = contact + timedelta(days=random.randint(0, 21))
            if quand > FIN:
                continue
            activites.append(dict(
                activity_id=f"A{id_act:06d}", lead_id=lead["lead_id"],
                rep=lead["owner"], activity_date=quand.isoformat(),
                activity_type="call" if i < n_appels else "email",
                connected=1 if (i < n_appels and random.random() < 0.34) else 0))
            id_act += 1

        # Une demo est le vrai point de bascule du cycle de vente.
        a_demo = lead["converted"] == 1 or random.random() < 0.38
        if a_demo:
            demo = contact + timedelta(days=max(1, int(random.gauss(5.5, 3.0))))
            if demo <= FIN:
                lead["demo_date"] = demo.isoformat()
                lead["stage"] = "demo"
                activites.append(dict(
                    activity_id=f"A{id_act:06d}", lead_id=lead["lead_id"],
                    rep=lead["owner"], activity_date=demo.isoformat(),
                    activity_type="demo", connected=1))
                id_act += 1

        if lead["converted"] == 1:
            lead["stage"] = "won"
            lead["closed_date"] = lead["converted_date"]
        else:
            age = (FIN - cree).days
            # Sous 45 jours l'affaire est encore en cours : la marquer perdue
            # fausserait le taux de reussite exactement comme la censure a droite
            # fausse le taux de pourvoi des postes.
            if age < 45:
                lead["stage"] = "open" if lead["stage"] != "new" else "new"
            else:
                perdu = cree + timedelta(days=random.randint(10, min(90, age)))
                lead["stage"] = "lost"
                lead["closed_date"] = perdu.isoformat()
                lead["lost_reason"] = random.choice(LOST_REASONS)
    return activites


# --------------------------------------------------------------------------------------
# 3. Candidates
# --------------------------------------------------------------------------------------

def construire_candidats(n=4200):
    candidats = []
    for i in range(1, n + 1):
        pays = choisir(COUNTRIES, COUNTRY_WEIGHTS)
        anglais = choisir(ENGLISH, ENGLISH_WEIGHTS)
        prenom, nom = random.choice(PRENOMS), random.choice(NOMS)
        candidats.append(dict(
            candidate_id=f"K{i:05d}",
            first_name=prenom, last_name=nom,
            # L'index rend l'adresse unique par construction : les seuls doublons de la
            # table seront ceux injectes volontairement plus bas, donc mesurables.
            email=f"{prenom.lower()}.{nom.lower()}{i}@example.com",
            country=pays, english_level=anglais,
            years_experience=max(0, int(random.gauss(4.5, 2.6))),
            primary_skill=random.choice(list(ROLE_FAMILIES)),
            source_channel=random.choice(CANDIDATE_SOURCES),
            registered_date=jour(random.randint(0, JOURS)).isoformat(),
            expected_rate_usd=random.choice([700, 900, 1100, 1400, 1700, 2000])))
    # Defaut qualite n°2 : 40 candidats reinscrits sous un second identifiant.
    # Meme nom, meme email, identifiant different — le doublon classique d'un ATS.
    for src in random.sample(candidats, 40):
        copie = dict(src)
        copie["candidate_id"] = f"K{len(candidats) + 1:05d}"
        copie["registered_date"] = (
            date.fromisoformat(src["registered_date"]) + timedelta(days=random.randint(20, 200))
        ).isoformat()
        candidats.append(copie)
    return candidats


# --------------------------------------------------------------------------------------
# 4. Vacancies, submittals, interviews, placements
# --------------------------------------------------------------------------------------

def construire_recrutement(clients, candidats):
    vacancies, submittals, interviews, placements = [], [], [], []
    id_v = id_s = id_i = id_p = 1

    par_pays = {}
    for c in candidats:
        par_pays.setdefault(c["primary_skill"], []).append(c)

    for client in clients:
        signup = date.fromisoformat(client["signup_date"])
        fin_relation = date.fromisoformat(client["churn_date"]) if client["churn_date"] else FIN
        n_postes = random.choices([1, 2, 3, 4, 5], weights=[42, 27, 16, 9, 6])[0]

        for _ in range(n_postes):
            ouverture = signup + timedelta(days=random.randint(0, max(1, (fin_relation - signup).days)))
            if ouverture > FIN:
                continue
            famille = random.choice(list(ROLE_FAMILIES))
            titre = random.choice(ROLE_FAMILIES[famille])
            code_v = f"V{id_v:05d}"
            id_v += 1
            priorite = random.choices(["Standard", "High", "Urgent"], weights=[62, 26, 12])[0]
            taux_cible = random.choice([800, 1000, 1200, 1500, 1800, 2100])

            # Le delai de pourvoi depend de la famille de poste : un profil technique
            # met plus longtemps a se placer qu'un assistant executif.
            base_delai = {"Technical": 34, "Bookkeeping": 26, "Marketing VA": 23,
                          "Sales VA": 19, "Customer Support": 17, "Executive VA": 21}[famille]
            if priorite == "Urgent":
                base_delai *= 0.75

            # Combien de candidats presentes au client pour ce poste
            n_soumis = max(1, int(random.gauss(6.5, 2.4)))
            vivier = par_pays.get(famille, candidats)
            retenus = random.sample(vivier, min(n_soumis, len(vivier)))

            embauche = None
            date_embauche = None
            # La cadence de presentation depend de la difficulte de la famille de poste :
            # un Data Analyst ne se presente pas au meme rythme qu'un appointment setter.
            cadence = base_delai / 6.0
            for rang, cand in enumerate(retenus):
                jour_soumission = ouverture + timedelta(
                    days=max(1, int(random.gauss(cadence * (1 + rang), cadence * 0.4))))
                if jour_soumission > FIN:
                    continue
                code_s = f"S{id_s:06d}"
                id_s += 1

                # Le niveau d'anglais pese lourd sur la suite du parcours : c'est le
                # critere de vente de l'agence, et il doit se voir dans les donnees.
                bonus_anglais = {"B1": -0.18, "B2": 0.0, "C1": 0.12, "C2": 0.18}[cand["english_level"]]
                p_entretien = min(0.92, max(0.08, 0.46 + bonus_anglais))
                a_entretien = random.random() < p_entretien

                stage = "submitted"
                reason = ""
                date_stage = jour_soumission

                if a_entretien:
                    jour_entretien = jour_soumission + timedelta(days=max(1, int(random.gauss(6, 3))))
                    if jour_entretien <= FIN:
                        no_show = random.random() < 0.07
                        realise = 0 if no_show else 1
                        p_offre = min(0.85, max(0.05, 0.34 + bonus_anglais))
                        offre = realise and (embauche is None) and (random.random() < p_offre)
                        interviews.append(dict(
                            interview_id=f"I{id_i:06d}", submittal_id=code_s,
                            scheduled_date=jour_entretien.isoformat(),
                            completed=realise, no_show=1 if no_show else 0,
                            outcome="offer" if offre else ("pass" if realise else "no_show")))
                        id_i += 1
                        stage, date_stage = "interview", jour_entretien

                        if offre:
                            jour_offre = jour_entretien + timedelta(days=max(1, int(random.gauss(4, 2))))
                            # Effet de selection volontairement encode : un candidat
                            # au meilleur anglais recoit des offres concurrentes et
                            # decline plus souvent. L'anglais augmente donc la
                            # probabilite d'ATTEINDRE une offre et diminue celle de
                            # la CONCLURE — les deux sont vrais et se mesurent.
                            p_acceptation = {"B1": 0.90, "B2": 0.82,
                                             "C1": 0.72, "C2": 0.65}[cand["english_level"]]
                            acceptee = random.random() < p_acceptation
                            if acceptee and jour_offre <= FIN:
                                stage, date_stage = "hired", jour_offre
                                embauche, date_embauche = cand, jour_offre
                            else:
                                stage, date_stage = "offer_declined", jour_offre
                                reason = "Candidate withdrew"
                        else:
                            stage = "rejected"
                            reason = random.choice(REJECT_REASONS)
                    else:
                        stage = "client_review"
                else:
                    stage = "rejected"
                    reason = random.choice(REJECT_REASONS)

                submittals.append(dict(
                    submittal_id=code_s, vacancy_id=code_v, candidate_id=cand["candidate_id"],
                    submitted_date=jour_soumission.isoformat(), stage=stage,
                    stage_updated_date=date_stage.isoformat(), reject_reason=reason,
                    english_level=cand["english_level"]))

            # Statut du poste
            if embauche is not None:
                jour_demarrage = date_embauche + timedelta(days=max(2, int(random.gauss(9, 4))))
                statut = "filled"
                frais = round(random.choice([1500, 2000, 2500, 3000]) * random.uniform(0.95, 1.05), 0)
                taux_mensuel = round(taux_cible * random.uniform(0.85, 1.15) / 50) * 50
                remplace = random.random() < 0.11
                fin_mission = ""
                statut_placement = "active"
                if remplace:
                    jour_fin = jour_demarrage + timedelta(days=random.randint(20, 180))
                    if jour_fin <= FIN:
                        fin_mission, statut_placement = jour_fin.isoformat(), "replaced"
                placements.append(dict(
                    placement_id=f"P{id_p:05d}", vacancy_id=code_v,
                    candidate_id=embauche["candidate_id"], client_id=client["client_id"],
                    start_date=jour_demarrage.isoformat(), monthly_rate_usd=taux_mensuel,
                    placement_fee_usd=frais, status=statut_placement, end_date=fin_mission))
                id_p += 1
                jour_pourvu = date_embauche.isoformat()
            else:
                # Poste toujours ouvert, gele ou annule
                age = (FIN - ouverture).days
                if age > base_delai * 2.4:
                    statut = random.choices(["cancelled", "on_hold"], weights=[70, 30])[0]
                else:
                    statut = "open"
                jour_pourvu = ""

            vacancies.append(dict(
                vacancy_id=code_v, client_id=client["client_id"], role_title=titre,
                role_family=famille, priority=priorite,
                opened_date=ouverture.isoformat(), status=statut,
                filled_date=jour_pourvu,
                target_monthly_rate_usd=taux_cible))

    return vacancies, submittals, interviews, placements


def injecter_defauts(vacancies, submittals, placements):
    """Cinq defauts de plus, chacun correspondant a un controle de reconciliation."""
    index_v = {v["vacancy_id"]: v for v in vacancies}

    # n°3 : 12 postes marques 'filled' sans placement enregistre en aval.
    pourvus = [v for v in vacancies if v["status"] == "filled"]
    orphelins = random.sample(pourvus, 12)
    codes_orphelins = {v["vacancy_id"] for v in orphelins}
    placements[:] = [p for p in placements if p["vacancy_id"] not in codes_orphelins]

    # n°4 : 9 postes encore 'open' alors qu'un placement existe.
    for p in random.sample(placements, 9):
        index_v[p["vacancy_id"]]["status"] = "open"
        index_v[p["vacancy_id"]]["filled_date"] = ""

    # n°5 : 6 dates de pourvoi anterieures a l'ouverture du poste.
    for v in random.sample([v for v in vacancies if v["filled_date"]], 6):
        v["filled_date"] = (date.fromisoformat(v["opened_date"]) - timedelta(days=random.randint(1, 9))).isoformat()

    # n°6 : 7 placements a taux nul ou negatif.
    for p in random.sample(placements, 7):
        p["monthly_rate_usd"] = random.choice([0, 0, -1200])

    # n°7 : 15 submittals dupliques (meme candidat, meme poste, meme jour).
    doublons = []
    for s in random.sample(submittals, 15):
        copie = dict(s)
        copie["submittal_id"] = s["submittal_id"].replace("S", "S9")
        doublons.append(copie)
    submittals.extend(doublons)


# --------------------------------------------------------------------------------------
# 5. Pipeline health
# --------------------------------------------------------------------------------------

def construire_pipelines():
    runs = []
    id_run = 1
    fiabilite = {"ats_submittals": 0.985, "ats_vacancies": 0.99, "stripe_invoices": 0.995,
                 "ga4_sessions": 0.97, "ads_spend": 0.90, "hubspot_leads": 0.96}
    erreurs = ["API rate limit exceeded", "Auth token expired", "Schema drift: new column",
               "Timeout after 900s", "Source returned 0 rows", "Duplicate key on merge"]
    for offset in range(JOURS + 1):
        d = jour(offset)
        for nom in PIPELINES:
            ok = random.random() < fiabilite[nom]
            duree = int(random.gauss(210, 70))
            if nom == "ga4_sessions":
                duree = int(random.gauss(680, 240))
            duree = max(20, duree)
            lignes = int(random.gauss(12000, 3500) * saisonnalite(d)) if ok else 0
            runs.append(dict(
                run_id=f"R{id_run:06d}", pipeline_name=nom,
                run_date=d.isoformat(),
                started_at=f"{d.isoformat()} 0{random.randint(2, 5)}:{random.randint(10, 59)}:00",
                status="success" if ok else "failed",
                rows_ingested=max(0, lignes),
                duration_seconds=duree,
                error_message="" if ok else random.choice(erreurs)))
            id_run += 1
    return runs


# --------------------------------------------------------------------------------------
# 6. Output
# --------------------------------------------------------------------------------------

def ecrire_csv(nom, lignes):
    os.makedirs(CSV_DIR, exist_ok=True)
    chemin = os.path.join(CSV_DIR, f"{nom}.csv")
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)
    return chemin


def charger_duckdb(tables):
    import duckdb
    chemin = os.path.join(RACINE, "agency.duckdb")
    if os.path.exists(chemin):
        os.remove(chemin)
    con = duckdb.connect(chemin)
    for nom in tables:
        con.execute(
            f"CREATE TABLE {nom} AS "
            f"SELECT * FROM read_csv_auto('{os.path.join(CSV_DIR, nom + '.csv')}', header=true)")
    con.close()
    return chemin


def main():
    spend, leads = construire_marketing()
    clients = construire_clients(leads)
    activites = construire_pipeline_ventes(leads)
    candidats = construire_candidats()
    vacancies, submittals, interviews, placements = construire_recrutement(clients, candidats)
    injecter_defauts(vacancies, submittals, placements)
    runs = construire_pipelines()

    tables = {
        "marketing_spend": spend, "leads": leads, "clients": clients,
        "sales_reps": [dict(rep=r["rep"], monthly_quota_clients=r["quota"],
                            hired_date=r["hired"]) for r in SALES_REPS],
        "sales_activities": activites,
        "candidates": candidats, "vacancies": vacancies, "submittals": submittals,
        "interviews": interviews, "placements": placements, "pipeline_runs": runs,
    }
    for nom, lignes in tables.items():
        ecrire_csv(nom, lignes)
        print(f"  {nom:<18} {len(lignes):>7} rows")
    chemin = charger_duckdb(tables)
    print(f"\nCSV  : {CSV_DIR}")
    print(f"DuckDB: {chemin}")


if __name__ == "__main__":
    main()
