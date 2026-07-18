# Architecture & System Design for Dashboards

This directory focuses on designing data aggregation pipelines, real-time analytics, and performant dashboard backends.

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
