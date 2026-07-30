# SQL drills, with answers

*Remote Leverage — Data Analyst · run against `practice/agency.duckdb`. Twelve drills, ordered from warm-up to the ones worth thinking about. Every expected result below was produced by executing the solution shown.*

**How to use this.** Read the question, write the query yourself, run it, then compare. Do not read the solution first — the point is to find out where you hesitate, because that is where you will hesitate on Monday with someone watching. Timebox each one to five minutes; if you are stuck at five, look, then write it again from memory the next day.

```bash
pip install duckdb
python3 -c "import duckdb; con = duckdb.connect('practice/agency.duckdb'); print(con.sql('SHOW TABLES'))"
```

---

## D1 — Warm-up: the open desk

*How many vacancies are currently open, when was the oldest one opened, and how old is it in days as of 26 July 2026?*

```sql
SELECT COUNT(*)                                                       AS open_vacancies,
       MIN(opened_date)                                               AS oldest_opened,
       MAX(DATE_DIFF('day', opened_date, DATE '2026-07-26'))          AS max_age_days
FROM vacancies WHERE status = 'open';
```

| open_vacancies | oldest_opened | max_age_days |
|---|---|---|
| 143 | 2025-03-02 | 511 |

A requisition open for 511 days is not open, it is abandoned. The analyst's instinct here is to question the *status field itself*: if nobody closes stale requisitions, every aging metric is polluted. Worth saying out loud — noticing that a status is unmaintained is a real finding.

---

## D2 — Ratio inside a group

*Submittal-to-interview ratio by role family.*

```sql
WITH f AS (
  SELECT v.role_family, s.submittal_id,
         MAX(CASE WHEN i.interview_id IS NOT NULL THEN 1 ELSE 0 END) AS had_interview
  FROM submittals s
  JOIN vacancies v USING (vacancy_id)
  LEFT JOIN interviews i USING (submittal_id)
  GROUP BY 1, 2
)
SELECT role_family, COUNT(*) AS submittals,
       ROUND(100.0 * SUM(had_interview) / COUNT(*), 1) AS s2i_pct
FROM f GROUP BY 1 ORDER BY s2i_pct DESC;
```

| role_family | submittals | s2i_pct |
|---|---|---|
| Marketing VA | 553 | 50,6 |
| Technical | 585 | 49,9 |
| Sales VA | 711 | 46,4 |
| Bookkeeping | 627 | 45,8 |
| Customer Support | 719 | 45,5 |
| Executive VA | 723 | 44,1 |

The inner CTE exists to **collapse to one row per submittal** before counting. Without it, a submittal with two interview records would be counted twice and the ratio would exceed 100 %. That is the fan-out problem, and pre-empting it is exactly the kind of thing to narrate while you type.

The finding itself is close to a non-finding: 44,1 % to 50,6 % is a narrow band, so shortlist quality is broadly consistent across role families. **Reporting "no meaningful difference" is a legitimate result** and saying so confidently is a mark of maturity — juniors invent a story.

---

## D3 — Top N

*Five clients by fee revenue, with placement counts.*

```sql
SELECT c.company_name,
       COUNT(p.placement_id)                 AS placements,
       CAST(SUM(p.placement_fee_usd) AS INT) AS fees
FROM clients c JOIN placements p USING (client_id)
GROUP BY 1 ORDER BY fees DESC LIMIT 5;
```

| company_name | placements | fees |
|---|---|---|
| Pinnacle Partners | 13 | 25 830 |
| Oakfield Solutions | 9 | 22 006 |
| Westbrook Solutions | 10 | 21 325 |
| Redstone LLC | 8 | 19 706 |
| Pinnacle Media | 8 | 18 537 |

Note Oakfield: nine placements but higher fees than Westbrook's ten, so its average fee is materially larger. **Concentration is the question worth asking next** — if the top five clients are a large share of revenue, losing one is a business risk, and that is the analysis a founder actually wants.

---

## D4 — Change over time

*Placements per month with the month-on-month change, excluding future start dates.*

```sql
SELECT DATE_TRUNC('month', start_date) AS month,
       COUNT(*)                        AS placements,
       COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', start_date)) AS delta
FROM placements
WHERE start_date <= DATE '2026-07-26'
GROUP BY 1 ORDER BY 1 DESC LIMIT 5;
```

