# BigQuery for analysts

*Remote Leverage — Data Analyst · interview Monday 3 August 2026. Practice locally with `practice/agency.duckdb`, whose dialect is close enough to BigQuery that almost everything transfers; the differences are listed in section 9.*

---

## Where you actually stand

You are not starting from zero here, and you should not present yourself as if you were. Your resume says you *"implemented ETL data pipelines via Apache Beam to migrate MongoDB data to BigQuery (GCP)"* at Tekkod. That is real, and it is more than most analyst candidates have — Beam is the engine behind Dataflow, which is Google's own managed pipeline service.

But there is an honest gap and you should know exactly what it is. You built pipelines that **wrote into** BigQuery. This job **reads from** it, all day, and the questions are different. A pipeline engineer is asked about throughput and idempotency. An analyst is asked *"this query costs forty dollars every time the dashboard refreshes — why, and what do you do about it?"*

That question, in some form, is the one they will ask. Section 2 is the answer.

---

## 1. The one thing that makes BigQuery different

BigQuery is a **columnar, serverless warehouse**, and on the default pricing model **you pay for the bytes your query scans**, not for the rows it returns and not for the time it takes.

Every consequence that matters follows from that single sentence.

Because storage is columnar, a query touching three columns of a two-hundred-column table reads three columns' worth of bytes. Column pruning is not an optimisation you request, it is how the engine works — which is exactly why `SELECT *` is expensive in a way it never was in MySQL or Postgres.

Because you pay for bytes scanned rather than rows returned, **`LIMIT 10` does not make a query cheap**. The engine still scans everything, then throws away all but ten rows. This is the single most common misconception about BigQuery and it is a very likely interview question. If you remember one fact from this module, remember this one.

Because it is serverless, there is no index to create. You do not tune BigQuery with indexes; you tune it with **partitioning, clustering, and by not reading what you do not need**.

The analogy worth carrying: a row-store database is a filing cabinet of folders — pulling one client's folder is cheap, scanning all of them is expensive. BigQuery is a warehouse of shelves where each shelf holds one *attribute* of every client. Fetching one attribute for everybody is trivial; fetching everything about everybody means walking every shelf. Design your questions accordingly.

---

## 2. Controlling cost — the answer they want to hear

**Never `SELECT *` on a wide table.** Name your columns. On a table with two hundred columns where you need four, this alone is a fiftyfold reduction in bytes billed.

**Filter on the partition column, always.** A table partitioned by day, queried without a date filter, scans its entire history. With a filter, it scans the days you asked for. On two years of daily data that is often a hundredfold difference.

**Check the estimate before running.** The BigQuery console shows a "This query will process X" estimate in the top right before you execute, and the CLI has `bq query --dry_run`. Getting into the habit of reading that number before pressing run is the behaviour that separates an analyst who costs the company money from one who does not. Say that you do this.

**Preview instead of querying when you just want to look.** Clicking the Preview tab on a table, or `bq head`, costs nothing. `SELECT * FROM t LIMIT 100` costs a full scan. Same information, wildly different bill.

**Materialise what is recomputed constantly.** If a dashboard runs the same twelve-table join every refresh for forty users, that join should be a scheduled table or a materialised view, not a live query. You pay once an hour instead of forty times an hour.

**Know that clustering makes filters cheaper, not just faster.** On a clustered table, a filter on the clustering column lets BigQuery skip blocks, and skipped blocks are not billed.

**Know the two pricing models.** On-demand bills per terabyte scanned; capacity pricing buys slots, a fixed amount of compute, which makes cost predictable and query cost irrelevant. Asking which model the company is on is an excellent interview question, because the right optimisation strategy is different under each: under on-demand you minimise bytes, under slots you minimise contention and long-running queries.

And a governance point worth one sentence: **custom quotas** can cap how many bytes a user or project may scan per day. If they have been surprised by a bill, that is part of the answer.

---

## 3. Partitioning and clustering

They solve different problems and interviewers like to see whether you can distinguish them.

**Partitioning** physically splits a table into segments, almost always by a date or timestamp column, sometimes by ingestion time or an integer range. A filter on the partition column eliminates whole segments before reading. You get up to four thousand partitions, so daily partitioning covers about eleven years. Partitioning by a high-cardinality column such as `client_id` is not possible and not the point.

**Clustering** sorts the data within each partition by up to four columns. A filter on a clustering column lets the engine skip blocks. Clustering is what you use for the high-cardinality columns — `client_id`, `vacancy_id` — and **order matters**: filtering on the first clustering column is most effective, and the benefit degrades as you move right, in the same way as the leftmost-prefix rule for a composite index.

