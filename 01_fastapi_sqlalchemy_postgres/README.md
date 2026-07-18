# Backend: FastAPI, SQLAlchemy, Alembic, and Postgres Aggregations

This directory is dedicated to reviewing database performance, aggregations, window functions, and FastAPI structures.

## Key Study Topics

### 1. Postgres Data Aggregations & Window Functions
* **Group By & Having**: Summarize metrics per group, filtering aggregated metrics.
* **CTEs (Common Table Expressions)**: Break down complex nested queries for clarity and readability.
* **Window Functions**:
  * `ROW_NUMBER() OVER (PARTITION BY tenant_id ORDER BY created_at DESC)` for getting the latest record.
  * `SUM(amount) OVER (PARTITION BY user_id ORDER BY transaction_date)` for cumulative running totals.
  * `LAG` and `LEAD` for computing differences between consecutive points (e.g., timeseries intervals).

### 2. SQLAlchemy Optimization (Avoiding the N+1 Problem)
* **Lazy Loading vs. Eager Loading**:
  * `lazy='select'` (default, triggers separate query per relationship access).
  * `joinedload` (SQL JOIN, best for one-to-many/many-to-one where data is always needed).
  * `subqueryload` or `selectinload` (separate query using IN, better for large collections).
* **Yield / Session Lifecycle**:
  * Using dependencies for database sessions in FastAPI:
    ```python
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    ```

### 3. FastAPI Performance
* **Async/Await vs. Sync**:
  * Use `async def` when executing non-blocking operations (e.g., async DB drivers like `asyncpg`, external API requests using `httpx`).
  * Avoid `async def` if calling synchronous blocking functions (e.g., `requests`, time.sleep); use normal `def` instead so FastAPI runs it in a separate thread pool.

### 4. Pydantic (v2) and Zod Comparison
* Both validate inputs/outputs against a defined schema.
* Pydantic (Python): `Field(..., description="...")`, custom validators with `@field_validator`.
* Zod (JS/TS): `z.object({ ... })`.
