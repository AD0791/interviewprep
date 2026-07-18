# Advanced PostgreSQL Aggregations & SQLAlchemy Optimization Guide

A comprehensive guide to database-level data aggregation, query performance tuning, and SQLAlchemy ORM integration for fullstack developers.

---

## 1. The Theory of Data Aggregation (Why & What)

### Why Aggregate at the Database Layer?
In dashboard systems, aggregating data (calculating totals, moving averages, daily sign-ups, or performance ranks) is computationally expensive. Developers often face the decision of where to execute this aggregation: in the **Database Engine**, the **Backend Application (Python/FastAPI)**, or the **Client Browser (JS/React)**.

Performing aggregation in the database layer is almost always the optimal choice because:
1. **Network I/O Reduction**: Fetching 1,000,000 raw transaction logs to calculate a single daily sum sends megabytes of data over the network. Aggregating in Postgres sends a single numerical result (a few bytes).
2. **Memory Efficiency**: Database engines are highly optimized in C++ or C to perform sorts, hashes, and mathematical aggregates directly in memory (`work_mem`) or via disk spills if necessary. Python application memory is garbage-collected and has a higher memory footprint per data structure.
3. **Execution Speed**: PostgreSQL can utilize indexes (B-Tree, Hash, BRIN) and parallel workers to execute aggregations orders of magnitude faster than a single-threaded Python event loop or runtime environment.

### What is the Difference Between GROUP BY and Window Functions?

There are two primary paradigms for aggregating data in SQL:

1. **`GROUP BY` (Collapsing Aggregation)**:
   * **Behavior**: Collapses multiple rows matching a grouping key into a single summary row.
   * **Usage**: Best for high-level KPIs, metrics tables, and distribution charts (e.g., total sales per product category).
2. **Window Functions (`OVER (...)`) (In-place Aggregation)**:
   * **Behavior**: Performs aggregations across a set of table rows that are related to the current row, but *does not collapse* the rows. Each row retains its individual identity.
   * **Usage**: Best for running totals, moving averages, difference calculations between periods (using `LAG`/`LEAD`), and rankings (using `ROW_NUMBER`/`DENSE_RANK`).

```mermaid
graph TD
    subgraph Collapse ["GROUP BY (Collapsing)"]
        R1[Row 1: Category A, Val 10] --> G1[Group Category A]
        R2[Row 2: Category A, Val 20] --> G1
        G1 --> Out1[Result 1: Category A, Sum 30]
    end

    subgraph Window ["Window Functions (In-Place)"]
        W1[Row 1: Category A, Val 10] --> O1[Row 1: Category A, Val 10, Cumulative Sum 10]
        W2[Row 2: Category A, Val 20] --> O2[Row 2: Category A, Val 20, Cumulative Sum 30]
        W1 -. Partition & Order .-> W2
    end
```

---

## 2. Database Layer Aggregation (How)

### Common Table Expressions (CTEs)
A CTE (defined via the `WITH` clause) acts as a temporary result set that you can reference within another `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement. 
* **Why use it?** It breaks down complex queries into logical steps, making the SQL highly readable and helping the query planner structure execution.
* **Materialization**: In Postgres 12+, CTEs are automatically inlined unless they are recursive, have side-effects, or are explicitly marked `MATERIALIZED` (which forces Postgres to write the intermediate state to a temporary table).

### PostgreSQL Query Implementations
Here is a gist-style raw SQL script illustrating complex data aggregations using CTEs, window functions, and time-bucket grouping:

```sql
-- Gist: advanced_postgres_aggregations.sql
-- Goal: Retrieve dashboard metrics for a multi-tenant subscription platform:
-- 1. Daily running total of sales per tenant.
-- 2. Month-over-Month (MoM) revenue growth using LAG.
-- 3. Ranks of top-performing tenants based on total sales.

