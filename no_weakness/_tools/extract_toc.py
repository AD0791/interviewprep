#!/usr/bin/env python3
"""Extract a table of contents from every book in no_weakness/ into <subject>/_toc/.

Three paths:

  1. Embedded PDF outlines via pypdf. Works for 40 of the 53 PDFs and gives
     nesting plus destination pages for free.
  2. A text scrape via `pdftotext` for the rest. Front-matter page ranges differ
     per book, so FALLBACK carries a hand-tuned range and pattern flavour for
     each one. Anything that still yields nothing is reported, never written as
     an empty file.
  3. The EPUB navigation document, read out of the container with stdlib
     `zipfile` and `xml.etree`. An EPUB already ships the structure the two PDF
     paths have to reconstruct, so no new dependency is warranted.

Run:  uv run --with pypdf python _tools/extract_toc.py [--report] [--only SUBSTR]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Books that are not subject material.
EXCLUDE = {"knowledge_graph_theory.pdf"}
EXCLUDE_DIRS = {"_archive", "_tools", "_toc"}

# Books with no usable embedded outline. Values are (first_page, last_page)
# 1-indexed inclusive ranges covering the printed contents pages, found by
# eyeballing pdftotext output. `flavour` selects the line pattern:
#   "numbered" - lines opening with 1 / 1.2 / 1.2.3 or roman numerals
#   "dotted"   - lines with a dot-leader running to a page number
#   "loose"    - either of the above, plus bare Chapter/Part headings
#   "columnar" - a printed TOC where depth is leading indentation and the page
#                number is separated by whitespace rather than a dot leader
#   "slides"   - a slide deck: one heading per page, taken as the first
#                substantial line, with the running copyright banner dropped
#   "headings" - no contents page at all; numbered section headings are scanned
#                out of the body over the full page range
# Paths are post-renumbering (see AGENTS.md §8 for the old->new directory map).
FALLBACK: dict[str, tuple[int, int, str]] = {
    "05_python/PythonMastery.pdf": (1, 550, "slides"),
    "06_concurrency/Concurrent.pdf": (1, 84, "slides"),
    "06_concurrency/tpc2010.pdf": (1, 14, "loose"),
    "09_sql/ullman_the_complete_book.pdf": (5, 22, "loose"),
    "09_sql/data warehouse.pdf": (1, 52, "headings"),
    "09_sql/olap-solutions-building-multidimensional-information-systems"
    "978047140030125538.pdf": (5, 20, "loose"),
    "12_bigquery/9789352139217_toc.pdf": (1, 8, "columnar"),
    "23_app_dev/app-design-workbook-AU.pdf": (1, 127, "slides"),
    "19_data_analysis/Data Science _ Big Data Analytics ( PDFDrive ).pdf": (5, 20, "loose"),
    "20_datascience/Computational-thinkingby Venkatesh.pdf": (1, 12, "loose"),
    "20_datascience/book.pdf": (1, 14, "numbered"),
    "03_dsa/Dynamic Programming - A Computational Tool.pdf": (5, 16, "loose"),
    "21_dataengineering/2.pdf": (1, 11, "slides"),
    "18_eventbus/celeryproject-readthedocs-io-zh-cn-latest.pdf": (1, 20, "loose"),
    "25_Java/O'Reilly Java Threads (2nd Edition).pdf": (3, 4, "columnar"),
}

MIN_OUTLINE = 15  # below this, an embedded outline is treated as absent

RE_NUMBERED = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(\S.*?)\s*$")
RE_DOTTED = re.compile(r"^\s*(.+?)\s*\.{4,}\s*(\d+)\s*$")
RE_CHAPTERISH = re.compile(
    r"^\s*((?:Chapter|Part|Appendix|Lesson|Hour|Section)\s+[\dIVXLC]+\b.*?)\s*$",
    re.IGNORECASE,
)
RE_TRAILING_PAGE = re.compile(r"\s+(\d{1,4})\s*$")

# Lines that are page furniture rather than contents.
RE_NOISE = re.compile(
    r"^\s*(?:contents?|table of contents|index|copyright|"
    r"www\.|https?://|page \d+|\d+\s*$)",
    re.IGNORECASE,
)


@dataclass
class Entry:
    depth: int
    title: str
    page: int | None = None


@dataclass
class Result:
    book: Path
    method: str
    entries: list[Entry] = field(default_factory=list)
    note: str = ""
    # Pages the scrape was asked to cover. A short document that yields roughly
    # one entry per page has been fully extracted even if that is under
    # MIN_OUTLINE, so the flat threshold would report a false failure.
    span: int = 0

    @property
    def ok(self) -> bool:
        if len(self.entries) >= MIN_OUTLINE:
            return True
        return self.span > 0 and len(self.entries) >= self.span * 0.8


def slugify(name: str) -> str:
    s = name.lower().removesuffix(".pdf").removesuffix(".epub")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70].rstrip("-")


def clean_title(t: str) -> str:
    t = t.replace(" ", " ")
    t = re.sub(r"\.{3,}", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# --------------------------------------------------------------------------
# path 1: embedded outline
# --------------------------------------------------------------------------


def from_outline(pdf: Path) -> Result:
    res = Result(pdf, "outline")
    try:
        from pypdf import PdfReader
    except ImportError:
        res.note = "pypdf not installed (run with: uv run --with pypdf)"
        return res

    try:
        reader = PdfReader(str(pdf))
    except Exception as exc:  # noqa: BLE001 - corrupt PDFs are expected here
        res.note = f"unreadable: {type(exc).__name__}"
        return res

    def page_of(item) -> int | None:
        try:
            return reader.get_destination_page_number(item) + 1
        except Exception:  # noqa: BLE001
            return None

    def walk(items, depth: int) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
            else:
                title = clean_title(str(getattr(item, "title", "") or ""))
                if title:
                    res.entries.append(Entry(depth, title, page_of(item)))

    try:
        outline = reader.outline
    except Exception as exc:  # noqa: BLE001
        res.note = f"outline unreadable: {type(exc).__name__}"
        return res

    if outline:
        walk(outline, 0)
    return res


# --------------------------------------------------------------------------
# path 2: pdftotext scrape
# --------------------------------------------------------------------------


def pdftotext(pdf: Path, first: int, last: int) -> str:
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", "-f", str(first), "-l", str(last), str(pdf), "-"],
            capture_output=True,
            timeout=180,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.decode("utf-8", errors="replace")


# A wide-gap columnar TOC row: indented title, whitespace or spaced dots, page.
RE_COLUMNAR = re.compile(r"^(\s*)(\S.*?)[\s.]{3,}(\d{1,4})\s*$")

# Copyright / author / URL banners repeated on every slide.
RE_BANNER = re.compile(
    r"(copyright\s*\(c\)|©|dabeaz\.com|www\.|https?://|"
    r"all rights reserved|^\s*\d+\s*/\s*\d+\s*$|apache beam apache beam)",
    re.IGNORECASE,
)

# A numbered section heading sitting in running text: "3.1  What Is a ...".
RE_BODY_HEADING = re.compile(r"^\s{0,12}(\d{1,2}(?:\.\d{1,2}){1,2})\s+([A-Z].{3,90})$")


def scrape_columnar(pdf: Path, first: int, last: int) -> Result:
    """Printed contents pages where indentation carries the level.

    Some columnar TOCs print a page number only on the chapter-level line and
    leave sub-entries unnumbered, which makes the true entry count a handful
    of chapters rather than MIN_OUTLINE's default floor. `span` mirrors
    `scrape_slides`'s 80%-of-pages fallback so a thin-but-complete two-page
    contents spread is not reported as a failed extraction.
    """
    res = Result(pdf, f"columnar[{first}-{last}]", span=last - first + 1)
    text = pdftotext(pdf, first, last)
    if not text.strip():
        res.note = "pdftotext produced no text (scanned images?)"
        return res

    for raw in text.splitlines():
        if not raw.strip() or RE_NOISE.match(raw):
            continue
        m = RE_COLUMNAR.match(raw)
        if not m:
            continue
        indent, title, page = len(m.group(1)), clean_title(m.group(2)), int(m.group(3))
        if len(title) < 3 or title.isdigit():
            continue
        # Indent buckets: flush-left is a chapter, each ~2 spaces a level down.
        depth = 0 if indent <= 2 else min((indent - 1) // 2, 4)
        res.entries.append(Entry(depth, title, page))
    return res


def scrape_slides(pdf: Path, first: int, last: int) -> Result:
    """One heading per slide, taken as the first substantial non-banner line."""
    res = Result(pdf, f"slides[{first}-{last}]", span=last - first + 1)
    text = pdftotext(pdf, first, last)
    if not text.strip():
        res.note = "pdftotext produced no text (scanned images?)"
        return res

    # pdftotext separates pages with a form feed.
    for offset, page_text in enumerate(text.split("\f")):
        for raw in page_text.splitlines():
            line = clean_title(raw)
            if len(line) < 4 or len(line) > 90:
                continue
            if RE_BANNER.search(line) or RE_NOISE.match(line):
                continue
            if line.isdigit() or not re.search(r"[A-Za-z]{3}", line):
                continue
            res.entries.append(Entry(0, line, first + offset))
            break
    return res


def scrape_headings(pdf: Path, first: int, last: int) -> Result:
    """No contents page — pull numbered section headings out of the body."""
    res = Result(pdf, f"headings[{first}-{last}]")
    text = pdftotext(pdf, first, last)
    if not text.strip():
        res.note = "pdftotext produced no text (scanned images?)"
        return res

    seen: set[str] = set()
    for offset, page_text in enumerate(text.split("\f")):
        for raw in page_text.splitlines():
            m = RE_BODY_HEADING.match(raw.rstrip())
            if not m:
                continue
            number, title = m.group(1), clean_title(m.group(2))
            # Body prose wrapping onto a numbered line ends mid-sentence.
            if title.endswith((",", "and", "the", "of", "-")):
                continue
            key = f"{number} {title}"
            if key in seen:
                continue
            seen.add(key)
            res.entries.append(Entry(number.count("."), key, first + offset))
    return res


def scrape(pdf: Path, first: int, last: int, flavour: str) -> Result:
    if flavour == "columnar":
        return scrape_columnar(pdf, first, last)
    if flavour == "slides":
        return scrape_slides(pdf, first, last)
    if flavour == "headings":
        return scrape_headings(pdf, first, last)

    res = Result(pdf, f"scrape[{first}-{last}]")
    text = pdftotext(pdf, first, last)
    if not text.strip():
        res.note = "pdftotext produced no text (scanned images?)"
        return res

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or RE_NOISE.match(line):
            continue

        if m := RE_DOTTED.match(line):
            title, page = clean_title(m.group(1)), int(m.group(2))
            depth = title.count(".") if re.match(r"^\d+\.", title) else 0
            if num := re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", title):
                depth = num.group(1).count(".")
            if len(title) > 2:
                res.entries.append(Entry(depth, title, page))
            continue

        if m := RE_NUMBERED.match(line):
            number, rest = m.group(1), m.group(2)
            page = None
            if p := RE_TRAILING_PAGE.search(rest):
                page = int(p.group(1))
                rest = rest[: p.start()]
            rest = clean_title(rest)
            # A bare "3 14" is a page-number pair, not a heading.
            if len(rest) > 2 and not rest.isdigit():
                res.entries.append(Entry(number.count("."), f"{number} {rest}", page))
            continue

        if flavour == "loose" and (m := RE_CHAPTERISH.match(line)):
            title = m.group(1)
            page = None
            if p := RE_TRAILING_PAGE.search(title):
                page = int(p.group(1))
                title = title[: p.start()]
            res.entries.append(Entry(0, clean_title(title), page))

    # Dedupe consecutive repeats (running heads bleed into layout mode).
    deduped: list[Entry] = []
    for e in res.entries:
        if deduped and deduped[-1].title == e.title:
            continue
        deduped.append(e)
    res.entries = deduped
    return res


# --------------------------------------------------------------------------
# path 3: EPUB navigation document
# --------------------------------------------------------------------------

# Every element in an NCX or an XHTML nav document carries a namespace, and
# which one differs by producer — calibre writes the default DAISY namespace,
# Packt's toolchain writes it under an `ncx:` prefix. ElementTree reports both
# as `{uri}tag`, so matching on the local name is the only portable test.
RE_LOCAL_TAG = re.compile(r"\{[^}]*\}")

# EPUB 3 replaced the NCX with an XHTML `nav` document; both spellings of the
# filename are in circulation.
NAV_NAMES = ("toc.xhtml", "toc.html", "nav.xhtml", "nav.html")

# An NCX that carries only the front matter and a handful of part dividers is
# worse than the nav document sitting beside it. Below this, try the fallback.
MIN_NCX = 12


def local_name(tag: str) -> str:
    return RE_LOCAL_TAG.sub("", tag)


def epub_member(z: zipfile.ZipFile, suffixes: tuple[str, ...]) -> str | None:
    """Find a navigation member anywhere in the container.

    The OPF may place the navigation document in any directory, so the archive
    is searched by suffix rather than by an assumed path. Shallower paths win,
    which puts a real `OEBPS/toc.ncx` ahead of a stray copy in a subfolder.
    """
    hits = [n for n in z.namelist() if n.lower().endswith(suffixes)]
    return min(hits, key=lambda n: (n.count("/"), len(n))) if hits else None


def from_ncx(z: zipfile.ZipFile, member: str) -> list[Entry]:
    """Walk the NCX navMap. `navPoint` nesting is the depth, `navLabel/text`
    the title. Pages are meaningless in a reflowable EPUB, so none are set."""
    entries: list[Entry] = []

    def walk(el: ET.Element, depth: int) -> None:
        for child in el:
            if local_name(child.tag) != "navPoint":
                walk(child, depth)  # navMap, or a producer's wrapper element
                continue
            title = ""
            for sub in child.iter():
                if local_name(sub.tag) == "text" and (sub.text or "").strip():
                    title = clean_title(sub.text or "")
                    break
            if title:
                entries.append(Entry(depth, title))
            walk(child, depth + 1)

    walk(ET.fromstring(z.read(member)), 0)
    return entries


def from_nav_xhtml(z: zipfile.ZipFile, member: str) -> list[Entry]:
    """Walk the EPUB 3 nav document's nested `<ol>`/`<li>` lists.

    Depth is how many `<ol>` elements enclose the item; the title is the text
    of the `<a>` (or `<span>`, for an unlinked heading) directly inside the
    `<li>`, excluding the nested list underneath it.
    """
    entries: list[Entry] = []

    def text_of(li: ET.Element) -> str:
        for child in li:
            if local_name(child.tag) in {"a", "span"}:
                return clean_title("".join(child.itertext()))
        return ""

    def walk(el: ET.Element, depth: int) -> None:
        for child in el:
            tag = local_name(child.tag)
            if tag == "ol":
                walk(child, depth + 1)
            elif tag == "li":
                if title := text_of(child):
                    entries.append(Entry(max(depth - 1, 0), title))
                walk(child, depth)
            else:
                walk(child, depth)

    walk(ET.fromstring(z.read(member)), 0)
    return entries


def from_epub(epub: Path) -> Result:
    res = Result(epub, "epub")
    try:
        z = zipfile.ZipFile(epub)
    except (zipfile.BadZipFile, OSError) as exc:
        res.note = f"unreadable: {type(exc).__name__}"
        return res

    with z:
        ncx = epub_member(z, (".ncx",))
        nav = epub_member(z, NAV_NAMES)

        if ncx:
            try:
                res.entries = from_ncx(z, ncx)
                res.method = "epub-ncx"
            except ET.ParseError as exc:
                res.note = f"{ncx} unparsable: {exc}"

        # A thin NCX is common in EPUB 3, where the nav document is the real
        # table of contents and the NCX is a compatibility stub.
        if len(res.entries) < MIN_NCX and nav:
            try:
                fallback = from_nav_xhtml(z, nav)
            except ET.ParseError as exc:
                res.note = res.note or f"{nav} unparsable: {exc}"
            else:
                if len(fallback) > len(res.entries):
                    res.entries = fallback
                    res.method = "epub-nav"

    if not res.entries and not res.note:
        res.note = "no toc.ncx or nav document in the container"
    return res


# --------------------------------------------------------------------------


def render(res: Result) -> str:
    lines = [
        f"# TOC — {res.book.name}",
        "",
        f"*Extracted by `_tools/extract_toc.py` ({res.method}). "
        f"{len(res.entries)} entries. Machine-generated — do not hand-edit.*",
        "",
    ]
    for e in res.entries:
        indent = "  " * min(e.depth, 5)
        page = f"  · p{e.page}" if e.page else ""
        lines.append(f"{indent}- {e.title}{page}")
    lines.append("")
    return "\n".join(lines)


def discover() -> list[Path]:
    books: list[Path] = []
    for pattern in ("*.pdf", "*.epub"):
        for p in ROOT.rglob(pattern):
            rel = p.relative_to(ROOT)
            if rel.parts[0] in EXCLUDE_DIRS or p.name in EXCLUDE:
                continue
            if len(rel.parts) == 1:  # root-level book that is not subject material
                continue
            books.append(p)
    return sorted(books)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print a per-book summary")
    ap.add_argument("--only", default="", help="restrict to paths containing this substring")
    args = ap.parse_args()

    books = [b for b in discover() if args.only in str(b)]
    results: list[Result] = []

    for book in books:
        rel = str(book.relative_to(ROOT))
        if book.suffix.lower() == ".epub":
            res = from_epub(book)
            if not res.ok:
                res.note = res.note or f"nav document had {len(res.entries)} entries"
        elif rel in FALLBACK:
            first, last, flavour = FALLBACK[rel]
            res = scrape(book, first, last, flavour)
        else:
            res = from_outline(book)
            if not res.ok:
                res.note = res.note or f"outline had {len(res.entries)} entries"

        results.append(res)
        if res.ok:
            out_dir = book.parent / "_toc"
            out_dir.mkdir(exist_ok=True)
            (out_dir / f"{slugify(book.name)}.toc.md").write_text(
                render(res), encoding="utf-8"
            )

    failed = [r for r in results if not r.ok]

    if args.report or failed:
        print(f"\n{'STATUS':<7} {'ENTRIES':>7}  {'METHOD':<16} BOOK")
        print("-" * 100)
        for r in sorted(results, key=lambda r: (r.ok, str(r.book))):
            status = "ok" if r.ok else "FAIL"
            note = f"   <- {r.note}" if r.note and not r.ok else ""
            print(
                f"{status:<7} {len(r.entries):>7}  {r.method:<16} "
                f"{r.book.relative_to(ROOT)}{note}"
            )

    print(f"\n{len(results)} books · {len(results) - len(failed)} extracted · {len(failed)} unparsed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
