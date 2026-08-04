# Indexes and the query planner

*Why the database ignored your index, and how to find out before production does.*

**Level: L3–L4.** Every plan and timing below was produced by running the query against a SQLite database of **200,000 accounts and 1,000,000 transactions**, with `ANALYZE` run. SQLite is the engine here because it is the one you can reproduce in thirty seconds; where Postgres differs materially, it is flagged. The reasoning transfers — B-trees, selectivity and statistics are not vendor-specific.

---

## 1. The thing you already do

```sql
CREATE INDEX ix_acct_branch_opened ON accounts(branch, opened);

SELECT COUNT(*) FROM accounts WHERE branch = 'BR07';
```

You add an index on the columns in the `WHERE` clause. The query gets faster. You move on.

---

## 2. The question you cannot answer about it

You have an index on `(branch, opened)` and you query on `opened` alone. Is the index used? The rule everyone repeats is "leftmost prefix only," so the answer should be no — but run it and the planner does use it. What is the rule *actually*?

You have an index on `posted`. `WHERE posted >= '2026-03-01'` runs in 1.8ms. `WHERE substr(posted,1,7) = '2026-03'` runs in 62ms on the same column, the same index, the same rows. **Thirty-five times slower for the same answer.** What changed?

You have a perfectly good index and the planner chooses a full scan anyway. Is it broken?

And the one that has cost you a whole afternoon at some point: you write a `LEFT JOIN`, add a condition on the right-hand table, and rows silently disappear. Which rows, and why?

---

## 3. What the machine actually does

### 3.1 An index is a sorted copy, and that is the whole idea

A B-tree index on `(branch, opened)` is a separate structure holding those two columns plus a pointer back to the row, **kept sorted by branch first and then by opened within each branch**. Like a phone book sorted by surname, then first name.

Three consequences follow from "sorted," and they explain almost every index behaviour you will meet.

Because it is sorted, the engine can binary-search it — that is where the speed comes from. Because it is sorted **in a specific order**, the sortedness is only useful in that order: within `BR07` the `opened` values are in sequence, but across the whole index they are scattered. And because it is a *copy*, it costs storage and it costs write time — every `INSERT` maintains every index on the table. Indexes are not free, which is why "add an index" is a design decision rather than a reflex.

### 3.2 The leftmost-prefix rule, and the exception nobody mentions

The standard rule: an index on `(a, b, c)` serves queries filtering on `a`, on `a, b`, and on `a, b, c` — but not on `b` alone.

Measured, against `ix_acct_branch_opened`:

```
-- leftmost column only
  SEARCH accounts USING COVERING INDEX ix_acct_branch_opened (branch=?)
   0.2 ms
-- both columns
  SEARCH accounts USING COVERING INDEX ix_acct_branch_opened (branch=? AND opened=?)
   0.0 ms
-- SECOND column only
  SEARCH accounts USING COVERING INDEX ix_acct_branch_opened (ANY(branch) AND opened=?)
   0.0 ms
```

Look at the third plan. It used the index, and the giveaway is `ANY(branch)`. That is a **skip-scan**: because `branch` has only 30 distinct values, the engine walks each one and does a small ranged lookup inside it — 30 cheap searches instead of one scan of 200,000 rows.

This is worth knowing precisely, because it is where a memorised answer gets exposed. The honest rule is not "the index is useless without the leading column." It is: **an index is only useful in its sort order, and if the leading column has few enough distinct values the engine can afford to iterate them.** Postgres has the same capability under the name *index skip scan* for certain query shapes, and both engines depend on statistics to know the cardinality — which is why `ANALYZE` matters.

The version to say aloud: *"the leading column normally has to be in the predicate, but if its cardinality is low enough the planner can skip-scan across its distinct values, which is why I'd read the plan rather than rely on the rule."*

### 3.3 Why wrapping a column in a function destroys the index

The index stores `posted`. It does not store `substr(posted,1,7)`. Sortedness in `posted` says nothing about the ordering of some function applied to `posted`, so the engine cannot binary-search — it must compute the function for every row and compare.

```
-- substr() wrapping the column
  SCAN txns USING COVERING INDEX ix_txn_posted
   62.4 ms
-- range on the bare column
  SEARCH txns USING COVERING INDEX ix_txn_posted (posted>? AND posted<?)
   1.8 ms
```

**35× slower**, same data, same index, same answer.

Read the two plan lines carefully, because the distinction is the single most useful thing on this page. Both say "index" — but the first says **SCAN** and the second says **SEARCH**. `SCAN ... USING INDEX` means it read the entire index end to end, using it only to avoid touching the table. `SEARCH` means it binary-searched to a position and read a range. Seeing the word "index" in a plan and concluding it is fine is a very common mistake.