| month | placements | delta |
|---|---|---|
| 2026-07 | 50 | +12 |
| 2026-06 | 38 | −1 |
| 2026-05 | 39 | +18 |
| 2026-04 | 21 | −4 |
| 2026-03 | 25 | +1 |

Two things are being tested. `LAG` over an aggregate — a window function applied on top of `COUNT(*)`, which is legal and idiomatic. And the `WHERE` clause: **some start dates are in the future**, because a placement is agreed before the VA begins. Without that filter the current month is inflated by people who have not started. Catching it unprompted is worth more than the query.

---

## D5 — Duplicates

*How many duplicate candidate records exist, by email?*

```sql
SELECT COUNT(*) AS dup_groups, SUM(n) - COUNT(*) AS extra_rows
FROM (SELECT email, COUNT(*) AS n FROM candidates GROUP BY 1 HAVING COUNT(*) > 1);
```

| dup_groups | extra_rows |
|---|---|
| 40 | 40 |

Forty groups, forty surplus rows — so every duplicate is a clean pair. Now say what you would do about it, because detection is the easy half. You keep the earliest registration as the survivor, repoint any submittals from the duplicate to it, and archive the discarded row rather than deleting it. And you never merge automatically on a fuzzy match: **presenting the same person twice to the same client is embarrassing, but merging two different people is worse.**

The removal query is the pattern you already know:

```sql
SELECT candidate_id FROM (
  SELECT candidate_id,
         ROW_NUMBER() OVER (PARTITION BY email ORDER BY registered_date, candidate_id) AS rn
  FROM candidates
) WHERE rn > 1;
```

---

## D6 — Cross-system reconciliation

*List the vacancies marked filled that have no placement record.*

```sql
SELECT v.vacancy_id, c.company_name, v.role_title, v.filled_date
FROM vacancies v
JOIN clients c USING (client_id)
LEFT JOIN placements p USING (vacancy_id)
WHERE v.status = 'filled' AND p.placement_id IS NULL
ORDER BY v.filled_date;
```

| vacancy_id | company_name | role_title | filled_date |
|---|---|---|---|
| V00071 | Westbrook Capital | Helpdesk Agent | 2025-04-03 |
| V00040 | Redstone Solutions | Automation Specialist | 2025-08-28 |
| V00400 | Cedar Creek Partners | Executive Assistant | 2025-12-14 |
| V00361 | Summit Capital | Data Analyst | 2026-01-09 |
| V00178 | Summit Partners | Email Marketer | 2026-02-07 |

Twelve rows in total. The `LEFT JOIN ... WHERE right side IS NULL` anti-join is the most reusable pattern in this whole document — "who is in A but not in B" answers a third of all analyst questions.

**This is the drill to remember**, because the output is not a data-quality report, it is a list of twelve fees that may never have been invoiced, with client names attached. Turning a technical check into a revenue question is the difference between an analyst and a report-writer.

---

## D7 — The counter-intuitive result

*Offer acceptance rate by candidate English level.*

```sql
WITH offers AS (
  SELECT s.english_level, s.submittal_id, s.stage
  FROM submittals s JOIN interviews i USING (submittal_id)
  WHERE i.outcome = 'offer'
)
SELECT english_level,
       COUNT(*)                                    AS offers,
       COUNT(*) FILTER (WHERE stage = 'hired')     AS accepted,
       ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'hired') / COUNT(*), 1) AS accept_pct
FROM offers GROUP BY 1 ORDER BY 1;
```

| english_level | offers | accepted | accept_pct |
|---|---|---|---|
| B1 | 20 | 20 | 100,0 |
| B2 | 161 | 127 | 78,9 |
| C1 | 214 | 157 | 73,4 |
| C2 | 87 | 55 | 63,2 |

This **reverses** the direction from [module 01](01_recruiting_sales_marketing_metrics.md), where stronger English meant a far higher hire rate. Here, stronger English means a *lower* acceptance rate, and both are true.

The explanation is a selection effect: C1 and C2 candidates receive competing offers and can decline, while a B1 candidate who reaches an offer has fewer alternatives. So English level raises your odds of *reaching* an offer and lowers your odds of *closing* it — which has a real operational consequence, namely that speed matters most on your strongest candidates.

