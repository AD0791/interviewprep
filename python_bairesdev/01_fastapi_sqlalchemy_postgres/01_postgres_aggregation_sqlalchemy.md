# PostgreSQL Aggregations & SQLAlchemy Optimization Masterclass

A deep-dive academic guide to database-level data aggregation, query execution plans, index scans, and SQLAlchemy ORM memory management.

---

## 1. The Theory of Database-Level Aggregation (Why & What)

### Why Aggregate at the Database Layer?
When building real-time dashboards, developers must choose where to calculate summary analytics: in the database engine, the backend API, or the frontend browser. Shifting this computation to the database layer is the industry standard due to:

1. **Network Payload Minimization**: Fetching 1,000,000 transaction records to calculate a single cumulative value transfers megabytes of raw JSON data over the wire. Database-level aggregation returns only the calculated summary (a few bytes), avoiding network saturation.
2. **Memory Footprint**: Database engines (like PostgreSQL) execute sorting and hash operations directly in native C/C++ memory pools (`work_mem`). Python processes, by contrast, create wrapper objects for every list element, leading to garbage collection pauses.
3. **Optimized Execution Engines**: Databases analyze queries using planner systems to execute tasks in parallel, using physical indexes (B-Trees, BRIN) rather than traversing data sequentially.

### GROUP BY vs. Window Functions
SQL aggregations use two main paradigms:

* **`GROUP BY` (Collapsing)**: 
  * *What*: Collapses rows matching a partition key into a single summary output row.
  * *Why*: Ideal for high-level dashboard charts (e.g. monthly revenue summaries).
* **Window Functions (`OVER(...)`) (In-place)**:
  * *What*: Calculates aggregations across a defined partition of rows related to the current row, but *does not collapse* them. Each row retains its individual parameters and properties.
  * *Why*: Essential for calculating running cumulative sums, moving averages, period comparisons (`LAG`/`LEAD`), and ranks (`DENSE_RANK`).

```mermaid
graph TD
    subgraph GroupBy ["GROUP BY (Collapsing)"]
        R1[Row 1: User A, $10] --> G[Group: User A]
        R2[Row 2: User A, $20] --> G
        G --> Out1[Output: User A, Sum $30]
    end

    subgraph Window ["Window Function (In-Place)"]
        W1[Row 1: User A, $10] --> O1[Row 1: User A, $10, Run Total: $10]
        W2[Row 2: User A, $20] --> O2[Row 2: User A, $20, Run Total: $30]
        W1 -. Partition & Order .-> W2
    end
```

---

## 2. Advanced PostgreSQL Implementation (How)

### Common Table Expressions (CTEs)
A CTE (declared via `WITH`) acts as a named temporary result set. In PostgreSQL 12+, CTEs are automatically inlined unless marked `MATERIALIZED`, which forces the optimizer to write the intermediate state to a temporary table.

### Query Gist: advanced_aggregations.sql
```sql
-- Gist: advanced_aggregations.sql
-- Goal: Calculate running totals, MoM growth rates, and dense ranking within partitions.

WITH daily_totals AS (
    -- Group entries by day to reduce window scan complexity
    SELECT 
        tenant_id,
        DATE_TRUNC('day', created_at) AS transaction_day,
        SUM(amount) AS daily_amount
    FROM transactions
    WHERE status = 'completed'
    GROUP BY tenant_id, DATE_TRUNC('day', transaction_day)
),

cumulative_sales AS (
    -- Window Function: Calculate running sum without collapsing days
    SELECT 
        tenant_id,
        transaction_day,
        daily_amount,
        SUM(daily_amount) OVER (
            PARTITION BY tenant_id
            ORDER BY transaction_day
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_sales_pool
    FROM daily_totals
),

monthly_comparison AS (
    -- LAG Window: Fetch previous month total within tenant partition
    SELECT 
        tenant_id,
        DATE_TRUNC('month', transaction_day) AS transaction_month,
        SUM(daily_amount) AS monthly_volume,
        LAG(SUM(daily_amount), 1) OVER (
            PARTITION BY tenant_id
            ORDER BY DATE_TRUNC('month', transaction_day)
        ) AS prev_month_volume
    FROM daily_totals
    GROUP BY tenant_id, DATE_TRUNC('month', transaction_day)
)

SELECT 
    m.tenant_id,
    m.transaction_month,
    m.monthly_volume,
    m.prev_month_volume,
    COALESCE(
        ((m.monthly_volume - m.prev_month_volume) / NULLIF(m.prev_month_volume, 0)) * 100, 
        0
    ) AS mom_growth,
    DENSE_RANK() OVER (
        PARTITION BY m.transaction_month
        ORDER BY m.monthly_volume DESC
    ) AS ranking_in_month
FROM monthly_comparison m
ORDER BY m.transaction_month DESC, ranking_in_month ASC;
```