WITH daily_sales AS (
    -- Step 1: Bucket transactions by day and tenant
    -- Why: COLLAPSE rows to make running totals and comparisons cleaner
    SELECT 
        tenant_id,
        DATE_TRUNC('day', created_at) AS sales_date,
        SUM(amount) AS total_amount,
        COUNT(id) AS transaction_count
    FROM transactions
    WHERE status = 'completed'
    GROUP BY tenant_id, DATE_TRUNC('day', created_at)
),

sales_with_running_total AS (
    -- Step 2: Calculate running total in-place using WINDOW function
    -- Why: Keep dates separate but perform partition aggregation
    SELECT 
        tenant_id,
        sales_date,
        total_amount,
        SUM(total_amount) OVER (
            PARTITION BY tenant_id 
            ORDER BY sales_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_cumulative_sales
    FROM daily_sales
),

monthly_comparison AS (
    -- Step 3: Compute Month-over-Month changes using LAG
    -- Why: LAG accesses the previous month's row in the same partition
    SELECT 
        tenant_id,
        DATE_TRUNC('month', sales_date) AS sales_month,
        SUM(total_amount) AS monthly_revenue,
        LAG(SUM(total_amount), 1) OVER (
            PARTITION BY tenant_id 
            ORDER BY DATE_TRUNC('month', sales_date)
        ) AS previous_month_revenue
    FROM daily_sales
    GROUP BY tenant_id, DATE_TRUNC('month', sales_date)
)

-- Step 4: Final Selection and Rank Generation
SELECT 
    m.tenant_id,
    m.sales_month,
    m.monthly_revenue,
    m.previous_month_revenue,
    COALESCE(
        ((m.monthly_revenue - m.previous_month_revenue) / NULLIF(m.previous_month_revenue, 0)) * 100, 
        0
    ) AS mom_growth_percentage,
    DENSE_RANK() OVER (
        PARTITION BY m.sales_month 
        ORDER BY m.monthly_revenue DESC
    ) AS monthly_rank_in_platform
FROM monthly_comparison m
ORDER BY m.sales_month DESC, monthly_rank_in_platform ASC;
```

---

## 3. SQLAlchemy v2 Integration & Optimization (How)

To integrate these complex database aggregates into a FastAPI dashboard backend, we use SQLAlchemy ORM.

### The N+1 Query Problem Explained
The N+1 query problem occurs when an application loads a list of parent entities (e.g., 100 Tenants) and then, for each parent, issues an individual query to load child entities (e.g., their Transactions). 

```mermaid
sequenceDiagram
    autonumber
    participant App as FastAPI Backend
    participant DB as PostgreSQL
    App->>DB: SELECT * FROM tenants LIMIT 50;
    Note over DB: Returns 50 rows (1 query)
    loop For each Tenant
        App->>DB: SELECT * FROM transactions WHERE tenant_id = ?;
        Note over DB: Executed 50 times (N queries)
    end
    Note over App,DB: Total Queries: 51 (N+1)
```

#### Eager Loading Strategies to Solve N+1:
* **`joinedload()`**: Emits a single SQL `LEFT OUTER JOIN` to load the parent and children in one database trip.
  * *Best for*: Many-to-One and One-to-One relationships, or collections with few children.
* **`selectinload()`**: Emits a second query using an `IN` clause containing parent IDs (e.g., `SELECT ... WHERE tenant_id IN (1, 2, 3...)`).
  * *Best for*: One-to-Many collections. It avoids the large, duplicated result sets generated by cartesian products in large JOINs.

### FastAPI & SQLAlchemy v2 Aggregate Endpoint Implementation
The following gist demonstrates:
1. Setting up a highly optimized database mapping in SQLAlchemy v2.
2. Formulating a window function/CTE query in the ORM.
3. Defining input/output structures in Pydantic v2.
4. Exposing the metrics through a FastAPI endpoint using an async session lifecycle.

```python
# Gist: main.py
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, over, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

# ---------------------------------------------------------
# DATABASE CONFIGURATION & MODELS
# ---------------------------------------------------------
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard_db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Async Session Dependency
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class Base(DeclarativeBase):
    pass

class Tenant(Base):
    __tablename__ = "tenants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    
    # Relationship to transactions
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="tenant")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(nullable=False, index=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="completed")
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    
    # Back-populates
    tenant: Mapped["Tenant"] = relationship(back_populates="transactions")

