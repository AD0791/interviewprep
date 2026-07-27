from typing import List, Protocol
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.banking import Account, Transaction

# 1. Repository Protocol Interface
class BankingRepository(Protocol):
    async def get_accounts(self) -> List[Account]:
        ...
    async def create_account(self, account: Account) -> Account:
        ...
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        ...
    async def get_cumulative_volume(self) -> List[tuple]:
        ...

# 2. Database implementation
class SQLBankingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_accounts(self) -> List[Account]:
        stmt = select(Account).order_by(Account.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_account(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        return account

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        # A. Insert transaction record
        self.session.add(transaction)
        await self.session.flush()

        # B. Update target Account balance (Unit of Work aggregation)
        account_stmt = select(Account).where(Account.id == transaction.account_id)
        account_result = await self.session.execute(account_stmt)
        account = account_result.scalar_one()

        if transaction.transaction_type == "deposit":
            account.balance = float(account.balance) + float(transaction.amount)
        elif transaction.transaction_type == "withdrawal":
            if float(account.balance) < float(transaction.amount):
                raise ValueError("Insufficient balance to execute withdrawal transaction")
            account.balance = float(account.balance) - float(transaction.amount)

        return transaction

    async def get_cumulative_volume(self) -> List[tuple]:
        # Perform advanced Window function directly in database
        daily_summary_stmt = (
            select(
                func.date_trunc('day', Transaction.created_at).label("sales_date"),
                func.sum(Transaction.amount).label("daily_volume")
            )
            .where(Transaction.status == "completed")
            .group_by(func.date_trunc('day', Transaction.created_at))
        ).subquery()

        stmt = (
            select(
                daily_summary_stmt.c.sales_date,
                daily_summary_stmt.c.daily_volume,
                func.sum(daily_summary_stmt.c.daily_volume)
                .over(
                    order_by=daily_summary_stmt.c.sales_date
                )
                .label("running_cumulative_volume")
            )
            .order_by(daily_summary_stmt.c.sales_date.asc())
        )

        result = await self.session.execute(stmt)
        return list(result.all())
