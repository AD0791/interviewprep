# AGENTS.md — the textbook contract

This file governs everything inside `no_weakness/`. It supersedes [`interviewprep/AGENTS.md`](../AGENTS.md) wherever the two conflict.

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
textbook chapter a node in the graph eventually earns. Its format is binding and lives in
[`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md): section order, word budgets, the
simple-to-complex code progression, the diagram rules, and the ban on practice material.
**Read `MODULE_SPEC.md`, not this file, before writing or revising a module.** A module's front
matter names the graph node(s) it covers; the graph node's own `**Article:**` line points back
once the module exists.

**Every number** either of those layers quotes is governed by
[`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §6: it names its source in the sentence that
makes it, or it does not appear. [`MEASUREMENTS.md`](MEASUREMENTS.md) and
[`_tools/MEASUREMENT_SPEC.md`](_tools/MEASUREMENT_SPEC.md) are a closed archive of the figures
the eleven pre-spec modules were built on, citable but no longer extended.

This file states the principles the three specs implement, and is the tiebreaker when they are
silent or appear to conflict.

**As of this writing, the graph layer is complete for all 26 subjects (482 nodes) and the text
layer is not** — 11 modules are written. Building a graph node is not a promise that a module
follows immediately; see §9.

---

## 1. What this folder is

**A programming textbook** covering, as of this writing, twenty-six subjects at
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

What replaces them: a **reference summary** at the end of each module — a condensed statement of the module's facts, written as something to look up, not something to be quizzed on.

The v1 self-assessment diagnostic, the `RECALL.md` rehearsal script, the competency-table syllabi and the drills that went with them have all been **deleted**, not merely deprecated. Nothing in this repository should link to them or reproduce their shape. [`MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §2 carries the operative list, including the two section titles that are permanently retired because they encode the banned framing.

---

## 3. The module structure

Every module is 6,000–8,000 words across six sections, in a fixed order: the problem this
solves, the mechanism built up from the smallest example, failure modes with the errors they
produce, trade-offs with a mandatory cost column, and a reference summary. Diagrams are
integrated into the mechanism section rather than collected into one of their own.

**The binding format, with the section budgets and the full rules for each, is
[`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §3.** Three of its requirements are the ones
drafts most often miss, so they are worth stating here as principles rather than as format:

**Build up, never decompose.** The mechanism section starts with the smallest complete example
that runs — five to ten lines, one idea, output shown — and extends it one dimension at a time
until it reaches the shape the thing takes in production. Presenting the complex form first and
taking it apart is the failure mode this rule exists to prevent.

**Draw the picture where a paragraph would be harder to visualise than one.** This is a
requirement rather than a permission, because an earlier version of this folder under-used
diagrams badly. The test is to delete the diagram and reread the paragraph: if the paragraph is
fine alone, the diagram was decoration.

**Code is exposition, not homework.** Every listing is there to be read and understood on the
page. A module never tells the reader to run it, try it, install something first, or stand up a
service — see §7.

## 4. Prose rules

Complete sentences everywhere. Never fragment bullets, arrow chains (`A → B → fails`), or "Skeleton:" outlines. Bullets and tables only for genuinely enumerable facts, with the reasoning in surrounding prose. Register: a good technical book — patient, concrete, precise, unhurried.

Write about the subject, not about the reader. No second-person challenges, no "you probably think", no "most people get this wrong".

---

## 5. Sourcing honesty

A claim a reader could reasonably doubt names where it came from, in the sentence that makes it.
A claim with no attributable source does not appear at all. This matters most for numbers,
because a number reads as authoritative whether or not anything stands behind it.

This is not an abstract worry. The rule exists because an early module was written about a
database with no server available locally, so its query plans came from vendor documentation
while its size calculations were genuinely computed — and on the page the two were
indistinguishable.

An earlier version of this folder answered that with a measurement requirement: a number had to
come out of a terminal on a named machine, recorded in a ledger with a command and an
environment. It caught the right problem and chose the wrong remedy. **This is a book to read,
and nothing in it may depend on the reader — or the author — having an environment.** The
measurement rule made a reference text conditional on a running daemon and an installed
toolchain, and it left six subjects marked unwritable for that reason alone. Attribution catches
the same dishonesty at none of that cost: *"Ramalho's chapter 3 gives the resize threshold as
two-thirds load"* is checkable by anyone holding the book, and needs no machine at all.

**The operative rule, with the four kinds of admissible source and the line between what needs
attribution and what the code on the page shows for itself, is
[`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §6.**
[`MEASUREMENTS.md`](MEASUREMENTS.md) and [`_tools/MEASUREMENT_SPEC.md`](_tools/MEASUREMENT_SPEC.md)
remain as a closed archive: the figures behind the eleven pre-spec modules, citable as sources
like any other documentation and with their environment named, never extended.

---

## 6. Quality checks before a module is marked written

The operative checklist is [`_tools/MODULE_SPEC.md`](_tools/MODULE_SPEC.md) §5, which is what a
module is actually checked against. The two checks that carry the most weight, and the reasoning
behind them, are these.

**The noun-swap test.** No paragraph may survive having its subject swapped for a different
technology. Generic filler does survive it — *"indexes improve read performance at the cost of
write performance"* works for Postgres, MongoDB and MySQL, which is exactly why it is worthless.
Specific writing does not survive it, because it names a version, a default, a constant, or an
attributed figure.

**Attribution.** Every quantitative claim names its source in the sentence that makes it, and
nothing is written as though it were a reading taken off a machine. A failure mode may quote the
exception a language or library defines, because that is documented surface rather than a
measurement; it may not quote a timing, a ratio, a memory figure or a hand-composed traceback. A
mechanism explained without a figure is honest and useful; a mechanism decorated with an invented
one is neither.

---

## 7. Standing prohibitions

**Nothing dated goes in this folder.** No interview dates, no employer names, no "for the call on Thursday". This is a reference text with an indefinite life.

**Nothing here asks anyone to set up an environment.** No installation steps, no toolchain
prerequisites, no containers to start, no "run this and see what happens", no version of anything
that has to be present before a chapter makes sense. This is a book. The only thing required to
use it is reading it, and a module that assumes otherwise is broken regardless of how good its
explanation is.

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
| 08 | `08_typescript` | 16 | `16_webrtc` | 24 | `24_golang` |
| | | | | 25 | `25_Java` |
| | | | | 26 | `26_spring` |

`06_concurrency` sits at position 06 rather than immediately after `05_python` because
`07_javascript`'s event-loop node and `09_sql`'s transaction-isolation node both need "a race
condition" to already mean something precise, and both sit downstream of it. `13_http` is the
widest fan-out point in the whole numbering: six later subjects (`14`–`17`, `24`, and `26`)
require it directly.

**A subject added after the first pass appends rather than renumbers.** The original twenty-three
directories were numbered together, in one derivation from the graph's `requires` edges. A
subject added after that takes the next free number, and renumbering nineteen directories to insert
it in DAG order is not worth the churn — every cross-subject reference, every relative link and
every node ID would move. `24_golang` is the first such case: nothing in Go's language core requires
another subject, so a from-scratch derivation would place it near the front alongside Python and
JavaScript, and it sits at 24 instead. `25_Java` and `26_spring` are the second and third, added
together as a two-subject pass: Java, like Go, is near-root (only one node names an OS
prerequisite), but Spring is not — every node in it requires Java, and several reach further into
HTTP and SQL — so the append rule produces the first case in this repository where a subject's
directory number actively understates its depth in the DAG.

The consequence is that the directory numbers are a *weak* ordering, consistent with the DAG for
the original twenty-three and merely non-contradictory for anything appended after — `24_golang`
happens to satisfy its own `requires` edges into `02_os` and `13_http` because both are lower, and
`25_Java`/`26_spring` happen to as well, but that is a coincidence rather than a guarantee, and a
future subject might not be so lucky.
[`KNOWLEDGE_GRAPH.md`](KNOWLEDGE_GRAPH.md) §2 is authoritative for real prerequisite order; this
table is a directory listing. Within the original twenty-three, if the graph's `requires` edges ever
imply a different order than the table above, the numbering is wrong and should be brought back into
agreement with the graph, not the other way around.

---

## 9. Status — this work is unfinished

**The knowledge graph is built for all 26 subjects (482 nodes, 0 validator errors).** The
written-module layer is not: **11 modules are written**, all of them in the two subjects built
before the graph existed. The repo is incomplete and is expected to stay under active
construction for a long time — 482 nodes does not mean 482 modules are coming; some nodes will
stay graph-only indefinitely, and which ones is a judgment made per subject, not a quota.

| Topic | Written | Graph nodes | Article gap |
|---|---|---|---|
| `05_python/` | 01, 03, 05 | 24 (`PY-01`…`PY-24`) | 21 nodes with no module |
| `06_concurrency/` | 01, 02, 03, 04 | 17 (`CONC-01`…`CONC-17`) | 13 nodes with no module |
| `07_javascript/` | 03 | 22 (`JS-01`…`JS-22`) | 21 nodes with no module |
| `08_typescript/` | 02 | 20 (`TS-01`…`TS-20`) | 19 nodes with no module |
| `09_sql/` | 01, 04 | 20 (`SQL-01`…`SQL-20`) | 18 nodes with no module |
| `24_golang/` | — | 23 (`GO-01`…`GO-23`) | all of them |
| `25_Java/` | — | 23 (`JAVA-01`…`JAVA-23`) | all of them |
| `26_spring/` | — | 17 (`SPRG-01`…`SPRG-17`) | all of them |
| every other subject | — | 316 across 18 subjects | all of them |

Each subject's `00_knowledge_graph.md` node record carries an `**Article:**` line once a module
exists for it — that is the authoritative record of what is written, not this table, which will
drift as modules get added.

**No subject is blocked.** An earlier version of this section listed six of them as unwritable
until a Docker daemon, a `gcloud` install, a Go toolchain or a current JDK appeared — MongoDB,
BigQuery, four SQL modules, the free-threading module, Go, Java and Spring. That list was a
consequence of the measurement requirement §5 has now replaced, and it went with it. Every
subject is writable from its shelf plus the primary sources its `Δ current` lines already name.

What those `Δ current` lines were built for is precisely this case: where a book has gone stale,
the correction is sourced to a PEP, an RFC, a release note or a vendor's own documentation, all
of which are readable and citable without anything installed. `JAVA-14`'s virtual threads come
from JEP 444, `GO-12`'s from the Go 1.25 release notes, `PY-15`'s from the Pydantic 2.0
migration guide. A chapter written that way is not a weaker chapter — it is the same chapter
without a machine-shaped dependency wrapped around it.

**All eleven written modules predate `MODULE_SPEC.md` and none of them conforms to it.** An audit
of the written layer found this is not partial drift in the earliest three, as an earlier version
of this section claimed, but a different structure end to end. Every module uses the same
superseded seven-section skeleton: a quiz-framed second section ("the questions you cannot answer
about it"), an `## Interview angles` section of spoken answers, and a closing section feeding
`RECALL.md` — a file that no longer exists. None of the eleven has the reference summary that
`MODULE_SPEC.md` §3.6 requires, which is the contract's deliberate replacement for practice
material.

The word counts follow from that. Removing the three non-conforming sections leaves 2,675–4,678
words standing per module, median around 2,940, against a 6,000-word floor. Each therefore needs
roughly 3,000 new words — about 33,000 across all eleven. That gap is not padding: it is the
simple-to-complex code progression and the reference summary, neither of which the old skeleton
asked for.

They also carry front matter from the superseded contract: a `**Syllabus:**` line where §3.0 now
requires `**Covers:**`, a `**Measurement:**` line where it now requires `**Sources:**`, and a
`**Roles:** DE ● FS ●` line that is the résumé framing §7 bans outright.

Treat these as **rewrites against `MODULE_SPEC.md`, not revisions.** Fold anything genuinely
explanatory out of an interview-angles section into the mechanism or trade-offs sections rather
than deleting it outright. Figures the old text quotes bare come out unless they can be
attributed — either to a source, or to a `MEASUREMENTS.md` row cited by ID with its environment
named in the sentence, which is what that archive is now for.

**Before writing a new module**, check the target node's `Currency` tag and `Δ current` line in
its subject's `00_knowledge_graph.md`. A `stale-major` or `absent` node means the source books
cannot carry the module alone — the `Δ current` line already names what to lead with instead,
and was written for exactly this purpose.
