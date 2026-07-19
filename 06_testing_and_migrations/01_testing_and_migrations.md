# Database Migrations & Async Testing Frameworks Masterclass

A deep-dive academic guide to managing database migrations using Alembic and testing asynchronous FastAPI routers with Pytest.

---

## 1. Migrations Management & Safety Policies (Why & What)

In production databases containing millions of rows, deploying migrations blindly will result in server outages.

### The DDL Table Lock Issue
Executing Data Definition Language (DDL) operations (like `ALTER TABLE ADD COLUMN` with a non-nullable default value) forces PostgreSQL to acquire an exclusive lock (`AccessExclusiveLock`) on the target table. While this lock is active, all incoming SELECT, INSERT, and UPDATE queries are blocked, causing API requests to queue up and time out.

### The Mitigation Plan (The Safe Migration Pattern)
To deploy database changes without table locks:
1. **Add the Column as Nullable first**: 
   ```sql
   ALTER TABLE transactions ADD COLUMN status VARCHAR(20) NULL;
   ```
2. **Deploy the updated application code** to write to the new column, using a fallback value if the column is null.
3. **Seed existing records in batches** via a background migration script to update null fields to defaults.
4. **Apply a non-nullable constraint concurrently** if necessary.

---

## 2. Asynchronous Testing Frameworks (Why & How)

Testing asynchronous backends requires configuring testing frameworks to support concurrent I/O.

### Testing Async Web Handlers
FastAPI handles requests asynchronously. When writing unit tests using Pytest, you cannot use standard blocking clients. 
* **The Solution**: Use the `httpx.AsyncClient` library alongside `pytest-asyncio` fixtures, allowing tests to await endpoint executions natively.
* **Dependency Overrides**: In conftest files, override the database dependency injection logic (`get_db_session`) to point to an isolated in-memory SQLite database, ensuring tests run in complete isolation.

---

## 3. Testing Implementation Blueprints (How)

### Gist: pytest_async_conftest.py
A complete `conftest.py` file setting up async SQLite in-memory databases and overriding database dependency injections.

```python
# Gist: pytest_async_conftest.py
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app, get_db_session  # Assume models are imported
from app.models import Base

# 1. Initialize isolated async database engine in memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# 2. Database setup and teardown fixture
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    # Create tables before each test execution
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after test completes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 3. Session injector override
@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.close()

# 4. HTTP client wrapper running against the overridden app
@pytest_asyncio.fixture
async def test_client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override database dependency injection
    app.dependency_overrides[get_db_session] = lambda: test_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Gist: test_analytics_api.py
An integration test verifying the cumulative analytics API.

```python
# Gist: test_analytics_api.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Transaction

@pytest.mark.asyncio
async def test_get_cumulative_sales_api(test_client: AsyncClient, test_session: AsyncSession):
    # 1. Seed database records
    tenant = Tenant(id=1, name="Test Tenant")
    test_session.add(tenant)
    await test_session.commit()

    tx = Transaction(tenant_id=1, amount=150.0, status="completed")
    test_session.add(tx)
    await test_session.commit()

    # 2. Fetch endpoint
    response = await test_client.get("/api/v1/analytics/cumulative-sales")

    # 3. Assert correct response structure
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_name"] == "Test Tenant"
    assert data[0]["daily_sales"] == 150.0
    assert data[0]["running_cumulative_sales"] == 150.0
```