# ---------------------------------------------------------
# PYDANTIC SCHEMAS (Validation & Serialization)
# ---------------------------------------------------------
class TenantSalesMetric(BaseModel):
    tenant_id: int
    tenant_name: str
    sales_date: datetime.date
    daily_sales: float
    running_cumulative_sales: float

    class Config:
        from_attributes = True

# ---------------------------------------------------------
# FASTAPI APPLICATION AND ROUTE
# ---------------------------------------------------------
app = FastAPI(title="Highly Optimized Analytics Dashboard API")

@app.get("/api/v1/analytics/cumulative-sales", response_model=List[TenantSalesMetric])
async def get_cumulative_sales(
    start_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Fetches daily sales metrics and running cumulative totals per tenant.
    Utilizes SQL Window Functions inside SQLAlchemy v2 ORM to shift aggregation workload to PG.
    """
    # Define start date fallback (default past 30 days)
    filter_date = start_date or (datetime.date.today() - datetime.timedelta(days=30))
    
    # Constructing SQL Window Function in SQLAlchemy v2 ORM:
    # SQL: SUM(amount) OVER (PARTITION BY tenant_id ORDER BY DATE(created_at))
    daily_date = func.date(Transaction.created_at).label("sales_date")
    
    # Subquery / CTE to aggregate raw logs to day buckets first
    daily_summary_stmt = (
        select(
            Transaction.tenant_id,
            daily_date,
            func.sum(Transaction.amount).label("daily_sales")
        )
        .where(Transaction.status == "completed")
        .where(func.date(Transaction.created_at) >= filter_date)
        .group_by(Transaction.tenant_id, daily_date)
    ).subquery()
    
    # Final Selection combining subquery with Window Functions and Join
    # Why Join Tenant: Avoid N+1 requests for tenant details (Eagerly resolve names)
    stmt = (
        select(
            daily_summary_stmt.c.tenant_id,
            Tenant.name.label("tenant_name"),
            daily_summary_stmt.c.sales_date,
            daily_summary_stmt.c.daily_sales,
            func.sum(daily_summary_stmt.c.daily_sales)
            .over(
                partition_by=daily_summary_stmt.c.tenant_id,
                order_by=daily_summary_stmt.c.sales_date
            )
            .label("running_cumulative_sales")
        )
        .join(Tenant, Tenant.id == daily_summary_stmt.c.tenant_id)
        .order_by(daily_summary_stmt.c.sales_date.desc(), text("running_cumulative_sales DESC"))
    )
    
    # Execute query asynchronously
    result = await db.execute(stmt)
    rows = result.all()
    
    # Map row result objects directly to response schema
    metrics = [
        TenantSalesMetric(
            tenant_id=row.tenant_id,
            tenant_name=row.tenant_name,
            sales_date=row.sales_date,
            daily_sales=float(row.daily_sales),
            running_cumulative_sales=float(row.running_cumulative_sales)
        )
        for row in rows
    ]
    
    return metrics
```

---

## 4. Key Performance Tuning Summary

| Optimization Target | Technique | Benefit |
| :--- | :--- | :--- |
| **Transaction Table Query** | Composite Index: `(tenant_id, status, created_at)` | Accelerates filters (`WHERE`) and groupings (`GROUP BY`) to scan index leaves rather than raw disk blocks. |
| **N+1 Entity Fetching** | `joinedload` (One-to-One) / `selectinload` (One-to-Many) | Cuts database roundtrips down from \(N+1\) to exactly 1 or 2. |
| **Timeseries Range Queries** | Partition transactions by range (e.g., monthly) | Postgres dynamically discards partitions outside the `start_date` range, minimizing total scan area. |
| **Heavy UI Rendering** | Push Window calculations to Postgres | Keeps the React main thread free to draw frames rather than sorting and aggregating arrays. |
