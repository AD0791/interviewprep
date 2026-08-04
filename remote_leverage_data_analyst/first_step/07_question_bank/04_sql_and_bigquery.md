# SQL and BigQuery questions

*Q63–Q90. Every query below was executed against `../practice/agency.duckdb` and returned the output shown. The DuckDB dialect is very close to BigQuery Standard SQL; where they diverge, the divergence is called out.*

---

## How to behave in a live SQL exercise

Before the questions, the thing that decides how a screen-shared SQL test goes: **narrate while you type.** They are assessing reasoning at least as much as syntax, and a candidate who says "I'm going to start from the interviews table rather than the submittal status column, because status overwrites history" has already earned most of the marks before the query runs.

Ask about grain before writing anything. Say the words *"what's the grain of this table — what does one row represent?"* out loud. If you get stuck on syntax, say what you are trying to do in words and keep going; interviewers hand you the function name and remember that you knew the shape. And if a query returns something surprising, do not paper over it — say "that's more rows than I expected, let me check whether the join fanned out." Catching your own error in front of them is worth more than not making it.

---

## Q63 — What's the grain of a table, and why do you ask?

> "The grain is what a single row represents — one submittal, one interview, one day of spend for one channel. I ask before writing any query because almost every serious analytical error is a grain error. If I join placements to submittals and the relationship isn't one-to-one, the rows multiply, and every SUM in the report inflates without anything erroring. The chart renders beautifully and the number is wrong, which is the dangerous kind of failure. So the habit is: state the grain of each table, state what the grain of the result should be, and check the row count against that expectation after the join."

## Q64 — Write a query for the submittal-to-interview ratio by role family.

```sql
SELECT v.role_family,
       COUNT(DISTINCT s.submittal_id)                       AS submittals,
       COUNT(DISTINCT i.submittal_id)                       AS reached_interview,
       ROUND(100.0 * COUNT(DISTINCT i.submittal_id)
             / NULLIF(COUNT(DISTINCT s.submittal_id), 0), 1) AS pct
FROM submittals s
JOIN vacancies  v ON v.vacancy_id  = s.vacancy_id
LEFT JOIN interviews i ON i.submittal_id = s.submittal_id
GROUP BY 1
ORDER BY pct DESC;
```

| role_family | submittals | reached_interview | pct |
|---|---|---|---|
| Marketing VA | 553 | 280 | 50.6 |
| Technical | 585 | 292 | 49.9 |
| Sales VA | 711 | 330 | 46.4 |
| Bookkeeping | 627 | 287 | 45.8 |
| Customer Support | 719 | 327 | 45.5 |
| Executive VA | 723 | 319 | 44.1 |

Worth noticing out loud: **Technical has the second-highest submittal-to-interview rate despite having the longest time to fill.** Those are not in tension — they say that technical candidates who get submitted are well screened and clients want to meet them, and the delay is elsewhere in the process, most likely in sourcing enough of them in the first place. Reading two metrics against each other like that, rather than one at a time, is the thing that turns a query result into a finding.

Two things to narrate while writing it. The `LEFT JOIN` is deliberate — an inner join would silently drop every submittal that never reached interview, which is precisely the population you are measuring. And `COUNT(DISTINCT i.submittal_id)` rather than `COUNT(*)` because a submittal can have more than one interview, and counting rows would count second interviews as extra people.

## Q65 — How would you find duplicates?

```sql
SELECT vacancy_id, candidate_id, submitted_date, COUNT(*) AS n
FROM submittals
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1
ORDER BY n DESC;
```

That returns 15 groups. The framing to add: *"finding them is the easy half — the question is what a duplicate means here. The same candidate submitted twice to the same vacancy on the same day is almost certainly a system artefact, so I'd dedupe. The same candidate submitted to the same vacancy three weeks apart might be a genuine resubmission after the client's requirements changed, and deduping that would destroy real information. I'd never write a dedupe rule without asking what the business meaning is."*

## Q66 — How do you keep one row per group — the latest record, say?

Window function, and in BigQuery you get to use `QUALIFY`, which is the neatest form.

