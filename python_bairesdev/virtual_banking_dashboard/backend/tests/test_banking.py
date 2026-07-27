import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.banking import Account

@pytest.mark.asyncio
async def test_create_and_read_account(client: AsyncClient, db_session: AsyncSession):
    # 1. Create a banking account via API post
    payload = {
        "account_number": "FR7630006000011234567890123",
        "holder_name": "John Doe",
        "initial_balance": 1000.00
    }
    create_response = await client.post("/api/v1/accounts", json=payload)
    assert create_response.status_code == 200
    created_data = create_response.json()
    assert created_data["holder_name"] == "John Doe"
    assert created_data["balance"] == 1000.00

    # 2. Get list of accounts to assert presence
    list_response = await client.get("/api/v1/accounts")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1
    assert list_data[0]["account_number"] == "FR7630006000011234567890123"
