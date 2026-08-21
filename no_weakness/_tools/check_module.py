#!/usr/bin/env python3
"""Validate a written module against _tools/MODULE_SPEC.md.

Run:  uv run python _tools/check_module.py 05_python/
      uv run python _tools/check_module.py 05_python/01_object_model_and_attribute_lookup.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULE_NAME_RE = re.compile(r"^\d{2}_.+\.md$")

CANONICAL_HEADINGS = [
    "1. The problem this solves",
    "2. The mechanism, built up",
    "3. Failure modes",
    "4. Trade-offs",
    "5. Reference summary",
]
SECTION_MIN_WORDS = [400, 2500, 1500, 900, 300]
TOTAL_MIN, TOTAL_MAX = 6000, 8000
MIN_FAILURE_MODES, MAX_FAILURE_MODES = 3, 5

# A fenced block's contents (code or Mermaid — Mermaid diagrams are
# ```mermaid fences too) is not prose. Counting it toward a section's word
# budget is exactly what let the pre-spec modules read short: the fences
# padded a `wc -w` number without adding a sentence a reader has to parse.
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
FOOTER_RE = re.compile(r"\n-{3,}\s*\n+←.*\Z", re.S)
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.M)
H2_RE = re.compile(r"^## (.+?)\s*$", re.M)
WORD_RE = re.compile(r"[A-Za-z0-9']+")
COVERS_RE = re.compile(r"^\*\*Covers:\*\*\s*(.+)$", re.M)
SOURCES_RE = re.compile(r"^\*\*Sources:\*\*", re.M)
RETIRED_FRONTMATTER_RE = re.compile(r"^\*\*(Syllabus|Measurement|Roles):\*\*", re.M)
COVERS_ID_RE = re.compile(r"^[A-Z]{2,5}-\d{2}$")
ARTICLE_RE = re.compile(r"\*\*Article:\*\*\s*\[[^\]]*\]\(([^)]+)\)")

RETIRED_TITLE_PATTERNS = [
    re.compile(r"the questions you cannot answer", re.I),
    re.compile(r"interview angles", re.I),
    re.compile(r"the thing you already do", re.I),
    re.compile(r"break it on purpose", re.I),
    re.compile(r"the judgment call", re.I),
]
BARE_DIAGRAMS_RE = re.compile(r"^(?:\d+\.\s*)?diagrams\s*$", re.I)
RECALL_RE = re.compile(r"RECALL\.md", re.I)

PRACTICE_PHRASES = [
    "rate yourself", "say this out loud", "flashcard", "test yourself",
    "spaced repetition",
]
SETUP_PHRASES = [
    "run this and see", "try it yourself", "install it first", "on your machine",
]


@dataclass
class Result:
    path: Path
    total_words: int = 0
    section_words: list[int] = field(default_factory=lambda: [0] * 5)
    heading_count: int = 0
    mermaid_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def strip_code(text: str) -> str:
    return CODE_FENCE_RE.sub("", text)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def check(path: Path) -> Result:
    r = Result(path)
    raw = path.read_text(encoding="utf-8")

    if RECALL_RE.search(raw):
        r.errors.append("mentions RECALL.md, a file that no longer exists")

    for level, title in HEADING_RE.findall(raw):
        for pat in RETIRED_TITLE_PATTERNS:
            if pat.search(title):
                r.errors.append(f"retired heading {level} {title!r}")
        if level == "##" and BARE_DIAGRAMS_RE.match(title):
            r.errors.append(f"retired heading {level} {title!r} — diagrams are never their own section")

    r.mermaid_count = raw.count("```mermaid")

    stripped = strip_code(raw)
    stripped = FOOTER_RE.sub("", stripped)

    h2s = list(H2_RE.finditer(stripped))
    r.heading_count = len(h2s)
    found_headings = [m.group(1).strip() for m in h2s]
    if found_headings != CANONICAL_HEADINGS:
        r.errors.append(
            "H2 headings are not exactly the five canonical headings in order: "
            f"found {found_headings!r}"
        )

    front_matter = stripped[: h2s[0].start()] if h2s else stripped

    covers_ids: list[str] = []
    if m := COVERS_RE.search(front_matter):
        for token in m.group(1).split(","):
            token = token.strip()
            if token and not COVERS_ID_RE.match(token):
                r.errors.append(f"**Covers:** token {token!r} does not match ID pattern")
            elif token:
                covers_ids.append(token)
    else:
        r.errors.append("missing **Covers:** line")

    if not SOURCES_RE.search(front_matter):
        r.errors.append("missing **Sources:** line")

    for m in RETIRED_FRONTMATTER_RE.finditer(front_matter):
        r.errors.append(f"front matter carries a superseded **{m.group(1)}:** line")

    r.total_words = count_words(stripped)
    if not (TOTAL_MIN <= r.total_words <= TOTAL_MAX):
        r.errors.append(f"total word count {r.total_words} outside {TOTAL_MIN}-{TOTAL_MAX}")

    for i in range(len(h2s)):
        start = h2s[i].end()
        end = h2s[i + 1].start() if i + 1 < len(h2s) else len(stripped)
        section_text = stripped[start:end]
        words = count_words(section_text)
        if i < len(r.section_words):
            r.section_words[i] = words
        if i < len(SECTION_MIN_WORDS) and words < SECTION_MIN_WORDS[i]:
            r.errors.append(
                f"section {i + 1} ({CANONICAL_HEADINGS[i] if i < len(CANONICAL_HEADINGS) else '?'}) "
                f"has {words} words, below the {SECTION_MIN_WORDS[i]}-word minimum"
            )

        if i == 2:  # section 3, Failure modes
            h3_count = len(re.findall(r"^### ", section_text, re.M))
            if not (MIN_FAILURE_MODES <= h3_count <= MAX_FAILURE_MODES):
                r.errors.append(
                    f"section 3 has {h3_count} ### failure-mode subsections, "
                    f"expected {MIN_FAILURE_MODES}-{MAX_FAILURE_MODES}"
                )

    if r.mermaid_count == 0:
        r.warnings.append("zero Mermaid diagrams")

    lower_raw = raw.lower()
    for phrase in PRACTICE_PHRASES:
        if phrase in lower_raw:
            r.errors.append(f"contains practice-material phrase {phrase!r}")
    for phrase in SETUP_PHRASES:
        if phrase in lower_raw:
            r.warnings.append(f"contains setup-instruction phrase {phrase!r}")

    if covers_ids:
        graph_path = path.parent / "00_knowledge_graph.md"
        graph_text = graph_path.read_text(encoding="utf-8") if graph_path.exists() else ""
        graph_rel = graph_path.relative_to(ROOT) if graph_path.exists() else graph_path.name
        for node_id in covers_ids:
            if not _node_covered_by_article(graph_text, node_id, path.name):
                r.errors.append(
                    f"{node_id} has no **Article:** line in {graph_rel} "
                    f"pointing back at {path.name}"
                )

    return r


def _node_block(graph_text: str, node_id: str) -> str:
    m = re.search(
        rf"^###\s+`{re.escape(node_id)}`.*?(?=^###\s+`|\Z)",
        graph_text, re.M | re.S,
    )
    return m.group(0) if m else ""


def _node_covered_by_article(graph_text: str, node_id: str, filename: str) -> bool:
    block = _node_block(graph_text, node_id)
    if not block:
        return False
    m = ARTICLE_RE.search(block)
    return bool(m) and Path(m.group(1)).name == filename


def iter_targets(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files = []
    for p in sorted(target.glob("*.md")):
        if p.name == "00_knowledge_graph.md":
            continue
        if not MODULE_NAME_RE.match(p.name):
            continue
        files.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="a subject directory (e.g. 05_python/) or a single module file")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
        if not target.exists():
            target = (ROOT / args.target).resolve()

    if not target.exists():
        print(f"no such path: {args.target}")
        return 1

    files = iter_targets(target)
    if not files:
        print(f"no modules found under {args.target}")
        return 1

    results = [check(f) for f in files]

    print(f"\n{'MODULE':<55} {'WORDS':>6} {'S1':>5} {'S2':>5} {'S3':>5} {'S4':>5} {'S5':>5}  H2")
    print("-" * 100)
    for r in results:
        rel = r.path.relative_to(ROOT) if r.path.is_relative_to(ROOT) else r.path
        s = r.section_words
        print(f"{str(rel):<55} {r.total_words:>6} "
              f"{s[0]:>5} {s[1]:>5} {s[2]:>5} {s[3]:>5} {s[4]:>5}  {r.heading_count}")
    print("-" * 100)

    all_warnings = [(r, w) for r in results for w in r.warnings]
    all_errors = [(r, e) for r in results for e in r.errors]

    if all_warnings:
        print(f"\n--- {len(all_warnings)} warning(s) ---")
        for r, w in all_warnings:
            rel = r.path.relative_to(ROOT) if r.path.is_relative_to(ROOT) else r.path
            print(f"  {rel}: {w}")

    if all_errors:
        print(f"\n--- {len(all_errors)} ERROR(s) ---")
        for r, e in all_errors:
            rel = r.path.relative_to(ROOT) if r.path.is_relative_to(ROOT) else r.path
            print(f"  {rel}: {e}")
        print(f"\nFAILED · {len(results)} module(s) checked")
        return 1

    print(f"\nOK · {len(results)} module(s) checked, 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
