from datetime import datetime
from pydantic import BaseModel, Field

class TransactionBase(BaseModel):
    amount: float = Field(..., description="Amount of money transferred")
    transaction_type: str = Field(..., pattern="^(deposit|withdrawal)$")

class TransactionCreate(TransactionBase):
    account_id: int

class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    account_number: str = Field(..., min_length=10, max_length=34)
    holder_name: str = Field(..., min_length=2, max_length=100)

class AccountCreate(AccountBase):
    initial_balance: float = Field(default=0.0, ge=0.0)

class AccountResponse(AccountBase):
    id: int
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Metrics Responses
class DailyAggregatedMetric(BaseModel):
    sales_date: datetime
    daily_volume: float
    running_cumulative_volume: float
