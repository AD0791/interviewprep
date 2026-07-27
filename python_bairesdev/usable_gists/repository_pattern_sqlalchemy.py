# Use Case: Decoupled Data Access Layer (Repository Pattern)
# Purpose: Abstract database queries from routing controllers to simplify testing.
# Key features: Python typing Protocols, SQLAlchemy v2 mappings, and dependency injection.

from typing import List, Protocol
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Transaction  # Assume ORM model path

# 1. Define Repository Interface (Protocol)
# Why: Enables mocking transactions during unit testing without accessing database engines
class TransactionRepository(Protocol):
    async def get_by_tenant(self, tenant_id: int) -> List[Transaction]:
        ...
    async def create(self, transaction: Transaction) -> Transaction:
        ...

# 2. SQL Implementation of Repository Interface
class SQLTransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tenant(self, tenant_id: int) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.tenant_id == tenant_id)
            .order_by(Transaction.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.flush() # Sync with database to populate primary key IDs
        return transaction

# 3. FastAPI Endpoint Dependency Injection Integration
from fastapi import APIRouter, Depends
from app.database import get_db_session  # Assume async session generator

router = APIRouter()

@router.get("/transactions/{tenant_id}")
async def read_transactions(
    tenant_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    # Bind async session dynamically
    repo: TransactionRepository = SQLTransactionRepository(db)
    
    # Clean controller mapping, zero database queries inside route logic
    transactions = await repo.get_by_tenant(tenant_id)
    return transactions
