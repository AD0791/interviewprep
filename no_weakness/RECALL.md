# RECALL

*Everything you must be able to answer cold. One line each, no explanations — the explanations are in the modules.*

**How to use this.** Read a line, say the full answer out loud, move on. Twenty minutes, no notes, ideally walking around. This is the file you re-read before any technical interview regardless of employer, and it is the cheapest high-frequency activity in the repo — under a 3–5 hour week it carries more of the load than reading does.

A line you cannot expand into thirty seconds of speech is a line to go back to the module for. Measured figures are in **bold** — those are yours, you produced them, and quoting a number you measured is the strongest move available in a technical interview.

---

## Python — async execution model
[→ module](01_python/01_async_execution_model.md)

- Calling an `async def` returns a coroutine object; **nothing has executed**
- Coroutines are driven by `.send()`; the return value arrives inside `StopIteration`
- The loop is one thread, cooperative, **cannot preempt** a callback
- `await` suspends the frame and hands control back; the frame resumes on the same line
- GIL released around blocking syscalls and every ~5ms; **irrelevant under asyncio, not defeated**
- CPU-bound: **1 job 0.42s · 4 threads 1.64s · 4 processes 0.52s**
- Blocking call in `async def`: **0.53s → 5.06s** for 10 concurrent requests
- `def` endpoint → Starlette threadpool, default **40** threads; cliff measured at 40
- `await` in a loop = serial; `gather` = concurrent; bound it with a semaphore
- `create_task` without a strong reference can be garbage-collected mid-flight
- Blocked-loop signature: **unrelated endpoints slow down together**
- `asyncio.run(..., debug=True)` warns above `slow_callback_duration` (100ms)

## Python — concurrency
[→ module](01_python/02_concurrency_threads_processes.md)

- Process = own address space and **own GIL**. Thread = shared address space, own stack.
- I/O: **serial 10.09s · 20 threads 0.51s · 20 coroutines 0.50s · 8 processes 1.54s**
- Memory: **2000 coroutines 4.5MB · 2000 threads 32.1MB**
- `balance += 1` is **four bytecodes**, not atomic. No lock → **5,900 of 8,000 lost**
- Tight loop lost **nothing** in 5 runs → the GIL makes races **rare, not impossible**
- Processes: children mutate **copies**; parent counter stayed 0, silently
- `mp.Value` gives shared storage, **not** atomicity — still needs `get_lock()`
- Lambdas across a process boundary → `PicklingError`
- `fork` inherits open DB connections → create pools **inside** the worker
- NumPy/Polars/DuckDB **release the GIL** — vectorise before you parallelise

## SQL — indexes and the planner
[→ module](02_sql/01_indexes_and_the_query_planner.md)

- An index is a **sorted copy** — useful only in its sort order, costs storage and write time
- Plan vocabulary: **SEARCH** = binary-searched a range · **SCAN using index** = read it all
- Function on the column kills it: **62.4ms vs 1.8ms (35×)**. Move the function to the constant.
- Leftmost prefix — with a **skip-scan exception** when the leading column has low cardinality
- Selectivity: index at 2% → **1.4ms** · at 98% → **13.2ms** vs 7.8ms scan (**index made it slower**)
- `LEFT JOIN` + condition in `WHERE`: **207,001 → 55,538 rows**, silently. Condition belongs in `ON`.
- Index beats query shape: **19,183ms → 1.1ms**; subquery vs join was under 2×
- `COUNT(*)` **1,000,000** · `COUNT(col)` **900,000** (skips NULLs) · `COUNT(DISTINCT)` 198,662
- Stale statistics = plan optimised for a database that no longer exists
- Find it: `pg_stat_statements` by **total** time; then estimated vs actual rows

## JavaScript — event loop
[→ module](03_js_ts/01_event_loop_and_microtasks.md)

