# no_weakness

*A programming textbook, indexed by a knowledge graph. Twenty-three subjects, at the depth
where understanding actually begins.*

---

## What this is

A reference text with an indefinite life, covering twenty-three subjects at senior-and-above
depth. Not a course, not a training regimen, not interview prep with exercises.

The reader is an experienced engineer who wants these subjects understood properly — the object
model, the GIL, the query planner, the event loop, the type system, the storage engine, the
execution model. Modules are written the way a good technical book is written: exposition that
builds, complete code that runs from a minimal example to a realistic one, diagrams wherever a
picture beats a paragraph, verbatim output from real failures, and honest trade-offs.

**The subject map is a knowledge graph, not a table of contents.** [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md)
is the root index — 413 nodes across 23 subjects, each one a directed edge-labelled graph in
the sense of Hogan et al.'s *Knowledge Graphs* survey (the method source is
[`knowledge_graph_theory.pdf`](knowledge_graph_theory.pdf)). Every node names the mechanism it
covers, its prerequisites, the books that treat it, and — the part that makes the graph worth
more than a merged table of contents — **how far those books have drifted from what is true
now**, sourced against current specs, release notes, and documentation rather than asserted.

**Every number in a written module came out of a terminal on a real machine**, and is recorded
in [`MEASUREMENTS.md`](MEASUREMENTS.md) with its command, environment and an honesty tag.
Claims that could not be measured are tagged `documented` and never written as though they
were. Two experiments failed to reproduce and are reported as negative results rather than
replaced with invented ones.

**No practice material.** No quizzes, diagnostics, drills, self-ratings or rehearsal scripts.
The full contract is in [`AGENTS.md`](AGENTS.md) and it is binding — read it before writing
anything here. Graph construction has its own binding spec, [`_tools/KG_SPEC.md`](_tools/KG_SPEC.md).

---

## The twenty-three subjects

