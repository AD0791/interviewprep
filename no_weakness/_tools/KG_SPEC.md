# KG_SPEC — how to build a subject knowledge graph

This is the binding format for every `00_knowledge_graph.md` in `no_weakness/`. A graph that
does not validate against `_tools/validate_kg.py` is not finished.

---

## 1. What you are building, and what you are not

You are building **a map of a subject**: which mechanisms exist, how they depend on each
other, and — critically — **where the books on the shelf have fallen behind reality**.

You are **not** writing articles. No module prose, no tutorials, no code examples beyond a
symbol name. The articles come later and are governed by `AGENTS.md`; your job is to define
the nodes they will be written against.

You are also **not** re-indexing the tables of contents. A TOC is a book's structure. A
knowledge graph is the subject's structure, and the two differ: three books will cover the
same mechanism under three different chapter names, and that is **one node**, not three.

The model is Hogan et al., *Knowledge Graphs* (ACM CSUR 2021) — a directed edge-labelled
graph with a schema layer. Nodes are concepts, edges are typed relations.

---

## 2. Inputs

For each subject directory `NN_subject/` you are given:

- `NN_subject/_toc/*.toc.md` — machine-extracted tables of contents, one per book. **Read all
  of them.** These are your source material.
- The web, via `WebSearch` and `WebFetch`, for the currency pass in §6.

The superseded competency-table syllabi that earlier graphs were sanity-checked against have
been deleted along with the rest of the v1 archive. Their competency IDs were dead already and
their interview-framed columns were forbidden source material; nothing in this spec depends on
them.

**Do not open the PDFs.** The TOC files exist so you do not have to. Opening a 900-page book
will exhaust your context and produce a worse graph than the TOC gives you.

---

## 3. Node identifiers

Each subject has a fixed prefix. Use it. Numbers run `01`, `02`, … in the order nodes appear
in the file, with no gaps.

| Directory | Prefix | Directory | Prefix |
|---|---|---|---|
| `01_computation` | `COMP` | `13_http` | `HTTP` |
| `02_os` | `OS` | `14_browser_networking` | `BNET` |
| `03_dsa` | `DSA` | `15_websocket` | `WS` |
| `04_sh` | `SH` | `16_webrtc` | `RTC` |
| `05_python` | `PY` | `17_grpc` | `GRPC` |
| `06_concurrency` | `CONC` | `18_eventbus` | `BUS` |
| `07_javascript` | `JS` | `19_data_analysis` | `STAT` |
| `08_typescript` | `TS` | `20_datascience` | `DS` |
| `09_sql` | `SQL` | `21_dataengineering` | `DE` |
| `10_mongodb` | `MDB` | `22_android` | `AND` |
| `11_redis_caching` | `RDS` | `23_app_dev` | `APPD` |
| `12_bigquery` | `BQ` | `24_golang` | `GO` |
| | | `25_Java` | `JAVA` |
| | | `26_spring` | `SPRG` |

The pattern is `^[A-Z]{2,5}-\d{2}$`. IDs are globally unique across the whole repo, which the
prefix table guarantees.

---

## 4. Node granularity

**12 to 25 nodes per subject.** A node is *one mechanism that would justify a full 6,000-word
article*. Test it two ways:

- **Too coarse** if you cannot state what breaks when the reader misunderstands it. "SQL
  performance" is not a node. "Index selection and the planner's cost model" is.
- **Too fine** if it is a fact rather than a mechanism. "The `EXPLAIN` keyword" is not a node;
  it belongs on the `Covers:` line of the planner node.

Everything the books cover must land *somewhere* — either as a node or on a node's `Covers:`
line. Nothing is dropped silently. If a book chapter has no home, that is a signal you are
missing a node, or the chapter belongs to a different subject and becomes a cross-subject
edge.

A subject whose books are thin may still need nodes the books do not cover. Admit them with
`Currency: absent` (§6). **The graph maps the subject, not the bookshelf.**

---

## 5. Edge vocabulary

Closed set. The validator rejects anything else.

| Edge | Meaning | Direction |
|---|---|---|
| `requires` | Hard prerequisite: the target must be understood first | directed, acyclic |
| `refines` | This node is a narrower case of the target | directed, acyclic |
| `composes` | This node is a component part of the target | directed, acyclic |
| `implements` | This node is a concrete realisation of the abstract target | directed, acyclic |
| `supersedes` | The target is historical; this node replaced it | directed, acyclic |
| `contrasts` | Best understood by comparison with the target | symmetric, may cycle |

Rules:

