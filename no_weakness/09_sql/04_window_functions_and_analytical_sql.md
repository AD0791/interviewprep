# Window functions and analytical SQL

*The default frame that silently breaks every running total, ties that make your top-N return the wrong number of rows, and the row-number trick that solves streaks.*

**Level:** L4–L5 · **Prerequisites:** [`02` execution order and joins](00_knowledge_graph.md)
**Syllabus:** [`SQL-18`–`SQL-23`](00_knowledge_graph.md) · **Roles:** DA ●●● DE ●●
**Measurement:** `Measured` — SQLite 3.51.0 on `ENV-A`. Every result below came out of a terminal. Window function semantics are ANSI-standard, so these results transfer to PostgreSQL and BigQuery; where a dialect adds something (`QUALIFY`, `FILTER`) it is noted and tagged `documented`.

---

## 1. The thing you already do

A running balance, which every financial dashboard needs:

```sql
-- Gist: running_balance.sql
SELECT created_at,
       amount,
       SUM(amount) OVER (ORDER BY created_at) AS running_balance
FROM transactions
WHERE account_id = 1
ORDER BY created_at;
```

And a top-N-per-group, which every leaderboard needs:

```sql
-- Gist: top_products.sql
SELECT * FROM (
  SELECT branch, product, revenue,
         RANK() OVER (PARTITION BY branch ORDER BY revenue DESC) AS rnk
  FROM sales
) WHERE rnk <= 3;
```

Both are the standard published answer to their question. Both are wrong in ways that produce plausible numbers.

The first returns a running total that **jumps**, skipping intermediate values, whenever two transactions share a timestamp — which for a date column is most of the time. The second returns **four rows** for a branch when you asked for three, or five, depending on ties.

Neither errors. Both look right in a spot check.

---

## 2. The questions you cannot answer about it

**What is the default window frame?** You have written `SUM(...) OVER (ORDER BY d)` many times without specifying one, so there is a default. Name it exactly, then say what it does when the `ORDER BY` column has duplicates.

**When would `RANK` give you more rows than you asked for?** And when is that the behaviour you actually want, rather than a bug?

**How do you find the longest run of consecutive days per user?** There is a standard technique. Being able to *derive* it rather than recall it is the L5 signal, because the derivation is one observation.

**And the one that should bother you.** Take a running total over a date column where two rows share a date. The published answer gives:

```text
    ('2024-01-01', 100.0, 150.0)
    ('2024-01-01',  50.0, 150.0)
```

The first row has a running total of **150 before its own 50 has been added**. The running total for a row includes a row that comes *after* it. Add one clause and it becomes 100 then 150.

If you can explain all four, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: a moving window over a sorted deck

A window function does not collapse rows the way `GROUP BY` does. Every input row produces an output row. What changes is that each row can **see** a set of other rows — its window — and compute something across them.

Think of a sorted deck of cards laid out in a line. For each card you place a frame around some of its neighbours and compute over what falls inside. `PARTITION BY` decides which piles are separate decks. `ORDER BY` decides the order within a deck. And the **frame** decides how far the window extends around the current card.

The frame is the part almost nobody specifies, which is why almost everybody gets the default's behaviour by accident.

### 3.2 The default frame is `RANGE`, and that is the bug

There are three clauses in a window specification and most people write two.

```sql
OVER (PARTITION BY acct ORDER BY d [frame])
```

When you supply `ORDER BY` and omit the frame, the default is:

