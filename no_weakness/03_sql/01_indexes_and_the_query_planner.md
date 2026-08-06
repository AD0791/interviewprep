# Indexes and the query planner

*A 31,786× result, the index the planner refuses to help you with, and 57,654 rows that vanished without an error.*

**Level:** L4–L5 · **Prerequisites:** none
**Syllabus:** [`SQL-01`–`SQL-07`](00_syllabus.md) · **Roles:** DE ●● DA ●● FS ●
**Measurement:** `Measured` — SQLite 3.51.0 on `ENV-A`, against a purpose-built schema of **200,000 accounts and 1,000,000 transactions** (50 MB), statistics refreshed with `ANALYZE`. Every figure below came out of a terminal. Where PostgreSQL behaves differently the difference is stated and tagged `documented` inline, since the Docker daemon is down on this machine.

---

## 1. The thing you already do

A reporting query, of the kind behind every dashboard you have built:

```sql
-- Gist: monthly_fees.sql
SELECT a.branch,
       count(*)      AS fee_count,
       sum(t.amount) AS fee_total
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id
WHERE t.kind = 'fee'
  AND substr(t.created_at, 1, 7) = '2024-01'
GROUP BY a.branch;
```

It returns numbers. The numbers look plausible. Someone puts them in a Looker Studio dashboard and a programme officer makes a decision with them.

That query has **two independent defects**, and neither produces an error. One makes it roughly ninety times slower than it needs to be. The other silently changes which rows are counted, so the answer is wrong — not slow, *wrong* — and nothing anywhere will tell you.

---

## 2. The questions you cannot answer about it

**What is an index, in one sentence?** Not "a thing that makes queries faster" — that is a description of the effect. There is a one-sentence definition from which every property of indexes can be derived, including the ones that surprise people.

**When does adding an index make a query slower?** It happens, the planner knows it happens, and being able to say when separates someone who adds indexes from someone who designs them.

**Does the shape of your query matter more than the indexes on it?** Developers argue about subqueries versus joins in code review constantly. There is a measurement that settles it.

**And the two that should bother you.** First: the same query, run against the same data, with and without one index. **53.7ms versus 0.02ms.** Then the shape argument, measured properly — rewriting a correlated subquery as a join changed the runtime by **1.3×**, while the presence of the index changed it by **31,786×**.

Second: change one word in the query above — move `t.kind = 'fee'` from `WHERE` to `ON` — and the row count goes from 307,160 to 249,506. **Fifty-seven thousand rows disappear**, with no error, no warning, and a result set that looks entirely reasonable.

If you can explain all four, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: an index is a sorted copy

Here is the definition to carry: **an index is a sorted copy of selected columns, with pointers back to the full rows.**

That is it. Every property people memorise separately falls out of that one sentence.

It is *sorted*, so it helps only in its own sort order — which is why an index on `(a, b)` helps a query filtering on `a` and not one filtering only on `b`.

It is *sorted*, so range queries work: everything between two values is physically contiguous, so the engine finds the start and reads forwards.

It is a *copy*, so it costs disk, and every `INSERT`, `UPDATE` and `DELETE` must maintain it — which is why indexing every column is not free insurance.

It has *pointers back*, so using it costs a second lookup per row to fetch the rest of the data — and that cost is exactly why the planner sometimes refuses to use one, per §3.4.

### 3.2 What the index is worth

```python
# Gist: s1_index.py
Q = "SELECT * FROM transactions WHERE account_id = 12345"
# before and after CREATE INDEX ix_tx_acct ON transactions(account_id)
```

```text
=== 1. index presence ===
  NO INDEX  :     53.7 ms   SCAN transactions
  WITH INDEX:     0.02 ms   SEARCH transactions USING INDEX ix_tx_acct (account_id=?)
  -> 2,401x faster
```

**53.7ms to 0.02ms** ([`SQL-IDX-01`](../MEASUREMENTS.md)). Two thousand four hundred times.

