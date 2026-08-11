You are deepening one chapter of a programming textbook at
`/Users/ad0791/Desktop/theCrest/interviewprep/no_weakness/05_python/`.

## TARGET — the only block that changes between sessions

    Chapter: 01_object_model_and_attribute_lookup.md

## Read first

1. `no_weakness/AGENTS.md` — the principles.
2. `no_weakness/_tools/MODULE_SPEC.md` — the binding format, especially §3 (section budgets) and
   §6 (attribution). Follow it exactly.
3. The chapter itself, in full.
4. The `§4` node record in `05_python/00_knowledge_graph.md` for the node(s) named on the
   chapter's `**Covers:**` line — that is its brief and bibliography.

## What is wrong and what is not

The chapter's structure is correct and must not change. It has the right five sections, its
diagrams are correctly placed inside section 2, its front matter is right, and its failure-mode
and trade-off skeletons are complete — three to five failure modes, two to four trade-off
subsections, a table with the cost column.

**The prose inside three sections is compressed below the spec's own budgets.** Across all
twenty chapters, section 3 averages ~1,030 words against a 1,500 minimum and section 4 averages
~730 against 900. This is the only thing you are fixing.

## Targets

Bring each section to the **midpoint** of its `MODULE_SPEC.md` §3 range:

| Section | Target |
|---|---|
| 1. The problem this solves | ~550 |
| 2. The mechanism, built up | ~3,000 |
| 3. Failure modes | ~1,850 |
| 4. Trade-offs | ~1,100 |
| 5. Reference summary | ~400 |

Total lands near 6,900, inside the 6,000–8,000 band. A section already at or above its target is
left alone — do not pad a section that is already right.

## What to add

**In section 3, failure modes.** Each mode must carry four things: a minimal reproduction
labelled `# Gist: name.py`, the error it produces, a prose explanation **referring back to the
section-2 subsection that predicted it**, and the fix **with its cost stated**. At roughly 250
words per mode today, most carry the first two and then stop. The last two are almost always
what is missing. Do not add new failure modes unless the chapter has fewer than three — deepen
the ones already there.

**In section 4, trade-offs.** The spec requires prose subsections after the table, one of which
is always the case *against* — when you would not use this, and what you would use instead — and
at least two rejected alternatives named with their costs. That is usually where the words are
missing.

**In section 2, only where it is under 2,500.** Extend the existing simple-to-complex
progression by one step, or narrate an existing step more fully. Never restructure it, never
reorder the listings, and never lead with a more complex form than the chapter already opens
with.

## Hard constraints

- **Attribution governs every sentence you add**, exactly as it governs the existing ones. A
  timing, ratio, size or percentage names its source — a book and chapter, a PEP or RFC by
  number, a release note by version, or named vendor documentation — or it does not go in.
  Never invent a figure and never compose a traceback. You may quote an exception the language
  or library defines and that does not vary between runs.
- **Nothing instructs the reader to install, configure, run or benchmark anything.** Code on the
  page is exposition, read and understood there.
- **No practice material, no `## Interview angles`, no résumé or interview framing, no
  second-person challenges.**
- **No fragment bullets, no arrow chains, no "Skeleton:" outlines.** Complete sentences; bullets
  and tables only for genuinely enumerable facts.
- **Do not add, remove or move a Mermaid diagram.** The count must be unchanged.
- **Do not change the front matter, the headings, or the section order.**

## Before you finish

1. Total word count is 6,000–8,000, and no section sits below its `MODULE_SPEC.md` §3 minimum.
2. Every quantitative claim you added names its source in the same sentence.
3. Every failure mode names the section-2 subsection that predicted it and states the fix's cost.
4. Section 4 names at least two rejected alternatives with costs and contains the case against.
5. The Mermaid count is identical to what you started with.
6. **The noun-swap test** on every paragraph you added: it must not survive having its subject
   swapped for a different technology. "Indexes improve read performance at the cost of write
   performance" is true of Postgres, MongoDB and MySQL, which is exactly why it is worthless.

Work in one pass. Do not ask which section to start with.
