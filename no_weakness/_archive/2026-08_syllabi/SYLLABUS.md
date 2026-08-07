# SYLLABUS — the master map

Three things live here that do not belong in any single topic: how the seven topics weight against the three target roles, an ordered reading path for each role, and an honest accounting of what this repo deliberately does not cover.

The per-topic detail — competencies, probes, module manifests — lives in each `NN_topic/00_syllabus.md`. This file does not repeat it.

---

## 1. The role matrix

Roughly 190 competencies across seven topics is too many to hold in mind, so they collapse here to a per-topic weight per role. Three dots means an interview for that role will probe this topic hard; one dot means it may come up once.

| Topic | Data Analyst | Data Engineer | Fullstack SWE |
|---|:---:|:---:|:---:|
| [Python](05_python_00_syllabus.md) | ●○○ | ●●● | ●●● |
| [Concurrency](06_concurrency_00_syllabus.md) | ○○○ | ●●● | ●●● |
| [SQL](09_sql_00_syllabus.md) | ●●● | ●●● | ●●○ |
| [JavaScript](07_javascript_00_syllabus.md) | ○○○ | ●○○ | ●●● |
| [TypeScript](08_typescript_00_syllabus.md) | ○○○ | ●●○ | ●●● |
| [MongoDB](10_mongodb_00_syllabus.md) | ●○○ | ●●● | ●●○ |
| [BigQuery](12_bigquery_00_syllabus.md) | ●●● | ●●● | ○○○ |

**Data analyst.** The interview is `09_sql/04` and `12_bigquery/04` — window functions and analytical SQL at scale — harder than everything else in this repo combined. Add `09_sql/05` because correctness questions follow directly from the DQA supervision claim on the resume, and the `COUNT(col)` trap is the most common silent reporting error there is. Nobody will ask about the method resolution order. Nobody will ask about the GIL.

**Data engineer.** The widest surface, and the one the CV supports best. It runs on pipeline correctness rather than language trivia: `09_sql/01` and `09_sql/03` for planner and isolation, the whole MongoDB-to-BigQuery arc in `10_mongodb/05` and `12_bigquery/05`, `12_bigquery/02` for cost, and `06_concurrency/07` for idempotency and delivery semantics. The single line *"Implemented ETL data pipelines via Apache Beam to migrate MongoDB data to BigQuery"* is the most probable subject of a fifteen-minute deep dive in any interview for this role.

**Fullstack SWE.** Python and concurrency depth plus the JavaScript and TypeScript surface. This is the role where the CV is weakest relative to what will be asked — the words JavaScript and TypeScript never appear on it — and therefore the role where the boundary scripts in each claim audit matter most.

---

## 2. The three reading paths

A candidate with a call on Thursday reads one path, not the repo. Each is ordered; each stops where the interview stops.

### Data analyst

1. [`09_sql/04`](09_sql_00_syllabus.md) — window functions, frames, ranking, gaps-and-islands, cohort retention with censoring. **This is the interview.**
2. [`09_sql/05`](09_sql_00_syllabus.md) — NULL semantics, the `COUNT` trio, money types, time zones. This is where correctness questions land.
3. [`09_sql/02`](09_sql_00_syllabus.md) — evaluation order and the `LEFT JOIN` row-loss bug.
4. [`12_bigquery/04`](12_bigquery_00_syllabus.md) — `UNNEST`, `QUALIFY`, approximate aggregates and when approximation is defensible.
5. [`12_bigquery/02`](12_bigquery_00_syllabus.md) — cost control, because an analyst who knows why `SELECT *` is expensive stands out immediately.
6. [`09_sql/01`](09_sql_00_syllabus.md) — indexes and plans, if there is time.

### Data engineer

