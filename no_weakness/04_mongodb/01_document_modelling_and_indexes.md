# Document modelling and the ESR rule

*Where the 16MB limit really bites, why your index was ignored, and what "schemaless" costs.*

**Level: L3–L4.**

**A note on evidence, and read it before quoting anything here.** The sandbox this repo is built in has no `mongod`, so unlike the [Python](../01_python/01_async_execution_model.md), [SQL](../02_sql/01_indexes_and_the_query_planner.md) and [JavaScript](../03_js_ts/01_event_loop_and_microtasks.md) modules, **the query plans and timings below are not measured — they are stated from documented behaviour.** The one section with real numbers is 3.3, where BSON document sizes were encoded and measured directly.

This matters for how you use the module. Everything here is defensible in an interview, but flag to yourself that you have not watched it happen. The highest-value follow-up work in this repo is to run a local `mongod`, reproduce section 4, and replace the asserted numbers with measured ones. Until then, prefer "the way Mongo does this is…" over "I measured…" when you speak.

---

## 1. The thing you already do

```js
db.accounts.find({ branch: "BR07", status: "open" }).sort({ opened: -1 }).limit(20)
db.accounts.createIndex({ branch: 1, status: 1, opened: -1 })
```

Index the fields in the query. It gets faster. Same instinct as SQL, and mostly the same result.

---

## 2. The question you cannot answer about it

You created that compound index. Is the field order right? There is a rule — Equality, Sort, Range — and the ordering it prescribes is **not** the order the fields appear in your query. Why that order and not another?

Your aggregation starts with `$match` on an indexed field and then does a `$group`. The `$match` uses the index. What happens to every stage after the `$group`, and why?

You have an account document with an array of transactions. It works beautifully in development. What breaks first as it grows — and it is not the 16MB limit.

And the one that catches people coming from SQL: MongoDB is "schemaless." After five years of writes, what shape is your data actually in, and how would you find out?

---

## 3. What the machine actually does

### 3.1 Indexes are B-trees, exactly as in SQL

