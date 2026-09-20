"""
Level 7, in Python — the counterpart to solutions/07_indexer.ts.

The indexer is the heart of the job, so it is worth having written it in the
language you actually think in. Nothing here is Web3-specific: a checkpoint, a
natural key, an upsert, one transaction.

Run: ./.venv/bin/python 07_indexer.py
"""

import os
import sqlite3
import tempfile
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

RPC = os.environ.get("RPC_URL", "https://polygon-amoy.drpc.org")
w3 = Web3(Web3.HTTPProvider(RPC))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)   # see 02_read_the_chain.py

NATIVE = Web3.to_checksum_address("0x0000000000000000000000000000000000001010")
LOG_FEE_TRANSFER = w3.keccak(
    text="LogFeeTransfer(address,address,address,uint256,uint256,uint256,uint256,uint256)"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS indexed_log (
  block_number INTEGER NOT NULL,
  block_hash   TEXT    NOT NULL,
  tx_hash      TEXT    NOT NULL,
  log_index    INTEGER NOT NULL,
  payer        TEXT    NOT NULL,
  -- The idempotency key, exactly as in the TypeScript. Seeing the same log
  -- twice is normal; this constraint makes it harmless.
  PRIMARY KEY (block_hash, tx_hash, log_index)
);
CREATE TABLE IF NOT EXISTS checkpoint (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  last_block INTEGER NOT NULL
);
"""


def persist_batch(conn, logs, to_block, fail_after=None):
    """Write logs and move the checkpoint in ONE transaction."""
    inserted = 0
    try:
        with conn:                       # commits on success, rolls back on exception
            for seen, log in enumerate(logs, start=1):
                cur = conn.execute(
                    """INSERT OR IGNORE INTO indexed_log
                       (block_number, block_hash, tx_hash, log_index, payer)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        log["blockNumber"],
                        log["blockHash"].hex(),
                        log["transactionHash"].hex(),
                        log["logIndex"],
                        "0x" + log["topics"][2].hex()[-40:],
                    ),
                )
                inserted += cur.rowcount
                if fail_after is not None and seen >= fail_after:
                    raise RuntimeError("simulated crash mid-batch")

            conn.execute(
                """INSERT INTO checkpoint (id, last_block) VALUES (1, ?)
                   ON CONFLICT (id) DO UPDATE SET last_block = excluded.last_block""",
                (to_block,),
            )
    except RuntimeError as error:
        return 0, str(error)
    return inserted, None


def summarise(conn):
    rows = conn.execute("SELECT COUNT(*) FROM indexed_log").fetchone()[0]
    checkpoint = conn.execute("SELECT last_block FROM checkpoint WHERE id = 1").fetchone()
    fingerprint = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(log_index), 0), COALESCE(MAX(block_number), 0) FROM indexed_log"
    ).fetchone()
    return rows, (checkpoint[0] if checkpoint else 0), ":".join(str(x) for x in fingerprint)


head = w3.eth.block_number
from_block = head - 20
logs = w3.eth.get_logs(
    {"address": NATIVE, "topics": [LOG_FEE_TRANSFER], "fromBlock": from_block, "toBlock": head}
)
print(f"fetched {len(logs)} logs from blocks {from_block}–{head}\n")

# --- Part 1: the same range, twice ----------------------------------------

clean = sqlite3.connect(os.path.join(tempfile.gettempdir(), "metaspace-py-clean.sqlite"))
clean.executescript("DROP TABLE IF EXISTS indexed_log; DROP TABLE IF EXISTS checkpoint;" + SCHEMA)

print("--- Part 1: the same range, indexed twice ---")
first, _ = persist_batch(clean, logs, head)
second, _ = persist_batch(clean, logs, head)
print(f"first pass  : {first} inserted")
print(f"second pass : {second} inserted")
print(f"checkpoint  : {summarise(clean)[1]}")

# --- Part 2: crash mid-batch ----------------------------------------------

print("\n--- Part 2: crash halfway through, then restart ---")
crashed = sqlite3.connect(os.path.join(tempfile.gettempdir(), "metaspace-py-crash.sqlite"))
crashed.executescript("DROP TABLE IF EXISTS indexed_log; DROP TABLE IF EXISTS checkpoint;" + SCHEMA)

_, error = persist_batch(crashed, logs, head, fail_after=max(1, len(logs) // 2))
print("crashed with:", error)
print("rows after crash      :", summarise(crashed)[0])
print("checkpoint after crash:", summarise(crashed)[1])

persist_batch(crashed, logs, head)
a, b = summarise(clean), summarise(crashed)
print(f"\nclean run   : {a[0]} rows, fingerprint {a[2]}")
print(f"crashed run : {b[0]} rows, fingerprint {b[2]}")
print(f"identical   : {a[2] == b[2]}")

print(
    "\nThe same property as the TypeScript, reached with `with conn:` instead of\n"
    "BEGIN/COMMIT — sqlite3's context manager commits on success and rolls back\n"
    "on an exception, so the rows and the checkpoint move together or not at all.\n"
    "This is the part of the job where Python is not merely adequate but genuinely\n"
    "comfortable: it is an ETL pipeline with a checkpoint, and Python has been the\n"
    "right language for that for twenty years."
)