```sql
-- BigQuery DDL
CREATE TABLE `agency.submittals`
(
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
  require_partition_filter = TRUE,   -- a query with no date filter is rejected outright
  partition_expiration_days = 1095
);
```

`require_partition_filter = TRUE` is the setting to mention out loud. It makes the expensive mistake *impossible* rather than merely discouraged — the same philosophy as a database constraint. That framing will land well with anyone who has been burned by a runaway bill.

A practical note: partition on the column people actually filter by, which is usually the **event date**, not the row's ingestion date. Getting this wrong means everybody filters on `submitted_date` while the table is partitioned by `_PARTITIONTIME`, and no pruning ever happens.

---

## 4. The Standard SQL you need at your fingertips

### Safety functions

`SAFE_DIVIDE(a, b)` returns `NULL` instead of raising a division-by-zero error. It is the idiomatic BigQuery way to write a rate, and it is shorter than `a / NULLIF(b, 0)` — though both work and knowing both is good.

`SAFE_CAST(x AS INT64)` returns `NULL` instead of failing when a value will not convert. Essential on data landed from an ad platform or a CSV where one row in a thousand contains `"n/a"`.

Any function can be prefixed with `SAFE.` — `SAFE.PARSE_DATE('%m/%d/%Y', d)` — which turns a parse failure into a null instead of killing the whole query. On messy source data this is the difference between a job that completes with a documented gap and a job that fails at 3 a.m.

`IFNULL(x, 0)` and `COALESCE(a, b, c)` do what you expect.

### QUALIFY

`QUALIFY` filters on a window function without a wrapping subquery. It is BigQuery, Snowflake and DuckDB; it is not standard everywhere, so say "in BigQuery" when you use it.

```sql
-- The first requisition each client ever opened
SELECT client_id, vacancy_id, opened_date, role_family
FROM vacancies
QUALIFY ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY opened_date) = 1;
```

| client_id | vacancy_id | opened_date | role_family |
|---|---|---|---|
| C0001 | V00001 | 2026-03-15 | Bookkeeping |
| C0002 | V00002 | 2025-02-11 | Marketing VA |
| C0003 | V00003 | 2025-03-03 | Executive VA |

That deduplication pattern — partition by the business key, order by a keep-rule, keep row number one — is the same one you already use. It is the most reusable four lines in analytics: latest record per entity, first touch per customer, deduplicating a replayed load.

### SELECT * EXCEPT and REPLACE

```sql
SELECT * EXCEPT (email, phone),          -- everything but the PII columns
       UPPER(country) AS country
FROM candidates;

SELECT * REPLACE (ROUND(placement_fee_usd, 0) AS placement_fee_usd)
FROM placements;
```

`SELECT * EXCEPT (...)` is genuinely useful and slightly showy in a good way. It is also a neat, natural place to mention that you strip PII columns by default — which connects straight to the "use AI tools securely" line in the job description.

### Arrays and structs

BigQuery stores nested and repeated data natively, which is why it swallows JSON from APIs so comfortably. An `ARRAY` is a repeated field; a `STRUCT` is a record. `UNNEST` flattens an array into rows, and a cross join with `UNNEST` is the standard idiom.

```sql
-- One row per vacancy, carrying its shortlist as nested data
SELECT v.vacancy_id,
       COUNT(s.submittal_id) AS n_submitted,
       ARRAY_AGG(STRUCT(s.candidate_id, s.english_level)
                 ORDER BY s.submitted_date LIMIT 5) AS shortlist
FROM vacancies v
JOIN submittals s USING (vacancy_id)
GROUP BY 1;

-- And back out again
SELECT vacancy_id, c.candidate_id, c.english_level
FROM shortlists, UNNEST(shortlist) AS c;
```

This matters for your story: **a MongoDB document maps naturally onto a BigQuery struct**. When you describe the Tekkod migration, saying that you mapped nested Mongo documents onto BigQuery's nested and repeated fields rather than flattening everything into wide tables shows you understood the target model, not just the transfer.

### Window functions

The same set you already know: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `NTILE`, running totals with `SUM() OVER (ORDER BY ...)`, moving averages with `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`.

```sql
SELECT month,
       fees,
       ROUND(100.0 * (fees - LAG(fees) OVER (ORDER BY month))
             / LAG(fees) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM (SELECT DATE_TRUNC(start_date, MONTH) AS month, SUM(placement_fee_usd) AS fees
      FROM placements GROUP BY 1)
ORDER BY month DESC;
```

