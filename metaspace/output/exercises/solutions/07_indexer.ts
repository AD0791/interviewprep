/**
 * Level 7 — A checkpointed, idempotent indexer.
 *
 * Use case:  The game must answer "what does this player own?" in a
 *            millisecond, from Postgres, without ever calling an RPC. That
 *            means something has to copy chain events into your database and
 *            keep doing it forever, surviving restarts, duplicates and
 *            provider failures.
 * Purpose:   Build that thing, then abuse it: run the same range twice, and
 *            crash it mid-batch. Prove the database is identical either way.
 * Key facts: Delivery is at-least-once, so ingestion must be idempotent. The
 *            natural key of a log is (blockHash, transactionHash, logIndex).
 *            The checkpoint must move in the SAME transaction as the rows it
 *            accounts for, or the two can disagree after a crash.
 *
 * Storage:   node:sqlite, built into Node 24 — nothing to install. Every
 *            statement here is deliberately ordinary SQL; the Postgres version
 *            differs only in the upsert syntax, noted inline.
 *
 * Run: npm run l7        (network required; read-only; no key involved)
 */

import { DatabaseSync } from "node:sqlite";
import { createPublicClient, http, parseAbiItem, type Address } from "viem";
import { polygonAmoy } from "viem/chains";
import { tmpdir } from "node:os";
import { join } from "node:path";

const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

const NATIVE: Address = "0x0000000000000000000000000000000000001010";
const logFeeTransfer = parseAbiItem(
  "event LogFeeTransfer(address indexed token, address indexed from, address indexed to, uint256 amount, uint256 input1, uint256 input2, uint256 output1, uint256 output2)",
);

// ---------------------------------------------------------------------------
// The schema. Every constraint here prevents a specific failure.
// ---------------------------------------------------------------------------

const SCHEMA = `
CREATE TABLE IF NOT EXISTS indexed_log (
  block_number  INTEGER NOT NULL,
  block_hash    TEXT    NOT NULL,
  tx_hash       TEXT    NOT NULL,
  log_index     INTEGER NOT NULL,
  payer         TEXT    NOT NULL,
  amount        TEXT    NOT NULL,   -- a 256-bit integer; TEXT, never a float
  -- The idempotency key. Seeing the same log twice is normal, not exceptional:
  -- a retry, an overlapping range, a restart. This constraint turns "have I
  -- seen this?" from a question the code asks into one the database answers.
  PRIMARY KEY (block_hash, tx_hash, log_index)
);

-- One row per block we have seen, so level 8 can ask "is the chain still the
-- chain I indexed?" You cannot detect a reorg without having recorded hashes.
CREATE TABLE IF NOT EXISTS indexed_block (
  block_number INTEGER PRIMARY KEY,
  block_hash   TEXT NOT NULL
);

-- The checkpoint. A single row, moved only inside the same transaction as the
-- logs it accounts for.
CREATE TABLE IF NOT EXISTS checkpoint (
  id               INTEGER PRIMARY KEY CHECK (id = 1),
  last_block       INTEGER NOT NULL
);
`;

function openDatabase(path: string): DatabaseSync {
  const db = new DatabaseSync(path);
  db.exec(SCHEMA);
  return db;
}

// ---------------------------------------------------------------------------
// The indexer.
// ---------------------------------------------------------------------------

async function fetchRange(fromBlock: bigint, toBlock: bigint) {
  return client.getLogs({ address: NATIVE, event: logFeeTransfer, fromBlock, toBlock });
}

// Let viem's inference define the row shape rather than hand-writing it. Doing
// this by hand is how you end up asserting that `args.from` is always present
// when the ABI says it may not be — the compiler catches that, and it is right
// to: a log whose topics did not decode really can arrive with missing args.
type FeeLog = Awaited<ReturnType<typeof fetchRange>>[number];

/**
 * Persist one batch and move the checkpoint, in a single transaction.
 * `failAfter` exists only to simulate a crash: it throws after that many rows,
 * from inside the transaction.
 */
function persistBatch(
  db: DatabaseSync,
  logs: readonly FeeLog[],
  toBlock: bigint,
  failAfter = Infinity,
): { inserted: number; skipped: number } {
  const insertLog = db.prepare(
    // SQLite's "OR IGNORE" is Postgres's "ON CONFLICT DO NOTHING". Same idea:
    // a duplicate is a no-op, not an error, because duplicates are expected.
    `INSERT OR IGNORE INTO indexed_log
       (block_number, block_hash, tx_hash, log_index, payer, amount)
     VALUES (?, ?, ?, ?, ?, ?)`,
  );
  const insertBlock = db.prepare(
    `INSERT OR REPLACE INTO indexed_block (block_number, block_hash) VALUES (?, ?)`,
  );
  const moveCheckpoint = db.prepare(
    `INSERT INTO checkpoint (id, last_block) VALUES (1, ?)
       ON CONFLICT (id) DO UPDATE SET last_block = excluded.last_block`,
  );

  let inserted = 0;
  let seen = 0;

  // Everything below is one transaction. If anything throws, the rows AND the
  // checkpoint roll back together, which is the only reason a crash is safe.
  db.exec("BEGIN");
  try {
    for (const log of logs) {
      const result = insertLog.run(
        Number(log.blockNumber),
        log.blockHash,
        log.transactionHash,
        log.logIndex,
        log.args.from ?? "",
        String(log.args.amount ?? 0n),
      );
      if (result.changes > 0) inserted += 1;
      insertBlock.run(Number(log.blockNumber), log.blockHash);

      seen += 1;
      if (seen >= failAfter) throw new Error("simulated crash mid-batch");
    }
    moveCheckpoint.run(Number(toBlock));
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }

  return { inserted, skipped: logs.length - inserted };
}

