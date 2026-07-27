# Use Case: Concurrency-Safe Balance Transfer (Pessimistic + Optimistic Locking)
# Purpose: Demonstrate both defenses against the read-modify-write race:
#          SELECT FOR UPDATE for hot rows (money), version columns for cold ones.
# Key features: with_for_update, deterministic lock ordering (deadlock avoidance),
#               version_id_col + StaleDataError retry loop.
# Deps: pip install sqlalchemy[asyncio] asyncpg

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.exc import StaleDataError


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[float] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    # Optimistic lock: SQLAlchemy emits UPDATE ... WHERE id=? AND version=?
    # and raises StaleDataError when 0 rows match (a concurrent writer won).
    __mapper_args__ = {"version_id_col": version}


class InsufficientFunds(Exception):
    pass


# 1. PESSIMISTIC: SELECT FOR UPDATE — block competing writers up front.
#    Use for high-contention, must-not-fail writes (money movements).
async def transfer_pessimistic(
    session: AsyncSession, src_id: int, dst_id: int, amount: float
) -> None:
    async with session.begin():  # lock lifetime == transaction lifetime
        # Deadlock avoidance: ALWAYS lock rows in a stable order (ascending id).
        # Two transfers A->B and B->A locking in argument order deadlock each other.
        first_id, second_id = sorted((src_id, dst_id))

        rows = (
            await session.scalars(
                select(Account)
                .where(Account.id.in_([first_id, second_id]))
                .order_by(Account.id)
                .with_for_update()  # rows locked until COMMIT; readers unaffected
            )
        ).all()
        accounts = {a.id: a for a in rows}
        src, dst = accounts[src_id], accounts[dst_id]

        if src.balance < amount:
            raise InsufficientFunds(f"account {src_id}")
        src.balance -= amount
        dst.balance += amount
    # COMMIT releases both row locks; the blocked competitor now sees fresh balances.


# 2. OPTIMISTIC: version column + retry — detect the conflict instead of preventing it.
#    Use for low-contention writes (profile edits) where waiting on locks is wasteful.
async def credit_optimistic(
    session: AsyncSession, account_id: int, amount: float, max_retries: int = 3
) -> None:
    for attempt in range(max_retries):
        try:
            async with session.begin():
                acct = await session.get(Account, account_id)
                acct.balance += amount
                # flush emits: UPDATE accounts SET balance=?, version=version+1
                #              WHERE id=? AND version=?
            return  # committed cleanly — we held no lock while computing
        except StaleDataError:
            # A concurrent writer bumped the version between our read and write.
            await session.rollback()
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(0.05 * (2**attempt))  # jittered backoff in real code


# Rule of thumb: contention level chooses the strategy —
# FOR UPDATE for hot rows, version columns for cold ones.
