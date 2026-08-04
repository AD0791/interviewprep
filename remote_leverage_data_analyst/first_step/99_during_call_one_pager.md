# One pager — keep this open during the call

*Monday 3 August 2026. One screen. Do not scroll looking for something mid-answer — if it is not here, answer from your head.*

---

## Open with

> "I'm a data analyst with about five years of experience, and what's slightly unusual is that I've worked both sides of the stack — the analysis and the pipelines underneath it."

Then: dashboards in Power BI and Looker Studio · ETL in Apache Beam moving MongoDB into BigQuery · monitoring runs, chasing failures, reconciling systems that disagreed · "most people do one of those three well."

**Say "data analyst" in the first five words. Do not lead with MEAL.**

---

## Numbers

| | |
|---|---|
| Funnel | 3 918 submittals → 1 835 interviews → 482 offers → 362 hires |
| Ratios | 46,8 % submittal→interview · 28,0 % interview→offer · 75,1 % acceptance |
| Time to fill | 28 days Technical, 17 days Customer Support |
| Time to **first submittal** | 5 days Technical, 2 days Support — the metric the client feels |
| English effect | B1 2,9 % hire rate → C1 13,4 % → C2 13,4 % |
| …but acceptance reverses | C2 accept 63,2 % of offers vs B2 78,9 % — competing offers |
| Paid Social | $134 127 spend → $80 027 fees → **ROAS 0,60** |
| Paid Search | $181 124 → $325 109 → ROAS 1,79 |
| CPL vs CAC | Outbound cheapest CPL $83,78 · Paid Social CAC $3 625 vs Search $1 362 |
| Referral | 22,3 % lead→client, ~2,6× search, zero recorded spend |
| Sales reps | Best closer 11,1 % win rate vs 8,2 % worst · nobody hits quota (68 % best) |
| Leads never worked | 256, or 6,5 % — paid for, never contacted |
| Repeat clients | 58,7 % opened a second requisition |
| Censoring | July fill rate 11,9 % vs stable ~55 % — cohort too young |
| Fixed-window fix | Filled-within-30-days: 42–51 % across months, no collapse |
| Reconciliation | **12 vacancies marked filled with no placement record** |
| Pipeline | `ads_spend` fails 10 % of runs, schema drift — and it feeds the CAC dashboard |

Prefix with: *"in the dataset I've been practising on…"*

---

## The three answers that decide it

**Tableau.** Name the gap first. Power BI and Looker Studio depth · FIXED LOD ≈ `CALCULATE` + `ALLEXCEPT` · extract = import mode, live = DirectQuery · "I installed Tableau Public and rebuilt a recruiting funnel dashboard this weekend — I can send the link" · productive in two to three weeks. **Do not say "fast learner" — send the link instead.**

**n8n.** "Haven't used it. Same class of thing in Beam and Python on AWS — scheduled ETL with retries and alerting. Spent an evening in it this week. What are you automating with it?"

**Day one.** "I'd run a reconciliation suite before building anything — I'd rather find the problems than have someone find them in my chart. On my practice data that surfaces twelve filled vacancies with no placement record, which isn't a data curiosity, it's twelve fees possibly never invoiced."

---

## Lines to land

- "Cheap leads that don't convert are expensive — I optimise for CAC, not CPL."
- "Six and a half percent of your leads were never contacted — that's paid demand thrown away."
- "I'd never trend fill rate on the current month without handling censoring."
- "Status columns overwrite history; event tables preserve it."
- "What's the grain of this table?"
- "In BigQuery you pay for bytes scanned, not rows returned — so `LIMIT` doesn't make it cheaper."
- "`require_partition_filter` makes the expensive mistake impossible, not just discouraged."
- "Constraints prevent what can be prevented; checks detect what can't."
- "A FIXED LOD is computed before dimension filters — unless you promote the filter to context."
- "A dashboard is only as trustworthy as its least reliable upstream job."
- "I never paste real client or candidate data into an AI prompt."
- **"I don't know that one — here's how I'd find out."**

---

## If asked

**Overlapping dates** — "Consulting engagements alongside a primary programme role; standard in the Haitian market." One sentence, then move on.

**Salary** — "The range works. I'd aim at the upper end given I bring the engineering side too. Is there a review cycle as scope grows?"

**Weakness** — Tendency to build the durable version before the urgent one. What I do now: deliver what's needed this week first, then harden it.

**Wrong dashboard** — Reproduce before defending. Check grain and filters, reconcile to source. If it's wrong, say so fast and plainly.

---

## Ask them

1. **"What's the first thing you'd want this person to fix?"** ← always
2. What's the stack end to end, and what orchestrates it?
3. On-demand or capacity pricing in BigQuery?
4. Who owns a metric definition when two teams disagree?
5. What is n8n currently automating?
6. Contractor or employment — and how does payment work from Haiti?
7. What does success look like at ninety days?

---

## Before you join

Camera, mic, connection tested an hour ahead · hotspot ready · Tableau link in a tab · practice data in another · notepad · water · door shut.

**During:** give a number whenever you have one · ask a clarifying question before answering anything ambiguous · take notes for the follow-up.

**After:** three-sentence email within 24 hours, referencing one specific thing they said, with the Tableau link.

---

*Full detail: [00 plan](00_prep_plan_and_cheatsheet.md) · [01 metrics](01_recruiting_sales_marketing_metrics.md) · [02 BigQuery](02_bigquery_for_analysts.md) · [03 Tableau](03_tableau_in_five_days.md) · [04 positioning](04_positioning_and_mock_interview.md) · [05 drills](05_sql_drills_with_answers.md)*
