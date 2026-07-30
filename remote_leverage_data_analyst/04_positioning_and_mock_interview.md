# Positioning, honest answers, and the mock interview

*Remote Leverage — Data Analyst · interview Monday 3 August 2026. Source of truth for every claim below: `../../curiculum-vitae-and-letter/alexandrodislaResume.tex`. Nothing here invents experience you do not have.*

---

## 1. The problem this module solves

Read the qualification line again: **"3+ years of experience as a Data Analyst or in a similar role."**

Now read your job titles in order: Software Engineer (Fullstack), Data Analyst & MEAL Consultant, mWater & Data Analyst Consultant, Backend Developer & Data Engineer, Monitoring & Evaluation Officer, Software Consultant, Economist.

You have far more than three years of analyst work. But a recruiter scanning for the phrase will see a developer who also does data, or an NGO monitoring officer, and both readings put you in the wrong pile. Your resume title line — *"MEAL Specialist | Data Engineer | Software Engineer | Applied Economist"* — is accurate and, for this application, actively unhelpful: it leads with the least relevant identity and never says "Data Analyst".

This is a **framing** problem, not a credentials problem. Everything below fixes the framing without changing a single fact.

---

## 2. The one-line repositioning

For this conversation, you are a **Data Analyst with five years across analytics and data engineering, who has built the pipelines as well as the dashboards.**

That is true, it is provable from the resume, and it turns your unusual background from a liability into the differentiator. Most analysts cannot monitor a pipeline or debug why it failed. The job description asks for exactly that in responsibility four. You can do it because you have written them.

If you send an updated CV before Monday, change one line: make the title read **"Data Analyst | Data Engineer | BI & Analytics"** and move the MEAL framing into the body. Everything else can stay.

---

## 3. The 90-second pitch

Read it aloud four or five times. Do not memorise it word for word — memorised text sounds memorised. Learn the four beats: what I am, the analytics proof, the engineering proof, why this role.

> "I'm a data analyst with about five years of experience, and what's slightly unusual about my background is that I've worked both sides of the data stack. On the analysis side, I've owned reporting for multi-site programmes — building the indicator frameworks, writing the SQL, and shipping the dashboards that leadership and funders actually made decisions from, in Power BI and Looker Studio. On the engineering side, I've built the pipelines underneath: ETL jobs in Apache Beam moving MongoDB data into BigQuery, Python jobs running on AWS, and I've done the unglamorous parts — monitoring runs, chasing failures, reconciling numbers between systems that disagreed. That combination is why this role interested me. You're asking for someone who can write and optimise BigQuery SQL, build dashboards, *and* keep an eye on pipeline health and data quality — and most people do one of those three well. I've also spent a lot of my career working with distributed teams across time zones, in English and French, which I gather is the normal way of working here."

Four things that pitch does deliberately. It says "data analyst" in the first five words. It gives concrete proof of both halves rather than adjectives. It names the job description's own responsibilities back at them. And it closes on remote-team fit, which for a company built entirely on remote placement is not a throwaway.

**What it does not do is mention humanitarian work.** That is not hiding anything — it comes up naturally when you describe the projects — but leading with "MEAL specialist" invites them to file you as sector-specific. Lead with the function; the sector is context.

---

## 4. Translating your achievements

Every strong story you own is currently phrased in humanitarian language. Same fact, commercial register:

| What you would normally say | Say this instead |
|---|---|
| "Reduced manual processing time by 40% with Python/SQL reports" | "Automated recurring reporting, cutting the manual production cycle by 40% and freeing the team for analysis" |
| "Established DQA protocols for MySQL-integrated data" | "Built a data quality and reconciliation framework — a suite of automated checks that had to pass before any figure was published" |
| "Maintained 100% data integrity on mWater surveys" | "Owned end-to-end data quality on a multi-country collection system, with zero reconciliation gaps across reporting cycles" |
| "Built ITT and indicator tracking tables aligned to JMP standards" | "Defined the metric layer — single agreed definitions for every KPI, so the same number meant the same thing in every report" |
| "Dashboards for donor reporting" | "Stakeholder-facing dashboards for external reporting, where the numbers were audited" |
| "Beneficiaries reached" | "Coverage against target" |
| "Trained field teams on data collection tools" | "Ran enablement for non-technical users, and wrote the documentation so it outlasted me" |
| "Resolved N+1 query problem, 36 seconds to under 0.5" | Keep exactly as is — this one already speaks the language |

The last row matters. **Your Tekkod performance story needs no translation** and it is the single most impressive technical anecdote you own. Have it ready; it answers "tell me about a time you optimised something" perfectly.

---

## 5. The CV coherence map

Your dates overlap heavily. That is normal for consulting, and it is also the kind of thing an interviewer circles. Have the answer ready so it takes ten seconds and sounds relaxed rather than defensive.