1. [`09_sql/01`](09_sql_00_syllabus.md) — indexes and the planner.
2. [`09_sql/03`](09_sql_00_syllabus.md) — transactions, isolation, deadlocks.
3. [`10_mongodb/01`](10_mongodb_00_syllabus.md) and [`10_mongodb/02`](10_mongodb_00_syllabus.md) — modelling, then indexes and `explain`.
4. [`12_bigquery/02`](12_bigquery_00_syllabus.md) — partitioning, clustering, cost.
5. [`12_bigquery/03`](12_bigquery_00_syllabus.md) — loading, streaming, idempotency.
6. [`10_mongodb/05`](10_mongodb_00_syllabus.md) → [`12_bigquery/05`](12_bigquery_00_syllabus.md) — the two halves of the flagship bullet, read back to back.
7. [`06_concurrency/07`](06_concurrency_00_syllabus.md) — MVCC, the connection-pool ceiling, delivery semantics.
8. [`05_python/07`](05_python_00_syllabus.md) — lazy pipelines and memory-bounded processing.

### Fullstack SWE

1. [`05_python/01`](05_python_00_syllabus.md) — the object model and descriptors.
2. [`05_python/05`](05_python_00_syllabus.md) — bytecode, then
3. [`06_concurrency/01`](06_concurrency_00_syllabus.md) and [`02`](06_concurrency_00_syllabus.md) — the GIL and races.
4. [`06_concurrency/04`](06_concurrency_00_syllabus.md) — asyncio, including why a blocking call in an `async def` slows unrelated endpoints.
5. [`07_javascript/01`](07_javascript_00_syllabus.md) — closures and the stale-closure bug he has already shipped a fix for.
6. [`07_javascript/03`](07_javascript_00_syllabus.md) — the event loop.
7. [`07_javascript/02`](07_javascript_00_syllabus.md) — prototypes and `this`.
8. [`08_typescript/02`](08_typescript_00_syllabus.md) — generics, inference, variance.
9. [`08_typescript/04`](08_typescript_00_syllabus.md) — typing the boundary, and the Pydantic-versus-Zod comparison.
10. [`05_python/03`](05_python_00_syllabus.md) — decorators and metaprogramming.

---

## 3. Cross-topic answers

A handful of answers span topics, and they are the ones that read as senior immediately because almost nobody prepares them. They are noted here so they do not get lost inside a single module.

**Threads for CPU work: JavaScript wins, Python loses.** `worker_threads` are isolated V8 heaps with no shared interpreter state, so there is nothing for a global lock to protect and CPU work genuinely parallelises. Python threads on the same benchmark show no speedup at all. Both runtimes pay the identical price for that isolation — structured clone on one side, pickle on the other. Lives across [`06_concurrency/01`](06_concurrency_00_syllabus.md) and [`06`](06_concurrency_00_syllabus.md).

**Typing runs in opposite directions.** Python keeps annotations at runtime, so Pydantic reads the types and derives validation from them. TypeScript erases them entirely, so Zod does the reverse — you write the validator and infer the type from it. Same destination, opposite direction of travel. Lives across [`05_python/06`](05_python_00_syllabus.md) and [`08_typescript/04`](08_typescript_00_syllabus.md).

**N+1 is one shape in three costumes.** An ORM lazy load, a correlated subquery, and a `$lookup` executing per input document are the same mistake: a cheap operation run once per row. The measured version is worth quoting — one index moved a query from 19,183 ms to 1.1 ms. Lives across [`09_sql/07`](09_sql_00_syllabus.md), [`09_sql/01`](09_sql_00_syllabus.md) and [`10_mongodb/03`](10_mongodb_00_syllabus.md).

**Relational versus document is a question about *when you decide*.** MongoDB makes you decide your query patterns at modelling time and is excellent when you can. PostgreSQL makes you pay upfront in normalisation and buys flexibility later. Neither is the safe default. Lives across [`09_sql/06`](09_sql_00_syllabus.md) and [`10_mongodb/01`](10_mongodb_00_syllabus.md).

**Async in Python and JavaScript is the same model with one sharp difference.** Both suspend a frame and resume it later. But calling an async function in JavaScript runs the body up to the first `await` immediately, while calling one in Python executes **nothing at all** and returns a coroutine object waiting to be driven. Lives across [`06_concurrency/04`](06_concurrency_00_syllabus.md) and [`07_javascript/03`](07_javascript_00_syllabus.md).