The plan text is the part to learn to read. **`SCAN`** means the engine examined every one of the million rows and discarded the ones that did not match — work proportional to table size, so it degrades as the table grows. **`SEARCH … USING INDEX`** means it descended the B-tree and went directly to the matching entries — work proportional to the *result* size, so it barely degrades at all.

That difference in scaling behaviour matters more than the raw multiple. The unindexed query gets worse every month. The indexed one does not.

In PostgreSQL the same distinction reads `Seq Scan` versus `Index Scan` / `Index Only Scan`, and `EXPLAIN (ANALYZE, BUFFERS)` additionally gives you actual row counts and how much came from cache. *(`documented` — Postgres is not running on this machine.)*

### 3.3 Sargability: a function on the column destroys the index

Now the first defect in §1's query.

```python
# Gist: s1_index.py (part 2)
A = "SELECT count(*) FROM transactions WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01'"
B = "SELECT count(*) FROM transactions WHERE substr(created_at,1,7) = '2024-01'"
```

```text
  range predicate :     0.6 ms   SEARCH transactions USING COVERING INDEX ix_tx_date (created_at>? AND created_at<?)
  substr(col)     :    52.5 ms   SCAN transactions USING COVERING INDEX ix_tx_date
  -> 92x penalty
```

**Ninety-two times slower**, for two queries that return the identical answer ([`SQL-IDX-02`](../MEASUREMENTS.md)).

The reason follows directly from §3.1. The index is a sorted copy of `created_at`. It contains `'2024-01-15'`; it does **not** contain `substr('2024-01-15', 1, 7)`. To evaluate the second predicate the engine must compute the function for every row, and a value it has to compute cannot be looked up in a structure sorted by something else.

A predicate the engine can satisfy by seeking in an index is called **sargable** — search-argument-able. `column >= constant` is sargable. `function(column) = constant` is not.

Note the plan text in the second case: `SCAN … USING COVERING INDEX`. It still used the index, but as a *scan* — reading every entry in it — because the index happened to contain all the columns needed. That is a real trap when reading plans: the word "INDEX" appearing does not mean the index is doing useful work. **`SCAN` versus `SEARCH` is the word that matters.**

Two fixes. Rewrite the predicate as a range on the raw column, which is what the fast version does and costs nothing. Or build an expression index on `substr(created_at, 1, 7)`, which makes the original query sargable at the cost of another index to maintain.

The same trap catches `WHERE DATE(created_at) = '2024-01-01'`, `WHERE UPPER(owner) = 'ALEXANDRO'`, and `WHERE account_id + 0 = 12345`. Keep the column bare on one side of the comparison.

### 3.4 Selectivity: when the index is the wrong choice

An index is not always an improvement, and the planner knows it.

```text
=== 3. selectivity: the index the planner REFUSES ===
  kind='fee' matches 249,506 rows (25% of the table)
     42.5 ms   SEARCH transactions USING INDEX ix_tx_kind (kind=?)
```

Twenty-five percent of a million rows, retrieved through an index, took **42.5ms** — nearly as slow as the unindexed scan in §3.2 ([`SQL-IDX-03`](../MEASUREMENTS.md)).

The mechanism is the "pointers back" clause of §3.1. Using an index means: descend the tree, find a matching entry, follow its pointer to the actual row, repeat. Those pointer-follows are **random access**. A table scan is **sequential access**, which is dramatically friendlier to disk read-ahead and to CPU cache.

So there is a crossover. For a highly selective predicate — a handful of rows out of a million — random access to a few rows beats reading everything. For a poorly selective one — a quarter of the table — you do 250,000 random reads to avoid one sequential pass, and you lose.

**Selectivity is the deciding factor, not the presence of an index.** A cost-based planner estimates how many rows a predicate will match, using the statistics that `ANALYZE` collects, and picks accordingly. In PostgreSQL a query like this typically produces a `Seq Scan` even with the index present, and the planner is right to. *(`documented`.)*

Which gives the practical rule: **index high-cardinality columns.** `account_id` with 198,622 distinct values is an excellent index. `kind` with four values is usually a waste of disk and write throughput, unless one value is rare and you index it partially.