| Period | Role | Nature |
|---|---|---|
| Nov 2015 – Mar 2021 | CassionSoft (UNOPS) | Consulting |
| Mar 2021 – May 2024 | Tekkod — Backend Dev & Data Engineer | Contract |
| Oct 2021 – Aug 2024 | Caris Foundation — M&E Officer | Programme role |
| Oct 2023 – Jan 2026 | HANWASH — mWater & Data Analyst | Consulting, Upwork |
| Jan 2026 – Mar 2026 | Anseye Pou Ayiti — Data Analyst & MEAL | Short consultancy |
| Feb 2026 – Present | Tekkod — Software Engineer | Returned |

The line to use: *"Several of those run in parallel because they were consulting engagements rather than full-time posts — that's normal in the Haitian market, where organisations contract specialists per project. The Caris role was my main programme engagement while Tekkod and HANWASH were parallel consulting contracts."* Say it once, plainly, and move on. Over-explaining is what makes it sound like a problem.

Be ready for the follow-up: *"Why did you go back to Tekkod?"* Answer honestly — you had an existing relationship, they had a modernisation project that needed someone who knew the codebase. And be ready for *"Are you currently employed?"* Answer straight, and if you are looking to move, give a forward-looking reason rather than a complaint.

---

## 6. The three honest answers

### Tableau

The full script is at the end of [module 03](03_tableau_in_five_days.md). The structure: name the gap first, prove transfer with a *specific* technical equivalence (FIXED LOD ≈ `CALCULATE` with `ALLEXCEPT`), offer evidence you built over the weekend, give a realistic ramp estimate. Never say "I'm a fast learner" without the evidence attached — with the link, you do not need the phrase at all.

### n8n

> "I haven't used n8n itself. I've built the same class of thing in code — Apache Beam pipelines, scheduled Python jobs on AWS with retry and failure alerting — so the concepts are familiar and honestly the node-based approach is a shorter learning curve than what I'm used to. I spent an evening in it this week to get the shape of it. What are you currently automating with it?"

Do actually spend the evening. Forty minutes on their quickstart with a schedule trigger, an HTTP node and a filter makes that sentence true and turns a gap into evidence of initiative.

### GCP

You are stronger than you think: Apache Beam is the programming model Dataflow runs, you have loaded BigQuery, and you have shipped Looker Studio dashboards on top. The honest framing is that you have worked the loading and reporting ends and are deliberately deepening the analyst end — cost control, partitioning, `INFORMATION_SCHEMA` monitoring. Say what you did, not what you were called.

### Using AI securely

The job description asks for it explicitly, and almost every candidate will give a vague answer. Yours should be concrete:

> "I use Claude and ChatGPT daily — drafting and reviewing SQL, sanity-checking analysis logic, writing documentation, and as a rubber duck for debugging. The security rule I hold to is simple: never paste real client or candidate data into a prompt. I work with schemas, column names and synthetic examples, which is almost always enough to get the help I need. If I need to reason about actual values, I use anonymised or generated data. And I treat anything it produces as a draft to verify — I've seen models produce SQL that runs perfectly and answers the wrong question, so I check the row counts and the grain before I trust the output."

That answer is strong for two reasons. The "never paste real data" line is the one that matters to a company holding candidate PII, and it comes from real conviction rather than a policy document. And "SQL that runs perfectly and answers the wrong question" is a sentence that tells them you have actually used these tools on real work.

---

## 7. Money, and the model

The posting says **$1,920–$2,080 per month**, roughly $23–25k a year. That is the LatAm placement band, not a US analyst band, and it is stated as a range rather than an invitation to negotiate — so treat it as near-fixed and aim for the top of it rather than above it.

If asked what you are looking for: *"I saw the range in the posting and it's workable. I'd be aiming for the upper end given I bring the engineering side as well as analysis — I can maintain the pipelines, not just consume them. Is there a review cycle or a path for that to move as scope grows?"* Calm, anchored at the top, and it moves the conversation to progression, which is where the real value is.

Questions worth asking about the arrangement, because they determine what the number actually means. Is this a contractor engagement or employment, and through which entity? How does payment work for someone based in Haiti — which currency, which method, what frequency? Are the hours fixed to a US time zone? Is there paid time off? Is equipment provided or expected?

None of these are awkward. A company whose entire product is cross-border remote work will have crisp answers, and an inability to answer them clearly is itself information.

**On due diligence**: the public signal is positive — Glassdoor shows 4.9/5 across roughly 299 reviews — but an industry comparison noted the absence of verified client feedback on Clutch or Trustpilot. Nothing alarming. The ordinary precautions apply: never pay anything to be hired, never share bank credentials before a signed agreement, and expect a written contract before you start.

---

## 8. English, between now and Monday

Your resume says fluent and your written English is strong. The risk is not vocabulary, it is **fluency under pressure in a language you have not been rehearsing in** — every piece of prep in this workspace is in French.