```sql
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

The word that matters is `RANGE`, and its definition is the whole issue. **`RANGE` is defined in terms of values, not positions.** "Current row" under `RANGE` means *the current row and every row that ties with it on the `ORDER BY` expression* — its **peers**.

`ROWS` is defined in terms of physical position. "Current row" under `ROWS` means this row and no other.

With unique ordering values the two are identical, which is exactly why the bug survives testing on toy data. With duplicates they diverge:

```python
# Gist: w1_windows.py
q1 = "SELECT d, amt, SUM(amt) OVER (ORDER BY d) AS default_frame FROM tx WHERE acct=1"
q2 = "SELECT d, amt, SUM(amt) OVER (ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rows_frame FROM tx WHERE acct=1"
```

```text
  default frame is RANGE (peers summed together):
    ('2024-01-01', 100.0, 150.0)
    ('2024-01-01', 50.0, 150.0)
    ('2024-01-02', 30.0, 180.0)
    ('2024-01-03', 20.0, 200.0)
  explicit ROWS (true running total):
    ('2024-01-01', 100.0, 100.0)
    ('2024-01-01', 50.0, 150.0)
    ('2024-01-02', 30.0, 180.0)
    ('2024-01-03', 20.0, 200.0)
```

Look at row one ([`SQL-WIN-01`](../MEASUREMENTS.md)). Under the default, a transaction of 100 shows a running balance of **150** — it has already absorbed the 50 from the row beneath it, because both rows tie on `2024-01-01` and are therefore peers.

Under `ROWS`, row one shows 100 and row two shows 150, which is what "running total" means in every other context.

Both columns end at 200, so a spot check of the final value passes. The error lives entirely in the intermediate rows — which is precisely what a running-balance chart plots.

**The rule: if you are ordering by a date, a timestamp truncated to a day, or anything else with ties, write `ROWS` explicitly.** `RANGE` is correct when you genuinely want peers grouped — a rank-like cumulative distribution — and that is rarer than the default implies.

Frames also extend forwards. `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` is a seven-day moving average. `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` is a three-point smoother. `RANGE BETWEEN INTERVAL '7' DAY PRECEDING AND CURRENT ROW` in PostgreSQL and BigQuery gives a genuine seven-*day* window rather than seven rows, which handles missing days correctly. *(`documented` — SQLite lacks interval ranges.)*

### 3.3 The ranking family, and why the choice changes your row count

Three functions that look interchangeable and are not.

```python
# Gist: w1_windows.py (part 2)
SELECT name, score,
       ROW_NUMBER() OVER(ORDER BY score DESC) rn,
       RANK()       OVER(ORDER BY score DESC) rk,
       DENSE_RANK() OVER(ORDER BY score DESC) dr
FROM s
```

```text
    ('a', 90, 1, 1, 1)
    ('b', 90, 2, 1, 1)
    ('c', 80, 3, 3, 2)
    ('d', 70, 4, 4, 3)
```

Two rows tie at 90, and the three functions disagree about everything after that ([`SQL-WIN-02`](../MEASUREMENTS.md)).

**`ROW_NUMBER`** assigns 1, 2, 3, 4 — always distinct, and the tie is broken **arbitrarily**. Which of `a` and `b` gets 1 is not defined unless you add a tiebreaker to the `ORDER BY`. That non-determinism matters: the same query can return different rows across runs, which turns a paginated report into a source of duplicated and missing rows.

**`RANK`** gives 1, 1, 3, 4 — ties share a rank and the next value **skips**, so no row is ever ranked 2. This is competition ranking: two gold medals, no silver.

**`DENSE_RANK`** gives 1, 1, 2, 3 — ties share, and the sequence does not skip.

The consequence for top-N is the point. `WHERE rnk <= 3` with `RANK` returns however many rows tie into the top three, which could be three or thirty. With `ROW_NUMBER` it returns exactly three, chosen arbitrarily among ties.

Neither is correct in general — **it is a product question**. "Top 3 products" for a fixed-size dashboard slot wants `ROW_NUMBER` plus a deterministic tiebreaker. "Everyone who placed in the top 3" wants `RANK`, and the caller must handle a variable row count.

### 3.4 `LAG` and `LEAD`, and the gap that breaks them

Period-over-period comparison is the other half of analytical SQL:

```sql
-- Gist: mom_growth.sql
SELECT month,
       revenue,
       LAG(revenue) OVER (PARTITION BY branch ORDER BY month) AS prev,
       revenue - LAG(revenue) OVER (PARTITION BY branch ORDER BY month) AS delta
