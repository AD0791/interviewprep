# MEASUREMENT_SPEC — how the archived figures are read

> **Superseded, and retained only to explain the archive.**
>
> This file was the binding format for every number in a written module: measure it on a named
> machine, record the command, carry a tag. That requirement is gone.
> [`MODULE_SPEC.md`](MODULE_SPEC.md) §6 replaces it with attribution — a claim names its source
> in the sentence that makes it — because a reference text may not be conditional on the author
> or the reader having an environment. [`AGENTS.md`](../AGENTS.md) §5 gives the reasoning.
>
> **What survives:** [`MEASUREMENTS.md`](../MEASUREMENTS.md) is a closed archive of real
> measurements, citable as sources like any other documentation. The tag vocabulary in §2 below
> is what its rows are written in, so this file stays readable for that purpose alone. **No new
> module carries a `Measurement:` line, and no new row is added to the ledger.**

This was the binding format for [`MEASUREMENTS.md`](../MEASUREMENTS.md) and for every number that
appeared in a written module. It sits alongside [`MODULE_SPEC.md`](MODULE_SPEC.md), which governs
module shape, and [`KG_SPEC.md`](KG_SPEC.md), which governs the knowledge graph.

---

## 1. Why the ledger existed

The discipline came out of a concrete failure rather than a theory. An early module was written
about a database with no server available locally, so its plans and timings were taken from
vendor documentation while its size calculations were genuinely computed. On the page the two
were indistinguishable. The tags in §2 exist so that they never are again.

That failure is still worth preventing, and `MODULE_SPEC.md` §6 prevents it — by requiring the
source rather than the machine. Where this file said *measure it or do not write it*, the rule
now is *attribute it or do not write it*, which catches the same dishonesty without making a
book depend on a running daemon.

**The ledger is not an interview aid.** It records provenance so a reader can trust a figure and
re-derive it, and so a later pass can tell which figures went stale when the machine changed.
Any framing that treats a measurement as something to defend under questioning belongs to a
superseded version of this folder and must not return — see `AGENTS.md` §7.

---

## 2. The tags

These are the tags the archive's rows are written in, and the tags the eleven pre-spec modules
carry in their front matter — one per module, the **weakest** among the claims it makes, with
individual claims sometimes carrying a stricter one. New modules carry a `Sources:` line instead
and no tag at all.

| Tag | Meaning |
|---|---|
| `measured` | The number came out of a terminal on a named machine on a named date, and the command is recorded here with an ID |
| `reproduced-small` | Measured on a toy that demonstrates the mechanism correctly but whose magnitude does not transfer. **Never quote the magnitude** |
| `documented` | Taken from vendor documentation with no measurement. The tag appears in the front matter *and* is repeated in prose at the point of use |
| `measured-stale-env` | Measured, but on an environment that no longer exists. May be quoted **only** with that environment named in the same sentence |

A `documented` claim may never be written as though it were measured. A `measured-stale-env`
figure quoted without its environment is the same error wearing a better tag.

---

## 3. Identifiers

Ledger IDs are `SUBJECT-TOPIC-NN` — three segments, such as `CONC-ASY-01`, `SQL-IDX-05`,
`PY-CONC-03`. The middle segment names the module or topic the figure came from.

**The third segment is not optional, and this is the rule that matters.** Knowledge-graph node
IDs are two-segment (`^[A-Z]{2,5}-\d{2}$` — `BQ-01`, `CONC-04`, `SQL-17`). A two-segment ledger
ID is therefore indistinguishable from a graph node ID, and a module citing `BQ-01` would be
ambiguous between a BigQuery concept and a BigQuery measurement.

Never mint a two-segment ledger ID. When a topic segment feels redundant, use the module's own
short name rather than dropping it.

---

## 4. Environments

Every environment gets a block at the top of the ledger with an `ENV-x` label, a full toolchain
inventory, and a plain statement of whether it is the current machine. Rows name their
environment; rows measured on a superseded one are tagged `measured-stale-env`.

When a new environment supersedes an old one, state in prose **which differences change results
rather than merely shifting them** — a core-count change invalidates every process-pool scaling
claim, an interpreter change invalidates bytecode-level timings, and a version that went
*backwards* invalidates anything depending on a newer default. That paragraph is what makes the
stale tags actionable instead of decorative.

Rows worth re-measuring first are marked **re-run priority** in the tag column.

---

## 5. What a ledger row carries

One table per module or topic, under a heading naming it, with a short provenance line above the
table giving the date and the setup. Columns are fixed:

```markdown
| ID | Claim | Environment | Tag |
|---|---|---|---|
| `SQL-IDX-01` | A function applied to the indexed column defeats the index: **62.4 ms** versus **1.8 ms** | ENV-B, SQLite | `measured-stale-env` |
```

The claim states the figure and what it means, with the numbers in bold. Prose beneath a table
may draw out what a pair of rows shows together; that prose describes the mechanism, never the
reader and never an audience.

**Provenance must be self-contained.** A row may not depend on a file outside the ledger to be
intelligible: if the originating module is removed, its date, environment and setup move into
the ledger rather than leaving a dead path behind.

---

## 6. Negative results

A measurement that failed to reproduce the expected failure is recorded as a **negative result**
with the same weight as any other row, and never quietly replaced with a figure that behaved
better.

The honest framing is almost always that the failure is nondeterministic rather than absent —
which is usually the more useful finding, because a bug that appears rarely is more dangerous
than one that appears every time.

---

## 7. Before quoting a figure anywhere

1. It has a row in `MEASUREMENTS.md` with an ID.
2. The ID has three segments.
3. The tag is read, not assumed — `documented` and `measured-stale-env` both constrain how the
   figure may be written.
4. If `measured-stale-env`, the environment is named in the same sentence.
5. If `reproduced-small`, the magnitude is not quoted at all.

← [writing contract](../AGENTS.md) · [module spec](MODULE_SPEC.md) · [the ledger](../MEASUREMENTS.md)
