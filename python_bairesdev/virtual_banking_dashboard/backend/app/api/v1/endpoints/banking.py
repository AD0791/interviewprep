from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.repositories.banking import SQLBankingRepository, BankingRepository
from app.schemas.banking import AccountCreate, AccountResponse, TransactionCreate, TransactionResponse, DailyAggregatedMetric
from app.models.banking import Account, Transaction

router = APIRouter()

@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(db: AsyncSession = Depends(get_db_session)):
    repo: BankingRepository = SQLBankingRepository(db)
    return await repo.get_accounts()

@router.post("/accounts", response_model=AccountResponse)
async def create_account(account_in: AccountCreate, db: AsyncSession = Depends(get_db_session)):
    repo: BankingRepository = SQLBankingRepository(db)
    new_account = Account(
        account_number=account_in.account_number,
        holder_name=account_in.holder_name,
        balance=account_in.initial_balance
    )
    return await repo.create_account(new_account)

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(tx_in: TransactionCreate, db: AsyncSession = Depends(get_db_session)):
    repo: BankingRepository = SQLBankingRepository(db)
    new_tx = Transaction(
        account_id=tx_in.account_id,
        amount=tx_in.amount,
        transaction_type=tx_in.transaction_type
    )
    try:
        return await repo.create_transaction(new_tx)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/cumulative-volume", response_model=List[DailyAggregatedMetric])
async def get_cumulative_volume(db: AsyncSession = Depends(get_db_session)):
    repo: BankingRepository = SQLBankingRepository(db)
    rows = await repo.get_cumulative_volume()
    return [
        DailyAggregatedMetric(
            sales_date=row.sales_date,
            daily_volume=float(row.daily_volume),
            running_cumulative_volume=float(row.running_cumulative_volume)
        )
        for row in rows
    ]
