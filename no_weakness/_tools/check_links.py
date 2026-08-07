#!/usr/bin/env python3
"""Report every relative Markdown link under no_weakness/ that resolves nowhere.

Run:  uv run python _tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_SCHEME = re.compile(r"^(https?:|mailto:|#|file:)")
FENCE = re.compile(r"^\s*(```|~~~)")


def strip_fences(text: str) -> str:
    """Drop fenced code blocks — links inside them are illustrative samples,
    not navigation. AGENTS.md's front-matter template is the case in point."""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    broken: list[tuple[Path, str]] = []
    checked = 0

    for md in sorted(ROOT.rglob("*.md")):
        if "_toc" in md.parts:
            continue
        body = strip_fences(md.read_text(encoding="utf-8"))
        for target in LINK.findall(body):
            if SKIP_SCHEME.match(target):
                continue
            path = unquote(target.split("#", 1)[0])
            if not path:
                continue
            checked += 1
            if not (md.parent / path).resolve().exists():
                broken.append((md.relative_to(ROOT), target))

    for src, target in broken:
        print(f"BROKEN  {src}  ->  {target}")
    print(f"\n{checked} relative links checked · {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