Directory numbers encode **prerequisite order, not writing order** — derived from the graph's
own `requires` edges, not assigned by hand. See [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §2
for the full subject-level DAG.

| # | Subject | Nodes | Modules written |
|---|---|---|---|
| 01 | [Computation](01_computation/00_knowledge_graph.md) | 18 | 0 |
| 02 | [Operating Systems](02_os/00_knowledge_graph.md) | 21 | 0 |
| 03 | [Data Structures & Algorithms](03_dsa/00_knowledge_graph.md) | 24 | 0 |
| 04 | [Shell and SSH](04_sh/00_knowledge_graph.md) | 19 | 0 |
| 05 | [Python](05_python/00_knowledge_graph.md) — object model, metaprogramming, runtime | 20 | 01, 03, 05 |
| 06 | [Concurrency](06_concurrency/00_knowledge_graph.md) — the GIL, threads, processes, asyncio | 17 | **01, 02, 03, 04** |
| 07 | [JavaScript](07_javascript/00_knowledge_graph.md) — closures, prototypes, the event loop | 20 | 03 |
| 08 | [TypeScript](08_typescript/00_knowledge_graph.md) — structural typing, generics, variance | 20 | 02 |
| 09 | [SQL](09_sql/00_knowledge_graph.md) — planner, transactions, analytical SQL | 20 | 01, 04 |
| 10 | [MongoDB](10_mongodb/00_knowledge_graph.md) — modelling, indexes, replication, sharding | 17 | 0 |
| 11 | [Redis and caching](11_redis_caching/00_knowledge_graph.md) | 18 | 0 |
| 12 | [BigQuery](12_bigquery/00_knowledge_graph.md) — slots, partitioning, ingestion, Beam | 20 | 0 |
| 13 | [HTTP](13_http/00_knowledge_graph.md) | 18 | 0 |
| 14 | [Browser networking](14_browser_networking/00_knowledge_graph.md) | 15 | 0 |
| 15 | [WebSocket](15_websocket/00_knowledge_graph.md) | 13 | 0 |
| 16 | [WebRTC](16_webrtc/00_knowledge_graph.md) | 14 | 0 |
| 17 | [gRPC](17_grpc/00_knowledge_graph.md) | 16 | 0 |
| 18 | [Event bus and messaging](18_eventbus/00_knowledge_graph.md) — Kafka, RabbitMQ, Celery | 25 | 0 |
| 19 | [Data analysis](19_data_analysis/00_knowledge_graph.md) | 21 | 0 |
| 20 | [Data science](20_datascience/00_knowledge_graph.md) | 15 | 0 |
| 21 | [Data engineering](21_dataengineering/00_knowledge_graph.md) | 13 | 0 |
| 22 | [Android](22_android/00_knowledge_graph.md) | 17 | 0 |
| 23 | [App design](23_app_dev/00_knowledge_graph.md) | 12 | 0 |

`06_concurrency` sits at position 06 rather than immediately after `05_python` because
`07_javascript`'s event-loop node and `09_sql`'s transaction-isolation node both need "a race
condition" to already mean something precise. `13_http` is the widest fan-out point in the
numbering — four later subjects require it directly.

Each subject's `00_knowledge_graph.md` opens with a source audit (which books, what era, what
they're still good for) and a node index; a node's `**Article:**` line, once present, points at
its written module.

---

## Currency at a glance

The knowledge graph's most load-bearing finding: **51% of all 413 nodes needed a correction
against their source books.** Full breakdown, subject by subject, in
[`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §3.

| | |
|---|---|
| **Furthest from current** | `13_http` — zero nodes tagged `current`. Its sole source is a 2002 book describing a specification obsoleted twice since (RFC 7230–7235 in 2014, RFC 9110–9114 in 2022) |
| **Also badly dated** | `14_browser_networking` (93% needing correction), `16_webrtc` (86%), `10_mongodb` (82%) — the whole networking cluster and the document-database subject sit on decade-plus-old source material |
| **Held up best** | `20_datascience` (20% needing correction), `03_dsa` and `23_app_dev` (25% each) — mathematics and first-principles algorithms age slower than APIs and wire protocols |
| **Genuine gaps** | 26 nodes across the repo are tagged `absent` — concepts (free-threading, MongoDB transactions, Redis Streams, RabbitMQ quorum queues) that postdate every book in that subject's directory entirely |

---

## Files at the root

| File | What it is |
|---|---|
| [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) | The root index: subject DAG, currency dashboard, cross-subject edges, coverage gaps, reading paths |
| [`AGENTS.md`](AGENTS.md) | The textbook contract for written modules. Binding. Read before writing one |
| [`_tools/KG_SPEC.md`](_tools/KG_SPEC.md) | The binding format for a subject's `00_knowledge_graph.md`. Read before editing a graph |
| [`_tools/validate_kg.py`](_tools/validate_kg.py) | Mechanically checks every graph file — node IDs, edge cycles, currency tags, cross-subject reciprocity |
| [`_tools/extract_toc.py`](_tools/extract_toc.py) | Extracts a table of contents from a book PDF into `<subject>/_toc/`, the graph builder's only input |
| [`MEASUREMENTS.md`](MEASUREMENTS.md) | Every figure in a written module, with command, environment and tag |
| `_archive/2026-08_v1/` | Superseded first version, kept only as provenance for its measured figures |
| `_archive/2026-08_syllabi/` | The seven competency-table syllabi the knowledge graph replaced, kept for their module manifests |

---

## Status — unfinished

**The graph is built; the text is not.** All 23 subjects have a validated `00_knowledge_graph.md`
(413 nodes, 0 validator errors). **11 modules are written**, all in the two subjects — Python
and Concurrency — built before the graph existed. This is under active construction and is
expected to stay that way for a long time: 413 nodes is not a promise of 413 modules, since some
nodes will stay graph-only by design.

| Topic | Written | Nodes | Remaining |
|---|---|---|---|
| `05_python/` | 01, 03, 05 | 20 | 17 |
| `06_concurrency/` | 01, 02, 03, 04 | 17 | 13 |
| `07_javascript/` | 03 | 20 | 19 |
| `08_typescript/` | 02 | 20 | 19 |
| `09_sql/` | 01, 04 | 20 | 18 |
| every other subject | — | 316 | all |

### Environment blockers

Four groups of modules are gated on setup that has not been done — and the graph's own currency
pass independently confirms why each one matters:

- **MongoDB** needs the Docker daemon plus `mongo:8`, for real `explain("executionStats")`. Without it every plan claim is `documented`. The graph already carries four `absent` `10_mongodb` nodes (transactions, change streams, time-series collections, the warehouse-ingestion boundary) that the source book never covers regardless.
- **BigQuery** needs `gcloud`/`bq`. `bq query --dry_run` returns real bytes-processed at **zero cost**, which would make the cost-control module `measured` rather than documented.
- **SQL 02, 03, 06, 07** are better on Postgres than SQLite and need Docker plus `postgres:17`. Module 03 in particular wants a deadlock reproduced across two live `psql` sessions.
- **Concurrency 05** needs `uv python install 3.14t` for a measured GIL-versus-free-threaded comparison — one command, and a figure almost nobody has. The graph's `CONC-05` node is tagged `absent` for the same reason: no book on the shelf postdates the feature.

### Known debt in what exists

The three earliest modules — `05_python/01`, `03`, `05` — were written before the no-practice
rule and open with quiz-style framing ("the questions you cannot answer about it"). All eleven
modules carry a legacy `## Interview angles` section of spoken answers. Both need a revision
pass to match [`AGENTS.md`](AGENTS.md) §3: no rhetorical interrogation, and anything genuinely
explanatory folded into the mechanism or trade-off sections.

Diagram coverage is also thinner than the contract now requires. Several written modules have
one Mermaid diagram or none where the subject has real structure worth drawing.

---

← [interviewprep index](../README.md)
