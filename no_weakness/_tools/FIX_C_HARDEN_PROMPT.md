You are closing a defect loop in a textbook repository at
`/Users/ad0791/Desktop/theCrest/interviewprep/no_weakness/`.

Read `AGENTS.md` and `_tools/MODULE_SPEC.md` first. Three tasks, in this order — the checker in
Task 1 is what verifies Tasks 2 and 3.

## Why this pass exists

Twenty chapters were written into `05_python/` against `_tools/WRITE_MODULE_PROMPT.md`, and every
one of them carried the same two defects.

The first: each chapter emitted a `## 3. Diagrams` heading whose whole body was one sentence
saying the diagrams were integrated into section 2. The brief said, in bold, that diagrams are
never a section of their own — and then numbered them as one of "six sections, in this order".
The numbering won. `MODULE_SPEC.md` §3 has since been corrected to five canonical headings;
**`WRITE_MODULE_PROMPT.md` has not, and still contains the contradiction verbatim at the
"Structure — six sections, in this order" heading.** Pointed at a new subject today it would
reproduce the bug in every chapter.

The second: every chapter came in under the word floor, because the brief gave bare ranges with
no midpoint rule and no counting step, and because the section minimums sum to 5,600 — below the
6,000-word floor — so a writer hitting every minimum still fails.

Neither defect was caught, because nothing checks a written module mechanically. The graph layer
has had `_tools/validate_kg.py` since it was built, and `AGENTS.md` §0 says a graph that fails it
is not finished. The module layer has no counterpart: `_tools/style_check.py` looks at sentence
length and banned phrases only, never at headings or word counts. That is the hole to close.

## Task 1 — build `_tools/check_module.py`

A mechanical conformance checker for written modules — the module layer's counterpart to
`_tools/validate_kg.py`. **Read `validate_kg.py` first and follow its shape:** `ROOT`-relative
pathing off `Path(__file__).resolve().parent.parent`, module-level compiled regexes and constant
sets, a separated errors/warnings list, a summary table, and `sys.exit(main())` returning 1 when
any error is present. Standard library only.

It accepts either a subject directory (`05_python/`) or a single module file, and skips
`00_knowledge_graph.md` and anything not matching `NN_name.md`.

**Word counting excludes fenced code blocks and Mermaid blocks.** Put that in a comment: counting
them is what made the existing prose look longer than it reads, and it is the reason the
shortfall went unnoticed.

Checks, all errors unless marked otherwise:

| Check | Fails when |
|---|---|
| Headings | the H2s are not exactly `## 1. The problem this solves`, `## 2. The mechanism, built up`, `## 3. Failure modes`, `## 4. Trade-offs`, `## 5. Reference summary`, in that order |
| Retired titles | any H2 or H3 matching "the questions you cannot answer", "Interview angles", "The thing you already do", "Break it on purpose", "The judgment call", or a bare "Diagrams" H2; or any mention of `RECALL.md` |
| Front matter | `**Covers:**` or `**Sources:**` missing; `**Covers:**` not naming IDs matching `^[A-Z]{2,5}-\d{2}$`; any `**Syllabus:**`, `**Measurement:**` or `**Roles:**` line present |
| Total words | outside 6,000–8,000 |
| Section words | any section below its `MODULE_SPEC.md` §3 minimum: 400 / 2,500 / 1,500 / 900 / 300 |
| Failure modes | section 3 has fewer than 3 or more than 5 `###` subsections |
| Diagrams | zero Mermaid blocks — **warning**, since a rare subject may genuinely need none |
| Article wiring | a node ID on the `**Covers:**` line has no `**Article:**` line in the subject's `00_knowledge_graph.md` pointing back at this file |
| Practice material | "rate yourself", "say this out loud", "flashcard", "test yourself", "spaced repetition" |
| Setup instructions | "run this and see", "try it yourself", "install it first", "on your machine" — **warnings**, because a chapter on packaging or deployment legitimately discusses `pip install` as its subject |

Print a table of module, total words, per-section words and heading count, then the warnings,
then the errors, then `OK · N module(s) checked, 0 errors` or `FAILED · N module(s) checked`.

Then add one sentence to `MODULE_SPEC.md` §5: a module that fails `check_module.py` is not
finished — mirroring what `AGENTS.md` §0 already says about `validate_kg.py` and the graph layer.

