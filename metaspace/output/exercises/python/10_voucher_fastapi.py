"""
Level 10, in Python — the voucher service as FastAPI.

This is the file to read if you are asked "how would you build this in your own
stack?" It is the same three endpoints as the Express version, with the same
two guarantees: the voucher is EIP-712 typed data, and issuing one is
idempotent on the reward id.

Run:  ./.venv/bin/pip install "web3>=8" fastapi "uvicorn[standard]" httpx
      ./.venv/bin/python 10_voucher_fastapi.py          # runs a self-test
      ./.venv/bin/uvicorn 10_voucher_fastapi:app        # or serve it
"""

import sqlite3
import time
import uuid

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BACKEND_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
backend_signer = Account.from_key(BACKEND_KEY)
CONTRACT = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
CHAIN_ID = 80002

db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript(
    """
    CREATE TABLE reward (
      reward_id  TEXT PRIMARY KEY,
      player     TEXT    NOT NULL,
      item_id    INTEGER NOT NULL,
      amount     INTEGER NOT NULL,
      voucher_id INTEGER NOT NULL UNIQUE,
      signature  TEXT    NOT NULL,
      deadline   INTEGER NOT NULL
    );
    """
)

app = FastAPI(title="Metaspace voucher service")


class ClaimRequest(BaseModel):
    player: str
    item_id: int = 42
    amount: int = 1


def sign_voucher(player: str, item_id: int, amount: int, voucher_id: int, deadline: int) -> str:
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Voucher": [
                {"name": "to", "type": "address"},
                {"name": "itemId", "type": "uint256"},
                {"name": "amount", "type": "uint256"},
                {"name": "voucherId", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "primaryType": "Voucher",
        "domain": {
            "name": "Metaspace Items",
            "version": "1",
            "chainId": CHAIN_ID,
            "verifyingContract": CONTRACT,
        },
        "message": {
            "to": player,
            "itemId": item_id,
            "amount": amount,
            "voucherId": voucher_id,
            "deadline": deadline,
        },
    }
    signed = Account.sign_message(encode_typed_data(full_message=typed), private_key=backend_signer.key)
    return "0x" + signed.signature.hex().removeprefix("0x")


@app.post("/rewards/{reward_id}/claim")
def claim(reward_id: str, request: ClaimRequest):
    existing = db.execute(
        "SELECT player, item_id, amount, voucher_id, signature, deadline FROM reward WHERE reward_id = ?",
        (reward_id,),
    ).fetchone()

    if existing:
        # The retry path. Same voucher, every time, forever.
        player, item_id, amount, voucher_id, signature, deadline = existing
        return {
            "reused": True,
            "voucher": {
                "to": player,
                "itemId": item_id,
                "amount": amount,
                "voucherId": voucher_id,
                "deadline": deadline,
            },
            "signature": signature,
        }

    voucher_id = int(time.time() * 1000)
    deadline = int(time.time()) + 3600
    signature = sign_voucher(request.player, request.item_id, request.amount, voucher_id, deadline)

    try:
        with db:
            db.execute(
                """INSERT INTO reward (reward_id, player, item_id, amount, voucher_id, signature, deadline)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (reward_id, request.player, request.item_id, request.amount, voucher_id, signature, deadline),
            )
    except sqlite3.IntegrityError:
        # Another request won the race between our SELECT and our INSERT. The
        # constraint is the concurrency control; this except block is not error
        # handling, it is the happy path of a race we expect to lose sometimes.
        raise HTTPException(status_code=409, detail="voucher already issued")

    return {
        "reused": False,
        "voucher": {
            "to": request.player,
            "itemId": request.item_id,
            "amount": request.amount,
            "voucherId": voucher_id,
            "deadline": deadline,
        },
        "signature": signature,
    }


@app.get("/health")
def health():
    return {"signer": backend_signer.address, "contract": CONTRACT, "chainId": CHAIN_ID}


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    print("health      :", client.get("/health").json())

    first = client.post("/rewards/dungeon-run-77/claim", json={"player": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}).json()
    again = client.post("/rewards/dungeon-run-77/claim", json={"player": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}).json()

    print("first claim :", first["voucher"]["voucherId"], "reused:", first["reused"])
    print("retry       :", again["voucher"]["voucherId"], "reused:", again["reused"])
    print("same voucher:", first["voucher"]["voucherId"] == again["voucher"]["voucherId"])
    print("same sig    :", first["signature"] == again["signature"])

    type_hash = keccak(
        b"Voucher(address to,uint256 itemId,uint256 amount,uint256 voucherId,uint256 deadline)"
    )
    print("type hash   : 0x" + type_hash.hex())
    print(
        "\nThat type hash matches the TypeScript in `npm run l10` and the constant\n"
        "solc embedded in ItemLedgerV3. Three languages, one set of bytes — which\n"
        "is the point worth making if anyone asks whether the backend has to be\n"
        "Node. It does not. The contract cannot tell what signed its voucher."
    )
