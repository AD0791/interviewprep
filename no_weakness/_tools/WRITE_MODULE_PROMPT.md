# WRITE_MODULE_PROMPT — the standing brief for a module-writing session

Everything below the line is the prompt. Copy it whole into a fresh session, edit only the
`TARGET` block, and send it. One module per session.

The Python writing order is in §2 of this file, below the prompt — it doubles as the reading
order, and it is derived from `05_python/00_knowledge_graph.md`'s `requires` edges rather than
chosen by hand.

---

## 1. The prompt

You are writing one chapter of a programming textbook that lives in
`/Users/ad0791/Desktop/theCrest/interviewprep/no_weakness/`.

### TARGET — the only block that changes between sessions

```
Subject directory: 05_python/
Output file:       01_object_model_and_attribute_lookup.md
Covers nodes:      PY-01
Kind:              REWRITE          # REWRITE | NEW
```

### Read first, in this order

1. `no_weakness/AGENTS.md` — the principles behind everything below.
2. `no_weakness/_tools/MODULE_SPEC.md` — the binding format. Follow it exactly; where it is more
   specific than this prompt, it wins.
3. The target subject's `00_knowledge_graph.md`: the source audit in §1, and the §4 node record
   for every node named in `Covers`. That record is your brief. Its `Covers:` line is the
   outline, its `Sources:` line is the bibliography, and if it carries a `Δ current` line, that
   line names what the books get wrong and what is true now — **lead with the correction, not
   the book**, and cite the PEP, RFC, release note or vendor document it points at.
4. If `Kind: REWRITE`, the existing output file in full.

Do not read the other subjects' graph files unless a `Covers` node declares a cross-subject edge
you need.

### What this book is

A textbook for an experienced engineer who wants to understand a mechanism properly — the object
model, the query planner, the event loop, the collector. It is read, not performed. The measure
of a chapter is whether someone who reads it understands the mechanism afterwards.

### Absolute prohibitions

- **No practice material.** No quizzes, diagnostics, drills, flashcards, self-ratings, "say this
  aloud", spaced repetition, "test yourself before reading on".
- **No rhetorical quiz openings.** Never "can you answer this?", never a section titled *the
  questions you cannot answer about it*, never "if you can explain all four, skip ahead".
- **No `## Interview angles` section.** No résumé, employer, interview or date framing anywhere.
  The organising principle is the subject.
- **Nothing asks the reader to install, configure, run, benchmark, or set anything up.** No "try
  this", no "run it and see", no environment prerequisites, no containers, no toolchain, no
  version to install first. The reader has a book, not a terminal. Code on the page is exposition
  — it is there to be read and understood there.
- **No invented numbers.** Every timing, ratio, size, percentage or count is attributed in the
  sentence to a named source: a book and chapter, a PEP or RFC by number, a release note by
  version, or named vendor documentation. A figure you cannot attribute does not go in — write
  the mechanism without it, which is honest and still useful.
- **No fabricated terminal output.** Never compose a plausible-looking traceback, never write
  "would print approximately".
- **No fragment bullets, no arrow chains (`A → B → fails`), no "Skeleton:" outlines.** Complete
  sentences everywhere. Bullets and tables carry genuinely enumerable facts only, with the
  reasoning in the surrounding prose.
- **Write about the subject, not the reader.** No "you probably think", no "most people get this
  wrong", no second-person challenges.

### Structure — five sections, in this order

The written module's own headings are exactly these five, and only these five:

    ## 1. The problem this solves
    ## 2. The mechanism, built up
    ## 3. Failure modes
    ## 4. Trade-offs
    ## 5. Reference summary

**The section minimums sum to 5,600 words, short of the 6,000-word floor** — a chapter that hits
every minimum exactly still fails the total. Target the **midpoint** of each section's range, not
its minimum:

    1. The problem this solves    ~550
    2. The mechanism, built up  ~3,000
    3. Failure modes            ~1,850
    4. Trade-offs               ~1,100
    5. Reference summary          ~400

The midpoints sum to ~6,900, comfortably inside the 6,000–8,000 band.

**Front matter (~120 words).** The title, a one-line italic subtitle, then:

```
**Level:** L4 · **Prerequisites:** [<link to the prerequisite module, or "none">]
**Covers:** PY-01
**Sources:** Ramalho, *Fluent Python* 2nd ed. ch.11, 13, 22–24 (2022) · PEP 695 (2023)
```

Use `**Covers:**`, never `**Syllabus:**`. Never write a `**Measurement:**` line or a
`**Roles:**` line; both belong to a superseded version of this folder.