Then the discipline: **B1 shows 100 %, and it has only 20 offers.** A rate of exactly 100 % should always make you look at the denominator before you look at the finding — two declines would drop it to 90 %. The honest sentence is *"the direction is plausible and consistent with competing offers, but I wouldn't quote the B1 number at all with an n of twenty — what I'd stand behind is the gap between B2 at seventy-nine percent and C2 at sixty-three, where the denominators are large enough to mean something."*

Being able to hold both "here is the pattern" and "here is why I don't fully trust it yet" in the same breath is, more than any syntax, what a good analyst sounds like.

---

## D8 — Channel profit and loss

*Spend against fee revenue by acquisition channel, with return on ad spend.*

```sql
WITH spend AS (SELECT channel, SUM(spend_usd) AS s FROM marketing_spend GROUP BY 1),
     cl AS (SELECT c.acquisition_channel AS ch, COUNT(DISTINCT c.client_id) AS n,
                   SUM(p.placement_fee_usd) AS fees
            FROM clients c LEFT JOIN placements p USING (client_id) GROUP BY 1)
SELECT cl.ch AS channel, cl.n AS clients,
       CAST(ROUND(COALESCE(spend.s, 0)) AS INT)          AS spend,
       CAST(cl.fees AS INT)                              AS fees,
       CAST(ROUND(cl.fees - COALESCE(spend.s, 0)) AS INT) AS net,
       ROUND(cl.fees / NULLIF(COALESCE(spend.s, 0), 0), 2) AS roas
FROM cl LEFT JOIN spend ON spend.channel = cl.ch
ORDER BY net DESC;
```

| channel | clients | spend | fees | net | roas |
|---|---|---|---|---|---|
| Referral | 77 | 0 | 198 434 | +198 434 | — |
| Paid Search | 133 | 181 124 | 325 109 | +143 985 | 1,79 |
| Organic | 48 | 0 | 101 303 | +101 303 | — |
| Outbound | 32 | 40 633 | 70 404 | +29 771 | 1,73 |
| Paid Social | 37 | 134 127 | 80 027 | −54 100 | 0,60 |

Paid Social returns sixty cents per dollar. Paid Search returns 1,79 and Outbound 1,73 — but outbound's figure excludes the salary of the person sending the emails, which is its dominant cost, so its true return is materially lower than the table suggests. Paid Search is the only paid channel unambiguously working.

Three caveats to voice, because the recommendation is only as good as its assumptions. The revenue here is **fees to date**, not lifetime — a channel with slower but repeat clients looks worse than it is. Referral and Organic show zero spend because their costs simply are not in the ad-spend table, not because they are free. And this is **last-touch attribution**: a client who saw a paid social ad and later arrived through search is credited entirely to search.

The recommendation, stated properly: *"On the evidence I'd cut paid social and test moving that budget into search, but I'd want to see it by cohort over a longer window before committing, and I'd want to know what referral actually costs before calling it the best channel."*

---

## D9 — Pipeline forensics

*When does `ads_spend` fail most?*

```sql
SELECT DATE_TRUNC('month', run_date) AS month,
       COUNT(*) FILTER (WHERE status = 'failed') AS fails
FROM pipeline_runs WHERE pipeline_name = 'ads_spend'
GROUP BY 1 ORDER BY fails DESC LIMIT 4;
```

| month | fails |
|---|---|
| 2025-12 | 6 |
| 2026-07 | 5 |
| 2025-03 | 5 |
| 2026-01 | 5 |

Failures are **spread evenly**, not clustered. That matters diagnostically: a spike in one month suggests a one-off breaking change, while a steady five or six a month suggests a chronically fragile job — here, mostly schema drift and rate limiting.

The fix follows the diagnosis. Chronic drift means the loader should tolerate new columns rather than fail on them; chronic rate limiting means backoff and retry. And since this pipeline feeds the channel analysis in D8, its unreliability is not an infrastructure footnote — it is a caveat on the recommendation.

---

## D10 — Retention proxy

*What share of clients opened more than one requisition?*

```sql
SELECT COUNT(*) AS clients_with_2plus,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM clients), 1) AS pct
FROM (SELECT client_id FROM vacancies GROUP BY 1 HAVING COUNT(*) >= 2);
```

| clients_with_2plus | pct |
|---|---|
| 192 | 58,7 |

