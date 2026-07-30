# Remote Leverage — Data Analyst · plan and cheat sheet

*Interview: Monday 3 August 2026. Today: Wednesday 29 July. Five days.*

---

## 1. The company, in one screen

Remote Leverage is a **virtual-assistant placement agency** based in Florida. It recruits English-speaking VAs from Latin America and the Philippines for US businesses, and charges the client a **one-time flat fee** rather than an ongoing margin — the VA is then paid directly by the client, which is their main selling point against traditional staffing firms. A partner company handles payroll and compliance. Glassdoor shows roughly 4.9/5 across about 299 reviews; an industry comparison flags that they carry no verified client feedback on Clutch or Trustpilot.

**The role is in-house, not a client placement.** The posting says "you'll join our team contributing to shape the data that drives our business", so "sales, vacancies, and marketing performance" means *their* funnel: client acquisition, open requisitions, candidate pipeline, ad spend.

**What their business model implies for the metrics**, which is the thing most candidates will miss. A one-time fee means revenue tracks **placement volume**, not headcount under management — so fill rate, time to fill and acquisition cost matter far more than utilisation or billable hours. Paying the VA directly means the growth constraint is **candidate supply and quality**, which is why English level is not just an attribute in their database but the product specification. And a placement guarantee means **replacements are a cost centre**: a failed placement is the work done twice for one fee.

Compensation is $1,920–$2,080 a month. That is the LatAm placement band; treat it as near-fixed and aim at the top of it.

---

## 2. Where you stand

| Requirement | You | Action |
|---|---|---|
| Tableau dashboards | **Gap.** Power BI expert, no Tableau | Weekend build + honest script |
| BigQuery SQL | Real but engineer-side (Beam → BigQuery at Tekkod) | Analyst-side depth: cost, partitioning, `COUNTIF` |
| Sales / vacancy / marketing metrics | **Gap.** Vocabulary is MEAL | [Module 01](01_recruiting_sales_marketing_metrics.md) |
| Pipeline monitoring & troubleshooting | Strong | Reframe in commercial terms |
| Data quality, validation, reconciliation | **Very strong** | Lead with it |
| n8n | None | 40-minute quickstart, honest answer |
| Git / GitHub | Strong | Nothing to do |
| AI tools used securely | Strong, better than most | Rehearse the concrete answer |
| 3+ years as Data Analyst | True but obscured by job titles | Repositioning, [module 04](04_positioning_and_mock_interview.md) |
| Fluent spoken English | True but unrehearsed | 20 min/day out loud |

---

## 3. The five-day plan

**Wednesday 29 — evening, 2 hours.** Install Tableau Public and load `practice/csv/`. Read [module 01](01_recruiting_sales_marketing_metrics.md) end to end and run its queries yourself against `practice/agency.duckdb`. Do not read passively — type the queries.

**Thursday 30 — 3 hours.** [Module 02](02_bigquery_for_analysts.md). Rewrite five module-01 queries in BigQuery dialect by hand. Then 40 minutes on n8n's quickstart: build one workflow with a schedule trigger, an HTTP node and a filter. Twenty minutes reading the 90-second pitch aloud.

**Friday 31 — 3 hours.** [Module 03](03_tableau_in_five_days.md), then build Tableau sheets 1 and 2 — the funnel and time-to-fill. Expect the first hour to be frustrating; the interface is the only real obstacle. Twenty minutes of English drills.

**Saturday 1 August — 4 hours.** Finish the Tableau dashboard: aging, channel economics, monthly trend with the censored month marked. Assemble, add one filter action, **publish and save the link**. Then [module 04](04_positioning_and_mock_interview.md) and [module 06](06_sales_lens_and_objections.md) — the sales vocabulary and the rehearsed answer to "you've never worked in sales". Update the CV title line.

**Sunday 2 August — 3 hours.** Full mock interview out loud, timed, recorded. Play it back. Redo the three answers that came out worst. Re-run the module 01 queries from memory. Re-read this page. Stop by 8 p.m.

**Monday 3 August — morning.** Re-read sections 4, 5 and 6 of this page only. Test camera, microphone and connection an hour before. Have the Tableau link, the practice dataset and a notepad open. Do not cram.

---

## 4. Numbers to have in your head

All from the practice dataset — say "in the dataset I've been practising on" when you quote them.

