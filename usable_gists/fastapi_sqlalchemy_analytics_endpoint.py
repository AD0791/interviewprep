# Use Case: Highly Optimized FastAPI Analytics Endpoint (SQLAlchemy 2.0)
# Purpose: Fetches timeseries metrics using subqueries and window functions, avoiding N+1 queries.
# Key features: SQLAlchemy v2 async subquery, window functions, and Pydantic v2 schemas.

import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session  # Assume boilerplate session injection
from app.models import Tenant, Transaction  # Assume ORM models path

class TenantSalesMetric(BaseModel):
    tenant_id: int
    tenant_name: str
    sales_date: datetime.date
    daily_sales: float
    running_cumulative_sales: float

    class Config:
        from_attributes = True

app = FastAPI()

@app.get("/api/v1/analytics/cumulative-sales", response_model=List[TenantSalesMetric])
async def get_cumulative_sales(
    start_date: Optional[datetime.date] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    # Set default date range to past 30 days
    filter_date = start_date or (datetime.date.today() - datetime.timedelta(days=30))
    
    # 1. Define Subquery to aggregate raw transaction amount by date/tenant
    daily_summary_stmt = (
        select(
            Transaction.tenant_id,
            func.date(Transaction.created_at).label("sales_date"),
            func.sum(Transaction.amount).label("daily_sales")
        )
        .where(Transaction.status == "completed")
        .where(func.date(Transaction.created_at) >= filter_date)
        .group_by(Transaction.tenant_id, func.date(Transaction.created_at))
    ).subquery()
    
    # 2. Main Query combining Subquery with SQL Window Functions and Tenant Join
    # Why Join: Eagerly fetches Tenant names in a single database roundtrip, avoiding N+1
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
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        TenantSalesMetric(
            tenant_id=row.tenant_id,
            tenant_name=row.tenant_name,
            sales_date=row.sales_date,
            daily_sales=float(row.daily_sales),
            running_cumulative_sales=float(row.running_cumulative_sales)
        )
        for row in rows
    ]