The storage engine (WiredTiger) maintains a B-tree per index, sorted by the indexed fields in the declared order, with pointers back to documents. Everything from [the SQL module's section 3.1](../02_sql/01_indexes_and_the_query_planner.md) applies unchanged: sorted, therefore binary-searchable; sorted *in one order*, therefore useful only in that order; a copy, therefore costing storage and write time.

So the leftmost-prefix logic holds — an index on `{a:1, b:1, c:1}` serves queries on `a`, on `a,b`, and on `a,b,c`. What differs from SQL is what MongoDB additionally uses the sort order *for*, and that is where the ESR rule comes from.

### 3.2 ESR — Equality, Sort, Range

For a compound index, order the fields:

**Equality first.** Fields matched with an exact value. Each one narrows the search to a contiguous span of the B-tree, so putting them first makes everything after them cheaper.

**Sort second.** Because the index is physically ordered, if the sort fields come next the results *emerge already sorted* and MongoDB can skip the sort entirely. This is the point of the rule — an in-memory sort has a hard 32MB limit per operation and fails outright above it unless you allow disk use. Getting the sort from the index is not a small optimisation; it is the difference between a query that works and one that errors under load.

**Range last.** `$gt`, `$lt`, `$in` over a span. A range matches a contiguous region rather than a point, so **any field after a range field is no longer in a useful order.** Put a range before your sort field and the sortedness is destroyed — the engine has to collect and sort in memory.

Applied to `find({branch:"BR07", opened:{$gte:...}}).sort({balance:-1})`:

```js
db.accounts.createIndex({ branch: 1, balance: -1, opened: 1 })
//                        ^equality  ^sort       ^range
```

Note that this is *not* the order the fields appear in the query, which is why the rule is worth knowing by name. The senior framing: **ESR is a consequence of the index being sorted, not an arbitrary convention.** A range field scatters everything after it, so the sort has to be reached before the range.

### 3.3 Embed or reference — with real sizes

The platitude is "embed data that's accessed together." That is true and it does not help you decide. Here is the measurable version. Encoding actual BSON for an account with embedded transactions:

```
bare account document            :        102 bytes
  +      10 embedded transactions :      1,001 bytes    0.0% of 16MB
  +     100 embedded transactions :      9,011 bytes    0.1% of 16MB
  +   1,000 embedded transactions :     90,011 bytes    0.5% of 16MB
  +  10,000 embedded transactions :    909,011 bytes    5.4% of 16MB
  + 100,000 embedded transactions :  9,189,011 bytes   54.8% of 16MB

~bytes per embedded transaction   : 90
~transactions until 16MB          : 186,601
```

Now the decision is arithmetic rather than taste. About **186,000 transactions** fit in one account document. A retail customer at twenty transactions a month takes over seven hundred years to get there. A merchant account at a thousand a day hits it in **six months.**

So the actual rule has three parts and only one is about size.

**Is the array bounded by the domain?** Addresses, phone numbers, the last ten logins — bounded, embed. Transactions, events, comments, audit entries — unbounded, reference. If you cannot state a maximum, that is the answer.

**Is it always read with the parent?** Embedding costs you on every read of the parent, because Mongo fetches the whole document. An account document carrying 9MB of transactions makes *every* balance lookup transfer 9MB.

**Is it written independently?** Updating one element of a large array rewrites the document. Two writers touching different array elements contend on the same document lock.

### 3.4 What actually breaks first

It is not 16MB. Long before that:

**Read amplification.** Mongo returns whole documents. A 1MB account document means a balance check moves 1MB across the wire and through the working set.

**The working set stops fitting in RAM.** WiredTiger caches pages; performance is excellent while the working set is resident and falls off a cliff when it is not. Fat documents evict more per document, so you reach that cliff on far fewer accounts.

**Write amplification.** Push one element onto a 900KB array and the engine rewrites the document and updates every index on it.

The practical threshold is much lower than the hard limit, and the arithmetic above gives you the language to say so: *"the limit is 16MB and I'd design nowhere near it, because read amplification and cache pressure bite at a few hundred KB."*

### 3.5 The aggregation pipeline, and where the index stops

Stages run in order, each consuming the previous stage's output. Two things follow, and the second is the one people miss.

**Only the leading stages can use an index.** `$match` and `$sort` at the *front* of a pipeline may use one. Once a stage transforms the documents — `$group`, `$unwind`, `$project` that reshapes, `$lookup` — the output is a synthetic stream that exists nowhere on disk, so **no index can apply to anything downstream.**

The consequence is a rule you can state flatly: **filter as early as possible.** A `$match` before a `$group` uses an index and shrinks the working set; the same `$match` after the `$group` scans everything the group produced. Same result, different order of magnitude.

**The 100MB memory limit per stage.** A `$group` or `$sort` exceeding it fails unless `allowDiskUse: true`. In an analytics context this is the constraint you meet first, and the fix is usually a `$match` earlier rather than the flag.

`explain("executionStats")` is the tool, and the fields to read are the winning plan's stage — `IXSCAN` versus `COLLSCAN` — plus `totalKeysExamined`, `totalDocsExamined` and `nReturned`. **The ratio of documents examined to documents returned is the single most useful number**; if you examined 200,000 to return 20, the index is not doing its job.

---

## 4. Break it on purpose

*Reproduce these against a local `mongod` and replace the descriptions with measured plans — that is the outstanding work on this module.*

### 4.1 The unbounded array

An account with an embedded transactions array is the canonical MongoDB modelling mistake, and section 3.3 quantifies why: a merchant account reaches the hard limit in six months and becomes operationally painful long before, because every balance read drags the whole history along.

The failure is gradual, which is what makes it dangerous. There is no error until 16MB — just steadily worse latency on a query nobody changed.

The fix is the *bucket pattern*: one document per account per month holding that month's transactions, with a count. Bounded by the domain, sized predictably, and the common query — recent activity — touches one or two documents.

### 4.2 The silent COLLSCAN

A query that was fast in development scans in production. Three ordinary causes:

The index does not exist in production because it was created by hand in development and never made it into a migration. `createIndex` in a shell is not a deployment.

The field order violates ESR, so the index is used for equality and then MongoDB does an in-memory sort — which works at 1,000 documents and fails at 100,000 against the 32MB sort limit.

The types differ. Mongo indexes are type-sensitive: `{accountNo: "123"}` does not match a document storing `accountNo: 123`. In a collection written by two services over three years, both types are usually present.

`explain` names it, and `totalDocsExamined` versus `nReturned` quantifies it.

### 4.3 `$lookup` at scale

`$lookup` is a left outer join executed by running a lookup **per input document**. With an index on the foreign field it is a B-tree search per document; without one it is a collection scan per document — the [17,000× shape](../02_sql/01_indexes_and_the_query_planner.md#42-the-correlated-subquery-and-what-actually-matters) measured in the SQL module.

The judgment: an occasional `$lookup` on a small result set is fine. A `$lookup` in a hot path over thousands of documents is usually a **modelling signal** — either the data should have been embedded, or you are using a document store to do a relational join and should ask why.

### 4.4 Schema drift

"Schemaless" means the *database* enforces no schema. Your application still has one; it is just implicit, undocumented, and different in every document written before the last refactor.

After five years you will have documents missing fields added later, fields holding two types, fields renamed with both spellings present, and nested shapes that changed. Nothing failed — every write succeeded.

Finding it is an aggregation over `$type` per field, or `validate`, or a sampled scan. Fixing it without downtime is the standard three-phase migration: write both shapes, backfill in batches, then read only the new shape and drop the old. And going forward, **JSON Schema validation** on the collection makes the implicit schema explicit and rejects the next drift at write time.

---

## 5. The judgment call

### 5.1 When not to use MongoDB

This is the question you are best placed to answer well, because you have shipped both MySQL administration and MongoDB, and most candidates know one and have opinions about the other.

The honest case against: if your data is **naturally relational and queried from many angles**, you will re-implement joins in the application and lose. If you need **multi-document transactions as the normal case**, they exist since 4.0 on replica sets but they are the exception in the design, not the default. If your workload is **analytical** — arbitrary aggregation across large sets — a columnar store or a warehouse beats it. And if the team's strength is SQL, that is a real engineering input.

The honest case for: genuinely **hierarchical documents** read as a unit; a schema that must **evolve fast**; **horizontal scale** with a clear shard key; and high-volume writes of self-contained records.

The framing that lands: *"the question isn't which database is better, it's whether the access pattern is document-shaped. Mongo makes you decide your queries at modelling time, and it's very good when you can — and it punishes you when the queries change in ways you didn't foresee."*

### 5.2 The modelling checklist

Before creating a collection: what are the top three queries; is every array bounded by the domain; what is the shard key if this ever shards; what does the biggest document look like in three years.

That last question is the one nobody asks and the one section 3.3 lets you answer with a number.

### 5.3 Where your Beam pipeline sits

Your Tekkod work moved MongoDB into BigQuery through Apache Beam, and that boundary is a good interview story because it is exactly where the two models collide.

The interesting part is not the mechanics, it is that **BigQuery needs a schema and MongoDB did not enforce one**, so the pipeline is where five years of implicit schema becomes explicit — and where the drift from section 4.4 surfaces as type errors. Every field has to be given a declared type, every optional field a policy for absence, and every nested array a decision between a `RECORD` column and a flattened child table.

Have an opinion ready on that last one, because it is the natural follow-up. Flattening gives you clean SQL joins and multiplies row counts; repeated `RECORD` columns preserve the document shape and require `UNNEST` in every query. The answer depends on whether analysts will query the nested data directly, and saying so is better than picking one.

---

## 6. Interview angles

### "Embed or reference?"

> "The rule I use has three parts, and only one of them is about size. First, is the array bounded by the domain — addresses and phone numbers are bounded, so embed; transactions and audit events aren't, so reference. If I can't state a maximum, that's the answer. Second, is it always read with the parent, because Mongo returns whole documents, so embedding a big array means every read of the parent drags it along. Third, is it written independently, because updating one array element rewrites the whole document.
>
> I like to make it concrete. I measured the BSON: an embedded transaction is about ninety bytes, so roughly 186,000 fit in one account document before the 16MB limit. A retail customer at twenty a month would take centuries. A merchant at a thousand a day hits it in six months.
>
> But I'd design nowhere near the limit, because what breaks first isn't the limit — it's read amplification and cache pressure, and those bite at a few hundred kilobytes. For unbounded history I'd use the bucket pattern: one document per account per month."

### "Explain the ESR rule."

> "Equality, Sort, Range — the field order for a compound index. And it's worth understanding why rather than memorising it, because it falls straight out of the index being sorted.
>
> Equality fields go first because each one narrows you to a contiguous span of the B-tree, which makes everything after cheaper. Sort fields go next because if they come before any range, the results emerge already ordered and Mongo skips the sort completely — which matters a lot, since an in-memory sort has a hard 32MB cap and fails above it. Range goes last because a range matches a span rather than a point, so anything after it is no longer in a useful order.
>
> The practical consequence is that if you put a range field before your sort field, you've destroyed the sortedness and the engine falls back to sorting in memory — which works fine at a thousand documents and blows up at a hundred thousand. And notably ESR is often *not* the order the fields appear in the query, which is why it's worth knowing by name."

### "A query is slow. How do you diagnose it in Mongo?"

> "`explain("executionStats")`, and the number I go to first is the ratio of `totalDocsExamined` to `nReturned`. If it examined two hundred thousand documents to return twenty, the index isn't doing its job, and that ratio tells me more than the runtime does.
>
> Then I'd look at whether the winning plan is an `IXSCAN` or a `COLLSCAN`, and whether there's an in-memory sort stage — because that means the index gave equality but not order, which is usually an ESR problem in the field ordering.
>
> The causes I'd check in order: does the index actually exist in production, since one created by hand in a dev shell and never put in a migration is a classic; is the field order right; and are the types consistent, because Mongo indexes are type-sensitive and a collection written by two services over three years often has the same field as both a string and a number.
>
> And in an aggregation I'd check where the `$match` sits, because only the leading stages can use an index at all. Once you've hit a `$group` or an `$unwind` the output is synthetic and no index applies downstream — so a `$match` before the `$group` uses the index and the identical `$match` after it scans everything."

### "When would you not use MongoDB?"

> "I've shipped both, so I'd answer it as a modelling question rather than a preference. If the data is naturally relational and gets queried from many different angles, I'd use Postgres — otherwise you end up re-implementing joins in the application, and `$lookup` runs per input document, so at scale it's the N+1 shape. If multi-document transactions are the normal case rather than the exception, that's a relational signal too; Mongo has had them since 4.0 but they're not what the design is optimised for. And for analytical workloads I'd want a columnar store.
>
> Where I'd choose Mongo is genuinely hierarchical documents read as a unit, a schema that has to evolve quickly, or high write volume of self-contained records with a clear shard key.
>
> The way I'd sum it up is that Mongo makes you decide your queries at modelling time. It's very good when you can do that, and it punishes you when the queries change in ways you didn't foresee — which is the opposite trade-off from a relational database, where you pay upfront in normalisation and buy flexibility later."

---

## 7. To add to `RECALL.md`

- Indexes are B-trees — same leftmost-prefix logic as SQL
- **ESR**: Equality, Sort, Range. Falls out of sortedness; a range **scatters everything after it**
- In-memory sort limit **32MB** per operation; aggregation stage limit **100MB** (`allowDiskUse`)
- Measured BSON: ~**90 bytes** per embedded transaction → ~**186,000** before 16MB
- What breaks before 16MB: read amplification, working set eviction, write amplification
- Embed if **bounded by the domain**, read with the parent, written with the parent
- Unbounded history → **bucket pattern**, one document per account per month
- Only **leading** pipeline stages use an index; after `$group`/`$unwind` the stream is synthetic
- `explain("executionStats")` → **`totalDocsExamined` : `nReturned`** is the key ratio
- `$lookup` runs **per input document** — index the foreign field or it is N+1
- Mongo indexes are **type-sensitive**: `"123"` ≠ `123`
- Schemaless = the app has a schema, undocumented. Fix drift with a 3-phase migration + JSON Schema validation
- MongoDB→BigQuery is where implicit schema becomes explicit — flatten vs repeated `RECORD` is a real decision

---

← [MongoDB index](README.md) · [SQL: indexes and the planner](../02_sql/01_indexes_and_the_query_planner.md) · [repo plan](../README.md)