```sql
-- DuckDB and BigQuery both support QUALIFY
SELECT vacancy_id, candidate_id, submitted_date, stage
FROM submittals
QUALIFY ROW_NUMBER() OVER (
          PARTITION BY vacancy_id, candidate_id
          ORDER BY submitted_date DESC, submittal_id DESC) = 1;
```

`QUALIFY` filters on a window function the way `HAVING` filters on an aggregate, which removes the subquery you would otherwise need. The portable version, for a dialect without it:

```sql
SELECT * FROM (
  SELECT s.*, ROW_NUMBER() OVER (PARTITION BY vacancy_id, candidate_id
                                 ORDER BY submitted_date DESC) AS rn
  FROM submittals s) t
WHERE rn = 1;
```

Mention the tiebreaker. Ordering by `submitted_date` alone is non-deterministic when two rows share a date, so adding `submittal_id` makes the result reproducible — and a query that returns different rows on different runs is a bug that takes weeks to notice.

## Q67 — `ROW_NUMBER`, `RANK` and `DENSE_RANK` — what's the difference?

> "They differ only in how they handle ties. `ROW_NUMBER` never ties — it assigns 1, 2, 3, 4 arbitrarily among equal values, which is what you want for deduplication because you need exactly one winner. `RANK` gives tied rows the same number and then skips: 1, 1, 3. `DENSE_RANK` gives tied rows the same number and doesn't skip: 1, 1, 2. So for a top-N leaderboard where you want three rows, use `ROW_NUMBER`; for 'show me everyone in the top three including ties', use `RANK` or `DENSE_RANK` depending on whether you want the gap in the numbering."

## Q68 — What's the difference between `WHERE` and `HAVING`?

> "`WHERE` filters rows before aggregation, `HAVING` filters groups after it. So a condition on a raw column belongs in `WHERE` and a condition on an aggregate belongs in `HAVING`. It matters for performance as well as correctness — filtering in `WHERE` reduces what gets aggregated, so pushing a condition down there when you can is strictly cheaper. The order of evaluation is `FROM`, then `WHERE`, then `GROUP BY`, then `HAVING`, then `SELECT`, then `ORDER BY`, which is also why you can't reference a `SELECT` alias in `WHERE` but can in `ORDER BY`."

## Q69 — Compute month-over-month growth in placements.

```sql
WITH monthly AS (
  SELECT DATE_TRUNC('month', start_date) AS month, COUNT(*) AS placements
  FROM placements
  GROUP BY 1
)
SELECT month,
       placements,
       LAG(placements) OVER (ORDER BY month)                       AS prev_month,
       ROUND(100.0 * (placements - LAG(placements) OVER (ORDER BY month))
             / NULLIF(LAG(placements) OVER (ORDER BY month), 0), 1) AS mom_pct
FROM monthly
ORDER BY month DESC
LIMIT 6;
```

| month | placements | prev_month | mom_pct |
|---|---|---|---|
| 2026-08-01 | 6 | 58 | -89.7 |
| 2026-07-01 | 58 | 38 | 52.6 |
| 2026-06-01 | 38 | 39 | -2.6 |
| 2026-05-01 | 39 | 21 | 85.7 |
| 2026-04-01 | 21 | 25 | -16.0 |
| 2026-03-01 | 25 | 24 | 4.2 |

**Say the thing about the top row.** August is not down 90% — August has barely begun, and these are placement *start* dates, so the only August rows are the ones already scheduled. The same incompleteness that breaks fill-rate trends breaks growth trends. The fix is either to exclude the partial period or to compare like-for-like, month-to-date against month-to-date. Spotting that unprompted in a live exercise is worth more than the window function itself.

Note also the volatility underneath: −16%, +86%, −3%, +53%. On counts this small, month-over-month growth is mostly noise, and saying so is the responsible answer — *"at forty placements a month I wouldn't manage on month-over-month percentages, I'd use a three-month rolling average and keep MoM for the commentary."*

