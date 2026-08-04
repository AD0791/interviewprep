# SQL

*Depth modules. Each is L3–L4: mechanism, then failure, then the spoken answer.*

| # | Module | Level | Status |
|---|---|---|---|
| 01 | [Indexes and the query planner](01_indexes_and_the_query_planner.md) | L3–L4 | **Written** |
| 02 | Transactions, isolation levels, and deadlocks | L3–L4 | Planned |
| 03 | Window functions and the logical evaluation order | L3 | Planned |
| 04 | NULL semantics, three-valued logic, and the aggregate traps | L4 | Planned |
| 05 | Joins in depth — semi, anti, lateral, and when each is the answer | L3 | Planned |
| 06 | Query rewriting: CTEs, materialisation, and the optimisation fence | L4 | Planned |
| 07 | Schema design — normalisation, and when to stop | L5 | Planned |

Order past 01 is decided by [the diagnostic](../00_self_assessment.md), section B.

---

## Harvest before you build

This is the one area where the repo should **consolidate rather than write from scratch.** Substantial SQL material already exists in the campaign folders:

- `../../acted_bdd/01_sql_analyste_et_gestion_bdd.md` — indexes, execution plans, transactions, N+1, deadlocks *(in French)*
- `../../assitant_pmel/07_sql_analyse_pmel.md` — analytical SQL *(in French)*
- `../../remote_leverage_data_analyst/first_step/05_sql_drills_with_answers.md` — twelve drills with verified outputs *(English)*

Those were written to campaign standard, which is a level below this repo's L3–L4 bar, and two of them are in French. The work for modules 02–07 is mostly **levelling up and translating** existing material, not originating it — which is why SQL is second in the build order despite being enormous.

---

## Engines

Module 01 was measured on **SQLite** (200,000 accounts, 1,000,000 transactions) because it reproduces in thirty seconds with no server. Postgres differences are flagged inline where they matter.

Interviews will ask about Postgres, so the standing task for this folder is to re-run the module 01 experiments against a real Postgres instance and record the `EXPLAIN (ANALYZE, BUFFERS)` output alongside the SQLite plans. The reasoning transfers; the vocabulary does not.
