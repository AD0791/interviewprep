# Architecture & System Design for Dashboards

This directory focuses on designing data aggregation pipelines, real-time analytics, and performant dashboard backends.

## Documents in This Folder

1. [01_dashboard_system_architecture.md](01_dashboard_system_architecture.md) — Telemetry ingestion, pre-aggregation, multi-tenancy, production compose.
2. [02_modern_tooling_uv_vite.md](02_modern_tooling_uv_vite.md) — uv, Vite, uvicorn tooling.
3. [03_twelve_factor_config.md](03_twelve_factor_config.md) — 12-factor config, env, secrets.
4. [04_project_structure_standards.md](04_project_structure_standards.md) — Repo layout and API versioning conventions.
5. [05_design_patterns_reference.md](05_design_patterns_reference.md) — Repository/UoW/DI; container-presentational and hooks.
6. [06_api_contracts_idempotency_pagination.md](06_api_contracts_idempotency_pagination.md) — RFC 7807 errors, idempotency keys, rate limiting, offset vs keyset pagination.
7. [07_oauth2_jwt_lifecycle.md](07_oauth2_jwt_lifecycle.md) — OAuth2 flows (PKCE), JWT anatomy/validation, refresh rotation and reuse detection.
8. [08_redis_caching_strategies.md](08_redis_caching_strategies.md) — Cache-aside, invalidation strategies, stampede defenses, Redis vs matviews vs SWR.
9. [09_deployment_scaling_statelessness.md](09_deployment_scaling_statelessness.md) — gunicorn/uvicorn topology, worker sizing, statelessness, zero-downtime rollouts.

## Core Architectural Patterns

### 1. Data Aggregation Flow (Batch vs. Real-Time)
* **Real-time (Push)**: Client updates immediately using WebSockets or Server-Sent Events (SSE). Best for live logs, stock prices, or instant monitoring.
* **Near Real-time (Pull/Poll)**: Client polls API at intervals (e.g., SWR revalidation or short polling). Simple to implement, easily scalable with caching.
* **Batch / Pre-aggregation**: For heavy analytical databases, avoid running raw `SUM`/`COUNT` over millions of rows on demand. Use:
  * Materialized views in Postgres (refreshed periodically).
  * Cron/worker jobs (using Celery/Redis) to pre-aggregate hourly metrics into a summary table.

### 2. General Dashboard Architecture Template
```
[React Client (Tailwind / ChakraUI)]
                │
                │ Axios / SWR HTTP Requests
                ▼
  [FastAPI Gateway / REST API] (Pydantic schemas)
                │
                │ SQLAlchemy (Selectinload/Joinedload)
                ▼
       [PostgreSQL DB] (B-Tree indexes on search keys, Partitioned tables)
                ▲
                │ Periodic Refresh / Writes
        [Celery Workers] ◄── [Redis Queue]
```

### 3. Scaling & Caching Strategies
* **Database level**: Indexing (`CREATE INDEX idx_user_created ON orders (user_id, created_at)`), schema normalization levels, read replicas.
* **API level**: Redis caching for popular read endpoints.
* **CDN level**: Cache static assets and public dashboards.