There is also a measurement trap here worth knowing about. If you test selectivity using only columns that are *inside* the index, the engine never needs the pointer-follow at all — it answers from the index alone, which is the `COVERING INDEX` in §3.3 — and the cost that drives the whole trade-off disappears. You have to select a column outside the index to see the planner make a real decision.

### 3.5 The measurement that settles the shape argument

Developers argue about query shape endlessly. Here is what it is worth.

```python
# Gist: s2_joins.py
sub  = """SELECT a.id,(SELECT count(*) FROM transactions t WHERE t.account_id=a.id)
          FROM accounts a WHERE a.branch='PAP' LIMIT 500"""
join = """SELECT a.id,count(t.id) FROM accounts a LEFT JOIN transactions t ON t.account_id=a.id
          WHERE a.branch='PAP' GROUP BY a.id LIMIT 500"""
```

```text
  correlated subquery :     0.6 ms
  join + GROUP BY     :     0.4 ms
  -> shape mattered by 1.3x

  WITHOUT the index — subquery 18,450 ms | join 1,554 ms
  -> index mattered by 31,786x on the subquery
```

Read those two lines together, because together they are the most useful thing in this module ([`SQL-IDX-04`](../MEASUREMENTS.md)).

**With the index present, the shape mattered by 1.3×.** The join was marginally faster. That difference would be invisible in production and is not worth a code-review argument.

**The index mattered by 31,786×.** The same subquery went from 0.6 milliseconds to **18.5 seconds** when the index was dropped.

The subquery-versus-join debate is a rounding error next to whether the planner has the index it needs. And notice the second-order detail: without an index the join degraded to 1.55s while the subquery degraded to 18.5s — a twelve-fold difference — so shape only starts to matter once you have already lost the important battle.

This is also the N+1 problem in its SQL costume. A correlated subquery executes once per outer row; without an index each execution is a full scan. It is the same shape as an ORM lazy-load in a loop and the same shape as a `$lookup` per document in MongoDB. **One cause, three costumes: a cheap-looking operation executed once per row.**

### 3.6 The second defect: `LEFT JOIN` with a condition in `WHERE`

Now the correctness bug in §1's query, which is worse than the performance one.

```python
# Gist: s2_joins.py
on_  = "... LEFT JOIN transactions t ON t.account_id=a.id AND t.kind='fee'"
whr  = "... LEFT JOIN transactions t ON t.account_id=a.id WHERE t.kind='fee'"
```

```text
  condition in ON   :   307,160 rows   (LEFT JOIN preserved)
  condition in WHERE: 249,506 rows   (silently became an INNER JOIN)
  -> 57,654 rows vanished with no error
```

**57,654 rows** ([`SQL-IDX-05`](../MEASUREMENTS.md)).

The mechanism is evaluation order. A `LEFT JOIN` produces every left row, filling the right-hand columns with `NULL` where nothing matched. That is the entire point of `LEFT`. `WHERE` then runs **after** the join — and `NULL = 'fee'` is not true, so every one of those NULL-extended rows is discarded.

Putting the condition in `ON` makes it part of the join *matching* rule, so a row that fails it still appears with NULLs preserved.

So `LEFT JOIN … WHERE right_table.col = value` is an inner join written in six more characters, and the language will not warn you. In a report counting "accounts and their fees," the `WHERE` version silently drops every account that had no fees — which is precisely the population you were probably trying to identify.

The rule: **on a `LEFT JOIN`, conditions on the right-hand table belong in `ON`.** Conditions on the left-hand table belong in `WHERE`. If you genuinely want an inner join, write `INNER JOIN` so the reader can see it.

### 3.7 Three-valued logic, briefly

The same `NULL` semantics produce a sharper failure.

```text
    NOT IN (1, NULL)            ->         0 rows   <- returns NOTHING
    NOT IN (1)  [NULL filtered] ->   199,999 rows
    NULL = NULL is: None  (unknown, not true/false)
```

