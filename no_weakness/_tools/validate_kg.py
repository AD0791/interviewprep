#!/usr/bin/env python3
"""Validate every 00_knowledge_graph.md against _tools/KG_SPEC.md.

Run:  uv run python _tools/validate_kg.py [--subject 13_http]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PREFIX = {
    "01_computation": "COMP", "02_os": "OS", "03_dsa": "DSA", "04_sh": "SH",
    "05_python": "PY", "06_concurrency": "CONC", "07_javascript": "JS",
    "08_typescript": "TS", "09_sql": "SQL", "10_mongodb": "MDB",
    "11_redis_caching": "RDS", "12_bigquery": "BQ", "13_http": "HTTP",
    "14_browser_networking": "BNET", "15_websocket": "WS", "16_webrtc": "RTC",
    "17_grpc": "GRPC", "18_eventbus": "BUS", "19_data_analysis": "STAT",
    "20_datascience": "DS", "21_dataengineering": "DE", "22_android": "AND",
    "23_app_dev": "APPD",
}

TYPES = {"Mechanism", "Protocol", "Structure", "Algorithm", "Model", "Practice", "Tool"}
DEPTHS = {"L3", "L4", "L5"}
CURRENCY = {"current", "stale-minor", "stale-major", "absent"}
EDGES = {"requires", "refines", "composes", "implements", "supersedes", "contrasts"}
ACYCLIC = EDGES - {"contrasts"}

MIN_NODES, MAX_NODES = 12, 25
MAX_DIAGRAM_NODES = 15

RE_ID = re.compile(r"^[A-Z]{2,5}-\d{2}$")
RE_HEADING = re.compile(r"^###\s+`([A-Z]{2,5}-\d{2})`\s*·\s*(.+?)\s*$")
RE_FIELD = re.compile(r"^\*\*(Type|Depth|Covers|Sources|Edges|Currency|Δ current)"
                      r":?\*\*\s*(.*)$")
RE_TYPE_DEPTH = re.compile(r"\*\*Type:\*\*\s*(\w+)\s*·\s*\*\*Depth:\*\*\s*(L\d)")
RE_EDGE_GROUP = re.compile(r"`(\w+)`\s*\[([^\]]*)\]")
RE_TICKED_ID = re.compile(r"`([A-Z]{2,5}-\d{2})`")
RE_MERMAID_NODE = re.compile(r"\b([A-Z]{2,5}-?\d{2})\b")


@dataclass
class Node:
    id: str
    title: str
    subject: str
    line: int
    type: str = ""
    depth: str = ""
    covers: str = ""
    sources: str = ""
    currency: str = ""
    delta: str = ""
    edges: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class Graph:
    subject: str
    path: Path
    nodes: list[Node] = field(default_factory=list)
    cross_table: set[tuple[str, str, str]] = field(default_factory=set)
    diagrams: list[tuple[int, int]] = field(default_factory=list)  # (line, node count)
    toc_books: set[str] = field(default_factory=set)
    audit_rows: int = 0


def parse(path: Path, subject: str) -> Graph:
    g = Graph(subject, path)
    lines = path.read_text(encoding="utf-8").splitlines()

    node: Node | None = None
    in_mermaid = False
    mermaid_start, mermaid_ids = 0, set()
    in_cross = False

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip()

        if line.startswith("```mermaid"):
            in_mermaid, mermaid_start, mermaid_ids = True, i, set()
            continue
        if in_mermaid:
            if line.startswith("```"):
                g.diagrams.append((mermaid_start, len(mermaid_ids)))
                in_mermaid = False
            else:
                # `COMP01["COMP-01 Title"]` mentions the same node twice in two
                # spellings; normalise so the 15-node cap counts nodes, not
                # occurrences.
                mermaid_ids.update(
                    m.replace("-", "") for m in RE_MERMAID_NODE.findall(line)
                )
            continue

        if m := RE_HEADING.match(line):
            node = Node(m.group(1), m.group(2), subject, i)
            g.nodes.append(node)
            continue

        if line.startswith("## "):
            in_cross = "cross-subject" in line.lower()
            node = None
            continue

        # Cross-subject edge table rows: | `FROM` | `edge` | `TO` | why |
        if in_cross and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3:
                src = RE_TICKED_ID.findall(cells[0])
                dst = RE_TICKED_ID.findall(cells[2])
                kind = re.findall(r"`(\w+)`", cells[1])
                if src and dst and kind:
                    g.cross_table.add((src[0], kind[0], dst[0]))
            continue

        if node is None:
            continue

        if m := RE_TYPE_DEPTH.search(line):
            node.type, node.depth = m.group(1), m.group(2)
            continue

        if m := RE_FIELD.match(line):
            key, val = m.group(1), m.group(2).strip()
            if key == "Covers":
                node.covers = val
            elif key == "Sources":
                node.sources = val
            elif key == "Currency":
                node.currency = val.strip("`")
            elif key == "Δ current":
                node.delta = val
            elif key == "Edges":
                for kind, ids in RE_EDGE_GROUP.findall(val):
                    node.edges.setdefault(kind, []).extend(RE_TICKED_ID.findall(ids))
            continue

        # Δ current wraps across lines; keep appending until the next blank.
        if node.delta and line and not line.startswith(("#", "|", "**")):
            node.delta += " " + line.strip()

    toc_dir = path.parent / "_toc"
    if toc_dir.is_dir():
        g.toc_books = {p.name for p in toc_dir.glob("*.toc.md")}

    body = path.read_text(encoding="utf-8")
    if m := re.search(r"##\s*(?:§?1\.?\s*)?Source audit(.*?)(?=\n##\s)", body, re.S | re.I):
        g.audit_rows = len([r for r in m.group(1).splitlines()
                            if r.strip().startswith("|") and "---" not in r]) - 1

    return g


def has_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = defaultdict(int)
    stack: list[str] = []

    def visit(n: str) -> list[str] | None:
        colour[n] = GREY
        stack.append(n)
        for m in sorted(edges.get(n, ())):
            if colour[m] == GREY:
                return stack[stack.index(m):] + [m]
            if colour[m] == WHITE:
                if cyc := visit(m):
                    return cyc
        colour[n] = BLACK
        stack.pop()
        return None

    for n in sorted(edges):
        if colour[n] == WHITE:
            if cyc := visit(n):
                return cyc
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="", help="validate one directory only")
    args = ap.parse_args()

    graphs: list[Graph] = []
    for subject, prefix in PREFIX.items():
        if args.subject and args.subject != subject:
            continue
        path = ROOT / subject / "00_knowledge_graph.md"
        if path.exists():
            graphs.append(parse(path, subject))

    if not graphs:
        print("no 00_knowledge_graph.md files found")
        return 1

    all_ids: dict[str, str] = {}
    for g in graphs:
        for n in g.nodes:
            all_ids[n.id] = g.subject

    errors: list[str] = []
    warnings: list[str] = []

    def err(g: Graph, line: int, msg: str) -> None:
        errors.append(f"{g.subject}/00_knowledge_graph.md:{line}  {msg}")

    def warn(g: Graph, line: int, msg: str) -> None:
        warnings.append(f"{g.subject}/00_knowledge_graph.md:{line}  {msg}")

    directed: dict[str, set[str]] = defaultdict(set)

    # A node at the root of its subject's DAG has no outgoing `requires` — every
    # edge points *at* it. Counting only outgoing edges would report those as
    # isolated and push builders into inventing a downstream edge, which either
    # creates a cycle or fabricates a relation. Connectivity is undirected.
    incoming: dict[str, int] = defaultdict(int)
    for g in graphs:
        for n in g.nodes:
            for targets in n.edges.values():
                for t in targets:
                    incoming[t] += 1

    for g in graphs:
        prefix = PREFIX[g.subject]
        seen: set[str] = set()

        if not MIN_NODES <= len(g.nodes) <= MAX_NODES:
            err(g, 1, f"{len(g.nodes)} nodes, spec requires {MIN_NODES}-{MAX_NODES}")

        for idx, n in enumerate(g.nodes, 1):
            if not RE_ID.match(n.id):
                err(g, n.line, f"malformed id {n.id!r}")
            if not n.id.startswith(prefix + "-"):
                err(g, n.line, f"{n.id} does not use this subject's prefix {prefix}-")
            elif n.id != f"{prefix}-{idx:02d}":
                err(g, n.line, f"{n.id} out of sequence, expected {prefix}-{idx:02d}")
            if n.id in seen:
                err(g, n.line, f"duplicate id {n.id}")
            seen.add(n.id)

            if n.type not in TYPES:
                err(g, n.line, f"{n.id} type {n.type!r} not in {sorted(TYPES)}")
            if n.depth not in DEPTHS:
                err(g, n.line, f"{n.id} depth {n.depth!r} not in {sorted(DEPTHS)}")
            if n.currency not in CURRENCY:
                err(g, n.line, f"{n.id} currency {n.currency!r} not in {sorted(CURRENCY)}")

            if n.currency != "current" and len(n.delta) < 80:
                err(g, n.line, f"{n.id} tagged {n.currency!r} but Δ current is missing or too short")
            if n.currency == "current" and n.delta:
                warn(g, n.line, f"{n.id} tagged current but carries a Δ current line")

            if not n.sources:
                err(g, n.line, f"{n.id} has no Sources line")
            elif n.sources.strip() in {"—", "-"} and n.currency != "absent":
                err(g, n.line, f"{n.id} has empty Sources but is not tagged absent")

            if not n.covers:
                warn(g, n.line, f"{n.id} has no Covers line")

            if not n.edges and not incoming[n.id]:
                err(g, n.line, f"{n.id} is isolated — nothing points at it and it "
                               f"points at nothing")

            # `contrasts` is a peer relation. Asserting it alongside a directed
            # edge to the same node says two incompatible things about the pair,
            # and in practice only ever arises from reciprocating a contrasts
            # edge that should not have existed.
            directed_targets = {t for k, v in n.edges.items() if k != "contrasts"
                                for t in v}
            for t in n.edges.get("contrasts", []):
                if t in directed_targets:
                    err(g, n.line, f"{n.id} both contrasts and points a directed "
                                   f"edge at {t} — keep only the directed edge")

            for kind, targets in n.edges.items():
                if kind not in EDGES:
                    err(g, n.line, f"{n.id} uses unknown edge type {kind!r}")
                    continue
                for t in targets:
                    if t not in all_ids:
                        err(g, n.line, f"{n.id} --{kind}--> {t} : target does not exist")
                        continue
                    if t == n.id:
                        err(g, n.line, f"{n.id} --{kind}--> itself")
                    if kind in ACYCLIC:
                        directed[n.id].add(t)
                    if all_ids[t] != g.subject and (n.id, kind, t) not in g.cross_table:
                        err(g, n.line,
                            f"{n.id} --{kind}--> {t} crosses subjects but is not in "
                            f"the cross-subject table")

        for line, count in g.diagrams:
            if count > MAX_DIAGRAM_NODES:
                err(g, line, f"mermaid diagram has {count} nodes, max is {MAX_DIAGRAM_NODES}")

        if g.toc_books and g.audit_rows and g.audit_rows < len(g.toc_books):
            warn(g, 1, f"source audit has {g.audit_rows} rows but {len(g.toc_books)} "
                       f"books are in _toc/")

    if cyc := has_cycle(directed):
        errors.append("CYCLE in directed edges: " + " -> ".join(cyc))

    # Reciprocity: contrasts is symmetric.
    contrasts: set[tuple[str, str]] = set()
    for g in graphs:
        for n in g.nodes:
            for t in n.edges.get("contrasts", []):
                contrasts.add((n.id, t))
    for a, b in sorted(contrasts):
        if b in all_ids and (b, a) not in contrasts:
            warnings.append(f"{all_ids[a]}  {a} contrasts {b}, but {b} does not contrast back")

    tally: dict[str, int] = defaultdict(int)
    print(f"\n{'SUBJECT':<24} {'NODES':>5} {'EDGES':>6}  CURRENCY")
    print("-" * 88)
    for g in graphs:
        counts: dict[str, int] = defaultdict(int)
        edge_n = 0
        for n in g.nodes:
            counts[n.currency] += 1
            tally[n.currency] += 1
            edge_n += sum(len(v) for v in n.edges.values())
        summary = " ".join(f"{k}:{v}" for k, v in sorted(counts.items()) if v)
        print(f"{g.subject:<24} {len(g.nodes):>5} {edge_n:>6}  {summary}")
    print("-" * 88)
    print(f"{'TOTAL':<24} {sum(len(g.nodes) for g in graphs):>5} "
          f"{'':>6}  " + " ".join(f"{k}:{v}" for k, v in sorted(tally.items())))

    if warnings:
        print(f"\n--- {len(warnings)} warning(s) ---")
        for w in warnings:
            print("  ", w)
    if errors:
        print(f"\n--- {len(errors)} ERROR(s) ---")
        for e in errors:
            print("  ", e)
        print(f"\nFAILED · {len(graphs)} graph(s) checked")
        return 1

    print(f"\nOK · {len(graphs)} graph(s) checked, {len(all_ids)} nodes, 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
