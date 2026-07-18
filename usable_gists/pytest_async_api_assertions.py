# Use Case: Async API Route Integration Test
# Purpose: Seeds database, calls endpoints asynchronously, and asserts response models.
# Key features: pytest.mark.asyncio, session seeding, and HTTP status/schema validations.

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Transaction  # Assume models path

@pytest.mark.asyncio
async def test_get_cumulative_sales_success(client: AsyncClient, db_session: AsyncSession):
    # 1. Seed isolated test database records
    test_tenant = Tenant(id=1, name="Acme Corp")
    db_session.add(test_tenant)
    await db_session.commit()

    test_transaction = Transaction(tenant_id=1, amount=100.0, status="completed")
    db_session.add(test_transaction)
    await db_session.commit()

    # 2. Execute target route asynchronously using httpx client
    response = await client.get("/api/v1/analytics/cumulative-sales")

    # 3. Assert correct response structure
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_name"] == "Acme Corp"
    assert data[0]["daily_sales"] == 100.0
    assert data[0]["running_cumulative_sales"] == 100.0