**1. The problem this solves.** Open with the engineering situation the subject exists to
address, concretely and in code — what goes wrong without this mechanism, or what question it
answers. Never open with a definition. Never open by asking the reader what they know.

**2. The mechanism, built up.** The core of the chapter, and the thing drafts most often get
wrong. Start with the smallest complete example — five to ten lines, one idea — and say what it
produces. Then extend it one dimension at a time, each step adding exactly one concept, so the
reader follows the whole chain without a leap. End with the shape the thing takes in production
code, with the complications that implies. **Never present the complex form first and decompose
it.** The explanation lives in the paragraphs between the code blocks; comments annotate, they do
not teach. Trace one concrete execution through the machine in plain words at least once.

Diagrams belong inside this section. Where a paragraph would be harder to visualise than a
picture, draw the picture; this is a requirement, not a permission. Mermaid `graph`,
`sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, or a fenced ASCII block where byte-level layout
matters. Two to four per chapter is normal, more when the subject is structural. Draw when there
is a shape, an ordering or interleave, a lifecycle, a topology, or a memory layout. Apply the
delete test: remove the diagram and reread the paragraph — if the paragraph is fine alone, the
diagram was decoration. Never draw a diagram that restates a bulleted list, never draw generic
architecture boxes, never go past about fifteen nodes.

**3. Failure modes.** Three to five ways the mechanism breaks. Each carries a minimal reproduction
labelled `# Gist: name.py`, the error it produces, a prose explanation naming the section-2
subsection that predicted it, and the fix with its cost stated — all four elements, every time.
Each mode runs roughly 450 words; that is what four elements written out in full prose actually
takes. A mode that comes in under 300 words is missing at least one of the four, and in practice
the two that go missing are the back-reference to section 2 and the fix's cost.

You may quote an exception type and message that the language or library *defines* and that does
not vary between runs — `TypeError: unhashable type: 'list'`,
`RuntimeError: dictionary changed size during iteration`. That is documented surface. You may not
quote anything that varies with the machine: timings, ratios, memory figures, row counts,
addresses, thread interleavings. A nondeterministic failure is described as nondeterministic —
what makes it fire, what makes it hide, and why that is the hard part.

**4. Trade-offs.** A table with fixed columns — **Use when · Because · Real cost** — where the
cost column is never empty. Then prose subsections, one of which is always the case *against*:
when you would not use this, and what you would use instead. Name at least two rejected
alternatives with their costs.

**5. Reference summary.** A condensed, scannable statement of everything the chapter established,
with the load-bearing facts in bold. Written as a lookup for someone who read it and wants the
facts back. Never a self-test.

**Footer.** `← [<Subject> knowledge graph](00_knowledge_graph.md) · [repo index](../README.md)`

### If Kind is REWRITE

The existing file uses a superseded seven-section skeleton: *1. The thing you already do* ·
*2. The questions you cannot answer about it* · *3. What the machine actually does* · *4. Break
it on purpose* · *5. The judgment call* · *6. Interview angles* · *7. To add to `RECALL.md`*.
Sections 2, 6 and 7 are banned outright, and `RECALL.md` no longer exists.

Treat it as a rewrite, not a revision. Salvage the explanation rather than the shape: fold
anything genuinely explanatory out of the interview-angles section into section 2 or section 4
instead of deleting it. Carry the existing code and diagrams across where they still fit, and
reorder them simple-to-complex if they do not. Replace the `**Measurement:**` front-matter line
with a `**Sources:**` line, replace `**Syllabus:**` with `**Covers:**`, and delete any
`**Roles:**` line.

Any figure the old text quotes bare comes out unless it can be attributed — either to a source,
or to a `MEASUREMENTS.md` row cited by its ID with the environment named in the same sentence,
which is what that closed archive is now for.

Expect to add roughly 3,000 words. The old skeleton asked for neither the built-up code
progression nor the reference summary, so the gap is those two things and not padding.

### Before you finish

1. Word count is 6,000–8,000.
2. Five sections in order, with the reference summary present.
3. Section 2 opens with the smallest example and builds. No chapter opens with its most complex
   listing.
4. Every quantitative claim names its source in the same sentence.
5. Diagrams present where earned, each surviving the delete test.
6. Nothing asks the reader to run, install or set up anything.
7. At least two rejected alternatives in section 4, with costs.
8. **The noun-swap test.** No paragraph survives having its subject swapped for a different
   technology. *"Indexes improve read performance at the cost of write performance"* is true of
   Postgres, MongoDB and MySQL, which is exactly why it is worthless. Specific writing names a
   version, a default, a constant, or an attributed figure.