| month | fees | mom_growth_pct |
|---|---|---|
| 2026-07 | 135 660 | 53,3 |
| 2026-06 | 88 515 | 34,2 |
| 2026-05 | 65 956 | −9,9 |
| 2026-04 | 73 206 | 43,3 |

One caution the practice data will teach you: some `start_date` values fall **after** today, because a placement is agreed before the VA actually starts. A month-to-date revenue chart that includes future start dates is wrong. Filter with `WHERE start_date <= CURRENT_DATE()` and say why.

`SUM(SUM(x)) OVER (ORDER BY month)` — a window function over an aggregate — gives a cumulative total in one pass. It looks strange the first time; it is legal and it is idiomatic.

### Wildcard tables

Ad platforms and GA4 land one table per day. `_TABLE_SUFFIX` filters across them, and filtering on it prunes tables the same way a partition filter prunes partitions.

```sql
SELECT _TABLE_SUFFIX AS day, SUM(spend_usd) AS spend
FROM `project.ads.spend_*`
WHERE _TABLE_SUFFIX BETWEEN '20260601' AND '20260630'
GROUP BY 1;
```

Forgetting the `_TABLE_SUFFIX` filter scans every daily table ever created. This is a classic and expensive mistake, and knowing it is a strong signal.

### GROUP BY ALL

Recent BigQuery accepts `GROUP BY ALL`, which groups by every non-aggregated column in the select list. Convenient for exploration; be explicit in production code so that adding a column later does not silently change the grain.

---

## 5. MERGE — idempotent loads

`MERGE` is BigQuery's upsert, and it is how a scheduled job reloads the last few days of data without duplicating rows.

```sql
MERGE `agency.submittals` AS target
USING (
  SELECT * FROM `agency.staging_submittals`
  WHERE submitted_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
) AS source
ON  target.submittal_id = source.submittal_id
WHEN MATCHED AND target.stage <> source.stage THEN
  UPDATE SET stage = source.stage, stage_updated_date = source.stage_updated_date
WHEN NOT MATCHED THEN
  INSERT (submittal_id, vacancy_id, candidate_id, submitted_date, stage)
  VALUES (source.submittal_id, source.vacancy_id, source.candidate_id,
          source.submitted_date, source.stage);
```

Three points to make if this comes up. The three-day lookback window handles **late-arriving data** without reprocessing history. The `WHEN MATCHED AND ...` guard avoids rewriting rows that have not changed, which matters because BigQuery rewrites whole partitions on update. And the whole point is **idempotency**: rerunning the job produces the same table, which is precisely what you want when you are not sure whether last night's run completed.

You already know this concept from ETL work. The word to use is idempotent, and the reason to care is that in a bureau — or a small agency — someone will always rerun a job "just in case".

---

## 6. Data quality and monitoring, inside BigQuery

The reconciliation suite from [module 01](01_recruiting_sales_marketing_metrics.md) is just SQL and runs anywhere. BigQuery adds three tools worth naming.

**`ASSERT`** raises an error when a condition fails, which turns a check into something that can halt a pipeline instead of quietly logging.

```sql
ASSERT (SELECT COUNT(*) FROM `agency.placements` WHERE monthly_rate_usd <= 0) = 0
  AS 'Placements found with a non-positive monthly rate';
```

**`INFORMATION_SCHEMA`** is how you monitor freshness, volume and cost without any external tool. This is the query to remember, because "how would you monitor pipeline health" is responsibility four of the job description.

```sql
-- Freshness and size of every table in the dataset
SELECT table_id,
       TIMESTAMP_MILLIS(last_modified_time) AS last_loaded,
       row_count,
       ROUND(size_bytes / POW(1024, 3), 2) AS size_gb
FROM `agency.__TABLES__`
ORDER BY last_loaded;

-- The twenty most expensive queries of the last week, and who ran them
SELECT user_email,
       job_id,
       ROUND(total_bytes_billed / POW(1024, 4), 3) AS tb_billed,
       ROUND(total_slot_ms / 1000 / 60, 1)         AS slot_minutes,
       query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY' AND state = 'DONE'
ORDER BY total_bytes_billed DESC
LIMIT 20;
```

Offering to build that second query in your first week is a concrete, cheap, high-visibility contribution. Every company running BigQuery has a handful of queries burning most of the budget, and almost nobody has looked.

**Table snapshots and time travel.** BigQuery keeps seven days of history by default, so `FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)` recovers a table as it was before someone's bad `UPDATE`. Snapshots make that durable. This is your "restore" answer, and it is much cheaper than it sounds.