FROM monthly
```

`LAG` reads the previous row in the window; `LEAD` reads the next. Both take an optional offset and default.

The trap is that **`LAG` means "the previous row," not "the previous month."** If a branch had no revenue in February, there is no February row, and March's `LAG` reaches back to January while the column header still says "previous month." The growth figure is silently comparing a two-month gap.

The fix is a date spine: generate the complete set of periods, `LEFT JOIN` the data onto it, and `COALESCE` the missing values to zero before applying `LAG`. This is one of the few places where generating rows you do not have is the correct move, and it interacts directly with [module 01's](01_indexes_and_the_query_planner.md) `LEFT JOIN` warning — the condition must be in `ON` or the spine rows you just generated get filtered straight back out.

### 3.5 Gaps and islands, derived rather than recalled

"Find each user's longest streak of consecutive active days" is the classic analytical interview question, and it has a derivation you can reconstruct under pressure.

The observation: within a run of consecutive dates, **the date increases by one per row and the row number also increases by one per row.** So their difference is *constant* inside a run, and changes whenever a gap appears. That difference is a group key you did not have in the data.

```python
# Gist: w1_windows.py (part 3)
WITH g AS (
  SELECT u, d, julianday(d) - ROW_NUMBER() OVER (PARTITION BY u ORDER BY d) AS grp
  FROM act
)
SELECT u, MIN(d) AS start, MAX(d) AS end, COUNT(*) AS len
FROM g GROUP BY u, grp ORDER BY len DESC
```

```text
    (1, '2024-01-01', '2024-01-03', 3)
    (1, '2024-01-06', '2024-01-07', 2)
    (2, '2024-01-01', '2024-01-01', 1)