The fix is always the same shape: **move the function off the column and onto the constant.** Instead of `substr(posted,1,7) = '2026-03'`, write a half-open range on the bare column. Instead of `DATE(created_at) = '2026-01-01'`, write `created_at >= '2026-01-01' AND created_at < '2026-01-02'`. Instead of `UPPER(email) = 'X'`, store it normalised or build an expression index — Postgres supports `CREATE INDEX ON users (upper(email))`, which indexes the *result*, and then the original query works.

The same trap wears other costumes: an implicit type cast on the column, a leading-wildcard `LIKE '%foo'`, `column + 0`, or a timezone conversion applied to a timestamp column.

### 3.4 The planner is a cost estimator, and a scan is often correct

The planner does not know your data. It knows *statistics* — collected by `ANALYZE` in SQLite and Postgres — about row counts and value distributions, and it estimates how many rows each access path would touch.

If a predicate matches a small fraction of the table, an index is a huge win. If it matches most of the table, the index is *worse* than a scan, because you would follow a pointer per row and read the table in random order instead of sequentially.

Measured, on a `status` column that is 98% `'open'` and 2% `'closed'`:

```
-- before any index on status
  2% of rows  : SCAN accounts    7.6 ms
  98% of rows : SCAN accounts    7.8 ms

-- after CREATE INDEX ON accounts(status), selecting a column not in the index
  2% of rows  : SEARCH accounts USING INDEX ix_status (status=?)    1.4 ms
  98% of rows : SEARCH accounts USING INDEX ix_status (status=?)   13.2 ms
```

The index made the selective query **5× faster** and the unselective one **1.7× slower than the scan it replaced.** That is the whole concept of selectivity in one table, and it is why "the query is slow, add an index" is not a strategy.

The practical corollary: when the planner refuses your index, it is usually right, and the two situations where it is wrong are worth naming — **stale statistics** (the table has changed shape since the last `ANALYZE`, so its estimates describe a database that no longer exists) and a **type mismatch** forcing a cast on the column.

### 3.5 Covering indexes

`COVERING INDEX` in those plans means every column the query needed was already in the index, so the engine never touched the table at all. That is why the first `(branch, opened)` lookups reported 0.0ms.

It is also the trap in section 3.4's first attempt. When I measured selectivity using only columns present in the index, the planner used the index even at 98% selectivity — because with no table access, the usual cost of following pointers disappears. I had to select a column *outside* the index to see the planner make a real trade-off. Worth knowing that a covering index changes the arithmetic, and worth remembering when you benchmark: **measure with the columns your real query actually selects.**

---

## 4. Break it on purpose

### 4.1 The `LEFT JOIN` that silently becomes an `INNER JOIN`

Two queries. They differ by one word.

```sql
-- condition in ON
SELECT COUNT(*) FROM accounts a LEFT JOIN txns t
  ON t.account_id = a.id AND t.amount > 800;

-- condition in WHERE
SELECT COUNT(*) FROM accounts a LEFT JOIN txns t
  ON t.account_id = a.id
 WHERE t.amount > 800;
```

```
  condition in ON    ->  207,001 rows
  condition in WHERE ->   55,538 rows
  accounts total     ->  200,000
```

The first preserves all 200,000 accounts — those with no large transaction appear once with `NULL` on the right. The second returns 55,538, having **silently discarded 144,462 accounts.**

The mechanism is evaluation order. The `LEFT JOIN` runs first and produces `NULL`s for non-matching rows. Then `WHERE` filters that result — and `NULL > 800` is not true, so every row that the outer join was protecting gets thrown away. The `LEFT JOIN` became an `INNER JOIN` and nothing warned you.

This is the most dangerous bug in this module because **it produces a number, not an error.** A report runs, a figure appears, someone makes a decision. In reporting work it is how "accounts with no activity" quietly vanish from a total.

The rule: **conditions on the outer table's columns belong in `ON`; conditions on the preserved table belong in `WHERE`.** And when you genuinely want "rows with no match," the pattern is `WHERE t.id IS NULL`, which is the one legitimate use of a `WHERE` predicate on the outer side.

### 4.2 The correlated subquery, and what actually matters

The folk wisdom is that a correlated subquery is N+1 in SQL clothing and a join is always faster. Measured, on 6,600 accounts with the supporting index present:

```
-- correlated subquery : 10.4 ms
-- single join + GROUP BY : 17.2 ms
```