9. No practice material and no retired section titles.
10. Add the `**Article:**` line to the node's record in the subject's `00_knowledge_graph.md`,
    pointing at the file. Never add it speculatively.
11. Run `uv run python _tools/check_module.py <file>` and fix everything it reports. Nothing is
    finished while it reports an error.

Write the whole chapter in one pass. Do not ask which section to start with, and do not stop to
confirm the outline.

### When a subject's last chapter lands

The step above is per chapter: only the node's `**Article:**` line changes. When the chapter you
just finished is the *last* one for its subject — every node that is getting a module now has
one — also update the three records that describe the subject as a whole, in the same session:
`AGENTS.md` §9's table, `README.md`'s status section, and `KNOWLEDGE_GRAPH.md`'s header counts.
Skipping this step is why those three records drifted out of date in the first place: chapters
kept landing and nothing ever went back to update the subject-level tally.

---

## 2. The Python writing order

Python is the entry point: a root subject with no prerequisite, holding three of the eleven
pre-spec modules, and the subject every Python-adjacent node elsewhere assumes. `06_concurrency`
follows it, being the only subject that declares `requires 05`.

**The ordering rule.** Walk the subject's `requires` DAG from the root. A node that already
carries an `**Article:**` line is a `REWRITE`; a node without one is `NEW`. Rewrites take their
DAG position rather than being batched — which puts `PY-01` first, so the first chapter doubles
as the exemplar the rest are written against.

The 24 Python nodes group into 20 chapters. Reading order and writing order are the same list.

| # | Output file | Covers | Kind | Note |
|---|---|---|---|---|
| 01 | `01_object_model_and_attribute_lookup.md` | `PY-01` | REWRITE | DAG root; the exemplar |
| 02 | `02_the_special_method_protocol.md` | `PY-02`, `PY-13` | NEW | dunders and callables are one subject |
| 03 | `03_closures_decorators_and_metaprogramming.md` | `PY-03` | REWRITE | |
| 04 | `04_memory_management_and_the_cyclic_collector.md` | `PY-04` | NEW | `stale-minor` — flag the free-threaded divergence |
| 05 | `05_bytecode_and_the_runtime.md` | `PY-05` | REWRITE | |
| 06 | `06_sequences_dicts_and_sets.md` | `PY-09`, `PY-10` | NEW | a declared `contrasts` pair; one chapter |
| 07 | `07_iterators_generators_and_lazy_evaluation.md` | `PY-07` | NEW | |
| 08 | `08_the_import_system_and_packaging.md` | `PY-08` | NEW | |
| 09 | `09_the_gradual_type_system.md` | `PY-06` | NEW | `stale-minor` — lead with PEP 695 syntax |
| 10 | `10_data_classes_and_pattern_matching.md` | `PY-12`, `PY-20` | NEW | `PY-20` `refines` `PY-12` |
| 11 | `11_text_bytes_and_object_persistence.md` | `PY-11`, `PY-22` | NEW | |
| 12 | `12_the_ast_as_a_program_analysis_surface.md` | `PY-23` | NEW | |
| 13 | `13_building_an_interpreter_and_a_virtual_machine.md` | `PY-21` | NEW | |
| 14 | `14_tracing_a_running_program.md` | `PY-24` | NEW | `stale-major` — lead with `sys.monitoring` (PEP 669) |
| 15 | `15_asgi_request_handling_and_dependency_injection.md` | `PY-14` | NEW | `stale-minor` — `lifespan` only |
| 16 | `16_pydantic_validation.md` | `PY-15` | NEW | `stale-major` — v2 only, v1 as migration source |
| 17 | `17_async_database_access_with_sqlalchemy.md` | `PY-16` | NEW | `stale-major` — 2.0 style only |
| 18 | `18_authentication_and_authorization.md` | `PY-17` | NEW | `stale-minor` — password grant as legacy only |
| 19 | `19_microservice_decomposition.md` | `PY-18` | NEW | |
| 20 | `20_testing_and_deploying_a_python_service.md` | `PY-19` | NEW | `stale-minor` |

Chapters 01–14 are the language itself. Chapters 15–20 are the web-service layer and sit on
`CONC-04`, which is already written.

Six of the twenty carry a `stale-minor` or `stale-major` currency tag, and each of those has a
`Δ current` line in `05_python/00_knowledge_graph.md` §4 naming what to teach instead of the
book, with the PEP or vendor document that carries the correction. That line is the research
already done; no further source-hunting is needed.

← [writing contract](../AGENTS.md) · [module spec](MODULE_SPEC.md) · [graph spec](KG_SPEC.md)
