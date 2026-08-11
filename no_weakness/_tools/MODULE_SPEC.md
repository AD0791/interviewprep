# MODULE_SPEC — how to write a module

This is the binding format for every written module in `no_weakness/` — the textbook chapters
themselves, as distinct from the `00_knowledge_graph.md` index files governed by
[`KG_SPEC.md`](KG_SPEC.md). `AGENTS.md` states the principles; this file states the format.
Where the two appear to differ, this file is the operative one for module shape and `AGENTS.md`
for the reasons behind it.

Sourcing rules are in §6 and are binding: a module that quotes an unattributed figure is not
finished. [`MEASUREMENT_SPEC.md`](MEASUREMENT_SPEC.md) and [`MEASUREMENTS.md`](../MEASUREMENTS.md)
are a closed archive covering the eleven pre-spec modules and govern nothing written from here on.

---

## 1. What a module is

**One chapter of a programming textbook**, written against one or more nodes of a subject's
knowledge graph. The reader is an experienced engineer who wants to understand the mechanism —
the object model, the query planner, the event loop, the collector — not to be tested on it.

The measure of a module is whether someone who reads it understands the mechanism afterwards.

A module is 6,000–8,000 words. The section budgets in §3 sum to roughly that; a module landing
far short has almost always skipped the built-up code progression or the reference summary,
which are the two things this format asks for that a conventional tutorial does not.

---

## 2. No practice material. None.

A hard rule, and it reverses an earlier version of this folder.

**Never write:** self-assessment questions, diagnostics, quizzes, drills, flashcards, "rate
yourself 1–5" tables, "say this out loud" instructions, spaced-repetition schedules, "test
yourself before reading on", or anything else that asks the reader to perform rather than read.

**Never write rhetorical quiz openings** — "can you answer this?", "the questions you cannot
answer", "if you can explain all four, skip ahead". A textbook does not interrogate its reader.

**Never organise a module around a résumé or an interview.** No interview dates, no employer
names, no "what to say when asked". The organising principle is the subject. An earlier version
of this folder built every chapter around what a CV did and did not claim; that framing was
removed and must not return.

What replaces all of it is the **reference summary** in §3.5 — a condensed statement of the
module's facts, written to be looked up, not to be quizzed on.

Two section titles are permanently retired because they encode the banned framing: any heading
of the form *"the questions you cannot answer about it"*, and any *"Interview angles"* section.
Modules that still carry them predate this spec and are listed in `AGENTS.md` §9 as revision
debt.

---

## 3. The structure

Every module follows this, in order. The written module's own headings are exactly these five,
and only these five — so the count can never again be inferred from the sub-numbering below:

    ## 1. The problem this solves
    ## 2. The mechanism, built up
    ## 3. Failure modes
    ## 4. Trade-offs
    ## 5. Reference summary

Front matter and the footer are not sections and carry no heading of their own.

The section minimums below sum to 5,600 words, short of the 6,000-word floor, so a section
targets the **midpoint** of its range rather than its minimum. The midpoints — 550, 3,000, 1,850,
1,100, 400 — sum to 6,900, comfortably inside the 6,000–8,000 band.

### 3.0 Front matter (~120 words)

```markdown
# The GIL — what it protects, and when it lets go

*Reference counts, bytecode boundaries, and the five milliseconds nobody mentions.*

**Level:** L4 · **Prerequisites:** [05_python/05 bytecode](../05_python/05_bytecode_and_the_runtime.md)
**Covers:** CONC-01 … CONC-07
**Sources:** Ramalho, *Fluent Python* 2nd ed. ch.19–20 (2022) · Beazley, *Advanced Python
Mastery* §5 (2024) · PEP 703 (2023) · CPython `Python/ceval_gil.c` documentation
```

`Covers:` names knowledge-graph node IDs. The `Sources:` line is mandatory: it names the books
and chapters, PEPs, RFCs, release notes or vendor documentation the chapter is written from, and
it is the same bibliography the node record's own `Sources:` line carries, narrowed to what the
chapter actually used. There is no `Measurement:` line and no `Roles:` line; both belong to
superseded versions of this folder.