The subquery **won**. That is not what the folk wisdom predicts, and the reason is that SQLite recognised the pattern and the inner lookup was indexed, so each iteration was a cheap B-tree search.

Now drop the index on `txns.account_id` and run both over 500 accounts:

```
=== 500 accounts, NO index on txns.account_id ===
-- correlated subquery :    19183 ms
-- single join+GROUP BY:    19075 ms

=== same two queries, index restored ===
-- correlated subquery :      1.1 ms
-- single join+GROUP BY:      1.2 ms
```

**19,183ms to 1.1ms — roughly seventeen thousand times — from one index.** And note that the join was equally catastrophic without it.

The lesson is not the one usually taught. Query *shape* mattered by a factor of under two. The *index* mattered by a factor of seventeen thousand. When you are optimising, read the plan and find the missing access path before you rewrite the SQL — rewriting a query that is scanning a million rows just gives you a differently-shaped scan.

*Postgres note: Postgres will not always flatten a correlated subquery the way SQLite did here. The 17,000× index result transfers directly; the shape comparison is engine-specific, and the honest interview answer is "it depends on whether the planner can flatten it, which I'd check in the plan."*

### 4.3 `COUNT(*)` is not `COUNT(col)`

After setting 10% of `amount` values to `NULL`:

```
SELECT COUNT(*) FROM txns                    = 1,000,000    1.4 ms
SELECT COUNT(amount) FROM txns               =   900,000   38.8 ms
SELECT COUNT(DISTINCT account_id) FROM txns  =   198,662   28.5 ms
```

Three different numbers from three things that look interchangeable. `COUNT(*)` counts rows. `COUNT(col)` counts **non-null values in that column** — 100,000 fewer here — and it is 28× slower because it has to inspect a column instead of counting index entries. `COUNT(DISTINCT col)` deduplicates and is slower again.

In reporting work this is a silent correctness bug rather than a performance one. If you write `COUNT(amount)` intending "how many transactions," you will under-report by exactly the number of rows where the amount was never recorded — which is usually the rows a data-quality review most wants to see.

---

## 5. The judgment call

### 5.1 Reading a plan without memorising vendor syntax

The words differ — SQLite says `SCAN` and `SEARCH`, Postgres says `Seq Scan`, `Index Scan`, `Index Only Scan`, `Bitmap Heap Scan` — but you are looking for the same three things in any engine.

**Which access path?** A sequential scan of a large table in a query that filters narrowly is the signal for a missing or unusable index. A scan of a small table is fine and often optimal.

**Estimated versus actual rows.** This is the single highest-value thing in a plan and it needs `EXPLAIN ANALYZE` in Postgres to see. A planner estimating 50 rows and getting 500,000 has made every downstream decision on a false premise — usually because statistics are stale. Fixing the statistics fixes the plan; rewriting the query does not.

**Where the time went.** Which node, and how many times it was executed. A cheap node run 200,000 times is your N+1.

### 5.2 When not to add an index

Every index is a sorted copy that must be maintained on every write. On a write-heavy table, five indexes mean five B-tree updates per insert.

So: do not index low-cardinality columns unless the *rare* value is what you query — an index on a boolean that is 98% true earns nothing, as section 3.4 measured. Do not add an index whose leading columns duplicate an existing one; `(branch)` is redundant when `(branch, opened)` exists. And do not index a column you only ever wrap in a function, because it will never be used — index the expression instead, or normalise the stored value.

The question worth asking before every `CREATE INDEX` is what fraction of the table the predicate selects. Under a few percent, an index is usually a win. Above a third, usually not.

### 5.3 Finding the slow query in production

Not by guessing, and this is a standard follow-up. Postgres gives you `pg_stat_statements`, which aggregates by normalised query text and ranks by total time — the useful ranking is *total* rather than *mean*, because a 20ms query run a million times costs more than a 5s query run once, and only one of those shows up in a "slowest queries" list. From there, `EXPLAIN (ANALYZE, BUFFERS)` on the offender, and look at estimated-versus-actual before anything else.

Then `auto_explain` for logging plans of anything over a threshold in production, and — the part people forget — check whether `ANALYZE` has run recently, because a query that was fast last month and is slow today with unchanged code is a statistics problem far more often than a query problem.

---

## 6. Interview angles

### "You have an index but the query is still slow. Walk me through it."