---

## 7. The rest of GCP, in one paragraph each

**Cloud Storage** is where raw files land before loading; an external table can query a bucket in place, which is handy for a one-off but slow for anything repeated.

**Dataflow** is managed Apache Beam — *your* Apache Beam. If they ask about pipelines, this is the sentence: "the Beam pipelines I wrote to move MongoDB into BigQuery are the same programming model Dataflow runs as a managed service." That single connection turns a resume bullet into current relevance.

**Data Transfer Service** does scheduled loads from Google Ads, YouTube, Google Analytics and S3 without any code. Worth naming, because a lot of what a small agency needs is exactly this rather than a custom pipeline.

**Cloud Composer** is managed Airflow, for orchestrating multi-step dependencies. **Scheduled queries** are the lightweight alternative — a saved query on a cron, configured in the console in two minutes, which covers most of what a small team actually needs. Knowing when *not* to reach for Airflow is a maturity signal.

**Looker Studio** connects to BigQuery natively and you already know it — your resume says you built dashboards on it at Tekkod. Worth mentioning as evidence that you have taken BigQuery data all the way to an executive audience.

**IAM**, briefly: roles are granted at project, dataset or table level; `bigquery.dataViewer` reads, `bigquery.jobUser` runs queries. Authorised views let someone query a curated view without any access to the underlying table — the exact mechanism you described for restricting a donor to aggregate data, which transfers here as restricting a client-facing user to non-PII columns.

---

## 8. n8n, honestly

You have never used it. Do not pretend otherwise; it is listed as preferred, not required, and a bluff about a tool they use daily is the fastest way to lose credibility.

What it is: a self-hostable, open-source workflow automation tool — nodes wired into a graph, triggered by a schedule or a webhook, with connectors to hundreds of services and a code node for anything else. Think Zapier that you can host yourself and put in version control. In a company like this it typically moves data between the ATS, HubSpot, Stripe and Slack, and posts alerts when something needs attention.

The honest answer that still lands well: *"I haven't used n8n specifically. I've built the same class of thing in Apache Beam and in Python on AWS — scheduled extract, transform, load, with retries and failure alerting — so the concepts transfer and the node-based interface is a shorter learning curve than the code I'm used to writing. I'd expect to be productive in it within a week, and I'd want to know what you're currently automating with it."* Then ask the question. Asking beats claiming.

Between now and Monday, spend forty minutes on n8n's own quickstart and build one trivial workflow — a schedule trigger, an HTTP request, a filter. Then you can say "I spent an evening in it this week", which is true, verifiable, and shows initiative.

---

## 9. Dialect differences: DuckDB practice → BigQuery

The practice database lets you rehearse everything for free. These are the translations to keep in mind so that you do not write DuckDB syntax in a BigQuery interview.

| Concept | DuckDB (practice) | BigQuery (say this) |
|---|---|---|
| Date difference | `DATE_DIFF('day', a, b)` | `DATE_DIFF(b, a, DAY)` |
| Truncate to month | `DATE_TRUNC('month', d)` | `DATE_TRUNC(d, MONTH)` |
| Safe division | `a / NULLIF(b, 0)` | `SAFE_DIVIDE(a, b)` |
| Conditional count | `COUNT(*) FILTER (WHERE c)` | `COUNTIF(c)` |
| Array aggregation | `LIST(x)` | `ARRAY_AGG(x)` |
| Build a record | `STRUCT_PACK(a := x)` | `STRUCT(x AS a)` |
| Median | `MEDIAN(x)` | `APPROX_QUANTILES(x, 2)[OFFSET(1)]` |
| Current date | `CURRENT_DATE` | `CURRENT_DATE()` |
| String concat | `a \|\| b` | `CONCAT(a, b)` |
| Same in both | `QUALIFY`, `UNNEST`, `EXCEPT`, window functions, CTEs | — |

`COUNTIF` deserves a highlight: it is BigQuery's own shorthand and using it naturally reads as fluency. `COUNTIF(stage = 'hired')` instead of `SUM(CASE WHEN stage = 'hired' THEN 1 ELSE 0 END)`.

The median translation is worth understanding rather than memorising: BigQuery has no `MEDIAN`, and `APPROX_QUANTILES(x, 2)` splits the distribution into two buckets, whose middle boundary at `OFFSET(1)` is the median. For quartiles you would use `APPROX_QUANTILES(x, 4)`.

---

## 10. Exercises