function readCheckpoint(db: DatabaseSync): number {
  const row = db.prepare("SELECT last_block FROM checkpoint WHERE id = 1").get() as
    | { last_block: number }
    | undefined;
  return row?.last_block ?? 0;
}

function summarise(db: DatabaseSync) {
  const rows = db.prepare("SELECT COUNT(*) AS n FROM indexed_log").get() as { n: number };
  const fingerprint = db
    .prepare(
      `SELECT COUNT(*) AS n, COALESCE(SUM(log_index), 0) AS s, COALESCE(MAX(block_number), 0) AS m
         FROM indexed_log`,
    )
    .get() as { n: number; s: number; m: number };
  return { rows: rows.n, fingerprint: `${fingerprint.n}:${fingerprint.s}:${fingerprint.m}` };
}

// ---------------------------------------------------------------------------
// Part 1 — index a range, then index it again.
// ---------------------------------------------------------------------------

const head = await client.getBlockNumber();
const from = head - 20n;
const logs = await fetchRange(from, head);

console.log(`fetched ${logs.length} logs from blocks ${from}–${head}\n`);

const cleanPath = join(tmpdir(), `metaspace-indexer-clean-${Date.now()}.sqlite`);
const clean = openDatabase(cleanPath);

console.log("--- Part 1: the same range, indexed twice ---");
const first = persistBatch(clean, logs, head);
console.log(`first pass  : ${first.inserted} inserted, ${first.skipped} already present`);
const second = persistBatch(clean, logs, head);
console.log(`second pass : ${second.inserted} inserted, ${second.skipped} already present`);
console.log(`checkpoint  : ${readCheckpoint(clean)}`);
console.log(
  "\nThe second pass did no work and caused no error, which is the property the\n" +
    "whole design turns on. Delivery from any real source is at-least-once: you\n" +
    "will re-request a range after a timeout, you will overlap ranges on restart,\n" +
    "and a provider will occasionally hand you a log twice. If reprocessing were\n" +
    "harmful, every one of those ordinary events would corrupt a player's\n" +
    "inventory. Because the primary key rejects duplicates, reprocessing is free\n" +
    "and the indexer can be careless in exactly the right way.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — crash it mid-batch.
// ---------------------------------------------------------------------------

console.log("--- Part 2: crash halfway through, then restart ---");

const crashPath = join(tmpdir(), `metaspace-indexer-crash-${Date.now()}.sqlite`);
const crashed = openDatabase(crashPath);

try {
  persistBatch(crashed, logs, head, Math.floor(logs.length / 2));
} catch (error) {
  console.log(`crashed with: ${(error as Error).message}`);
}

console.log(`rows after crash      : ${summarise(crashed).rows}`);
console.log(`checkpoint after crash: ${readCheckpoint(crashed)}`);
console.log(
  "\nZero rows and a checkpoint of zero. Not 'half the rows' — the transaction\n" +
    "rolled back, so the crash left no trace at all. This is why the checkpoint\n" +
    "must move inside the same transaction as the rows: if it were a separate\n" +
    "write, a crash between the two would leave the database claiming to have\n" +
    "processed blocks it never wrote, and those events would be lost permanently\n" +
    "and silently.\n",
);

const resumed = persistBatch(crashed, logs, head);
console.log(`after restart         : ${resumed.inserted} inserted, checkpoint ${readCheckpoint(crashed)}`);

const a = summarise(clean);
const b = summarise(crashed);
console.log(`\nclean run   : ${a.rows} rows, fingerprint ${a.fingerprint}`);
console.log(`crashed run : ${b.rows} rows, fingerprint ${b.fingerprint}`);
console.log(`identical   : ${a.fingerprint === b.fingerprint}`);

console.log(
  "\nThat equality is the whole exercise. An indexer interrupted at an arbitrary\n" +
    "point and restarted converges on exactly the state it would have reached had\n" +
    "nothing gone wrong — which means a crash, a deploy, an OOM kill or a provider\n" +
    "outage is a non-event rather than an incident.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — what this buys the game, and what is still missing.
// ---------------------------------------------------------------------------

console.log("--- Part 3: the query the game actually runs ---");

const top = clean
  .prepare(
    `SELECT payer, COUNT(*) AS transactions
       FROM indexed_log
      GROUP BY payer
      ORDER BY transactions DESC
      LIMIT 3`,
  )
  .all() as { payer: string; transactions: number }[];

for (const row of top) console.log(`  ${row.payer}: ${row.transactions} fee payments`);

console.log(
  "\nThat query touched no RPC at all, which is the point of the entire\n" +
    "exercise: the chain is the source of truth for ownership, the\n" +
    "database is the source of truth for speed, and the indexer is the one-way\n" +
    "bridge. Swap LogFeeTransfer for TransferSingle and this is a game inventory.\n\n" +
    "Two things are still missing, and naming them yourself is worth more in an\n" +
    "interview than hiding them. First, this indexes a fixed range rather than\n" +
    "looping from its checkpoint forever — the loop is mechanical, the correctness\n" +
    "is what you just built. Second, and seriously: it trusts that the blocks it\n" +
    "read are still the chain. They may not be. Level 8 detects that and unwrites.",
);

clean.close();
crashed.close();
console.log(`\n(databases written to ${tmpdir()}; delete them whenever)`);