The `NULLIF` guards the first month, where `LAG` is null, and any period with zero placements. Division by zero in BigQuery raises an error rather than returning null, so `SAFE_DIVIDE(a, b)` is the idiomatic BigQuery form.

## Q70 — Write a running total.

```sql
SELECT DATE_TRUNC('month', start_date)                 AS month,
       SUM(placement_fee_usd)                          AS fees,
       SUM(SUM(placement_fee_usd)) OVER (
         ORDER BY DATE_TRUNC('month', start_date)
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_fees
FROM placements
GROUP BY 1
ORDER BY 1;
```

The nested `SUM(SUM(...)) OVER (...)` looks wrong the first time you see it and is correct: the inner `SUM` aggregates within the group, the outer one is a window function running over the aggregated result. Being able to explain that calmly is a small credibility win. Specifying the frame explicitly is a habit worth having — the default frame with an `ORDER BY` is `RANGE UNBOUNDED PRECEDING`, which behaves differently from `ROWS` when there are ties in the ordering column.

## Q71 — Find records in one table with no match in another.

Three ways, and knowing which is fastest matters.

```sql
-- LEFT JOIN with a null check: the reconciliation query
SELECT v.vacancy_id, v.role_family, v.filled_date
FROM vacancies v
LEFT JOIN placements p ON p.vacancy_id = v.vacancy_id
WHERE v.status = 'filled' AND p.placement_id IS NULL;
```

Twelve rows. The other two forms are `NOT EXISTS`, which is usually the fastest and is null-safe, and `NOT IN`, which is the one to warn about:

```sql
SELECT v.vacancy_id FROM vacancies v
WHERE v.status = 'filled'
  AND NOT EXISTS (SELECT 1 FROM placements p WHERE p.vacancy_id = v.vacancy_id);
```

> "I'd avoid `NOT IN` against a subquery that can return nulls, because `NOT IN` with a null in the list returns no rows at all rather than what you meant. It's a silent, total failure — you get an empty result and conclude there are no exceptions. `NOT EXISTS` doesn't have that behaviour, so it's my default."

That warning is a genuinely good answer and very few candidates give it.

## Q72 — What's the result of the reconciliation query, and why does it matter?

> "Twelve vacancies marked filled with no matching placement record, and nine placements attached to vacancies that aren't marked filled. Those aren't data curiosities, they're a reconciliation failure between two systems — the ATS says one thing and the billing side says another. Twelve filled vacancies with no placement record means twelve fees potentially never invoiced. That's the sentence I'd lead with, because it converts a data problem into a money problem, and a money problem gets acted on."

## Q73 — Compute a median in SQL.

```sql
SELECT role_family,
       COUNT(*)                                                    AS filled,
       ROUND(AVG(DATE_DIFF('day', opened_date, filled_date)), 1)   AS avg_days,
       MEDIAN(DATE_DIFF('day', opened_date, filled_date))          AS median_days
FROM vacancies
WHERE status = 'filled'
  AND filled_date IS NOT NULL
  AND filled_date >= opened_date          -- excludes 6 impossible rows
GROUP BY 1
ORDER BY median_days DESC;
```

| role_family | filled | avg_days | median_days |
|---|---|---|---|
| Technical | 49 | 26.4 | 28.0 |
| Bookkeeping | 53 | 23.7 | 22.0 |
| Executive VA | 59 | 20.3 | 19.0 |
| Marketing VA | 51 | 18.9 | 18.0 |
| Sales VA | 65 | 18.3 | 18.0 |
| Customer Support | 67 | 17.6 | 17.0 |

`MEDIAN` is DuckDB. In BigQuery there is no `MEDIAN`, so you write `APPROX_QUANTILES(x, 2)[OFFSET(1)]` for a fast approximate median, or `PERCENTILE_CONT(x, 0.5) OVER ()` for an exact one — and knowing that BigQuery's exact percentile functions are window functions rather than aggregates is a dialect detail worth having.

Say why you reported both: *"time-to-fill distributions have a long right tail, so a handful of four-month roles drag the mean up to describe nobody's actual experience. I report the median alongside it, and where they diverge I say so."*