| Metric | Value |
|---|---|
| Funnel | 3 918 submittals → 1 835 interviews scheduled → 1 719 completed → 482 offers → 362 hires |
| Submittal → interview | 46,8 % |
| Interview → offer | 28,0 % |
| Offer acceptance | 75,1 % |
| Median time to fill | 28 days Technical, 17 days Customer Support — an 11-day spread |
| Fill rate | 49,4 % filled, 20,2 % open, 21,6 % cancelled, 8,9 % on hold |
| English level effect | B1 2,9 % hire rate → C1 13,4 % → C2 13,4 % — more than 4× from B1 |
| Acceptance reverses | C2 accept only 63,2 % of offers vs B2 78,9 % — competing offers |
| CPL vs CAC | Outbound cheapest lead at $83,78; Paid Social $146,27 CPL but $3 625 CAC vs Paid Search $1 362 |
| Channel P&L | Paid Social spent $134 127, returned $80 027 in fees — ROAS 0,60 |
| Referral | 22,3 % lead-to-client, ~2,6× Paid Search, at zero recorded spend |
| Sales | Best closer wins 11,1 % of closed deals vs 8,2 % worst; nobody hits quota (68 % best) |
| Never worked | 256 leads — 6,5 % — were paid for and never contacted |
| Censoring | July fill rate 11,9 % vs a stable ~55 % — nothing is wrong, the cohort is too young |
| Reconciliation | 12 vacancies marked filled with no placement record — potentially uninvoiced fees |
| Pipeline health | `ads_spend` fails 10 % of runs, mostly schema drift — and it feeds the CAC dashboard |

---

## 5. Twelve sentences to be able to say

1. "Cheap leads that don't convert are expensive — I optimise for cost per acquisition, not cost per lead."
2. "I'd never trend fill rate on the current month without handling right-censoring, because the newest cohort always looks broken."
3. "Status columns overwrite history; event tables preserve it. I build funnels from events."
4. "What's the grain of this table?"
5. "In BigQuery you pay for bytes scanned, not rows returned — so `LIMIT` doesn't make a query cheaper."
6. "I'd set `require_partition_filter` so the expensive mistake is impossible rather than discouraged."
7. "Constraints prevent what can be prevented; checks detect what can't."
8. "Twelve filled vacancies with no placement record isn't a data problem, it's potentially twelve uninvoiced fees."
9. "A FIXED level-of-detail expression is computed before dimension filters, so filtering the view doesn't change it — unless you promote the filter to context."
10. "A dashboard is only as trustworthy as its least reliable upstream job, so freshness belongs on the dashboard."
11. "I never paste real client or candidate data into an AI prompt — schemas and synthetic examples get me the same help."
12. "I don't know that one — here's how I'd find out."

---

## 6. The three answers that decide it

**Tableau** — name the gap, prove transfer with the FIXED-LOD-equals-`CALCULATE`-`ALLEXCEPT` equivalence, offer the link you built this weekend, give a realistic ramp. Full script at the end of [module 03](03_tableau_in_five_days.md).

**Who you are** — "a data analyst with about five years, who's worked both sides of the stack." Full pitch in [module 04](04_positioning_and_mock_interview.md) §3. Say "data analyst" in the first five words; do not lead with MEAL.

**What you'd do first** — "run a reconciliation suite before building anything, because I'd rather find the problems than have someone find them in my chart." Then the twelve-uninvoiced-fees example.

---

## 7. Questions for them

What does the stack look like end to end, and what orchestrates it? On-demand or capacity pricing in BigQuery? What's the first thing you'd want this person to fix? Who owns a metric definition when two teams disagree? What is n8n currently automating? Contractor or employment, and how does payment work for someone based in Haiti? What does success look like at ninety days?

The one to always ask is **"what's the first thing you'd want this person to fix?"** — it gets you the real job description.

---

## 8. Monday checklist

Camera, microphone and connection tested an hour ahead. Backup connection identified — a phone hotspot. Tableau Public link open in a tab. Practice dataset open in another. Notepad and pen. Water. A quiet room with the door shut.

During the call: say "data analyst" early. Give a number whenever you have one. Ask a clarifying question before answering anything ambiguous — that is a strength in this role, not a hesitation. If you stumble, use a recovery phrase and continue; do not apologise twice. Take notes, because the follow-up email should reference something specific they said.

Send that follow-up within twenty-four hours: three sentences, one specific thing from the conversation, and the Tableau link if you have not already sent it.

---

*Modules: [01 Recruiting, sales & marketing metrics](01_recruiting_sales_marketing_metrics.md) · [02 BigQuery for analysts](02_bigquery_for_analysts.md) · [03 Tableau in five days](03_tableau_in_five_days.md) · [04 Positioning and mock interview](04_positioning_and_mock_interview.md) · [05 SQL drills with answers](05_sql_drills_with_answers.md) · [99 During-call one pager](99_during_call_one_pager.md)*

*Tailored CV for this application: `../../curiculum-vitae-and-letter/specific_situation/remoteleverage_data_analyst/outputs/` (Markdown, DOCX, PDF).*

*Sources for the company brief: [Remote Leverage](https://remoteleverage.com/) · [Remote Leverage on LinkedIn](https://www.linkedin.com/company/remote-leverage) · [Glassdoor reviews](https://www.glassdoor.com/Reviews/Remote-Leverage-Reviews-E10507181.htm) · [Global Hola comparison](https://globalhola.com/blog/remote-leverage-reviews-what-do-clients-talents-say/)*