`NOT IN` against a subquery containing even one `NULL` returns **no rows at all** ([`SQL-IDX-06`](../MEASUREMENTS.md)). Not fewer rows — none.

`x NOT IN (1, NULL)` expands to `x != 1 AND x != NULL`. The second comparison is `unknown`, and `true AND unknown` is `unknown`, which is not true, so no row ever qualifies. The empty result looks like "no matches found," which is a plausible business answer, so the bug ships.

`NOT EXISTS` does not have this problem and is the safer default. Alternatively filter the NULLs out of the subquery explicitly.

And the counting trio, from the same run:

```text
  COUNT(*)                     = 1,000,000
  COUNT(note)                  =   899,500
  COUNT(DISTINCT account_id)   =   198,622
```

`COUNT(*)` counts rows. `COUNT(col)` **skips NULLs** — a hundred thousand fewer here ([`SQL-IDX-07`](../MEASUREMENTS.md)). Two reports, both "correct," differing by 10%, and this is the single most common silent error in analytical SQL. It is also directly relevant to a DQA claim: knowing which rows a count excludes is the job.

---

## 4. Break it on purpose

### 4.1 The dashboard query that was ninety times too slow

§1's query, with `substr()` on an indexed column.

```text
  range predicate :     0.6 ms
  substr(col)     :    52.5 ms   -> 92x penalty
```

Nothing fails. At 200,000 rows nobody notices. At ten million the dashboard times out, and the instinct is to blame the dashboard, the network, or the database size — because the query "has an index on that column."

The diagnostic is to read the plan and look for `SCAN` rather than for the word `INDEX`. The trap in §3.3 is real: `SCAN … USING COVERING INDEX` contains the word INDEX and is still reading everything.

### 4.2 The report that quietly dropped a third of its subjects

§3.6's `LEFT JOIN`, in context.

```text
  condition in ON   :   307,160 rows
  condition in WHERE: 249,506 rows
```

A report of "fee activity by branch" that silently excludes every account with no fees. The totals are right for the accounts included. The population is wrong.

This is the worst class of bug in analytical work because **it is invisible in the output**. A slow query announces itself. A query returning 249,506 plausible rows instead of 307,160 plausible rows announces nothing, and the number reaches a decision-maker.

**Run this one yourself** on any join you have written recently. The check takes seconds — move the condition and compare counts — and I would run it on anything feeding a real decision.

### 4.3 The index that made it slower

```text
  kind='fee' matches 249,506 rows (25% of the table)
     42.5 ms   SEARCH transactions USING INDEX ix_tx_kind
```

Someone notices a slow `WHERE kind = 'fee'`, adds an index, and it does not get meaningfully faster — and now every write to the table maintains an extra structure for no gain.

The lesson is that "add an index" is not a strategy. **Selectivity decides**, and a four-value column will almost never repay a plain index. If one value is genuinely rare, a partial index on that value is the right tool: it indexes only the rows you care about and stays small.

### 4.4 The `NOT IN` that returned nothing

```text
    NOT IN (1, NULL) -> 0 rows
```

"Find accounts with no transactions in the exclusion list." The exclusion list has one NULL in it, from a nullable column nobody thought about. The query returns zero rows and someone reports that there are no such accounts.

`NOT EXISTS` is the fix and is NULL-safe by construction. The habit worth building is to treat any nullable column entering a `NOT IN` as a defect on sight.

---

## 5. The judgment call

### The options, honestly costed