- Every node must be connected to something. Connectivity counts in **both** directions: a
  foundational node at the root of the subject's DAG has no outgoing `requires` because
  everything points *at* it, and that is correct — leave its `Edges:` line off rather than
  inventing a downstream edge. Never manufacture a `contrasts` edge purely to satisfy the
  validator; a fabricated relation is worse than a sparse one.
- Watch for accidental two-node cycles. "Arithmetic circuits `composes` the CPU" and "the CPU
  `requires` arithmetic circuits" say the same thing in opposite directions, and the validator
  pools all directed edge types into one DAG. Pick one edge per pair — `requires` by default.
- Never put `contrasts` on a pair that already has a directed edge. `contrasts` is a relation
  between peers; if one node is a prerequisite of the other they are not peers, and the two
  claims contradict each other. The validator rejects it.
- `requires` is the backbone — it produces the DAG and the reading order. Be sparing: a
  `requires` edge means *genuinely cannot be understood first*, not *related to*.
- A cross-subject edge names the other subject's node ID directly (`` `HTTP-04` ``). It may
  point at a subject that has not been built yet. Declare it anyway; §9 collects it.
- Never invent a target ID. If you need a node in another subject and cannot know its number,
  put the concept in §10 (coverage gaps) as prose instead.

---

## 6. The currency pass — the part that matters most

**Every book on this shelf documents a moment in time.** `HTTP: The Definitive Guide` is from
2002 and stops before HTTP/2 exists. `MongoDB in Action` describes a storage engine MongoDB
no longer ships. A graph built from these TOCs alone would encode a museum and quietly teach
things that are wrong.

So: **for every node, establish what is true now**, using `WebSearch` and `WebFetch`. Search
the current specification, the current release notes, the current documentation. Then tag:

| Tag | Meaning |
|---|---|
| `current` | The books' treatment still holds. Nothing material has changed |
| `stale-minor` | Syntax, defaults, names or version numbers moved. The mechanism is intact |
| `stale-major` | The mechanism itself was replaced or substantially reworked |
| `absent` | The concept postdates every book here. `Sources: —` |

**`Δ current` is mandatory for every tag except `current`.** It is prose, two to six sentences,
and it must do three things:

1. Say what the book claims, and name the book.
2. Say what is true now, **citing a checkable artefact** — an RFC number, a release version,
   a PEP, a dated deprecation notice, a spec section.
3. Say what that means for an article written on this node — usually which of the two the
   article should lead with.

### Honesty rules, inherited from `AGENTS.md` §5

- **Never write an unsourced currency claim.** "This is now deprecated" without a version and
  a date is exactly the kind of confident wrongness this whole exercise exists to prevent.
- If a search does not settle a question, say so in the `Δ current` line — *"could not
  establish whether X is still the default as of the 8.x docs"* is a useful sentence. An
  invented answer is not.
- Do not describe a mechanism you did not verify. If the TOC gives you a chapter title and
  nothing more, the node title can reflect the title, but the `Δ current` line must not
  pretend to knowledge of the chapter's contents.

---

## 7. The node record

Exactly this shape. The validator parses it.

```markdown
### `HTTP-07` · Connection management and reuse
**Type:** Mechanism · **Depth:** L4
**Covers:** keep-alive, pipelining, head-of-line blocking, connection pools, TLS handshake cost
**Sources:** Totty & Gourley ch.4, ch.8 (2002) · Grigorik ch.11–12 (2013)
**Edges:** `requires` [`HTTP-03`] · `contrasts` [`WS-02`] · `composes` [`BNET-05`]
**Currency:** `stale-major`
**Δ current:** Totty stops at HTTP/1.1 keep-alive and pipelining. HTTP/2 multiplexing
(RFC 9113) and HTTP/3 over QUIC (RFC 9114) removed the head-of-line problem at the HTTP
layer; pipelining is disabled in every shipping browser. Grigorik covers h2 under its
SPDY-era naming and predates QUIC standardisation. An article leads with h2/h3 and treats
h1 connection reuse as the constraint that motivated them.
```

Field rules:

- **Type** — exactly one of `Mechanism`, `Protocol`, `Structure`, `Algorithm`, `Model`,
  `Practice`, `Tool`.
- **Depth** — `L3` (competent working knowledge), `L4` (senior: knows the mechanism and its
  failure modes), `L5` (knows why it was designed that way and what it costs). Most nodes are
  L4.
- **Covers** — the sub-topics folded into this node, comma-separated. This is where TOC
  entries too small to be nodes go.