In a one-time-fee business this is the closest thing to a satisfaction score, and 58,7 % is healthy: well over half of clients came back. It is also the number that justifies acquisition spend, because a client worth two placements tolerates twice the acquisition cost.

The natural follow-up, and a good exercise: does repeat rate differ by acquisition channel? Referral produced 89 placements from 77 clients in D8, the highest ratio of any channel — which is the argument for investing there.

---

## D11 — The metric the client feels

*Median days from vacancy opened to first candidate submitted, by role family.*

```sql
WITH first_sub AS (
  SELECT vacancy_id, MIN(submitted_date) AS first_submitted FROM submittals GROUP BY 1
)
SELECT v.role_family,
       MEDIAN(DATE_DIFF('day', v.opened_date, f.first_submitted)) AS median_days
FROM vacancies v JOIN first_sub f USING (vacancy_id)
GROUP BY 1 ORDER BY median_days DESC;
```

| role_family | median_days |
|---|---|
| Technical | 5,0 |
| Bookkeeping | 4,0 |
| Executive VA | 3,0 |
| Sales VA | 3,0 |
| Marketing VA | 3,0 |
| Customer Support | 2,0 |

Time to first submittal is the metric the **client experiences**, and it is very different from time to fill. Technical roles take 28 days to fill but only 5 days to first submittal, so the delay is not sourcing — it is the number of iterations before a match. That distinction changes what you would fix: better intake and expectation-setting, not more sourcing capacity.

Bringing an unasked-for metric like this into an interview shows you think about *who consumes the number*, not just how to compute it.

---

## D12 — The censoring fix, applied

*Share of vacancies filled within 30 days of opening, by cohort month.*

```sql
SELECT DATE_TRUNC('month', opened_date) AS cohort,
       COUNT(*) AS opened,
       COUNT(*) FILTER (WHERE filled_date IS NOT NULL AND filled_date >= opened_date
                          AND DATE_DIFF('day', opened_date, filled_date) <= 30) AS filled_30d,
       ROUND(100.0 * COUNT(*) FILTER (WHERE filled_date IS NOT NULL AND filled_date >= opened_date
                          AND DATE_DIFF('day', opened_date, filled_date) <= 30) / COUNT(*), 1) AS pct
FROM vacancies
WHERE opened_date <= DATE '2026-06-26'      -- only cohorts old enough to have had 30 days
GROUP BY 1 ORDER BY 1 DESC LIMIT 5;
```

| cohort | opened | filled_30d | pct |
|---|---|---|---|
| 2026-06 | 88 | 43 | 48,9 |
| 2026-05 | 72 | 37 | 51,4 |
| 2026-04 | 55 | 26 | 47,3 |
| 2026-03 | 50 | 21 | 42,0 |
| 2026-02 | 33 | 14 | 42,4 |

Compare with the raw fill rate from [module 01](01_recruiting_sales_marketing_metrics.md), where July collapsed to 11,9 % for no reason at all. Here the series moves in a plausible band between 42 % and 51 % with **no collapse at the recent end**, so a real change would be visible instead of being drowned by censoring noise.

Two design choices carry that: the fixed 30-day window makes every cohort measured identically, and the `WHERE` clause excludes cohorts too young to have had their full 30 days. Both must be present — the window alone still lets an immature cohort in.

This is the drill that best demonstrates the difference between computing a metric and *designing* one. If you only rehearse one query on Sunday, rehearse this one and be able to explain both lines of defence.

---

## Where to go if you have time left

Rewrite D2, D7 and D12 in BigQuery dialect using `COUNTIF`, `SAFE_DIVIDE`, `DATE_DIFF(b, a, DAY)` and `APPROX_QUANTILES(x, 2)[OFFSET(1)]` — the translation table is in [module 02](02_bigquery_for_analysts.md) §9.

Then take D6 and D8 into Tableau as two sheets, because those are the two you would most want to show someone. And work [module 06](06_sales_lens_and_objections.md), which drills the same skills on the sales side of the funnel — reps, quotas and deal stages.

---

*Back to: [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md) · [Recruiting metrics](01_recruiting_sales_marketing_metrics.md) · [BigQuery](02_bigquery_for_analysts.md) · [Tableau](03_tableau_in_five_days.md) · [Positioning](04_positioning_and_mock_interview.md)*