### 3.1 The problem this solves (400–700 words)

Open with the engineering situation the subject exists to address, concretely and in code. What
goes wrong without this mechanism, or what question it answers.

Never open with a definition. Never open by asking the reader what they know.

### 3.2 The mechanism, built up (2,500–3,500 words)

The core of the module, and where the **simple-to-complex code progression** lives. This is a
hard requirement, and it is the single most common thing a draft gets wrong.

**Start with the smallest complete example that runs.** Five to ten lines, one idea, output
shown.

**Then extend it one dimension at a time.** Each step adds exactly one concept and shows the
resulting output, so the reader follows the whole chain without a leap.

**End with a realistic version** — the shape the thing takes in production code, with the
complications that implies.

Never present the complex form first and decompose it. Build up.

Narrate in prose between the code blocks: the explanation lives in paragraphs, and comments
annotate rather than teach. Trace one concrete execution through the machine in plain words at
least once per module.

**Code is exposition.** It is on the page to be read and understood there, not to be run. Never
instruct the reader to try it, install anything, stand up a service, or set up an environment
before continuing. A chapter that only works for a reader with a terminal open is not a chapter.

**Diagrams belong inside this section.**

Where a paragraph would be harder to visualise than a picture, draw the picture. This is a
requirement rather than a permission; an earlier version of this folder under-used diagrams
badly.

Use Mermaid. Two to four per module is normal, and more is right when the subject is structural.
Draw when the subject has a shape (a chain, a tree, a DAG), an ordering or interleave (event
loops, races, protocol exchanges), a lifecycle (state machines), a topology (replica sets, shard
maps, query stages), or a layout (memory, address spaces, index pages).

Permitted: `graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, and fenced ASCII where
byte-level layout matters. Banned: a diagram that restates a bulleted list, generic
"architecture" boxes, and anything past roughly 15 nodes.

**The delete test.** Remove the diagram and reread the paragraph. If the paragraph is fine
alone, the diagram was decoration. If it got noticeably harder, the diagram earns its place.

### 3.3 Failure modes (1,500–2,200 words)

Three to five ways the mechanism breaks. Each one carries a minimal reproduction named
`# Gist: name.py`, the error it produces, a prose explanation referring back to the §3.2
subsection that predicted it, and the fix with its cost stated.

**What may be shown as output.** An exception type and message that the language or library
defines and that does not vary between runs — `TypeError: unhashable type: 'list'`,
`RuntimeError: dictionary changed size during iteration`, a `psycopg` `SerializationFailure` —
may be quoted, because it is part of the documented surface rather than a reading taken off a
machine. Say what the code raises, not what a particular terminal printed.

**What may not.** Anything that varies with the machine: timings, ratios, speed-ups, memory
figures, row counts from a dataset that exists nowhere, thread interleavings, addresses,
process IDs. A number in a failure-mode section is subject to §6 like any other, so it is
attributed to a named source or it is left out. Never compose a plausible-looking traceback and
never write "would print approximately".

A failure that is nondeterministic is described as nondeterministic — what makes it fire, what
makes it hide, and why that is the hard part — rather than dressed up with an invented run that
happened to show it.

### 3.4 Trade-offs (900–1,300 words)

An options table with fixed columns — **Use when · Because · Real cost** — where the cost column
is not optional. Then prose subsections, one of which is always the case *against*: when you
would not use this, and what you would use instead.

### 3.5 Reference summary (300–500 words)

A condensed, scannable statement of everything the module established, with the load-bearing
facts in bold. Written as a lookup for someone who read the chapter and wants the facts back —
never as a self-test.

### 3.6 Footer

`← [<Topic> knowledge graph](00_knowledge_graph.md) · [repo index](../README.md)`

---

## 4. Prose rules