## Q74 — Why did you exclude those six rows, and is that legitimate?

> "Six vacancies have a fill date before their open date, which is physically impossible, so they're corrupt rather than extreme. Excluding them is legitimate — including them would produce negative durations that drag the average down. But two things make it legitimate rather than convenient. I state the exclusion on the face of the output rather than burying it, and I raise the rows as a data-quality finding rather than just filtering them away, because six impossible dates means something upstream permits them and a constraint should have prevented it at write time. Silently dropping bad rows is how a data problem becomes permanent."

## Q75 — Write the funnel query.

```sql
SELECT (SELECT COUNT(*) FROM submittals)                              AS submittals,
       (SELECT COUNT(DISTINCT submittal_id) FROM interviews)          AS reached_interview,
       (SELECT COUNT(*) FROM interviews WHERE completed = 1)          AS interviews_completed,
       (SELECT COUNT(*) FROM interviews WHERE outcome = 'offer')      AS offers,
       (SELECT COUNT(*) FROM submittals WHERE stage = 'hired')        AS hires;
```

| submittals | reached_interview | interviews_completed | offers | hires |
|---|---|---|---|---|
| 3918 | 1835 | 1719 | 482 | 362 |

The point to make while typing: *"I'm computing the interview stage from the interviews table rather than from the submittal status column, because status records the terminal state and overwrites history. A candidate who interviewed and was then rejected shows 'rejected', and the interview disappears. Build the funnel from the status column and you get an 11% submittal-to-interview rate and a 100% interview-to-offer rate, both nonsense. Status columns overwrite history; event tables preserve it."*

## Q76 — Pivot: hires by role family across months, in one query.

```sql
SELECT v.role_family,
       COUNT(*) FILTER (WHERE DATE_TRUNC('month', p.start_date) = DATE '2026-05-01') AS may,
       COUNT(*) FILTER (WHERE DATE_TRUNC('month', p.start_date) = DATE '2026-06-01') AS jun,
       COUNT(*) AS total
FROM placements p
JOIN vacancies v ON v.vacancy_id = p.vacancy_id
GROUP BY 1
ORDER BY total DESC;
```

| role_family | may | jun | total |
|---|---|---|---|
| Customer Support | 8 | 11 | 65 |
| Sales VA | 7 | 6 | 65 |
| Executive VA | 7 | 5 | 60 |
| Bookkeeping | 3 | 7 | 55 |
| Technical | 6 | 6 | 51 |
| Marketing VA | 8 | 3 | 51 |

`COUNT(*) FILTER (WHERE ...)` is the standard-SQL form and DuckDB supports it. **In BigQuery you write `COUNTIF(condition)`**, which is shorter and does the same thing; `SUM(IF(cond, 1, 0))` works everywhere and is what you fall back on in older dialects. Knowing all three and naming the dialect each belongs to reads as someone who has actually moved between warehouses.

## Q77 — A join doubled my revenue number. What happened and how do you prevent it?

> "Fan-out. You joined a table at one grain to a table at a finer grain — one vacancy to many submittals, say — and every row on the coarse side got repeated once per matching row on the fine side. Then `SUM` on the coarse side's amount counts it several times. It never errors, and the total looks plausible, which is what makes it dangerous. Three defences. Aggregate before joining, so both sides are at the same grain when they meet. Or use a correlated subquery or a window function instead of a join when you only need one derived value. Or, if you must join first, sum a distinct-safe expression rather than the raw column. The habit that actually catches it is checking the row count before and after every join against what I expected — if a join changes the row count and I didn't intend it to, something is wrong even if the numbers look fine."

## Q78 — `COUNT(*)` versus `COUNT(column)` versus `COUNT(DISTINCT column)`?

> "`COUNT(*)` counts rows including ones where every column is null. `COUNT(column)` counts rows where that column is not null, so the two differ by exactly the number of nulls — which makes `COUNT(*) - COUNT(col)` a quick null audit. `COUNT(DISTINCT col)` counts unique non-null values and is much more expensive, because it has to hold or sort the distinct set. In BigQuery, `COUNT(DISTINCT)` on a large column is one of the more expensive things you can do, and `APPROX_COUNT_DISTINCT` uses HyperLogLog to get within about one percent for a fraction of the cost — which is fine for a dashboard tile and not fine for an invoice."