- Order: **sync → nextTick → promises/queueMicrotask → macrotasks**; microtasks drained **to exhaustion**
- `setImmediate` vs `setTimeout(0)`: deterministic from an I/O callback, **racy from the main module**
- `await` = suspend + resume as a **microtask**; the frame is preserved
- `await` in a loop **5052ms** vs `Promise.all` **503ms**
- `Promise.all` rejects on first failure; `allSettled` waits for all
- Closures capture **bindings**: `var` → **3 3 3**, `let` → **0 1 2** — this is the stale-closure bug
- `this` is set by the **call site**: detached method → `undefined`
- Blocking: timer for 0ms fired at **1002ms**. Signature = **all endpoints slow together**
- Unhandled rejection in Node ≥15 → **process exits(1)**; in a browser → an event, page survives
- **`0.1+0.2 = 0.30000000000000004`**; **`(1.005).toFixed(2) = "1.00"`** — use integer cents
- Microtask livelock: **1000 microtasks before a 0ms timer**
- `worker_threads`: **12012ms → 3280ms** on 4 cores. Isolated V8 heaps, **no GIL**
- async for waiting · workers for computing · cluster for serving

## TypeScript — the type system
[→ module](03_js_ts/02_the_type_system.md)

- **Structural**, not nominal: `AccountId` and `UserId` both `{id:string}` are interchangeable. Fix = **branding**
- Erasure: `interface` and `type` emit **nothing**; `enum` emits **real JS**
- No runtime type checking, ever. `typeof Transfer` is not valid — not a value.
- Excess property check fires on **object literals only**; via a variable it passes
- `as` is a claim, not a check → `TypeError: Cannot read properties of undefined`
- Arrays are **unsoundly covariant by design** → `dogs[1].bark is not a function`, zero compile errors
- `any` unchecks the whole subtree; `unknown` forces narrowing
- Function **parameters are contravariant** — caught only under `strictFunctionTypes`
- Guarantee: **internal consistency with declared types.** Not validation, not soundness.
- Python keeps annotations at runtime (Pydantic reads them); TS erases them (infer the type from the schema)

## MongoDB — modelling and indexes
[→ module](04_mongodb/01_document_modelling_and_indexes.md)

*Plans and timings here are unmeasured — say "the way Mongo does this is…", not "I measured…". Only the BSON sizes are real.*

- **ESR**: Equality, Sort, Range. Falls out of sortedness; a range **scatters everything after it**
- In-memory sort limit **32MB**; aggregation stage limit **100MB** (`allowDiskUse`)
- Measured BSON: ~**90 bytes** per embedded transaction → ~**186,000** before 16MB
- What breaks before 16MB: read amplification, working set eviction, write amplification
- Embed if **bounded by the domain**; unbounded history → **bucket pattern**
- Only **leading** pipeline stages use an index; after `$group`/`$unwind` the stream is synthetic
- `explain("executionStats")` → **`totalDocsExamined` : `nReturned`** is the key ratio
- `$lookup` runs **per input document** — index the foreign field or it is N+1
- Mongo indexes are **type-sensitive**: `"123"` ≠ `123`
- Schemaless = the app has a schema, undocumented. Fix drift with a 3-phase migration.

---

## The cross-language answers

These are the ones nobody expects and everybody is impressed by. Each should be a full spoken answer, not a line.

- **Python asyncio vs the JS event loop.** Same bookmark-in-a-function model. Python makes you start the loop; JS always has one. Calling an async function in JS runs the body to the first `await`; in Python it runs **nothing**.
- **Threads for CPU: JS wins, Python loses.** `worker_threads` are isolated V8 heaps with no shared interpreter state, so no GIL, so **12012ms → 3280ms**. Python threads on the same benchmark: **1.64s vs 0.42s serial — zero speedup.** Both pay the same price for isolation: structured clone / pickle.
- **Typing: opposite directions.** Python keeps annotations at runtime, so Pydantic derives validation *from* the types. TypeScript erases them, so Zod derives the types *from* the validation.
- **N+1 is one shape in three costumes.** ORM lazy-load, correlated subquery, `$lookup` per document. Same cause: a cheap operation executed per row. Measured: **19,183ms → 1.1ms** from one index.
- **Relational vs document is a question about when you decide.** Mongo makes you decide the queries at modelling time and is excellent when you can. Postgres makes you pay upfront in normalisation and buys flexibility later.

---

## Quarterly

Re-run [the diagnostic](00_self_assessment.md) with no notes. Same questions. The delta is the only honest measure of whether any of this is working.