| Choice | Use when | Because | Real cost |
|---|---|---|---|
| **No index** | Small tables, write-heavy, or a rarely-run query | Nothing to maintain; sequential scans are fast on small data | **Measured 53.7ms vs 0.02ms** on a million rows, and it degrades linearly |
| **Single-column index** | A high-cardinality column filtered frequently | Simple, and the planner uses it readily | Disk plus write cost on every mutation |
| **Composite index** | Queries filter on several columns together | One structure serves the combination | Only helps on the **leftmost prefix**; order is a design decision |
| **Covering index** | A hot query needs only a few columns | Answers from the index alone — no pointer-follow | Wider index, more disk, slower writes |
| **Partial index** | A predicate targets a rare value in a low-cardinality column | Tiny index for exactly the rows you query | Only usable when the query matches the predicate |
| **Expression index** | You genuinely cannot rewrite the predicate | Makes `function(col)` sargable | Another index to maintain; rewriting is usually cheaper |
| **Rewrite the query instead** | A function on a column, or a `WHERE` on a `LEFT JOIN` | **Measured 92× and 57,654 rows** — free to fix | None; this is strictly better than indexing around a bad predicate |

### When you would not do this

**Do not index every column.** Each index is a sorted copy maintained on every write. On a transactions table taking thousands of inserts a second, five unused indexes are a permanent tax paid for nothing. Index what queries actually filter and order by, which you find from the query log rather than from intuition.

**Do not argue about query shape before checking the indexes.** §3.5 is the whole argument: shape 1.3×, index 31,786×. If a code review is debating a subquery versus a join while nobody has looked at a plan, the review is optimising the wrong thing by four orders of magnitude.

**Do not index a low-cardinality column and expect a win.** §4.3 measured 25% selectivity performing no better than a scan. Reach for a partial index when one value is rare, or accept the scan.

**Do not trust a plan because it mentions an index.** `SCAN … USING COVERING INDEX` reads every entry. The words to look for are `SEARCH` in SQLite, `Index Scan` in Postgres — and in Postgres, the gap between *estimated* and *actual* rows, because a large gap means the statistics are stale and the plan was chosen for a table that no longer exists.

**Do not stop at the query.** Real diagnosis starts from `pg_stat_statements` ordered by **total** time rather than mean — a 20ms query run fifty thousand times costs far more than a 4-second report run once a day, and only total time reveals it. *(`documented`.)*

---

## 6. Interview angles

**"What is an index?"**

> A sorted copy of selected columns with pointers back to the rows — and I'd want to give the definition that way because everything else falls out of it. It's sorted, so it only helps in its own sort order, which is why an index on `(a, b)` does nothing for a query filtering only on `b`. It's sorted, so range queries work, because the matching values are physically contiguous. It's a copy, so it costs disk and it costs you on every write. And it has pointers back, so using it means a random read per row to fetch the rest of the data — which is the bit people skip, and it's the reason the planner sometimes refuses to use an index at all. On the value: I built a million-row transactions table and measured the same lookup at 53.7 milliseconds with no index and 0.02 with one, so about 2,400 times. But the number I find more useful is the scaling — the unindexed version is a `SCAN`, so it does work proportional to the table and gets worse every month, while the indexed version does work proportional to the result and basically doesn't.

**"Is a correlated subquery slower than a join?"**

> Usually people expect yes, and I measured it, and the honest answer is that the question is almost irrelevant. With the right index in place, the subquery ran in 0.6 milliseconds and the join in 0.4 — so shape mattered by about 1.3×, which would be invisible in production. Then I dropped the index and re-ran both: the subquery went to 18.5 seconds. So the index mattered by roughly **31,786×** on the same query where shape mattered by 1.3. That's four orders of magnitude between the thing people argue about in code review and the thing that actually decides it. I'd add one nuance, because it's the interesting part: without an index the join degraded to 1.55 seconds while the subquery degraded to 18.5, so shape *does* start mattering once you've already lost the important battle — the correlated subquery re-executes per outer row, and without an index each execution is a full scan. Which is the N+1 problem in SQL costume. It's the same shape as an ORM lazy-load in a loop and the same shape as a `$lookup` per document in Mongo: one cheap-looking operation executed once per row.

**"When does an index make a query slower?"**