## Q79 — `UNION` versus `UNION ALL`?

> "`UNION` removes duplicates, `UNION ALL` doesn't. Removing duplicates requires a sort or a hash of the entire result, so `UNION` is materially more expensive, and most of the time you know the sets are disjoint and the deduplication is pure waste. My default is `UNION ALL` unless I specifically want deduplication — which in a stacked data-quality check suite, for example, I never do, because each check is a distinct row by construction."

## Q80 — How do you handle nulls in aggregations and comparisons?

> "The rule is that aggregate functions ignore nulls but arithmetic propagates them, and that asymmetry catches people. `AVG(col)` skips nulls, so it divides by the count of non-null values, not by the row count — which means `AVG` of a column that's 90% null is the average of the 10%, and it looks like a real number. Comparisons are the other trap: `NULL = NULL` is not true, it's unknown, so any equality test against null fails silently. You use `IS NULL`, or `COALESCE` to substitute, or in BigQuery `IS NOT DISTINCT FROM` for a null-safe equality. And nulls in a `NOT IN` list poison the whole predicate, which is why I use `NOT EXISTS`."

## Q81 — Write the data-quality check suite.

```sql
SELECT 'DQ1 filled vacancy with no placement' AS check_name, COUNT(*) AS anomalies
FROM vacancies v LEFT JOIN placements p USING (vacancy_id)
WHERE v.status = 'filled' AND p.placement_id IS NULL
UNION ALL SELECT 'DQ2 placement on a non-filled vacancy', COUNT(*)
FROM placements p JOIN vacancies v USING (vacancy_id) WHERE v.status <> 'filled'
UNION ALL SELECT 'DQ3 filled_date before opened_date', COUNT(*)
FROM vacancies WHERE filled_date IS NOT NULL AND filled_date < opened_date
UNION ALL SELECT 'DQ4 non-positive monthly rate', COUNT(*)
FROM placements WHERE monthly_rate_usd <= 0
UNION ALL SELECT 'DQ5 duplicate submittals', COUNT(*) FROM (
  SELECT vacancy_id, candidate_id, submitted_date FROM submittals
  GROUP BY 1,2,3 HAVING COUNT(*) > 1)
UNION ALL SELECT 'DQ6 duplicate candidate emails', COUNT(*) FROM (
  SELECT email FROM candidates GROUP BY 1 HAVING COUNT(*) > 1)
UNION ALL SELECT 'DQ7 ad spend with no campaign', COUNT(*)
FROM marketing_spend WHERE campaign IS NULL OR campaign = '';
```

| check_name | anomalies |
|---|---|
| DQ1 filled vacancy with no placement | 12 |
| DQ2 placement on a non-filled vacancy | 9 |
| DQ3 filled_date before opened_date | 6 |
| DQ4 non-positive monthly rate | 7 |
| DQ5 duplicate submittals | 15 |
| DQ6 duplicate candidate emails | 40 |
| DQ7 ad spend with no campaign | 42 |

The value is in classifying them, not listing them. DQ1 and DQ2 are cross-system reconciliation failures — a money problem. DQ3 and DQ4 are impossible values a constraint should have prevented at write time. DQ5 and DQ6 are duplicates, and they need different treatment because duplicate submittals inflate every funnel denominator while duplicate candidate emails can put the same person in front of the same client twice. DQ7 is missing dimension data, which silently breaks attribution — forty-two days of spend that can't be assigned to a campaign.

## Q82 — What makes BigQuery different from Postgres or MySQL?