Complete sentences everywhere. Never fragment bullets, arrow chains (`A → B → fails`), or
"Skeleton:" outlines. Bullets and tables carry genuinely enumerable facts only, with the
reasoning in the surrounding prose.

Register: a good technical book — patient, concrete, precise, unhurried.

Write about the subject, not about the reader. No second-person challenges, no "you probably
think", no "most people get this wrong".

---

## 5. Before a module is marked written

1. **Word count** is 6,000–8,000.
2. **Five sections**, in the §3 order, with the §3.5 reference summary present.
3. **Attribution.** Every quantitative claim names its source in the same sentence, per §6.
   Nothing is presented as a reading taken off a machine.
4. **Code progression.** §3.2 starts with a minimal example and builds. No module opens with its
   most complex listing.
5. **Diagrams present where earned**, and every one survives the delete test.
6. **Nothing asks the reader to run anything.** No setup steps, no environment prerequisites, no
   "try this", no toolchain or service the chapter depends on.
7. **Rejected alternatives.** §3.4 names at least two, with costs.
8. **The noun-swap test.** No paragraph survives having its subject swapped for a different
   technology. Generic filler does survive it — *"indexes improve read performance at the cost of
   write performance"* works for Postgres, MongoDB and MySQL, which is why it is worthless.
   Specific writing names a version, a default, a constant, or an attributed figure.
9. **No practice material**, per §2, and no retired section titles.
10. The node's `**Article:**` line in its subject's `00_knowledge_graph.md` now points at the
    module. Never add that line speculatively.

`_tools/style_check.py` and `_tools/check_links.py` remain available and are advisory. Neither is
a gate: a chapter is finished when it passes the ten checks above.

---

## 6. Sourcing: where a claim is allowed to come from

The rule this folder used to enforce was that a number had to come out of a terminal on a named
machine. That rule was written to stop an author inventing figures, and the worry behind it is
sound — an early module quoted vendor query plans and genuinely computed sizes side by side, and
on the page the two were indistinguishable. What it got wrong was the remedy. It made a
reference text conditional on a working environment, and it left six subjects unwritable because
a daemon was not running.

**The remedy is attribution instead.** Every claim a reader could reasonably doubt names where
it came from, in the sentence that makes it:

- A book and chapter — *"Ramalho's chapter 3 measures the resize threshold at two-thirds load."*
- A PEP, RFC, or language specification, by number — *"PEP 659 describes the specialising
  interpreter's quickening step."*
- A release note or changelog, by version — *"Go 1.22 changed the loop variable to be
  per-iteration."*
- Vendor or project documentation, named — *"SQLAlchemy's own 2.0 migration guide documents
  `Query.get()` as legacy."*

**A claim with no attributable source does not go in.** This applies hardest to numbers, because
a number reads as authoritative whether or not it has anything behind it. If the fact matters
and no source states it, write the mechanism without the figure: *"the dictionary is resized
once it passes a load threshold"* is honest and useful, and an invented percentage is neither.

What needs no attribution is what the code on the page shows directly — that `__getattribute__`
runs before `__getattr__`, that a generator suspends at `yield` — because the reader can see it
in the listing. The line falls where a reader would have to take the author's word for it.

Figures in the eleven pre-spec modules trace to [`MEASUREMENTS.md`](../MEASUREMENTS.md), a closed
archive. Its rows are citable as sources like any other documentation, by ID and with their
environment named, per [`MEASUREMENT_SPEC.md`](MEASUREMENT_SPEC.md). Nothing new is added to it.

---

## 7. Before writing at all

Check the target node's `Currency` tag and `Δ current` line in its subject's
`00_knowledge_graph.md`. A `stale-major` or `absent` node means the source books cannot carry
the module alone — the `Δ current` line already names what to lead with instead, along with the
PEPs, RFCs and release notes that carry the correction, and was written for exactly this purpose.

← [writing contract](../AGENTS.md) · [graph spec](KG_SPEC.md) · [measurement archive](MEASUREMENT_SPEC.md)
