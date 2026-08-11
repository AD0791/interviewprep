# no_weakness

*A programming textbook, indexed by a knowledge graph. Twenty-six subjects, at the depth
where understanding actually begins.*

---

## What this is

A reference text with an indefinite life, covering twenty-six subjects at senior-and-above
depth. Not a course, not a training regimen, not interview prep with exercises.

The reader is an experienced engineer who wants these subjects understood properly — the object
model, the GIL, the query planner, the event loop, the type system, the storage engine, the
execution model. Modules are written the way a good technical book is written: exposition that
builds, complete code that runs from a minimal example to a realistic one, diagrams wherever a
picture beats a paragraph, verbatim output from real failures, and honest trade-offs.

**The subject map is a knowledge graph, not a table of contents.** [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md)
is the root index — 482 nodes across 26 subjects, each one a directed edge-labelled graph in
the sense of Hogan et al.'s *Knowledge Graphs* survey (the method source is
[`knowledge_graph_theory.pdf`](knowledge_graph_theory.pdf)). Every node names the mechanism it
covers, its prerequisites, the books that treat it, and — the part that makes the graph worth
more than a merged table of contents — **how far those books have drifted from what is true
now**, sourced against current specs, release notes, and documentation rather than asserted.

**Every claim a reader could reasonably doubt names its source in the sentence that makes it** —
a book and chapter, a PEP or RFC by number, a release note by version, or named vendor
documentation. A figure with nothing behind it does not appear at all. The rule is
[`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §6; the reasoning is
[`AGENTS.md`](AGENTS.md) §5.

**Nothing here asks anyone to set anything up.** No installation steps, no toolchain, no
containers, no "run this and see". Code on the page is exposition, to be read and understood
there. This is a book, and the only thing needed to use it is reading it.

**No practice material.** No quizzes, diagnostics, drills, self-ratings or rehearsal scripts.
The full contract is in [`AGENTS.md`](AGENTS.md) and it is binding — read it before writing
anything here. Graph construction has its own binding spec, [`_tools/KG_SPEC.md`](_tools/KG_SPEC.md).

---

## The twenty-six subjects

Directory numbers encode **prerequisite order, not writing order** — derived from the graph's
own `requires` edges, not assigned by hand. See [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §2
for the full subject-level DAG.

| # | Subject | Nodes | Modules written |
|---|---|---|---|
| 01 | [Computation](01_computation/00_knowledge_graph.md) | 18 | 0 |
| 02 | [Operating Systems](02_os/00_knowledge_graph.md) | 21 | 0 |
| 03 | [Data Structures & Algorithms](03_dsa/00_knowledge_graph.md) | 24 | 0 |
| 04 | [Shell and SSH](04_sh/00_knowledge_graph.md) | 19 | 0 |
| 05 | [Python](05_python/00_knowledge_graph.md) — object model, metaprogramming, runtime | 24 | 01, 03, 05 |
| 06 | [Concurrency](06_concurrency/00_knowledge_graph.md) — the GIL, threads, processes, asyncio | 17 | **01, 02, 03, 04** |
| 07 | [JavaScript](07_javascript/00_knowledge_graph.md) — closures, prototypes, the event loop | 22 | 03 |
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
| 24 | [Go](24_golang/00_knowledge_graph.md) — interfaces, goroutines, channels, the toolchain | 23 | 0 |
| 25 | [Java](25_Java/00_knowledge_graph.md) — the object model, the JVM, `java.util.concurrent` | 23 | 0 |
| 26 | [Spring](26_spring/00_knowledge_graph.md) — the IoC container, Spring Boot, Spring Security | 17 | 0 |

`06_concurrency` sits at position 06 rather than immediately after `05_python` because
`07_javascript`'s event-loop node and `09_sql`'s transaction-isolation node both need "a race
condition" to already mean something precise. `13_http` is the widest fan-out point in the
numbering — six later subjects require it directly. `24_golang`, `25_Java`, and `26_spring` sit
last because subjects added after the first numbering pass append rather than force a renumber;
see [`AGENTS.md`](AGENTS.md) §8.

Each subject's `00_knowledge_graph.md` opens with a source audit (which books, what era, what
they're still good for) and a node index; a node's `**Article:**` line, once present, points at
its written module.

---

## Currency at a glance

The knowledge graph's most load-bearing finding: **56% of all 482 nodes needed a correction
against their source books.** Full breakdown, subject by subject, in
[`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §3.

| | |
|---|---|
| **Furthest from current** | `13_http` — zero nodes tagged `current`. Its sole source is a 2002 book describing a specification obsoleted twice since (RFC 7230–7235 in 2014, RFC 9110–9114 in 2022) |
| **Also badly dated** | `24_golang` and `25_Java` (96% each), `14_browser_networking` (93%), `16_webrtc` (86%), `10_mongodb` (82%). Go is dated for a different reason from the rest: its nine books are good but stop at 2021, and four language changes since — generics, `log/slog`, per-iteration loop variables, iterators — invalidate what they teach as settled. Java is dated for a third reason again: three of its seven books are decades old and predate `java.util.concurrent`, HotSpot's modern collectors, and virtual threads entirely |
| **Held up best** | `20_datascience` (20% needing correction), `03_dsa` and `23_app_dev` (25% each) — mathematics and first-principles algorithms age slower than APIs and wire protocols |
| **Genuine gaps** | 28 nodes across the repo are tagged `absent` — concepts (free-threading, MongoDB transactions, Redis Streams, RabbitMQ quorum queues, Go's range-over-func iterators, Java's virtual threads and structured concurrency) that postdate every book in that subject's directory entirely |

---

## Files at the root

| File | What it is |
|---|---|
| [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) | The root index: subject DAG, currency dashboard, cross-subject edges, coverage gaps, reading paths |
| [`AGENTS.md`](AGENTS.md) | The contract: what this folder is, what it refuses to be, and which spec governs what. Read first |
| [`_tools/KG_SPEC.md`](_tools/KG_SPEC.md) | The binding format for a subject's `00_knowledge_graph.md`. Read before editing a graph |
| [`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) | The binding format for a written module — structure, word budgets, the code progression, the ban on practice material. Read before writing one |
| [`_tools/WRITE_MODULE_PROMPT.md`](_tools/WRITE_MODULE_PROMPT.md) | The standing brief for a module-writing session, plus the Python writing order derived from the graph's `requires` edges. Copy the prompt, set the TARGET block, write one chapter |
| [`_tools/MEASUREMENT_SPEC.md`](_tools/MEASUREMENT_SPEC.md) | **Superseded.** Explains the tag vocabulary the frozen ledger's rows are written in |
| [`_tools/validate_kg.py`](_tools/validate_kg.py) | Mechanically checks every graph file — node IDs, edge cycles, currency tags, cross-subject reciprocity |
| [`_tools/extract_toc.py`](_tools/extract_toc.py) | Extracts a table of contents from a book into `<subject>/_toc/`, the graph builder's only input. Three paths: a PDF's embedded outline, a `pdftotext` scrape for PDFs without one, and an EPUB's `toc.ncx` or XHTML nav document read straight out of the container |
| [`MEASUREMENTS.md`](MEASUREMENTS.md) | **A closed archive.** The figures behind the eleven pre-spec modules, citable as sources with their environment named, never extended |

---

## Status — unfinished

**The graph is built; the text is not.** All 26 subjects have a validated `00_knowledge_graph.md`
(482 nodes, 0 validator errors). **11 modules are written**, all in the two subjects — Python
and Concurrency — built before the graph existed. This is under active construction and is
expected to stay that way for a long time: 482 nodes is not a promise of 482 modules, since some
nodes will stay graph-only by design.

| Topic | Written | Nodes | Remaining |
|---|---|---|---|
| `05_python/` | 01, 03, 05 | 24 | 21 |
| `06_concurrency/` | 01, 02, 03, 04 | 17 | 13 |
| `07_javascript/` | 03 | 22 | 21 |
| `08_typescript/` | 02 | 20 | 19 |
| `09_sql/` | 01, 04 | 20 | 18 |
| `24_golang/` | — | 23 | all |
| `25_Java/` | — | 23 | all |
| `26_spring/` | — | 17 | all |
| every other subject | — | 316 | all |

### Nothing is blocked

An earlier version of this file listed five groups of modules as gated on setup — Docker for
MongoDB and Postgres, `gcloud` for BigQuery, a free-threaded Python build, a current-LTS JDK for
Java and Spring. Those blockers were a consequence of the measurement rule that
[`AGENTS.md`](AGENTS.md) §5 has since replaced with attribution, and they went with it. Every
subject is writable from its shelf plus the primary sources its `Δ current` lines already name:
`JAVA-14`'s virtual threads from JEP 444, `CONC-05`'s free-threading from PEP 703 and PEP 779,
`PY-15`'s validation rewrite from the Pydantic 2.0 migration guide.

The genuine gaps are the ones the currency pass found in the books themselves, and they are
recorded per subject in [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §5 rather than here.

### Known debt in what exists

**All eleven modules predate [`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) and none conforms
to it.** They share a superseded seven-section skeleton with a quiz-framed second section ("the
questions you cannot answer about it"), an `## Interview angles` section of spoken answers, and a
closing section feeding a `RECALL.md` that no longer exists — and none has the reference summary
the spec requires in its place. Their front matter carries `**Syllabus:**`, `**Measurement:**`
and `**Roles:**` lines that the current §3.0 replaces or bans outright.

Removing the three non-conforming sections leaves a median of about 2,940 words standing against
a 6,000-word floor, so each is roughly 3,000 words short — the built-up code progression and the
reference summary, neither of which the old skeleton asked for. Treat them as rewrites rather
than revisions; [`AGENTS.md`](AGENTS.md) §9 carries the detail and
[`_tools/WRITE_MODULE_PROMPT.md`](_tools/WRITE_MODULE_PROMPT.md) carries the procedure.

Diagram coverage is also thinner than the contract now requires. Several written modules have
one Mermaid diagram or none where the subject has real structure worth drawing.

---

← [interviewprep index](../README.md)