> "First I'd get the plan, because everything else is guessing. And the specific thing I look for is whether it says the index was *searched* or *scanned* — SQLite makes that distinction in words, Postgres in the difference between an Index Scan and a Seq Scan. Seeing the index named in the plan doesn't mean it helped; it can read the whole index end to end.
>
> The most common cause I find is a function wrapping the column. The index stores the column's values, not the function's results, so the sort order is meaningless and it can't binary-search. I measured this recently — a `substr()` on a date column took 62 milliseconds and the equivalent range query on the bare column took 1.8, which is 35 times, same data, same index. The fix is to move the function onto the constant: a half-open range instead of `DATE(x) = ...`. Or an expression index in Postgres, which indexes the result.
>
> If it isn't that, I'd check whether the planner is choosing not to use it, which is usually correct — if the predicate matches most of the table, a scan really is cheaper than following a pointer per row. And I'd compare estimated rows against actual, because if those are wildly apart the statistics are stale and the planner is optimising for a database that doesn't exist any more."

### "Explain composite indexes."

> "An index on two columns is sorted by the first and then by the second within each value of the first, like a phone book by surname then first name. So it serves queries on the first column, or on both — the leftmost prefix.
>
> The nuance I'd add is that the rule isn't absolute. I tested an index on branch and opened, querying on the second column only, and the planner did use it — via a skip scan, because branch only had thirty distinct values, so it was cheaper to walk those thirty and do a small ranged lookup inside each than to scan two hundred thousand rows. Postgres can do the same thing for some shapes. So my working rule is that an index is useful in its sort order, and whether the planner can skip the leading column depends on its cardinality and on the statistics being current. Which is really an argument for reading the plan rather than trusting the rule."

### "You wrote a LEFT JOIN and rows are missing."

> "Almost always a condition on the right-hand table sitting in `WHERE` instead of in `ON`. The join runs first and puts NULLs in for the non-matching rows, then `WHERE` filters the result — and NULL fails any comparison, so exactly the rows the outer join was protecting get discarded. The LEFT JOIN silently becomes an INNER JOIN.
>
> I measured it on a two hundred thousand row table: the condition in `ON` gave 207,001 rows and preserved every account; the same condition in `WHERE` gave 55,538. A hundred and forty-four thousand accounts disappeared, with no error.
>
> That's the one I'm most careful about in reporting work, because it doesn't fail — it produces a number, and someone makes a decision on it. It's how 'clients with no transactions' quietly vanish from a total. So the rule I hold to is that conditions on the outer table go in `ON`, and the only `WHERE` predicate that belongs on that side is `IS NULL` when I'm deliberately looking for non-matches."

### "How do you approach a slow query you've never seen before?"

> "I don't guess, I measure, and I try to fix the access path before I touch the SQL. I had a case recently that made the point well: a correlated subquery and an equivalent join were within a factor of two of each other, so on shape alone there was nothing to choose. But with the supporting index dropped, both took nineteen seconds; with it restored, both took about a millisecond. Seventeen thousand times, from an index, and the query shape barely mattered.
>
> So the order I work in is: get the plan, look for a large table being scanned in a query that filters narrowly, compare estimated against actual rows to catch stale statistics, and look for a cheap node being executed thousands of times, which is the N+1 shape. Only after that would I rewrite the query — because rewriting something that's scanning a million rows just gives you a differently shaped scan.
>
> Finding it in the first place, in production, I'd use `pg_stat_statements` ranked by *total* time rather than mean, because a twenty-millisecond query run a million times costs more than a five-second query run once, and only one of those turns up in a slowest-queries list."

---

## 7. To add to `RECALL.md`

- An index is a **sorted copy** — useful only in its sort order, costs storage and write time
- Plan vocabulary: **SEARCH** = binary-searched a range · **SCAN using index** = read it all. Both name the index.
- Function on the column kills it: `substr(posted,...)` **62.4ms** vs bare range **1.8ms** (35×)
- Fix: move the function to the constant, or build an expression index
- Leftmost prefix — with a **skip-scan exception** when the leading column has low cardinality
- Selectivity measured: index at 2% → 1.4ms · at 98% → 13.2ms vs 7.8ms scan (**index made it slower**)
- Covering index changes the arithmetic — benchmark with the columns you really select
- `LEFT JOIN` + condition in `WHERE`: **207,001 → 55,538 rows**, silently. Condition belongs in `ON`.
- Index beats query shape: **19,183ms → 1.1ms** from one index; subquery vs join was under 2×
- `COUNT(*)` 1,000,000 (1.4ms) · `COUNT(col)` 900,000 (38.8ms, skips NULLs) · `COUNT(DISTINCT)` 198,662
- Stale statistics = plan optimised for a database that no longer exists. Check `ANALYZE`.
- Find it: `pg_stat_statements` by **total** time; `EXPLAIN (ANALYZE, BUFFERS)`; estimated vs actual first

---

← [SQL index](README.md) · [repo plan](../README.md)