Rewrite five queries from [module 01](01_recruiting_sales_marketing_metrics.md) in BigQuery dialect — `COUNTIF`, `SAFE_DIVIDE`, `DATE_DIFF(b, a, DAY)`, `APPROX_QUANTILES` for the median time to fill. Write them out by hand; the muscle memory is the point.

Write the DDL for a partitioned and clustered `submittals` table, choose the partition and clustering columns deliberately, and be ready to justify both choices in one sentence each.

Write the `MERGE` that reloads the last three days of submittals idempotently, and explain what breaks without the lookback window.

Write the `INFORMATION_SCHEMA` query that lists last week's twenty most expensive queries, and decide what threshold would make you go and talk to whoever ran them.

Using `QUALIFY`, produce the most recent submittal per candidate, then the first placement per client — the same pattern twice, until it is automatic.

Take the funnel query from module 01 and rewrite it with `COUNTIF` throughout, then say which version you would put in production and why.

Estimate, in words, what a `SELECT *` on a two-year daily-partitioned table with two hundred columns costs relative to a properly filtered, column-pruned query. You will not be graded on the number; you will be graded on knowing that the answer is "orders of magnitude".

---

## Interview angles

**"How do you optimise a slow or expensive BigQuery query?"**

The first thing I do is separate slow from expensive, because in BigQuery they're different problems with different fixes. For expensive, the mental model is that you pay for bytes scanned, not rows returned, so I start with the two things that dominate everything else: select only the columns I need, because the storage is columnar and a `SELECT *` on a wide table reads every column; and filter on the partition column, because a query without a partition filter scans the entire table history. Those two changes alone are usually an order of magnitude. Then I look at whether the query is being recomputed constantly for a dashboard, in which case the right answer isn't to optimise it at all — it's to materialise it, either as a scheduled table or a materialised view, so you pay once an hour instead of forty times an hour. I also check the execution details for a join that explodes the row count, and for clustering on the high-cardinality columns people actually filter by. One thing I always mention because it surprises people: adding `LIMIT` doesn't reduce cost. The engine scans everything and then discards. If I just want to look at the data I use the table preview or `bq head`, which are free. And I check the estimate in the console before running anything unfamiliar, which takes two seconds and has saved me from some embarrassing bills. Structurally, the fix I'd push for is `require_partition_filter` on the big tables, so a query with no date filter is rejected rather than merely discouraged — the same reasoning as a database constraint: make the expensive mistake impossible rather than trusting everyone to remember.

**"What's the difference between partitioning and clustering?"**

Partitioning physically splits the table into segments, almost always by date, and a filter on the partition column eliminates whole segments before anything is read — so it's the coarse, high-impact lever, and it's limited to one column and to types that make sense as ranges. Clustering sorts the data within each partition by up to four columns, which lets the engine skip blocks that can't match, and it's the right tool for high-cardinality columns like a client ID or a vacancy ID that you'd never partition by. The order of clustering columns matters the way the leftmost prefix matters in a composite index: filtering on the first one gives you the most benefit and it degrades as you move right. In practice, for an events table I'd partition by the event date — the date people actually filter on, not the ingestion timestamp, because that's a classic mistake that means nobody ever gets pruning — and cluster by the one or two dimensions that appear in most `WHERE` clauses. And I'd set `require_partition_filter` to true so an unfiltered query fails loudly instead of quietly costing a hundred dollars.

**"Tell me about your experience with BigQuery."**

I'll be precise about the shape of it. At Tekkod I built the pipelines that fed it: Apache Beam jobs migrating MongoDB collections into BigQuery, which meant mapping nested documents onto BigQuery's nested and repeated fields rather than flattening everything into wide tables, and making the loads idempotent so a rerun didn't duplicate anything. Then I took the data out the other end into Looker Studio dashboards for operational visibility. So I've worked both ends of BigQuery — the loading side as an engineer and the reporting side. What I've done less of is the middle: living in it all day as an analyst writing exploratory SQL against someone else's warehouse, which is what this role is. That's why I've spent the last few days deliberately working on the analyst side — cost control, partition and cluster design, `QUALIFY` and `COUNTIF` and `SAFE_DIVIDE`, and the `INFORMATION_SCHEMA` queries for monitoring freshness and finding the queries that are burning the budget. That last one is something I'd offer to build in my first week, because nearly every company on BigQuery has a handful of queries consuming most of the spend and almost nobody has looked at which ones.

---

*Next: [Tableau in five days](03_tableau_in_five_days.md) · [Positioning and mock interview](04_positioning_and_mock_interview.md) · Back to [Recruiting metrics](01_recruiting_sales_marketing_metrics.md) · [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md)*
