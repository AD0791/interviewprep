# AGENTS.md — the textbook contract

This file governs everything inside `no_weakness/`. It supersedes `interviewprep/.agents/AGENTS.md` wherever the two conflict.

**Read this before writing or editing a single module.**

---

## 0. Two layers: the graph and the text

This folder has two kinds of file, built by two different contracts.

**The knowledge graph** — [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) at the root, and one
`00_knowledge_graph.md` per subject — is the structural index. It says what concepts exist in a
subject, how they depend on and contrast with each other, which books cover them, and — the
part that matters most — how far each concept has drifted from what is true now. It is built
and edited per [`_tools/KG_SPEC.md`](_tools/KG_SPEC.md), a separate, binding specification.
**Read `KG_SPEC.md`, not this file, before touching a `00_knowledge_graph.md`.**
[`_tools/validate_kg.py`](_tools/validate_kg.py) checks every graph file mechanically; a graph
that fails it is not finished.

**The written module** — everything else, e.g. `06_concurrency/01_the_gil_...md` — is the
textbook chapter a node in the graph eventually earns. The rest of *this* file, §1 onward,
governs that: what a module is, how it is structured, and the honesty rules around measured
claims. A module's front matter names the graph node(s) it covers; the graph node's own
`**Article:**` line points back once the module exists.

**As of this writing, the graph layer is complete for all 23 subjects (413 nodes) and the text
layer is not** — 11 modules are written. Building a graph node is not a promise that a module
follows immediately; see §9.

---

## 1. What this folder is

**A programming textbook** covering, as of this writing, twenty-three subjects at
senior-and-above depth. Not a course, not a training regimen, not interview prep with
exercises.

The reader is an experienced engineer who wants to *understand these subjects properly* — the
object model, the GIL, the query planner, the event loop, the type system, the storage engine,
the execution model. The measure of a module is whether someone who reads it understands the
mechanism afterwards, not whether they can be tested on it.

Write it the way a good technical book is written: exposition that builds, complete code that
runs, diagrams where prose genuinely strains, and honest treatment of trade-offs.

---

## 2. No practice material. None.

This is a hard rule and it reverses an earlier version of this folder.

**Do not write:** self-assessment questions, diagnostics, quizzes, drills, flashcards, "rate yourself 1–5" tables, "say this out loud" instructions, spaced-repetition schedules, "test yourself before reading on", or anything else that asks the reader to perform rather than read.

**Do not write** rhetorical quiz openings — "can you answer this?", "questions you cannot answer", "if you can explain all four, skip ahead". A textbook does not interrogate its reader.

`00_self_assessment.md` at the repo root is **deprecated** and outside the workflow. Do not extend it, link to it, or build anything that depends on it. `RECALL.md` as a rehearsal drill script is likewise abandoned.

What replaces them: a **reference summary** at the end of each module — a condensed statement of the module's facts, written as something to look up, not something to be quizzed on.

---

## 3. The module structure

Every module follows this, in order. Total 6,000–8,000 words.

### Front matter (~120 words)

```markdown
# The GIL — what it protects, and when it lets go

*Reference counts, bytecode boundaries, and the five milliseconds nobody mentions.*

**Level:** L4 · **Prerequisites:** [05_python/05 bytecode](../05_python/05_bytecode_and_the_runtime.md)
**Covers:** CONC-01 … CONC-07
**Measurement:** Measured — CPython 3.14.6, 8 cores, macOS 26.5. Every number below
came out of a terminal.
```

The measurement line is mandatory (see §5).

### §1 — The problem this solves (400–700 words)

Open with the engineering situation the subject exists to address. Concrete, in code. What goes wrong without this mechanism, or what question it answers.

Do not open with a definition. Do not open by asking the reader what they know.

### §2 — The mechanism, built up (2,500–3,500 words)

The core of the module, and where the **simple-to-complex code progression** lives. This is a hard requirement:

**Start with the smallest complete example that runs.** Five to ten lines. One idea. Output shown.

**Then extend it, one dimension at a time.** Each step adds exactly one new concept and shows the resulting output. The reader must be able to follow the whole chain without a leap.

**End with a realistic version** — the shape the thing actually takes in production code, with the complications that implies.

Never present the complex form first and decompose it. Build up.

Narrate in prose between the code blocks. The explanation lives in paragraphs; comments annotate, they do not teach.

Trace one concrete execution through the machine in plain words at least once per module.

### §3 — Diagrams (integrated into §2, not a separate section)

