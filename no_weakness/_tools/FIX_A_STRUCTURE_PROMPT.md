You are correcting a specification defect and its consequences in a textbook repository at
`/Users/ad0791/Desktop/theCrest/interviewprep/no_weakness/`.

Read `AGENTS.md` and `_tools/MODULE_SPEC.md` first. This is a mechanical correction pass: do not
rewrite prose, do not add or remove content, do not touch any Mermaid diagram.

## The defect

`_tools/MODULE_SPEC.md` §3 says "six sections" and numbers six items §3.1–§3.6, one of which is
Diagrams — while §3.3's own title says "Diagrams — integrated into §3.2, never a section of
their own". Both cannot be true. Every chapter in `05_python/` resolved it by emitting a
`## 3. Diagrams` heading with a one-sentence body saying the diagrams are integrated into
section 2. `AGENTS.md` §3 carries the same off-by-one: it says "six sections", then lists five.

## Task 1 — settle the spec at five body sections

In `_tools/MODULE_SPEC.md` §3, open the section with the canonical headings, verbatim, so the
count can never again be inferred from the sub-numbering:

    ## 1. The problem this solves
    ## 2. The mechanism, built up
    ## 3. Failure modes
    ## 4. Trade-offs
    ## 5. Reference summary

State that front matter and footer are not sections and carry no heading.

Fold the diagram rules into §3.2 as an unnumbered subsection — "Diagrams belong inside this
section" — keeping the delete test, the permitted-diagram list, the two-to-four guidance and the
bans intact. Then renumber: §3.4→§3.3, §3.5→§3.4, §3.6→§3.5, §3.7→§3.6.

Add the budget arithmetic as a short paragraph, because it is why the floor was unreachable: the
section minimums sum to 5,600, below the 6,000-word floor, so a section targets the **midpoint**
of its range rather than its minimum. The midpoints — 550, 3,000, 1,850, 1,100, 400 — sum to
6,900, comfortably inside the 6,000–8,000 band.

In `AGENTS.md`: change "six sections" to "five sections" in §3 (its own enumeration already lists
five), and update the reference to `MODULE_SPEC.md` §3.6 near line 266 to §3.5.

## Task 2 — restructure the twenty chapters

For every file matching `05_python/[0-2][0-9]_*.md`:

1. Delete the `## 3. Diagrams` heading, its one-sentence body, and the `---` rule that follows
   it. **The diagrams stay exactly where they are, inside section 2.** Verify the Mermaid count
   per file is unchanged when you are done.
2. Renumber the headings that follow: `## 4.` → `## 3.`, `## 5.` → `## 4.`, `## 6.` → `## 5.`
3. Fix internal cross-references that name a section by bare number — roughly 48 of them, e.g.
   "as section 4 shows" must become "as section 3 shows". Seventeen of the twenty files have at
   least one.

**Two things that look identical and must NOT be touched:**

- Subsection references of the form `section 2.5` — about 150 of them. Section 2 is not
  renumbered, so these are all still correct.
- Book citations in the `**Sources:**` front-matter line. `Beazley, *Advanced Python Mastery*
  §3–4` is a page reference to a book, not a section of the chapter.

## Task 3 — clear five measurement-era directives

The repository recently replaced its measurement rule with an attribution rule
(`MODULE_SPEC.md` §6): a claim names its source in the sentence that makes it, and nothing
instructs anyone to run, install or measure anything. Five lines in knowledge-graph files still
carry the old framing. Rewrite each to say what an article should **teach and cite** rather than
what it should measure, preserving the technical content:

- `05_python/00_knowledge_graph.md:141` (`PY-05`) — "The written article on this node already
  measures CPython 3.14.6 directly rather than leaning on a book". Also now factually wrong: the
  chapter was rewritten. Replace with what the article should cite for the 3.11+ specialising
  interpreter and the 3.14 JIT — PEP 659 and PEP 744.
- `06_concurrency/00_knowledge_graph.md:90` (`CONC-01`) — "The written article on this node
  measures the GIL-enabled default build".
- `24_golang/00_knowledge_graph.md:240` — "An article should use the modern `unsafe` helpers and
  measure cgo overhead on the machine rather than quoting a book." This now inverts the rule;
  the Go 1.26 release-note figure already in that same line is the correct source to lean on.
- `07_javascript/00_knowledge_graph.md:294` — "the measurement plan for `JS-14` is
  straightforward: grow a deliberate leak, diff two snapshots, and…".
- `12_bigquery/00_knowledge_graph.md:278` — "that measurement path remains open for whoever
  writes the…".

**Leave alone everything that merely looks similar:** nodes whose subject *is* benchmarking
(`GO-15`, `PY-24`), book descriptions noting that a book benchmarks something (`10_mongodb` on
MMAPv1, Oaks on JVM tuning), and attributed third-party figures (`08_typescript`'s TypeScript
7.0 numbers, `18_eventbus`'s explicitly-flagged vendor benchmarks). That last one is a model of
the attribution rule working correctly.

## Verify before finishing

- `grep -c "^## " 05_python/[0-2][0-9]_*.md` returns 5 for every chapter.
- `grep -l "## 3. Diagrams" 05_python/*.md` returns nothing.
- Mermaid counts per chapter are unchanged from before your edits (2–3 each, 1 in
  `06_sequences_dicts_and_sets.md`).
- Every remaining `section N` reference points at a section that exists under the new numbering,
  and no `**Sources:**` line was modified.
- `uv run python _tools/check_links.py` shows no new breakage. Three footer-template hits are
  known false positives and predate this work.

Report what you changed. Do not deepen or rewrite any prose — that is a separate pass.
