# MongoDB

*Narrower than the other tracks, and a differentiator rather than a commodity.*

| # | Module | Level | Status |
|---|---|---|---|
| 01 | [Document modelling and the ESR rule](01_document_modelling_and_indexes.md) | L3–L4 | **Written** — partly unmeasured, see below |
| 02 | The aggregation pipeline — stages, index eligibility, memory limits | L3–L4 | Planned |
| 03 | Replica sets, write and read concern, and what durability means | L3–L4 | Planned |
| 04 | Sharding — shard keys, and the ones that ruin you | L4–L5 | Planned |
| 05 | Schema drift, validation, and migrating without downtime | L4 | Planned |
| 06 | MongoDB → BigQuery — the schema boundary, from the Beam work | L5 | Planned |

Order past 01 is decided by [the diagnostic](../00_self_assessment.md), section E.

---

## Outstanding work — read before quoting module 01

**No `mongod` was available in the environment this repo was built in.** Module 01's BSON document sizes are real, measured by encoding actual documents. Its query plans and timings are **not measured** — they are stated from documented behaviour.

That is a weaker standard than every other module in this repo and it should be fixed rather than tolerated. The task:

```bash
docker run -d -p 27017:27017 --name mongo mongo:latest
```

Then reproduce section 4 — the unbounded array, the silent `COLLSCAN`, the ESR violation forcing an in-memory sort, and `$lookup` with and without an index on the foreign field — and replace the descriptions with real `explain("executionStats")` output.

Until that is done, speak about this material as *"the way Mongo handles this is…"* rather than *"I measured…"*. The distinction matters: the measured claims in the other modules are what make them worth more than documentation, and borrowing that authority for unmeasured claims would undermine all of it.

---

## Why this is worth doing at all

It is the smallest surface area of the five, and it is the one where you have an advantage almost nobody else in a candidate pool has.

Most engineers know a relational database well and MongoDB by rumour, or the reverse. You have shipped both — MySQL administration and DQA work at Caris, and MongoDB into BigQuery through Apache Beam at Tekkod. That makes the comparative answer available to you: *when would you not use MongoDB*, answered by someone who has actually run both, is a senior signal that costs one module to unlock.

Module 06 is the highest-value one in this folder for that reason. The MongoDB-to-BigQuery boundary is where a schemaless store meets a system that requires a schema, and it is genuinely interesting rather than merely technical — which makes it a good story to have ready.
