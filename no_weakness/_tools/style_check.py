#!/usr/bin/env python3
"""Flag generic-LLM prose patterns and rhythm tells in a written module.

Advisory, not a gate: style is judgment, and the checks here have real false
positives (a genuinely three-item list is not a tell). Read every flag; do
not chase the exit code to zero for its own sake.

Run:  uv run python _tools/style_check.py <module.md> [module2.md ...]
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Stock phrases and hedges that are symptoms of default LLM register,
# independent of which book a module draws its voice from. Grouped by what
# they're actually doing, since the fix differs by group.
# --------------------------------------------------------------------------

TRANSITIONAL_FILLER = [
    r"\bit'?s (?:important|worth) to (?:note|mention)\b",
    r"\bit(?:'s| is) worth (?:noting|mentioning)\b",
    r"\bnote that\b",
    r"\bat the end of the day\b",
    r"\bin today'?s (?:fast-paced |rapidly evolving |digital )?world\b",
    r"\blet'?s (?:dive|explore|take a look|unpack)\b",
    r"\bto summarize\b",
    r"\bin summary,",
    r"\bas we'?ve seen\b",
    r"\bas (?:mentioned|discussed) (?:earlier|above|previously)\b",
]

FILLER_VERBS_AND_ADJECTIVES = [
    r"\bleverage[sd]?\b",
    r"\bfoster(?:s|ing)?\b",
    r"\bunlock(?:s|ing)? (?:the |its )?(?:full )?potential\b",
    r"\bdelve[sd]?\b",
    r"\bnavigate the (?:complexit\w+)\b",
    r"\bin the realm of\b",
    r"\bholistic\b",
    r"\bseamless(?:ly)?\b",
    r"\brobust\b",
    r"\bpowerful\b",
    r"\bcutting-edge\b",
    r"\bstate-of-the-art\b",
    r"\belegant\b",
    r"\b(?:stands as|a) testament to\b",
]

HEDGE_STACKING = [
    r"\bcan (?:potentially|sometimes) \w+\b",
    r"\bmay (?:sometimes|potentially|often) \w+\b",
    r"\bit'?s generally considered\b",
    r"\bin many cases\b",
    r"\bessentially,",
    r"\bbasically,",
    r"\bsimply put,",
]

MANUFACTURED_BALANCE = [
    r"\bon (?:the )?one hand\b.{0,120}\bon the other hand\b",
]

STOCK_CONNECTIVES = [
    r"^(?:Moreover|Furthermore|Additionally),",
]

CHECKS = [
    ("transitional filler", TRANSITIONAL_FILLER),
    ("filler verbs/adjectives", FILLER_VERBS_AND_ADJECTIVES),
    ("hedge stacking", HEDGE_STACKING),
    ("manufactured on-one-hand balance", MANUFACTURED_BALANCE),
    ("stock paragraph-opening connective", STOCK_CONNECTIVES),
]

# A paragraph that opens with a bolded label and a colon, repeated down the
# page, is the listicle tic AGENTS.md already bans for bullets — this catches
# the prose version of the same habit. The module's own front matter
# (`**Level:** ... · **Prerequisites:** ...`, `**Measurement:** ...`) uses the
# same bold-label shape legitimately and by contract (AGENTS.md front-matter
# template) — skip everything before the first `## ` heading, where front
# matter always lives.
RE_BOLD_LABEL_OPEN = re.compile(r"^\*\*[A-Z][a-zA-Z0-9 /'-]{1,40}:\*\*\s")
RE_SECTION_HEADING = re.compile(r"^##\s")

RE_FENCE = re.compile(r"^\s*(```|~~~)")
RE_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'*`(])")


def strip_non_prose(text: str) -> str:
    """Drop fenced code/Mermaid blocks and Markdown tables — not prose."""
    out, in_fence = [], False
    for line in text.splitlines():
        if RE_FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or line.strip().startswith("|"):
            continue
        out.append(line)
    return "\n".join(out)


def sentence_lengths(prose: str) -> list[int]:
    flat = re.sub(r"\s+", " ", prose).strip()
    sentences = RE_SENTENCE_SPLIT.split(flat)
    lengths = []
    for s in sentences:
        words = [w for w in re.split(r"\s+", s.strip()) if w]
        if len(words) >= 3:  # drop headings/fragments that slipped through
            lengths.append(len(words))
    return lengths


def check_file(path: Path) -> int:
    if path.name == "00_knowledge_graph.md":
        print(f"\n=== {path} ===\n  SKIPPED — this is a graph index, not a written "
              f"module; its node records are legitimately bold-label-heavy by "
              f"KG_SPEC.md's own format. Point this tool at the article, not the graph.")
        return 0

    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    prose_lines = strip_non_prose(raw).splitlines()

    hits = 0
    print(f"\n=== {path} ===")

    for category, patterns in CHECKS:
        compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        for i, line in enumerate(lines, 1):
            if RE_FENCE.match(line):
                continue
            for pat in compiled:
                if pat.search(line):
                    hits += 1
                    print(f"  [{category}] line {i}: {line.strip()[:100]}")

    in_front_matter = True
    for i, line in enumerate(lines, 1):
        if RE_SECTION_HEADING.match(line):
            in_front_matter = False
        if not in_front_matter and RE_BOLD_LABEL_OPEN.match(line):
            hits += 1
            print(f"  [bold-label listicle tic] line {i}: {line.strip()[:100]}")

    prose = "\n".join(prose_lines)
    lens = sentence_lengths(prose)
    if len(lens) >= 8:
        mean = statistics.mean(lens)
        stdev = statistics.pstdev(lens)
        cv = stdev / mean if mean else 0
        flag = " <- suspiciously uniform, vary it" if cv < 0.35 else ""
        print(f"  [rhythm] {len(lens)} sentences, mean {mean:.1f} words, "
              f"stdev {stdev:.1f}, coefficient of variation {cv:.2f}{flag}")
    else:
        print("  [rhythm] too little prose to measure (< 8 sentences)")

    print(f"  {hits} phrase-level flag(s)")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()

    total = sum(check_file(p) for p in args.paths)
    print(f"\n{total} total flags across {len(args.paths)} file(s). "
          f"Advisory — read each one, fix what's real, ignore what isn't.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
