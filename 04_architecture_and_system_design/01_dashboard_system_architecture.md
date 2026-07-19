# Dashboard System Architecture & Telemetry Pipeline Masterclass

A deep-dive academic guide to data pipeline ingestion patterns, database multi-tenancy models, pre-aggregation pipelines, and rendering optimization.

---

## 1. Pipeline Ingestion & Pre-Aggregation (Why & What)

### The Real-Time Dashboard Scale Challenge
Dashboard architectures must process large write volumes (e.g. millions of transaction events per second) while simultaneously serving low-latency read APIs to users. Direct execution of complex analytical queries (e.g. calculating rolling averages) against a primary transaction database will saturate CPU pools and block active writes.

To solve this, system designers use **Pre-Aggregation & Streaming Pipelines**:
* **Pre-Aggregation (Background Aggregations)**: Rather than calculating metrics dynamically on every HTTP request, metrics are aggregated at set intervals (e.g. every minute) by background workers (like Celery or Faust) and stored in a read-optimized dashboard metrics table.
* **Write Throttling (Buffering)**: Incoming telemetry events are written to a message broker (like Redis or Kafka) instead of directly to PostgreSQL. A worker process reads these events in batches, executing bulk database writes to minimize transactional locks.

```mermaid
graph LR
    Tx[Incoming Transaction Events] -->|Write stream| Broker[Redis / Kafka Message Broker]
    Broker -->|Batch read| Worker[Celery / Faust Async Workers]
    Worker -->|1. Bulk write raw data| DB[(PostgreSQL Primary)]
    Worker -->|2. Compute metrics & write| Cache[(Redis Cache / Read DB)]
    Client[React Client] -->|Fetch analytics| API[FastAPI Gateway]
    API -->|Read pre-aggregated value| Cache
```

### Database Tenancy Isolation Models
When building SaaS platforms, you must isolate customer data securely:

1. **Logical Isolation (Shared Database, Shared Schema)**:
   * *Mechanism*: All tenants share the same tables. Every query must filter data using a `tenant_id` column (e.g., `WHERE tenant_id = 5`).
   * *Pros*: Simple to maintain, cost-effective, easy to run platform-wide migrations.
   * *Cons*: Risk of data leaks if developer forgets to filter by `tenant_id`.
2. **Schema-Level Isolation (Shared Database, Separate Schemas)**:
   * *Mechanism*: Every tenant has their own isolated PostgreSQL schema namespace (e.g. `tenant_a.transactions`, `tenant_b.transactions`).
   * *Pros*: Stronger security boundary.
   * *Cons*: Harder to run database migrations across thousands of schemas.

---

## 2. Architectural Implementation Blueprint (How)

### Gist: docker-compose-production-spec.yml
A production-grade Docker Compose architecture orchestrating a complete telemetry pipeline.

```yaml
version: '3.8'

# Gist: docker-compose-production-spec.yml
# Goal: Standardized container topology for real-time dashboards

services:
  # 1. Primary Database
  postgres:
    image: postgres:15-alpine
    container_name: production_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: core_telemetry
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # 2. Redis Cache & Messaging Broker
  redis:
    image: redis:7-alpine
    container_name: production_cache
    command: redis-server --appendonly yes --requirepass secretredispassword
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 3. FastAPI Web Application Gateway
  web_api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fastapi_gateway
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:secretpassword@postgres:5432/core_telemetry
      - REDIS_URL=redis://:secretredispassword@redis:6379/0
    ports:
      - "8000:8000"

  # 4. Celery Background Worker (Pre-Aggregation Engine)
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: telemetry_worker
    command: celery -A app.worker.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:secretpassword@postgres:5432/core_telemetry
      - REDIS_URL=redis://:secretredispassword@redis:6379/0

volumes:
  pg_data:
  redis_data:
```
