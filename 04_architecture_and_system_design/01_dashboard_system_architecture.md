# System Architecture Design for Multi-Tenant Dashboards

A senior-level blueprint for architecting scalable, multi-tenant analytics dashboards, covering data pipelines, caching tiers, and containerized development setups.

---

## 1. System Architecture Overview (Why & What)

### Design Goal
To build a dashboard system that aggregates millions of system-event and financial-transaction records, serves real-time charts to thousands of multi-tenant clients, and maintains a sub-second response time while keeping cloud infrastructure costs manageable.

### The Trade-Off: Pre-Aggregation vs. On-the-Fly Aggregation
* **Pre-Aggregation (Batch)**:
  * **Why**: For heavy statistical queries running over historical data, executing aggregate calculations (`SUM`, `AVERAGE`) on-demand blocks the database engine.
  * **What**: Pre-calculate and store hourly/daily metrics in summary tables. 
  * **How**: Use Celery workers to run a background task every hour to aggregate records from `transactions` and write them into `daily_tenant_stats`.
* **On-the-Fly Aggregation (Real-Time)**:
  * **Why**: Users need live metrics (e.g., current active orders).
  * **What**: Run queries directly on transaction logs.
  * **How**: Keep tables indexed on the search dimensions and partition raw event logs by time ranges (e.g., monthly partitions) so queries only scan relevant records.

```mermaid
graph TD
    Client[React Dashboard Client] -->|API Request| Gateway[FastAPI Backend]
    
    subgraph ReadPath ["Aggregated Read Path"]
        Gateway -->|Cache Miss| Redis[Redis Cache]
        Gateway -->|Query Summary Table| DB_Replica[(PostgreSQL Read Replica)]
    end
    
    subgraph WritePath ["Ingestion & Aggregation Path"]
        IngestionAPI[FastAPI Ingestion Endpoint] -->|Write Event| DB_Master[(PostgreSQL Master DB)]
        DB_Master -->|CDC / Replicate| DB_Replica
        
        Workers[Celery Workers] -->|Read Raw Events| DB_Master
        Workers -->|Pre-aggregate Metrics| DB_Master
    end
    
    Broker[Redis Queue] -->|Task Dispatch| Workers
```

---

## 2. Multi-Tenancy Data Isolation Patterns (Why & What)

When designing a dashboard for multiple tenants (e.g., enterprise companies), data isolation is a critical safety requirement.

### 1. Logical Isolation (Shared Database, Shared Schema)
* **What**: All tenants store data in the same tables. Every table contains a `tenant_id` column.
* **Why**: Easy to maintain, simple migrations, low infrastructure cost.
* **How**: Ensure every SQLAlchemy or SQL query includes `WHERE tenant_id = :current_tenant_id`.

### 2. Physical Isolation (Database-per-Tenant)
* **What**: Every tenant has their own isolated Postgres database instance or namespace schema.
* **Why**: Maximum security compliance, easy backup/restore per tenant, no "noisy neighbor" issues (a single tenant loading heavy charts won't slow down others).
* **How**: Middleware inspects the request headers (e.g., tenant ID) and dynamically binds the SQLAlchemy connection pool to the tenant's specific database URL.

---

## 3. Local Development Orchestration (How)

To test this multi-tier architecture locally, we orchestrate the components using Docker Compose. This ensures that the FastAPI application, PostgreSQL database, Redis broker, Celery worker pool, and React development server boot in a unified network interface.

### Gist: docker-compose.yml
An production-ready Docker Compose blueprint setting up a local fullstack dashboard ecosystem.

```yaml
# Gist: docker-compose.yml
version: '3.8'

services:
  # 1. Database Layer: PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: dashboard_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: supersecretpassword
      POSTGRES_DB: dashboard_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d dashboard_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  # 2. Caching & Message Broker Layer: Redis
  redis:
    image: redis:7-alpine
    container_name: dashboard_redis
    ports:
      - "6379:6379"

  # 3. Backend Layer: FastAPI API Gateway
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: dashboard_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:supersecretpassword@postgres:5432/dashboard_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  # 4. Background Workers: Celery (Running aggregations)
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: dashboard_worker
    command: celery -A app.worker.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:supersecretpassword@postgres:5432/dashboard_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - postgres

  # 5. Frontend Development Server: React + Vite
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: dashboard_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

volumes:
  pgdata:
```
