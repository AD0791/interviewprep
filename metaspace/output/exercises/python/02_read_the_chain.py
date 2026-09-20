"""
Level 2, in Python — the counterpart to solutions/02_read_the_chain.ts.

Run:  python -m venv .venv && ./.venv/bin/pip install "web3>=8"
      ./.venv/bin/python 02_read_the_chain.py

Read this beside the TypeScript. The shape is identical because the shape is
the JSON-RPC, not the library: a client, a chain id you assert, blocks, a
finality tag, a balance, a fee estimate.
"""

import os
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

RPC = os.environ.get("RPC_URL", "https://polygon-amoy.drpc.org")
w3 = Web3(Web3.HTTPProvider(RPC))

# WITHOUT THIS LINE, web3.py CANNOT READ A POLYGON BLOCK AT ALL.
#
# Polygon (like BSC and most proof-of-authority chains) puts more than 32 bytes
# in a block's extraData field, and web3.py validates that field against the
# Ethereum mainnet rule. Calling get_block without the middleware raises:
#
#   web3.exceptions.ExtraDataLengthError: The field extraData is 105 bytes,
#   but should be 32. It is quite likely that you are connected to a POA chain.
#
# viem has no equivalent step: its polygonAmoy chain definition already knows.
# This is the single most common first hour of Python-on-Polygon, and it is a
# fair summary of the difference between the two ecosystems — Python needs you
# to know one more thing, and tells you so only after it fails.
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

chain_id = w3.eth.chain_id
print("--- who am I talking to ---")
print("chain id          :", chain_id, "(Amoy)" if chain_id == 80002 else "(NOT Amoy!)")

latest = w3.eth.get_block("latest")
print("\n--- the head block ---")
print("number            :", latest["number"])
print("parentHash        :", latest["parentHash"].hex())
# NOTE: after the POA middleware runs, the field is renamed to
# "proofOfAuthorityData" — so code that reads latest["extraData"] now raises
# KeyError. The fix for one problem creates a second, smaller one.
print("transactions      :", len(latest["transactions"]))
print("gasUsed / gasLimit:", latest["gasUsed"], "/", latest["gasLimit"])
print("baseFeePerGas     :", w3.from_wei(latest.get("baseFeePerGas", 0), "gwei"), "gwei")

finalized = w3.eth.get_block("finalized")
print("\n--- finality ---")
print("latest    :", latest["number"])
print("finalized :", finalized["number"])
print("lag       :", latest["number"] - finalized["number"], "blocks")

someone = Web3.to_checksum_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
print("\n--- an account ---")
print("balance :", w3.from_wei(w3.eth.get_balance(someone), "ether"), "POL")
print("nonce   :", w3.eth.get_transaction_count(someone))

print("\n--- fee market ---")
print("gas price      :", w3.from_wei(w3.eth.gas_price, "gwei"), "gwei")
print("max priority   :", w3.from_wei(w3.eth.max_priority_fee, "gwei"), "gwei")

print(
    "\nThree differences from the TypeScript, and only one of them favours\n"
    "TypeScript. Python returns plain ints, because Python integers are already\n"
    "arbitrary precision — so the entire class of bigint mistakes in article 09\n"
    "does not exist here, and that is a real advantage. Against that: blocks come\n"
    "back as dict-like AttributeDicts with no static typing, so a mistyped key is\n"
    "a runtime KeyError rather than a compile error. And the chain had to be\n"
    "taught to the library rather than being known by it."
)
