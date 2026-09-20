"""
Level 4, in Python — the counterpart to solutions/04_sign_and_recover.ts.

Signing and recovery are where Python is at its strongest in this stack:
eth-account is mature, the API is small, and nothing about it is awkward.

Run: ./.venv/bin/python 04_sign_and_recover.py     (no network, no funds)
"""

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
from eth_utils import keccak

# Anvil account #0: published in every toolchain's docs, holds nothing.
PLAYER_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
player = Account.from_key(PLAYER_KEY)

# --- Part 1: sign, then recover -------------------------------------------

message = "Log me in to Metaspace"
signable = encode_defunct(text=message)          # this applies the EIP-191 prefix
signed = Account.sign_message(signable, private_key=player.key)

print("--- Part 1: the round trip ---")
print("signer address :", player.address)
print("signature      :", signed.signature.hex()[:24] + "…")
print("  r :", hex(signed.r)[:20] + "…")
print("  s :", hex(signed.s)[:20] + "…")
print("  v :", signed.v)

recovered = Account.recover_message(signable, signature=signed.signature)
print("recovered      :", recovered)
print("matches signer :", recovered == player.address)

# --- Part 2: the prefix, by hand ------------------------------------------

prefix = f"\x19Ethereum Signed Message:\n{len(message)}".encode()
by_hand = keccak(prefix + message.encode())

print("\n--- Part 2: what actually got signed ---")
print("hash by hand   :", by_hand.hex())
print("eth-account's  :", signable.body.hex() if hasattr(signable, "body") else "n/a")
print(
    "\nSame construction as the TypeScript: the key never signs your message, it\n"
    "signs a hash of the message with a fixed prefix glued on, and that prefix is\n"
    "what makes the signature structurally unable to be a transaction (EIP-191)."
)

# --- Part 3: the replay ---------------------------------------------------

print("\n--- Part 3: the replay ---")
for attempt in ("first login", "an hour later", "from anywhere, forever"):
    ok = Account.recover_message(signable, signature=signed.signature) == player.address
    print(f"  {attempt:<26} -> {ok}")

print(
    "\nIdentical to the TypeScript, and identically broken: a bare signature is a\n"
    "bearer token with no expiry. The fix is server-side state — a nonce issued,\n"
    "recorded and burned in one statement — not anything the wallet can do.\n"
)

# --- Part 4: EIP-712, the voucher -----------------------------------------

print("--- Part 4: typed data ---")

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
        "chainId": 80002,
        "verifyingContract": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    },
    "message": {
        "to": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "itemId": 42,
        "amount": 1,
        "voucherId": 9001,
        "deadline": 4102444800,
    },
}

signable_typed = encode_typed_data(full_message=typed)
signed_typed = Account.sign_message(signable_typed, private_key=player.key)
recovered_typed = Account.recover_message(signable_typed, signature=signed_typed.signature)

type_hash = keccak(
    b"Voucher(address to,uint256 itemId,uint256 amount,uint256 voucherId,uint256 deadline)"
)

print("type hash      :", type_hash.hex())
print("signature      :", signed_typed.signature.hex()[:24] + "…")
print("recovered      :", recovered_typed == player.address)
print(
    "\nThat type hash is the SAME 32 bytes the TypeScript computes and the same\n"
    "bytes solc embedded in the contract — run `npm run l10` and compare. Which\n"
    "is the real headline of this whole file: the interoperability is at the\n"
    "protocol, not the library. A Python backend can sign vouchers that a\n"
    "Solidity contract written against a TypeScript reference implementation\n"
    "accepts, because all three are hashing the same bytes."
)
