# Battle Card 04 — Caching, Scaling & Deployment

## 30-Second Answers

**Cache-aside.** "Read: check Redis, on miss query Postgres and populate with a TTL — the TTL is the staleness budget product agreed to. Write: mutate the DB, then *delete* the key after commit; recomputing inline reintroduces the race. Explicit invalidation for correctness, TTL as the backstop for paths you forgot."

**Stampede.** "A hot key expiring under 500 simultaneous users means 500 concurrent recomputations — the cache DDoSes your own DB. Defenses in cost order: jittered TTLs, a per-key rebuild lock, serve-stale-while-revalidate — which is literally the SWR pattern one tier down."

**Worker topology.** "gunicorn as process manager, UvicornWorker as the ASGI worker: one process, one event loop each. Async workers provision for CPU, so ~one per core — `2×cores+1` is the *sync* heuristic — then re-check pool math, because workers multiply DB connections."

**1 → 5 replicas.** "Whatever hid in process memory breaks: caches drift, rate limits become 5×, sessions log out, uploads 404, websocket broadcasts fragment, cron runs five times. State moves to Redis, S3, pub/sub, an external scheduler. The test: any replica must be killable with zero user-visible loss."

**Zero-downtime deploy.** "Expand-phase migration first — old and new code coexist mid-roll, so schema changes must be backward-compatible: add nullable, backfill in batches, constrain later. Then rolling replicas: readiness drains, SIGTERM, in-flight finish, lifespan teardown."

## Numbers & Facts

| Fact | Value |
|---|---|
| Latency ladder | process dict ~100 ns · Redis ~1 ms · indexed PG 1–10 ms · heavy aggregate 100 ms+ |
| Async worker count | ≈ cores (sync: 2×cores+1) |
| Memory per worker | ~150–300 MB (interpreter + imports + pool) |
| TTL jitter | base + random(0–20%) so keys don't expire in unison |
| Readiness vs liveness | remove from LB vs restart the pod |

## Rapid Fire

- **Why is Redis `INCR` safe without locks?** → Single-threaded server; every command is atomic.
- **Why delete, not update, the cache on write?** → Update reintroduces read-modify-write races; delete lets the next read repopulate from truth.
- **Sticky sessions to fix state?** → Anti-pattern: defeats balancing, dies with the pod, hides state instead of moving it.
- **When NOT to cache?** → Already ~1 ms via index, write-heavy invalidation churn, or zero staleness tolerance (balances).
- **`--max-requests` on gunicorn?** → Periodic worker recycling — cheap insurance against slow memory leaks.

## Trap Questions

- *"Cache in a module-level dict — it's fastest?"* — Fastest and wrong: N workers × M replicas = N×M private, drifting caches invalidation can't reach. Shared mutable cache state belongs in Redis.
- *"More workers = more throughput?"* — Only until CPU or `max_connections` is the wall; each worker adds a full pool and hundreds of MB. Async throughput usually scales with cores, not worker count.

## Deep Dives

[04/08 Redis caching](../../04_architecture_and_system_design/08_redis_caching_strategies.md) · [04/09 deployment & scaling](../../04_architecture_and_system_design/09_deployment_scaling_statelessness.md) · [01/03 pool math](../../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md)