## Task 2 — fix the standing brief

In `_tools/WRITE_MODULE_PROMPT.md`:

1. Replace "Structure — six sections, in this order" with the five canonical headings quoted
   verbatim, and fold the diagram rules into the section-2 entry as an unnumbered paragraph
   ("Diagrams belong inside this section"), keeping the delete test, the permitted-diagram list,
   the two-to-four guidance and the bans intact. Renumber the entries that follow. **Copy the
   resolution already applied in `MODULE_SPEC.md` §3 rather than inventing a second one** — two
   differing accounts of the same structure is how this defect started.
2. Replace the bare word ranges with a target table carrying the **midpoints**:

       1. The problem this solves    ~550
       2. The mechanism, built up  ~3,000
       3. Failure modes            ~1,850
       4. Trade-offs               ~1,100
       5. Reference summary          ~400

   State why: the minimums sum to 5,600, below the 6,000 floor, so writing every section to its
   minimum still fails. The midpoints sum to ~6,900.
3. In the failure-modes entry, add that each mode runs roughly 450 words and carries all four
   required elements — reproduction, the error, the prose explanation naming the section-2
   subsection that predicted it, and the fix with its cost. Say plainly that a mode under 300
   words is missing at least one, and that in practice the two that go missing are the
   back-reference and the cost.
4. Add to "Before you finish": run `uv run python _tools/check_module.py <file>` and fix
   everything it reports. Nothing is finished while it reports an error.
5. Add a **subject-completion step**, distinct from the per-chapter one. Per chapter, only the
   node's `**Article:**` line changes. When the *last* chapter of a subject lands, also update
   `AGENTS.md` §9's table, `README.md`'s status section, and `KNOWLEDGE_GRAPH.md`'s header
   counts. The absence of this step is why those records are now wrong.

## Task 3 — correct the status records

`AGENTS.md` §9, `README.md`'s status section and `KNOWLEDGE_GRAPH.md`'s header all describe a
repository that no longer exists. **Recompute every figure from the files rather than trusting
the numbers below** — they are what the review found, and they are what you should land on:

- **28 modules are written, not 11:** `05_python` 20, `06_concurrency` 4, `07_javascript` 1,
  `08_typescript` 1, `09_sql` 2.
- **32 of 482 nodes carry an `**Article:**` line**, so 450 do not — not the 471 currently
  claimed. The node count exceeds the module count because four Python chapters cover two nodes
  each.
- **`05_python/` is complete**, 24 of 24 nodes — the first finished subject in the repository.
  `AGENTS.md` §9's table currently lists it as "01, 03, 05" written with "21 nodes with no
  module". Mark it complete.
- **The pre-spec debt is 8 modules, not 11, and none of them is Python.** Three of the original
  eleven were Python chapters and have been rewritten. Name the remaining eight explicitly:
  `06_concurrency` 01–04, `07_javascript/03`, `08_typescript/02`, `09_sql` 01 and 04. **Do not
  rewrite them in this pass** — record them accurately and leave them queued.
- Say plainly that 19 of Python's 20 chapters are still below the word floor pending a deepening
  pass, so the completeness claim stays honest about what is owed.

Edit the prose of the graph files only. Do not touch node records, edges, or currency tags.

## Verify before finishing

- `uv run python _tools/check_module.py 05_python/` runs, reports chapter 01 clean, and reports
  the other 19 failing on total and section word counts. **A checker that passes all 20 today is
  not working** — 19 of them are genuinely short, and that is the fixture proving it detects.
- Pointed at `06_concurrency/`, `07_javascript/`, `08_typescript/` and `09_sql/`, it flags
  exactly the 8 pre-spec modules. That independently confirms the count in Task 3.
- `grep -n "six sections" _tools/WRITE_MODULE_PROMPT.md` returns nothing.
- `grep -rn "11 modules\|471 of the 482" AGENTS.md README.md KNOWLEDGE_GRAPH.md` returns nothing.
- `uv run python _tools/validate_kg.py` still reports 482 nodes and 0 errors. Task 3 rewrites
  prose in graph files and must not disturb their structure.

Report what you changed, and paste the `check_module.py` summary table for `05_python/` so the
19 outstanding chapters are visible as a work list.