> When the predicate isn't selective enough. Using an index means descending the tree and then following a pointer per row to get the actual data, and those pointer-follows are random reads, whereas a table scan is sequential — much friendlier to read-ahead and to cache. So there's a crossover point. I measured it: filtering on a column with four distinct values, matching about 25% of a million rows, took 42.5 milliseconds through the index, which is barely better than just scanning the table. Two hundred and fifty thousand random reads to avoid one sequential pass is a bad trade, and a cost-based planner will often refuse the index entirely and be right to. The practical rule I'd take from that is index high-cardinality columns — `account_id` with 198,622 distinct values is a great index, `kind` with four values usually isn't unless one value is rare and you make it a partial index. There's also a measurement trap I ran into: if you test this using only columns that are inside the index, the engine answers from the index alone and never does the pointer-follow, so the cost driving the whole trade-off disappears and the index looks good at any selectivity. You have to select a column outside the index to see a real decision.

**"A report's numbers look wrong but the query runs fine. How do you approach it?"**

> The first thing I'd check on any query with a `LEFT JOIN` is whether there's a condition on the right-hand table sitting in the `WHERE` clause, because that silently converts it to an inner join. `WHERE` runs after the join, and the NULL-extended rows a `LEFT JOIN` exists to produce fail any comparison, so they all get discarded. I measured it on my dataset — condition in `ON` gave 307,160 rows, the same condition in `WHERE` gave 249,506. Fifty-seven thousand rows vanished, no error, and a result set that looks completely reasonable. In a report of "accounts and their fees" that means every account with no fees disappears, which is usually exactly the population you were trying to find. After that I'd look at NULL handling, because that's the other silent one. `COUNT(*)` versus `COUNT(column)` differed by a hundred thousand on my table — a hundred percent versus ninety — because `COUNT(col)` skips NULLs. And `NOT IN` against a subquery with a single NULL in it returns **zero rows**, not fewer rows, because the comparison evaluates to unknown; I got 0 versus 199,999. That one's nasty because an empty result reads as a plausible business answer. `NOT EXISTS` is NULL-safe and I'd default to it. This is the area I'd emphasise given I've supervised DQA protocols — knowing exactly which rows a count silently excludes is the job.

---

## 7. To add to `RECALL.md`

- **An index is a sorted copy of selected columns with pointers back to the rows.** Sorted → own order only, ranges work; copy → disk + write cost; pointers → random reads
- Measured on 1M rows: **`SCAN` 53.7ms → `SEARCH` 0.02ms, 2,401×**. Scan work ∝ table; search work ∝ result
- Plan vocabulary: **`SEARCH` = seek** · **`SCAN` = read everything.** Postgres: `Seq Scan` vs `Index Scan`
- **`SCAN … USING COVERING INDEX` still reads everything** — the word "INDEX" in a plan proves nothing
- **Sargability:** `function(col) = x` cannot use an index on `col`. Measured **0.6ms vs 52.5ms — 92×**. Keep the column bare
- **The big one:** query shape mattered **1.3×**; the index mattered **31,786×** (0.6ms → 18,450ms). Check the plan before arguing about shape
- Without an index, join 1,554ms vs subquery 18,450ms — **shape only matters after you've lost the important battle**
- A correlated subquery is **N+1 in SQL costume** — same shape as ORM lazy-load and Mongo `$lookup` per document
- **Selectivity decides, not index presence.** 25% of rows via index = **42.5ms**, no better than a scan. Index high-cardinality columns
- Measurement trap: testing selectivity with only in-index columns hides the pointer-follow cost entirely
- **`LEFT JOIN` + condition in `WHERE` = silent `INNER JOIN`.** Measured **307,160 → 249,506, 57,654 rows gone**, no error. Right-table conditions go in `ON`
- **`NOT IN` with one NULL returns ZERO rows** — measured 0 vs 199,999. `x != NULL` is *unknown*. Use `NOT EXISTS`
- `NULL = NULL` is **unknown**, not false
- **`COUNT(*)` 1,000,000 · `COUNT(col)` 899,500 (skips NULLs) · `COUNT(DISTINCT)` 198,622** — the most common silent reporting error
- Diagnose from `pg_stat_statements` by **total** time, not mean; then estimated vs actual rows to spot stale statistics

---

← [SQL syllabus](00_syllabus.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