Four short drills, twenty minutes a day, which is enough.

Record yourself giving the 90-second pitch and play it back. You will hear the hesitations immediately, and hearing them once is worth more than ten silent readings.

Read the three "Interview angles" answers in [module 01](01_recruiting_sales_marketing_metrics.md) aloud at speaking pace, not reading pace. They are written to be spoken.

Rehearse the numbers out loud in English, because that is where people stumble: "forty-six point four percent", "three thousand three hundred and ninety-six submittals", "one thousand five hundred and forty-two dollars". Say them until they are automatic.

Practise three recovery phrases so a stumble does not become a spiral: *"Let me put that a different way."* · *"Sorry, could you rephrase that?"* · *"I want to make sure I understood — are you asking about X or about Y?"* The third one is not a weakness; asking a clarifying question before answering is what good analysts do.

---

## 9. Mock interview

Do this in one sitting, out loud, timed. Do not read the guidance until after you have answered.

**Opening.** Tell me about yourself. Why are you interested in this role? What do you know about Remote Leverage?

*Guidance: the pitch, then a reason grounded in their business model — the one-time-fee model makes placement volume and acquisition efficiency the metrics that matter, which is a genuinely interesting analytics problem — then show you did the homework: VA placement from LatAm and the Philippines, flat fee, VA paid directly by the client.*

**Domain.** What metrics would you track for a business like ours? How would you investigate a drop in fill rate? What's the difference between cost per lead and customer acquisition cost, and which would you optimise for?

*Guidance: full answers in [module 01](01_recruiting_sales_marketing_metrics.md). The CPL/CAC answer is the one to nail — cheap leads that do not convert are expensive, with the paid-social number as evidence.*

**Technical SQL.** Write a query for the submittal-to-interview ratio by role family. How do you find duplicates? How would you compute month-over-month growth? What's the difference between `WHERE` and `HAVING`? How do you make a load idempotent?

*Guidance: [module 01](01_recruiting_sales_marketing_metrics.md) and [module 02](02_bigquery_for_analysts.md). If they screen-share a SQL editor, narrate as you type — they are assessing reasoning as much as syntax.*

**BigQuery.** How do you reduce the cost of a query? Partitioning versus clustering? Does `LIMIT` make a query cheaper?

*Guidance: [module 02](02_bigquery_for_analysts.md). The `LIMIT` answer is no, and knowing that is disproportionately impressive.*

**Tableau.** What's your experience with Tableau? What does a FIXED LOD do? Live or extract?

*Guidance: [module 03](03_tableau_in_five_days.md), and the honest script.*

**Pipelines and quality.** How would you monitor pipeline health? A stakeholder says the dashboard is wrong — what do you do?

*Guidance: freshness, volume, schema drift; alerts must be actionable and rare. For the second: reproduce first, check the grain and the filters, then reconcile against source. Never argue before reproducing, and if the dashboard is wrong, say so quickly and plainly.*

**Behavioural.** A time you found an error in your own analysis. A time you disagreed with a stakeholder about a number. How do you prioritise when three people want three dashboards. How do you work with people you never meet in person.

*Guidance: real stories only. The error one wants the correction and what you changed in your process afterwards — a check that would have caught it. The disagreement one wants "I showed the query", not "I was right".*

**Closing.** What are your salary expectations? When could you start? Do you have questions for us?

*Guidance: section 7 for money. Always have questions — section 10.*

---

## 10. Your questions for them

Pick four or five. They signal seriousness and they get you information you actually need.

What does the data stack look like end to end — what lands in BigQuery, from which systems, and what orchestrates it? Are you on on-demand or capacity pricing? Which dashboards exist today and who uses them daily? What's the first thing you'd want the person in this role to fix? Who owns metric definitions when two teams disagree on a number? What is n8n currently automating? How is the data team structured and who would I report to? What does success look like at ninety days?

The strongest of these is **"what's the first thing you'd want this person to fix?"** It gets you the real job description, and it lets you respond to the actual need rather than the posting.

---

## 11. What to avoid

Do not claim Tableau experience. Do not lead with "MEAL specialist". Do not describe yourself as a software engineer who also does data — invert it. Do not over-explain the overlapping dates. Do not answer "what's your weakness" with a disguised strength; use the real one from the ACTED prep — the tendency to build the durable version before the urgent one, and what you now do about it. Do not say "I'm a fast learner" without evidence attached. And do not let a technical question you cannot answer turn into invention: *"I don't know that one — here's how I'd find out"* is a complete, respectable answer, and for a data role it is close to the right answer.

---

*Next: [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md) · Back to [Recruiting metrics](01_recruiting_sales_marketing_metrics.md) · [BigQuery](02_bigquery_for_analysts.md) · [Tableau](03_tableau_in_five_days.md)*