> "It's columnar and serverless, and on the default pricing model **you pay for the bytes your query scans**, not for rows returned and not for time taken. Every consequence follows from that sentence. Because storage is columnar, a query touching three columns of a two-hundred-column table reads three columns' worth of bytes — so `SELECT *` is expensive in a way it never was in MySQL. Because it's serverless there's no index to create; you tune with partitioning, clustering, and by not reading what you don't need. The mental picture I use is that a row-store is a filing cabinet of folders — pulling one client's folder is cheap, scanning all of them is expensive — while BigQuery is a warehouse where each shelf holds one *attribute* of every client. Fetching one attribute for everybody is trivial; fetching everything about everybody means walking every shelf."

## Q83 — Does `LIMIT 10` make a BigQuery query cheaper?

> "No, and this is the single most common misconception about BigQuery. The engine scans everything and then discards all but ten rows — you're billed for the full scan. If you just want to look at a table, use the Preview tab in the console or `bq head`, which cost nothing at all, rather than `SELECT * FROM t LIMIT 100`, which costs a full scan for the same information."

Short, confident, correct. Disproportionately impressive because so many people get it wrong.

## Q84 — How do you reduce the cost of a BigQuery query?

> "Five things, roughly in order of impact. Never `SELECT *` on a wide table — name your columns, which on a two-hundred-column table where you need four is a fiftyfold reduction in bytes billed. Always filter on the partition column, because a table partitioned by day and queried without a date filter scans its entire history. Check the estimate before running: the console shows 'this query will process X' before you execute, and the CLI has `bq query --dry_run` — reading that number before pressing run is the habit that separates an analyst who costs the company money from one who doesn't. Materialise anything that's recomputed constantly, because a twelve-table join running on every dashboard refresh for forty users should be a scheduled table or a materialised view — you pay once an hour instead of forty times. And know that clustering makes filters cheaper, not just faster, since skipped blocks aren't billed."

## Q85 — Partitioning versus clustering?

> "They solve different problems. Partitioning physically splits a table into segments, almost always by a date, so a filter on the partition column eliminates whole segments before reading anything. You get up to four thousand partitions, so daily partitioning covers about eleven years — and you can't partition by a high-cardinality column like `client_id`. Clustering sorts the data *within* each partition by up to four columns, letting the engine skip blocks. Clustering is what you use for the high-cardinality columns, and **order matters**: filtering on the first clustering column is most effective and the benefit degrades as you move right, the same way as the leftmost-prefix rule for a composite index. One practical trap: partition on the column people actually filter by, which is the event date, not the ingestion date. Get that wrong and everybody filters on `submitted_date` while the table is partitioned by `_PARTITIONTIME`, and no pruning ever happens."

```sql
CREATE TABLE `agency.submittals` (
  submittal_id   STRING NOT NULL,
  vacancy_id     STRING NOT NULL,
  candidate_id   STRING NOT NULL,
  submitted_date DATE   NOT NULL,
  stage          STRING,
  english_level  STRING
)
PARTITION BY submitted_date
CLUSTER BY vacancy_id, stage
OPTIONS (
  require_partition_filter  = TRUE,
  partition_expiration_days = 1095
);
```

> "`require_partition_filter = TRUE` is the one I'd mention out loud. It rejects any query with no date filter outright, which makes the expensive mistake *impossible* rather than merely discouraged — the same philosophy as a database constraint. That framing lands with anyone who's been surprised by a bill."

## Q86 — What are the two BigQuery pricing models, and why does it matter to an analyst?

> "On-demand bills per terabyte scanned. Capacity pricing buys slots — a fixed amount of compute — which makes the bill predictable and the cost of an individual query irrelevant. It matters because the right optimisation strategy is different under each: under on-demand you minimise bytes scanned, under slots you minimise contention and long-running queries, because your enemy is a colleague's query hogging the reservation rather than your own bill. That's why 'are you on on-demand or capacity pricing?' is one of the questions I'd ask you — it changes how I'd write and schedule things."

## Q87 — How do you make a load idempotent?

> "`MERGE` on a natural or surrogate key, so rerunning the same load updates rather than duplicates. This is the thing that matters most in practice, because pipelines get rerun — after a failure, after a backfill, after someone clicks the button twice — and a non-idempotent load quietly doubles a day's data."