- **Sources** — author or short title, chapter, publication year. `—` only when `absent`.
- **Edges** — `` `type` [`ID`, `ID`] `` groups separated by ` · `. Omit unused types entirely
  rather than writing `—`.
- **Currency** — one tag in backticks.
- **Δ current** — omit the line entirely when the tag is `current`.
- **Article** — optional, and only where a module has *already been written* for this node.
  Format `**Article:** [05_bytecode_and_the_runtime.md](05_bytecode_and_the_runtime.md)`.
  Place it directly after the heading. Never add it speculatively: a node with an `Article`
  line pointing at a file that does not exist is worse than no line at all.

---

## 8. File structure

`NN_subject/00_knowledge_graph.md`, sections in this order.

### Header

```markdown
# <Subject> — knowledge graph

*<One line: what this subject is, at the depth this repo treats it.>*

**Nodes:** 18 · **Books:** 6 · **Currency researched:** 2026-08-06
**Requires:** [`03_dsa`](../03_dsa/00_knowledge_graph.md), [`02_os`](../02_os/00_knowledge_graph.md)
**Feeds:** [`12_bigquery`](../12_bigquery/00_knowledge_graph.md)
```

### §1 Source audit

One row per book. This is where "the book is from 2002" gets said once, plainly, so it is not
rediscovered twenty times below.

```markdown
| Book | Year | Documents | Verdict |
|---|---|---|---|
| Totty & Gourley, *HTTP: The Definitive Guide* | 2002 | HTTP/1.1, RFC 2616 era | Foundational on h1 semantics; blind to h2/h3 |
```

The `Verdict` column is a judgement, in a sentence: what the book is still good for, and
where it must not be trusted.

### §2 Node index

```markdown
| ID | Node | Type | Depth | Currency |
|---|---|---|---|---|
| `HTTP-01` | Request/response semantics | Protocol | L3 | `current` |
```

### §3 The graph

One or more Mermaid `graph LR` blocks showing `requires` and `refines` edges only. **Maximum
15 nodes per diagram** (`AGENTS.md` §3) — split by cluster and give each split a heading
saying what it covers. Use node IDs as Mermaid node names and the short title as the label.

### §4 Node records

Every node, in ID order, in the §7 format.

### §5 Cross-subject edges

```markdown
| From | Edge | To | Why |
|---|---|---|---|
| `HTTP-07` | `contrasts` | `WS-02` | Persistent connection versus upgraded full-duplex |
```

Every edge whose target is outside this subject, repeated here even though it also appears in
the node record. The root graph is assembled from these tables.

### §6 Coverage gaps

Prose, not a table. What this subject requires that no book in the directory covers, and what
would close it — a specific book, a specific spec, or a measurement that needs an environment
that is not set up. Be concrete: *"nothing here covers QUIC's loss recovery; RFC 9002 would"*
beats *"more depth needed on QUIC"*.

### Footer

`← [repo index](../README.md) · [root graph](../KNOWLEDGE_GRAPH.md) · [writing contract](../AGENTS.md)`

---

## 9. Prose rules

Inherited from `AGENTS.md` §4 and non-negotiable even though this is a reference file:

- Complete sentences in every prose field. **No fragment bullets, no arrow chains (`A → B`),
  no "Skeleton:" outlines.** Tables carry enumerable facts; the reasoning goes in sentences.
- Write about the subject, not the reader. No second person, no "you probably think".
- **No practice material of any kind** — no questions, drills, self-ratings, or rhetorical
  quiz openings (`AGENTS.md` §2).
- **Nothing dated or personal.** No interview dates, employer names, or résumé framing
  (`AGENTS.md` §7). The organising principle is the subject.
- The noun-swap test (`AGENTS.md` §6.6) applies to `Δ current` lines: if a sentence would read
  identically with a different technology substituted in, it is filler. Name the version, the
  RFC, the default, the date.

---

## 10. Before you finish

1. Node count is 12–25, IDs contiguous from `01`, prefix correct.
2. Every node has at least one edge; no edge names an undeclared ID within this subject.
3. Every node has a `Type` and a `Currency` tag from the closed sets.
4. Every node not tagged `current` has a `Δ current` naming a checkable artefact.
5. Every node has `Sources:` populated, or `—` with tag `absent`.
6. Every cross-subject edge appears in §5.
7. No Mermaid diagram exceeds 15 nodes.
8. Every book in `_toc/` appears in the §1 source audit.

Then run, from `no_weakness/`:

```
uv run python _tools/validate_kg.py
```

and fix what it reports.
