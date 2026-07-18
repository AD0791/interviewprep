from datetime import datetime
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_number: Mapped[str] = mapped_column(String(34), unique=True, index=True)
    holder_name: Mapped[str] = mapped_column(String(100), index=True)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # One-to-many relationship: an account has many transactions
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="raise" # Enforce strict joinedload/selectinload loading rules
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    transaction_type: Mapped[str] = mapped_column(String(20)) # "deposit" or "withdrawal"
    status: Mapped[str] = mapped_column(String(20), default="completed") # "completed", "failed"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
