# no_weakness

*A programming textbook. Seven subjects, at the depth where understanding actually begins.*

---

## What this is

A reference text with an indefinite life, covering seven subjects at senior-and-above depth. Not a course, not a training regimen, not interview prep with exercises.

The reader is an experienced engineer who wants these subjects understood properly — the object model, the GIL, the query planner, the event loop, the type system, the storage engine, the execution model. Modules are written the way a good technical book is written: exposition that builds, complete code that runs from a minimal example to a realistic one, diagrams wherever a picture beats a paragraph, verbatim output from real failures, and honest trade-offs.

**Every number in this repo came out of a terminal on a real machine**, and is recorded in [`MEASUREMENTS.md`](MEASUREMENTS.md) with its command, environment and an honesty tag. Claims that could not be measured are tagged `documented` and never written as though they were. Two experiments failed to reproduce and are reported as negative results rather than replaced with invented ones.

**No practice material.** No quizzes, diagnostics, drills, self-ratings or rehearsal scripts. The full contract is in [`AGENTS.md`](AGENTS.md) and it is binding — read it before writing anything here.

---

## The seven subjects

Directory numbers encode **prerequisite order, not writing order**.

| # | Subject | Modules written |
|---|---|---|
| 01 | [Python](01_python/00_syllabus.md) — object model, metaprogramming, runtime | 01, 03, 05 of 8 |
| 02 | [Concurrency](02_concurrency/00_syllabus.md) — the GIL, threads, processes, asyncio | **01, 02, 03, 04** of 7 |
| 03 | [SQL](03_sql/00_syllabus.md) — planner, transactions, analytical SQL | 01, 04 of 7 |
| 04 | [JavaScript](04_javascript/00_syllabus.md) — closures, prototypes, the event loop | 03 of 6 |
| 05 | [TypeScript](05_typescript/00_syllabus.md) — structural typing, generics, variance | 02 of 5 |
| 06 | [MongoDB](06_mongodb/00_syllabus.md) — modelling, indexes, replication, sharding | none of 5 |
| 07 | [BigQuery](07_bigquery/00_syllabus.md) — slots, partitioning, ingestion, Beam | none of 5 |

Concurrency sits at 02 rather than last because `04_javascript/03` and `03_sql/03` both need "race" to already mean something precise.

Each topic's `00_syllabus.md` opens with a competency table: what the subject requires you to be able to do, at what depth, and which module covers it.

---

## Files at the root

| File | What it is |
|---|---|
| [`AGENTS.md`](AGENTS.md) | The textbook contract. Binding. Read before writing |
| [`SYLLABUS.md`](SYLLABUS.md) | Cross-subject map and reading paths |
| [`MEASUREMENTS.md`](MEASUREMENTS.md) | Every figure in the repo, with command, environment and tag |
| `00_self_assessment.md` | **Deprecated.** Practice material, outside the workflow. Do not extend or link it |
| `_archive/2026-08_v1/` | Superseded first version, kept only as provenance for its measured figures |

---

## Status — unfinished

**11 of 43 modules are written.** This is under active construction and is expected to stay that way for some time.

| Topic | Remaining |
|---|---|
| `01_python/` | 02 data model · 04 memory & GC · 06 runtime typing · 07 generators · 08 imports |
| `02_concurrency/` | 05 free-threading · 06 Node & browser · 07 database & pipeline |
| `03_sql/` | 02 joins · 03 transactions · 05 NULL semantics · 06 schema · 07 performance |
| `04_javascript/` | 01 closures · 02 prototypes · 04 coercion · 05 modules · 06 leaks |
| `05_typescript/` | 01 structural typing · 03 narrowing · 04 the boundary · 05 React & Node |
| `06_mongodb/` | all five |
| `07_bigquery/` | all five |

### Environment blockers

Four groups of modules are gated on setup that has not been done:

- **MongoDB** needs the Docker daemon plus `mongo:8`, for real `explain("executionStats")`. Without it every plan claim is `documented`.
- **BigQuery** needs `gcloud`/`bq`. `bq query --dry_run` returns real bytes-processed at **zero cost**, which would make the cost-control module `measured` rather than documented.
- **SQL 02, 03, 06, 07** are better on Postgres than SQLite and need Docker plus `postgres:17`. Module 03 in particular wants a deadlock reproduced across two live `psql` sessions.
- **Concurrency 05** needs `uv python install 3.14t` for a measured GIL-versus-free-threaded comparison — one command, and a figure almost nobody has.

### Known debt in what exists

The three earliest modules — `01_python/01`, `03`, `05` — were written before the no-practice rule and open with quiz-style framing ("the questions you cannot answer about it"). All eleven modules carry a legacy `## Interview angles` section of spoken answers. Both need a revision pass to match [`AGENTS.md`](AGENTS.md) §3: no rhetorical interrogation, and anything genuinely explanatory folded into the mechanism or trade-off sections.

Diagram coverage is also thinner than the contract now requires. Several written modules have one Mermaid diagram or none where the subject has real structure worth drawing.

---

← [interviewprep index](../README.md)