```sql
MERGE `agency.submittals` T
USING `staging.submittals_incoming` S
ON T.submittal_id = S.submittal_id
WHEN MATCHED AND S.stage_updated_date > T.stage_updated_date THEN
  UPDATE SET stage = S.stage, stage_updated_date = S.stage_updated_date
WHEN NOT MATCHED THEN
  INSERT (submittal_id, vacancy_id, candidate_id, submitted_date, stage)
  VALUES (S.submittal_id, S.vacancy_id, S.candidate_id, S.submitted_date, S.stage);
```

> "The alternative pattern for partitioned tables is delete-and-reinsert the affected partition in a single transaction, which is often simpler and cheaper than a `MERGE` when you're reloading a whole day. I did this in the Beam pipelines at Tekkod — making the MongoDB-to-BigQuery loads idempotent so reruns didn't duplicate data was a design requirement, not an afterthought."

## Q88 — Where do you use arrays and structs, and where do they bite?

> "They're BigQuery's answer to nested data, and they're the reason you don't have to flatten a document store into a dozen tables. A struct is a record with named fields; an array is a repeated field. You query them with `UNNEST`, which cross-joins each element into its own row. Where they bite is exactly there: `UNNEST` changes the grain, so any aggregation after it double-counts the parent unless you're careful. That's fan-out again, wearing a different hat. I used this pattern moving MongoDB collections into BigQuery at Tekkod — mapping nested documents onto nested and repeated fields rather than flattening, which keeps the natural grain of the document and avoids a join to reassemble it."

```sql
SELECT c.client_id, v.role_family
FROM `agency.clients` c, UNNEST(c.vacancies) AS v;
```

## Q89 — How would you monitor data quality inside BigQuery itself?

> "`INFORMATION_SCHEMA` is the part people don't know about, and it answers most monitoring questions without any external tooling. `INFORMATION_SCHEMA.PARTITIONS` gives you last-modified time per partition, which is a freshness check. `INFORMATION_SCHEMA.JOBS_BY_PROJECT` gives you every query run, with bytes billed — so you can find your most expensive queries and your most expensive users, which is usually the first thing anyone wants when a bill surprises them. And `TABLES` and `COLUMNS` let you detect schema drift by diffing today's column list against yesterday's. I'd schedule a query that writes those results into a small monitoring table and put a freshness tile on the dashboard fed from it."

## Q90 — What are the main dialect differences between what you practised on and BigQuery?

The practice dataset is DuckDB, so be ready for the translation to be probed.

| Concept | DuckDB | BigQuery |
|---|---|---|
| Conditional count | `COUNT(*) FILTER (WHERE c)` | `COUNTIF(c)` |
| Safe division | `a / NULLIF(b, 0)` | `SAFE_DIVIDE(a, b)` |
| Median | `MEDIAN(x)` | `APPROX_QUANTILES(x, 2)[OFFSET(1)]` |
| Date difference | `DATE_DIFF('day', a, b)` | `DATE_DIFF(b, a, DAY)` — note the argument order |
| String concatenation | `\|\|` or `CONCAT` | `CONCAT` (or `\|\|`) |
| Cast | `x::INT` | `CAST(x AS INT64)` |
| Exclude columns | `SELECT * EXCLUDE (c)` | `SELECT * EXCEPT (c)` |
| Group by everything | `GROUP BY ALL` | `GROUP BY ALL` (both support it) |
| Distinct-on | `DISTINCT ON` | `QUALIFY ROW_NUMBER() ... = 1` |

**`DATE_DIFF` is the one that will catch you**, because the argument order is reversed and it fails silently — you get a negative number rather than an error. If you write it live in front of them and pause to check, say why: *"BigQuery's `DATE_DIFF` takes the later date first, which is the opposite of DuckDB's, so I always check that one."* Naming a trap you're navigating is better than navigating it invisibly.

---

*Next: [05 Tableau and dashboards](05_tableau_and_dashboards.md) · Back to [question bank index](README.md) · Source: [02 BigQuery for analysts](../02_bigquery_for_analysts.md) · [05 SQL drills](../05_sql_drills_with_answers.md)*
