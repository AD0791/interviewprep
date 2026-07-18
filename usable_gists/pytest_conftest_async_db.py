# Use Case: Async Test Database Fixtures (Pytest)
# Purpose: Configures isolated async connection session overrides for FastAPI routing suites.
# Key features: pytest_asyncio fixtures, in-memory SQLite config, and FastAPI dependency overrides.

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app, get_db_session  # Assume boilerplate app path
from app.models import Base  # Assume declarative base path

# 1. Setup isolated in-memory test database engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)

# 2. Database setup and teardown fixture
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    # Create tables before each test runs
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after each test completes
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 3. Override dependency fixture
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.close()

# 4. HTTP client fixture running against the overridden app
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override FastAPI dependency injection
    app.dependency_overrides[get_db_session] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    # Clean overrides
    app.dependency_overrides.clear()