**Where a paragraph would be harder to visualise than a picture, draw the picture.** This is a requirement, not a permission — an earlier version of this folder under-used diagrams badly.

Use Mermaid. Two to four per module is normal; more is fine when the subject is structural.

Draw when the subject has: a **shape** (a chain, a tree, a DAG), an **ordering or interleave** (event loops, races, protocol exchanges), a **lifecycle** (state machines), a **topology** (replica sets, shard maps, query stages), or a **layout** (memory, address spaces, index pages).

Permitted: `graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, and fenced ASCII where byte-level layout matters.

Banned: a diagram that restates a bulleted list; generic "architecture" boxes; anything past ~15 nodes.

**Test:** delete the diagram and reread the paragraph. If the paragraph is fine alone, the diagram was decoration. If the paragraph got noticeably harder, the diagram earns its place.

### §4 — Failure modes (1,500–2,200 words)

Three to five ways the mechanism breaks, each with:

1. Minimal runnable reproduction, named `# Gist: name.py`
2. **Verbatim terminal output** in its own fenced block — copy-pasted, never composed by hand
3. Prose explanation referring back to the §2 subsection that predicted it
4. The fix, with its cost stated

Failures that could not be reproduced are **reported as negative results**, not invented. A nondeterministic failure honestly described is more useful than a fabricated one, and this folder has two good examples already.

### §5 — Trade-offs (900–1,300 words)

An options table with fixed columns: **Use when · Because · Real cost.** The cost column is not optional.

Then prose subsections, one of which is always the case *against* — when you would not use this, and what you would use instead.

### §6 — Reference summary (300–500 words)

A condensed, scannable statement of everything the module established. Measured figures in bold. Written as a **lookup table for someone who read the chapter and wants the facts back**, not as a self-test.

### Footer

`← [<Topic> knowledge graph](00_knowledge_graph.md) · [repo index](../README.md)`

---

## 4. Prose rules

Complete sentences everywhere. Never fragment bullets, arrow chains (`A → B → fails`), or "Skeleton:" outlines. Bullets and tables only for genuinely enumerable facts, with the reasoning in surrounding prose. Register: a good technical book — patient, concrete, precise, unhurried.

Write about the subject, not about the reader. No second-person challenges, no "you probably think", no "most people get this wrong".

---

## 5. Measurement honesty

The measured claims are what make these modules worth more than the documentation they compete with. Borrowing that authority for an unmeasured claim would undermine every claim that is real.

Every module carries exactly one tag in its front matter; individual claims may carry a stricter one.

**`Measured`** — the number came out of a terminal on a named machine on a named date, and the command is recorded in [`MEASUREMENTS.md`](MEASUREMENTS.md) with an ID.

**`Reproduced small`** — measured on a toy that demonstrates the mechanism correctly but whose magnitude does not transfer. Never quote the magnitude.

**`Documented`** — from vendor documentation, no measurement. The tag appears in the front matter *and* is repeated in prose at the point of use.

Figures inherited from an earlier environment carry `measured-stale-env` in the ledger and must name that environment wherever they appear.

---

## 6. Quality checks before a module is marked written

1. **Verbatim output.** Every §4 failure shows real terminal output. Zero hand-composed, zero "would print approximately".
2. **Code progression.** §2 starts with a minimal runnable example and builds. No module opens with its most complex listing.
3. **Diagrams present where earned.** At least one, and every one survives the delete test.
4. **Measurement density.** At least three claims cite `MEASUREMENTS.md` IDs.
5. **Rejected alternatives.** §5 names at least two, with costs.
6. **The noun-swap test.** No paragraph may survive having its subject swapped for a different technology. Generic filler survives noun-swapping — *"indexes improve read performance at the cost of write performance"* works for Postgres, MongoDB and MySQL, which is why it is worthless. Specific writing does not, because it names a version, a default, a constant, or a measured figure.
7. **No practice material.** Per §2.

---

## 7. Standing prohibitions

**Nothing dated goes in this folder.** No interview dates, no employer names, no "for the call on Thursday". This is a reference text with an indefinite life.

**Do not organise content around a résumé.** An earlier version built every syllabus around what a CV did and did not claim, with rehearsal scripts for the gaps. That framing is removed and must not return. The organising principle is **the subject**, at the depth a senior-and-above engineer needs.

**This folder never links out to a campaign folder.** Campaign folders link in. The dependency runs one way.

---

## 8. Directory numbering