**Speculative optimisation arrived twice.** V8's hidden classes and inline caches, and CPython 3.11's specialising adaptive interpreter, are the same idea: observe the types that actually occur, rewrite the hot path to assume them, and guard for when the assumption breaks. Lives across [`07_javascript/02`](07_javascript_00_syllabus.md) and [`05_python/05`](05_python_00_syllabus.md).

---

## 4. Coverage appendix — what the video syllabi contain and what this repo does with it

The `assets/` folder held four phone screenshots of YouTube chapter lists, treated for a while as this folder's syllabus. They are transcribed in [`_archive/2026-08_v1/video_syllabi.md`](../2026-08_v1/video_syllabi.md) and the images are deleted.

They were never a syllabus. A flat list of fifty topics with timestamps has no hierarchy, no objectives, no prerequisites and no indication of depth — and at **61 seconds per Python topic**, the format produces recognition rather than retrieval. That is exactly the depth level this folder exists to escape.

Their remaining use is this argument about coverage.

### Python video — 50 topics

**Covered at greater depth than the video reaches:** garbage collection with circular references, method resolution order, CPython internals, the GIL, concurrency, multithreading, multiprocessing, multiprocessing race conditions, shared memory, encapsulation and abstraction, inheritance and polymorphism, the data model, iterators, generators, `staticmethod`/`classmethod`, dependency injection, serialization, `__getstate__`/`__setstate__`, bytecode and `dis`, metaclasses, context managers both custom and nested, `weakref`, `WeakKeyDictionary`/`WeakValueDictionary`, `__slots__`, `memory_profiler`, `sys.getsizeof`, advanced decorators, dataclasses, metaprogramming, `functools`, and `asyncio`. That is 33 of the 50, each getting thousands of words instead of a minute.

**Deliberately skipped, with the reason:** arrays, `collections`, `heapq`, `bytes`, `memoryview`, higher-order functions, `filter`, advanced list comprehensions, the walrus operator, `operator.attrgetter`, `del`, and "not returning dicts and lists." These are syntax and standard-library surface — things you either know or can look up in ten seconds. Nobody has ever been rejected for not knowing `:=`. Parameterized testing and fixtures are skipped here because they belong with testing material rather than with what the language does.

**Added, because the video does not cover it and interviews do:** the descriptor protocol, the full `__getattribute__` resolution order, the `__eq__`/`__hash__` contract, cell objects and late binding, `functools.wraps` and what it restores, `__init_subclass__`/`__set_name__`, pymalloc arenas and why RSS never returns, the specialising adaptive interpreter, interning identity traps, runtime annotations and `get_type_hints`, `Protocol` and structural typing, the import system, and free-threaded CPython.

### JavaScript video — 14 sections

**Covered:** scope, closure, hoisting, execution context, prototype, OOP, asynchronous JavaScript, multi-threading in the browser, multi-threading in Node, and how Node works.

**Deliberately skipped:** event propagation, event delegation and memoization. The first two are DOM mechanics — ten-minute topics that rarely decide a senior interview, and neither target role centres on the DOM. Memoization gets eighteen minutes of video for what is a two-paragraph idea; it appears inside [`07_javascript/06`](07_javascript_00_syllabus.md) where caching interacts with memory leaks, which is the version that is actually interesting.

**Added:** the temporal dead zone, `this` binding rules in precedence order, V8 hidden classes and inline caches, the microtask-versus-macrotask ordering in full, the promise state machine, `async`/`await` desugaring, CommonJS versus ESM live bindings, tree shaking, module resolution and the `exports` map, heap-snapshot leak hunting, and async stack traces.

### What the videos do not cover at all

**SQL, MongoDB, BigQuery and TypeScript** — four of the seven topics here, including both halves of the flagship CV bullet and the entire data-analyst path. Two videos totalling five and a half hours cover, between them, less than half of what this repo needs to.

---

← [repo index](../../README.md) · [writing contract](../../AGENTS.md) · [measurement ledger](../../MEASUREMENTS.md)