---

## 3. SQLAlchemy v2 Integration & Session Management (How)

To execute these operations within FastAPI safely, we map them through SQLAlchemy 2.0's async model.

### The N+1 Query Bottleneck
The N+1 query problem occurs when an application loads a parent record (e.g., 50 accounts) and then loops over them to query child records (e.g., transactions). This triggers 51 database roundtrips.

```mermaid
sequenceDiagram
    autonumber
    App->>DB: SELECT * FROM accounts LIMIT 50;
    Note over DB: Returns 50 account records
    loop For each Account
        App->>DB: SELECT * FROM transactions WHERE account_id = ?;
        Note over DB: Executed 50 times
    end
```

#### Eager Loading Strategies
* **`selectinload()`**: Emits a second query using an `IN` clause with parent IDs (e.g., `SELECT ... WHERE account_id IN (1, 2...)`). **Best for One-to-Many collections**.
* **`joinedload()`**: Performs a `LEFT OUTER JOIN` in the same query. **Best for Many-to-One relationships**.

### Code Gist: optimized_analytics.py
```python
# Gist: optimized_analytics.py
import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

# Setup async engine
DATABASE_URL = "postgresql+asyncpg://postgres:secret@localhost:5432/core_db"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Async Session Dependency wrapper
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
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
    
    # lazy="raise" prevents accidental lazy loading, forcing selectinload
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="tenant", lazy="raise")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(nullable=False, index=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="completed")
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    
    tenant: Mapped["Tenant"] = relationship(back_populates="transactions")

class MetricResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    sales_date: datetime.date
    daily_sales: float
    running_cumulative_sales: float

app = FastAPI()

@app.get("/api/v1/analytics", response_model=List[MetricResponse])
async def read_metrics(
    start_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    filter_date = start_date or (datetime.date.today() - datetime.timedelta(days=30))
    
    # 1. Subquery to aggregate daily sales
    daily_summary = (
        select(
            Transaction.tenant_id,
            func.date(Transaction.created_at).label("sales_date"),
            func.sum(Transaction.amount).label("daily_sales")
        )
        .where(Transaction.status == "completed")
        .where(func.date(Transaction.created_at) >= filter_date)
        .group_by(Transaction.tenant_id, func.date(Transaction.created_at))
    ).subquery()
    
    # 2. Main query executing running total window calculations
    stmt = (
        select(
            daily_summary.c.tenant_id,
            Tenant.name.label("tenant_name"),
            daily_summary.c.sales_date,
            daily_summary.c.daily_sales,
            func.sum(daily_summary.c.daily_sales)
            .over(
                partition_by=daily_summary.c.tenant_id,
                order_by=daily_summary.c.sales_date
            )
            .label("running_cumulative_sales")
        )
        .join(Tenant, Tenant.id == daily_summary.c.tenant_id)
        .order_by(daily_summary.c.sales_date.desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        MetricResponse(
            tenant_id=row.tenant_id,
            tenant_name=row.tenant_name,
            sales_date=row.sales_date,
            daily_sales=float(row.daily_sales),
            running_cumulative_sales=float(row.running_cumulative_sales)
        )
        for row in rows
    ]