Directory numbers encode **prerequisite order**, not writing order, and are derived from the
subject-level `requires` edges in [`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §2 rather than
assigned by hand:

| # | Subject | # | Subject | # | Subject |
|---|---|---|---|---|---|
| 01 | `01_computation` | 09 | `09_sql` | 17 | `17_grpc` |
| 02 | `02_os` | 10 | `10_mongodb` | 18 | `18_eventbus` |
| 03 | `03_dsa` | 11 | `11_redis_caching` | 19 | `19_data_analysis` |
| 04 | `04_sh` | 12 | `12_bigquery` | 20 | `20_datascience` |
| 05 | `05_python` | 13 | `13_http` | 21 | `21_dataengineering` |
| 06 | `06_concurrency` | 14 | `14_browser_networking` | 22 | `22_android` |
| 07 | `07_javascript` | 15 | `15_websocket` | 23 | `23_app_dev` |
| 08 | `08_typescript` | 16 | `16_webrtc` | | |

`06_concurrency` sits at position 06 rather than immediately after `05_python` because
`07_javascript`'s event-loop node and `09_sql`'s transaction-isolation node both need "a race
condition" to already mean something precise, and both sit downstream of it. `13_http` is the
widest fan-out point in the whole numbering: four later subjects (`14`–`17`) require it
directly.

If the graph's `requires` edges ever imply a different order than the table above — a new
subject added, an edge corrected — the numbering is wrong and should be brought back into
agreement with the graph, not the other way around.

---

## 9. Status — this work is unfinished

**The knowledge graph is built for all 23 subjects (413 nodes, 0 validator errors).** The
written-module layer is not: **11 modules are written**, all of them in the two subjects built
before the graph existed. The repo is incomplete and is expected to stay under active
construction for a long time — 413 nodes does not mean 413 modules are coming; some nodes will
stay graph-only indefinitely, and which ones is a judgment made per subject, not a quota.

| Topic | Written | Graph nodes | Article gap |
|---|---|---|---|
| `05_python/` | 01, 03, 05 | 20 (`PY-01`…`PY-20`) | 17 nodes with no module |
| `06_concurrency/` | 01, 02, 03, 04 | 17 (`CONC-01`…`CONC-17`) | 13 nodes with no module |
| `07_javascript/` | 03 | 20 (`JS-01`…`JS-20`) | 19 nodes with no module |
| `08_typescript/` | 02 | 20 (`TS-01`…`TS-20`) | 19 nodes with no module |
| `09_sql/` | 01, 04 | 20 (`SQL-01`…`SQL-20`) | 18 nodes with no module |
| every other subject | — | 316 across 18 subjects | all of them |

Each subject's `00_knowledge_graph.md` node record carries an `**Article:**` line once a module
exists for it — that is the authoritative record of what is written, not this table, which will
drift as modules get added.

**Blocked on environment**, carried over from before the graph existed and still accurate:

- `10_mongodb/` — needs the Docker daemon running plus `mongo:8` for real `explain("executionStats")`. Without it every plan claim is `documented`, which the graph's own currency pass already confirms independently: `10_mongodb` carries four `absent` nodes (transactions, change streams, time-series collections, the warehouse-ingestion boundary) that the source book never covers at all.
- `12_bigquery/` — needs `gcloud`/`bq` installed. `bq query --dry_run` returns real bytes-processed at zero cost, which would make the cost-control module `measured` rather than `documented`.
- `09_sql/` 02, 03, 06, 07 — better on Postgres than SQLite; needs Docker plus `postgres:17`. Module 03 in particular wants a deadlock reproduced across two live `psql` sessions.
- `06_concurrency/05` — wants `uv python install 3.14t` for a measured GIL versus free-threaded comparison. The graph's own `CONC-05` node is tagged `absent` for exactly this reason: no book on the shelf covers free-threading, because none postdates it.

**The three modules written before this contract** — `05_python/01`, `03`, `05` — predate the no-practice rule and contain quiz-style §2 openings ("the questions you cannot answer about it") and rehearsal-oriented interview sections. They need revising to match §3. The eight later modules share the same structure and need the same pass.

Every module written so far also carries an `## Interview angles` section of spoken answers. Under this contract those are **legacy**: leave existing ones in place, do not add them to new modules, and fold anything genuinely explanatory from them into §2 or §5 when revising.

**Before writing a new module**, check the target node's `Currency` tag and `Δ current` line in
its subject's `00_knowledge_graph.md`. A `stale-major` or `absent` node means the source books
cannot carry the module alone — the `Δ current` line already names what to lead with instead,
and was written for exactly this purpose.
