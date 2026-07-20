# Battle Card 02 — Postgres & SQLAlchemy

## 30-Second Answers

**N+1.** "Load N parents, then query children per parent — N+1 roundtrips. Fix: `selectinload` (second query, IN clause — collections) or `joinedload` (single JOIN — many-to-one), with `lazy='raise'` so regressions fail loudly in dev."

**Slow query playbook.** "`EXPLAIN ANALYZE` first. Check estimated vs actual rows — a big gap means stale stats, run `ANALYZE`. Find the dominant node: Seq Scan discarding millions of rows means a composite index, equality columns before the range column. Re-measure. Only then talk caching."

**Pool sizing.** "Replicas × workers × (pool_size + max_overflow) must stay under `max_connections` minus headroom — Postgres connections are OS processes. When replicas multiply, PgBouncer multiplexes."

**Concurrency on one row.** "Contention chooses the strategy: `SELECT FOR UPDATE` serializes writers on hot rows (money) with locks ordered by key to avoid deadlocks; a version column with retry-on-StaleDataError handles cold rows without holding locks."

**Huge table.** "Past ~100M append-heavy rows: range-partition by time — pruning keeps queries on recent partitions, maintenance stays per-partition, and retention becomes `DROP TABLE`, not a bloating DELETE."

## Numbers & Facts

| Fact | Value |
|---|---|
| Postgres `max_connections` default | 100 (shared by everything) |
| Pool math example | 2 replicas × 4 workers × 15 = 120 > 100 → timeouts |
| Composite index rule | Equality columns first, range column last |
| Index Only Scan needs | Covering index (`INCLUDE`) + `Heap Fetches: 0` |
| Matview concurrent refresh needs | A unique index on the view |

## Rapid Fire

- **GROUP BY vs window function?** → Collapse rows vs annotate in place (running totals, LAG, ranks).
- **Why aggregate in the DB, not Python?** → Payload, native memory, and the planner's indexes/parallelism.
- **`idle in transaction` everywhere in pg_stat_activity?** → App code holding transactions open — the session-leak signature.
- **Matview vs Redis for a heavy aggregate?** → Matview if consumers keep querying it with SQL; Redis for sub-ms finished payloads with write-driven invalidation.
- **Two Alembic heads after a merge?** → `alembic merge`, then a single linear upgrade path.

## Trap Questions

- *"Just add an index to every column?"* — Each index taxes every write and eats RAM; index for measured queries, and column *order* in a composite index decides whether it's used at all.
- *"REFRESH MATERIALIZED VIEW is safe during traffic?"* — Plain refresh takes an exclusive lock and queues readers; you want `CONCURRENTLY`, which requires a unique index.

## Deep Dives

[01/01 aggregation](../../01_fastapi_sqlalchemy_postgres/01_postgres_aggregation_sqlalchemy.md) · [01/03 pools & locking](../../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md) · [01/04 EXPLAIN & partitioning](../../01_fastapi_sqlalchemy_postgres/04_explain_analyze_partitioning_matviews.md)
