# MODULE_SPEC — how to write a module

This is the binding format for every written module in `no_weakness/` — the textbook chapters
themselves, as distinct from the `00_knowledge_graph.md` index files governed by
[`KG_SPEC.md`](KG_SPEC.md). `AGENTS.md` states the principles; this file states the format.
Where the two appear to differ, this file is the operative one for module shape and `AGENTS.md`
for the reasons behind it.

Measurement rules live in [`MEASUREMENT_SPEC.md`](MEASUREMENT_SPEC.md) and are binding here too:
a module that quotes an untagged figure is not finished.

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

What replaces all of it is the **reference summary** in §3.6 — a condensed statement of the
module's facts, written to be looked up, not to be quizzed on.

Two section titles are permanently retired because they encode the banned framing: any heading
of the form *"the questions you cannot answer about it"*, and any *"Interview angles"* section.
Modules that still carry them predate this spec and are listed in `AGENTS.md` §9 as revision
debt.

---

## 3. The structure

Every module follows this, in order.

### 3.0 Front matter (~120 words)

```markdown
# The GIL — what it protects, and when it lets go

*Reference counts, bytecode boundaries, and the five milliseconds nobody mentions.*

**Level:** L4 · **Prerequisites:** [05_python/05 bytecode](../05_python/05_bytecode_and_the_runtime.md)
**Covers:** CONC-01 … CONC-07
**Measurement:** Measured — CPython 3.14.6, 8 cores, macOS 26.5. Every number below
came out of a terminal.
```

`Covers:` names knowledge-graph node IDs. The `Measurement:` line is mandatory and carries
exactly one tag from `MEASUREMENT_SPEC.md` §2.

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

### 3.3 Diagrams — integrated into §3.2, never a section of their own

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

### 3.4 Failure modes (1,500–2,200 words)

Three to five ways the mechanism breaks. Each one carries a minimal runnable reproduction named
`# Gist: name.py`, its **verbatim terminal output** in a fenced block, a prose explanation
referring back to the §3.2 subsection that predicted it, and the fix with its cost stated.

Terminal output is copy-pasted, never composed by hand, and never approximated.

Failures that could not be reproduced are **reported as negative results**, not invented. A
nondeterministic failure honestly described is more useful than a fabricated one, and this
folder already has two good examples of exactly that.

### 3.5 Trade-offs (900–1,300 words)

An options table with fixed columns — **Use when · Because · Real cost** — where the cost column
is not optional. Then prose subsections, one of which is always the case *against*: when you
would not use this, and what you would use instead.

### 3.6 Reference summary (300–500 words)

A condensed, scannable statement of everything the module established, with measured figures in
bold. Written as a lookup for someone who read the chapter and wants the facts back — never as a
self-test.

### 3.7 Footer

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
2. **Six sections**, in the §3 order, with the §3.6 reference summary present.
3. **Verbatim output.** Every failure mode shows real terminal output — zero hand-composed, zero
   "would print approximately".
4. **Code progression.** §3.2 starts with a minimal runnable example and builds. No module opens
   with its most complex listing.
5. **Diagrams present where earned**, and every one survives the delete test.
6. **Measurement density.** At least three claims cite `MEASUREMENTS.md` IDs, and the front
   matter tag matches the weakest claim in the module.
7. **Rejected alternatives.** §3.5 names at least two, with costs.
8. **The noun-swap test.** No paragraph survives having its subject swapped for a different
   technology. Generic filler does survive it — *"indexes improve read performance at the cost of
   write performance"* works for Postgres, MongoDB and MySQL, which is why it is worthless.
   Specific writing names a version, a default, a constant, or a measured figure.
9. **No practice material**, per §2, and no retired section titles.
10. The node's `**Article:**` line in its subject's `00_knowledge_graph.md` now points at the
    module. Never add that line speculatively.

Then run, from `no_weakness/`:

```
uv run python _tools/style_check.py <module>.md
uv run python _tools/check_links.py
```

`style_check.py` is built for articles rather than graph files; its output is meaningful here in
a way it is not when pointed at a `00_knowledge_graph.md`.

---

## 6. Before writing at all

Check the target node's `Currency` tag and `Δ current` line in its subject's
`00_knowledge_graph.md`. A `stale-major` or `absent` node means the source books cannot carry
the module alone — the `Δ current` line already names what to lead with instead, and was written
for exactly this purpose.

← [writing contract](../AGENTS.md) · [graph spec](KG_SPEC.md) · [measurement spec](MEASUREMENT_SPEC.md)