```

User 1's two separate streaks were correctly identified with their boundaries and lengths ([`SQL-WIN-03`](../MEASUREMENTS.md)) — a three-day run, a gap, then a two-day run.

The same trick generalises. For *value*-based islands rather than date-based — runs of consecutive failed logins, or periods where a balance stayed negative — you compare each row to its predecessor with `LAG`, flag where a new run starts, and take a running `SUM` of that flag as the group key:

```sql
-- Gist: value_islands.sql
SELECT *, SUM(is_new_run) OVER (PARTITION BY u ORDER BY d
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS island
FROM (SELECT *, CASE WHEN status = LAG(status) OVER (PARTITION BY u ORDER BY d)
                     THEN 0 ELSE 1 END AS is_new_run FROM events)
```

Note the explicit `ROWS` in that running sum — §3.2's rule applies here too, and with duplicate timestamps the default `RANGE` would assign the same island id across a boundary.

### 3.6 Cohort retention, and the censoring problem

A retention grid is the standard analytical deliverable, and it has a statistical trap most SQL tutorials omit.

```sql
-- Gist: retention.sql
WITH first_seen AS (
  SELECT user_id, DATE_TRUNC('month', MIN(activity_date)) AS cohort
  FROM activity GROUP BY user_id
),
periods AS (
  SELECT f.cohort,
         DATE_DIFF(DATE_TRUNC('month', a.activity_date), f.cohort, MONTH) AS period,
         a.user_id
  FROM activity a JOIN first_seen f USING (user_id)
)
SELECT cohort, period, COUNT(DISTINCT user_id) AS active
FROM periods GROUP BY cohort, period ORDER BY cohort, period
```

The mechanics are three steps: assign each user a cohort from first activity, compute each activity's offset from that cohort, then count distinct users per cohort-period cell.

**The trap is censoring.** A cohort that started last month has not had time to reach period 6. Its period-6 cell is empty — not because those users churned, but because the future has not happened. Plot that naively and the newest cohorts appear to collapse, which is exactly backwards from the usual reality that recent cohorts are your best.

The fix is to exclude cells where `period > months_elapsed_since_cohort`, showing them as blank rather than zero. **A zero and an unknown are different values, and conflating them is the most common way a retention chart lies.** This is the same three-valued-logic discipline as [`SQL-24`](00_knowledge_graph.md) — `NULL` means unknown, and rendering unknown as zero fabricates data.

### 3.7 Multi-level aggregation in one pass

`GROUPING SETS` computes several aggregation levels in a single scan:

```sql
-- Gist: grouping_sets.sql
SELECT branch, currency, SUM(amount)
FROM transactions
GROUP BY GROUPING SETS ((branch, currency), (branch), ())
```

That returns per-branch-per-currency rows, per-branch subtotals, and one grand total, from one pass instead of three queries stitched with `UNION ALL`. `ROLLUP(a, b)` is shorthand for the hierarchical set; `CUBE(a, b)` gives every combination.

The trap: subtotal rows have `NULL` in the columns they aggregate over, and that is **indistinguishable from a data NULL**. A branch whose currency is genuinely missing produces a row that looks exactly like the branch subtotal, and the report double-counts.

`GROUPING(currency)` returns 1 for a subtotal NULL and 0 for a data NULL, and it is the only reliable way to tell them apart:

```sql
CASE WHEN GROUPING(currency) = 1 THEN 'ALL CURRENCIES' ELSE COALESCE(currency, 'UNKNOWN') END
```

*(`documented` — `GROUPING SETS` is PostgreSQL and BigQuery; SQLite lacks it.)*

---

## 4. Break it on purpose

### 4.1 The running balance that ran ahead of itself

```text
    ('2024-01-01', 100.0, 150.0)     <- 150 before its own 50 was added
    ('2024-01-01',  50.0, 150.0)
```

A balance chart where a point already includes a transaction that appears later in the list. The final value is right; every intermediate value on a day with more than one transaction is wrong.

This ships constantly, for a specific reason: **it is correct on unique timestamps and wrong on dates.** Development data often has one row per day. Production has many. The bug appears when the data gets denser, not when the code changes, so nobody suspects the query.

The fix is `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, and it costs nothing.

**Run this one yourself** on any running total you have shipped. The check is one query with and without the explicit frame, compared on a day with multiple rows.

### 4.2 The top-3 that returned four rows

```text
    ('a', 90, 1, 1, 1)
    ('b', 90, 2, 1, 1)
```

`WHERE rnk <= 3` using `RANK` returns every row tied into the top three. A dashboard slot sized for three shows four, or the API contract promising three breaks, or a `LIMIT 3` applied afterwards silently drops one of a tied pair — arbitrarily, differently on each run.

And `ROW_NUMBER` without a tiebreaker has the mirror problem: it returns exactly three but *which* three is undefined. Under pagination that means a row can appear on page one and page two, while another appears on neither.

The fix in both cases is a deterministic total ordering — `ORDER BY revenue DESC, product_id` — so that ties are broken by something stable. The cost is that you must choose a tiebreaker and defend it, which is a product decision rather than a technical one.

### 4.3 The growth rate that compared the wrong months

```sql
LAG(revenue) OVER (PARTITION BY branch ORDER BY month)
```

A branch with no February revenue has no February row. March's `LAG` returns January. The report says "month-over-month growth" and computes a two-month change, which makes the growth look larger and appears exactly when a branch was struggling enough to have a blank month — so the metric is most wrong precisely when it matters most.

Nothing errors. The number is plausible.

The fix is a generated date spine `LEFT JOIN`ed to the data with zeros filled in, so every period has a row and `LAG` steps one period at a time.

### 4.4 The retention curve that showed a collapse

The censoring trap from §3.6, as it appears in a meeting: the newest cohorts fall off a cliff at period 4, and someone concludes the product got worse.

The cells were empty because those cohorts are three months old. Rendering an unknown as a zero manufactured a trend that does not exist, and it is the single most common defect in a retention chart.

The fix is to compute the maximum observable period per cohort and blank anything beyond it. The discipline generalises: **in analytical SQL, never `COALESCE` an unknown to zero without asking whether zero is a fact.**

---

## 5. The judgment call

### The options, honestly costed

| Choice | Use when | Because | Real cost |
|---|---|---|---|
| **`ROWS` frame** | Any running total or moving average | Positional — one row means one row | Must be written explicitly; the default is not this |
| **`RANGE` frame** | You genuinely want tied rows treated as one | Value-based; correct for cumulative distributions | **Measured: silently wrong for running totals on dates** |
| **`ROW_NUMBER`** | Fixed-size top-N, deduplication, pagination | Always exactly N rows | Ties broken **arbitrarily** — non-deterministic without a tiebreaker |
| **`RANK`** | "Everyone who placed in the top N" | Ties share a rank, honestly | **Variable row count** the caller must handle |
| **`DENSE_RANK`** | Ranking into a fixed number of bands | No gaps in the sequence | Rank number no longer indicates how many are ahead |
| **`LAG`/`LEAD`** | Period-over-period on complete series | Simple and index-friendly | **Means "previous row," not "previous period"** — needs a date spine |
| **`GROUPING SETS`** | Several aggregation levels at once | One pass instead of `UNION ALL` | Subtotal NULLs are ambiguous without `GROUPING()` |
| **Self-join instead** | Almost never for these problems | Familiar to everyone | O(n²) shapes and far harder to read than a window |

### When you would not do this

**Do not omit the frame on a running total.** This is the rule I would put above every other in this module, because §3.2 measured a wrong answer from the published idiom. The default `RANGE` is only correct when your ordering column is unique, and dates are not.

**Do not use `ROW_NUMBER` for pagination without a total ordering.** Ties broken arbitrarily mean a row can appear on two pages and another on none. Any `ORDER BY` used for pagination must be deterministic, which usually means appending the primary key.

**Do not push window functions to the application.** Fetching a million rows to compute a running total in Python is slower, uses far more memory, and is the [module 01](01_indexes_and_the_query_planner.md) N+1 mistake in another costume. The window function runs where the data already is.

**Do watch the sort cost at scale.** A window function with `PARTITION BY` requires the data sorted by the partition and order keys. On a warehouse that partition step is a shuffle, so **skew in the partition key is what makes it slow** — one key with a disproportionate share of rows sends everything to one worker. A composite index matching `(partition_key, order_key)` can let a relational engine skip the sort entirely.

**Do not render an unknown as zero.** §4.4. It fabricates trends, and in a retention chart it fabricates the most consequential one.

---

## 6. Interview angles

**"Write me a running total."**

> I'd write `SUM(amount) OVER (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` — and the reason I'd write that frame explicitly rather than leaving it off is the interesting part of the answer. If you omit the frame you get `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, and `RANGE` is defined in terms of *values* rather than positions. So "current row" under `RANGE` means the current row **and all its peers** — every row tied on the ordering expression. I tested this: two transactions on the same date, 100 and 50, and the default frame gave the first row a running total of **150**, before its own 50 had been added. It had already absorbed the row beneath it. With an explicit `ROWS` frame you get 100 then 150, which is what anyone means by a running total. What makes it dangerous is that both versions end at the same grand total, so a spot check of the final number passes — the error is entirely in the intermediate rows, which is exactly what a balance chart plots. And it's correct on unique timestamps and wrong on dates, so it appears when the data gets denser rather than when the code changes.

**"Give me the top three products per category."**

> The shape is `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC)` in a subquery, filtered to `<= 3` outside — you can't filter on a window function in the same `WHERE` because windows are evaluated after `WHERE`. In BigQuery or Snowflake I'd use `QUALIFY` and skip the subquery. But I'd want to ask a question back before writing it, because the choice of ranking function is a product decision. `ROW_NUMBER` gives you exactly three rows and breaks ties arbitrarily. `RANK` gives ties the same rank and skips — I measured it on two rows tied at 90 and got 1, 1, 3, so nothing is ever ranked 2 — which means `rnk <= 3` can return more than three rows. If the dashboard has three slots, `ROW_NUMBER` with a deterministic tiebreaker so it's stable across runs. If the question is "everyone who placed in the top three," `RANK`, and the caller handles a variable count. The failure I'd actually guard against is `ROW_NUMBER` without a tiebreaker under pagination — ties break arbitrarily, so a row can show up on page one and page two while another shows up on neither.

**"Find each user's longest streak of consecutive active days."**

> This is gaps-and-islands, and I'd rather derive it than recite it because the derivation is one observation. Within a run of consecutive dates, the date goes up by one per row and the row number also goes up by one per row — so the *difference* between them is constant inside a run and changes at every gap. That difference is a group key you didn't have in the data. So: `julianday(d) - ROW_NUMBER() OVER (PARTITION BY user ORDER BY d)` as a grouping column, then `GROUP BY user, that_key` with `MIN(d)`, `MAX(d)` and `COUNT(*)` to get each streak's start, end and length. I ran it and it correctly separated a three-day run from a two-day run with a gap between them. The same trick generalises to value-based islands — runs of failed logins, or periods where a balance stayed negative — except there you compare each row to its predecessor with `LAG`, flag where a new run starts, and take a running sum of that flag as the island id. And that running sum needs an explicit `ROWS` frame for the same reason as the running total.

**"Build me a cohort retention chart."**

> Three steps: assign each user a cohort from the month of their first activity, compute each subsequent activity's offset from that cohort month, then count distinct users per cohort-period cell. That's a `MIN(activity_date)` grouped by user, a date-diff against it, and a `COUNT(DISTINCT user_id)` grouped by cohort and period. The part I'd raise unprompted is censoring, because it's where these charts lie. A cohort that started last month hasn't had time to reach period 6 — that cell is empty because the future hasn't happened, not because those users churned. If you render it as zero, the newest cohorts appear to fall off a cliff, and someone concludes the product got worse when the truth is the opposite. So I'd compute the maximum observable period per cohort and blank everything past it rather than filling zeros. It's the same discipline as three-valued logic generally — `NULL` means unknown, zero is a fact, and `COALESCE`ing one into the other fabricates data. That's the thing I'd check first on anyone's retention chart, including my own.

---

## 7. To add to `RECALL.md`

- Window functions **do not collapse rows**; `PARTITION BY` picks the deck, `ORDER BY` sorts it, the **frame** decides what each row can see
- **Default frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`** — and `RANGE` is value-based, so "current row" includes **all peers**
- **Measured:** two rows on one date — default gave the first a running total of **150 before its own 50**; explicit `ROWS` gave **100 then 150**
- Both versions reach the same grand total, so **a spot check of the final value passes**. Wrong only in the middle — which is what a chart plots
- Correct on unique timestamps, wrong on dates → **the bug appears when data gets denser, not when code changes**
- **Measured ties at 90:** `ROW_NUMBER` 1,2,3,4 · `RANK` 1,1,3,4 (**never a 2**) · `DENSE_RANK` 1,1,2,3
- `RANK` + `<= 3` returns a **variable** row count; `ROW_NUMBER` returns exactly 3 but **arbitrarily** — a product decision, not a technical one
- `ROW_NUMBER` without a tiebreaker breaks pagination: a row on **two pages**, another on **none**. Always append a unique key
- **`LAG` means "previous row," not "previous period."** A missing month makes it reach back two — worst exactly when a branch was struggling. Fix with a **date spine**
- **Gaps and islands:** `date − ROW_NUMBER()` is **constant within a consecutive run**. Group by it. Measured: correctly split a 3-day and a 2-day streak
- Value-based islands: `LAG` to flag run starts, running `SUM` of the flag as island id — **with an explicit `ROWS` frame**
- **Cohort censoring:** a young cohort's later periods are **unknown, not zero**. Rendering zero manufactures a collapse. Blank past `max observable period`
- `GROUPING SETS`/`ROLLUP`/`CUBE` = several levels in one pass; **`GROUPING(col)` distinguishes a subtotal NULL from a data NULL**
- Windows are evaluated **after `WHERE`** → filter in a subquery, or `QUALIFY` in BigQuery/Snowflake
- At warehouse scale `PARTITION BY` is a **shuffle** — skew in the partition key is what makes it slow

---

← [SQL knowledge graph](00_knowledge_graph.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
