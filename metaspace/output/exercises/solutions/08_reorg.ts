/**
 * Level 8 — Reorg handling: detect it, then unwrite it.
 *
 * Use case:  Your indexer wrote rows because it saw events in blocks near the
 *            head. Those blocks can be replaced. If they are, the rows are
 *            claims about a history that no longer exists — and in a game, a
 *            row saying a player owns a sword is an item created from nothing.
 * Purpose:   Build the detector and the rollback, and prove the database
 *            converges on the true chain no matter where the fork happened.
 * Key facts: You cannot detect a reorg without having stored block hashes.
 *            The check is a parent-hash comparison, not a block-number one.
 *            Derived state must be REBUILDABLE, never incremented in place.
 *
 * Simulation: real reorgs on Polygon after Rio are rare — that is the point of
 *            an elected block producer. So this file indexes real blocks from
 *            Amoy, then rewrites its own record of history to simulate one.
 *            The detector does not know the difference; it only compares.
 *
 * Run: npm run l8        (network required; read-only; no key involved)
 */

import { DatabaseSync } from "node:sqlite";
import { createPublicClient, http, type Address, type Hex } from "viem";
import { polygonAmoy } from "viem/chains";
import { withRetry } from "./_rpc.ts";

const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

const NATIVE: Address = "0x0000000000000000000000000000000000001010";

// ---------------------------------------------------------------------------
// Schema: the same as level 7, plus the derived table the game reads.
// ---------------------------------------------------------------------------

const db = new DatabaseSync(":memory:");
db.exec(`
CREATE TABLE indexed_block (
  block_number INTEGER PRIMARY KEY,
  block_hash   TEXT NOT NULL,
  parent_hash  TEXT NOT NULL
);

CREATE TABLE indexed_log (
  block_number INTEGER NOT NULL,
  block_hash   TEXT    NOT NULL,
  tx_hash      TEXT    NOT NULL,
  log_index    INTEGER NOT NULL,
  payer        TEXT    NOT NULL,
  PRIMARY KEY (block_hash, tx_hash, log_index)
);

-- Derived state. NOT incremented as events arrive: recomputed from the log
-- table. That single decision is what makes rollback possible, because you
-- cannot un-increment a counter you have lost the inputs to.
CREATE TABLE player_activity (
  payer  TEXT PRIMARY KEY,
  events INTEGER NOT NULL
);

CREATE TABLE checkpoint (id INTEGER PRIMARY KEY CHECK (id = 1), last_block INTEGER NOT NULL);
`);

const insertBlock = db.prepare(
  "INSERT OR REPLACE INTO indexed_block (block_number, block_hash, parent_hash) VALUES (?, ?, ?)",
);
const insertLog = db.prepare(
  `INSERT OR IGNORE INTO indexed_log (block_number, block_hash, tx_hash, log_index, payer)
   VALUES (?, ?, ?, ?, ?)`,
);
const setCheckpoint = db.prepare(
  `INSERT INTO checkpoint (id, last_block) VALUES (1, ?)
     ON CONFLICT (id) DO UPDATE SET last_block = excluded.last_block`,
);

/** Recompute derived state from the log table. Cheap here; in production this
 *  is scoped to the affected players rather than the whole table. */
function rebuildDerivedState(): void {
  db.exec("DELETE FROM player_activity");
  db.exec(`
    INSERT INTO player_activity (payer, events)
    SELECT payer, COUNT(*) FROM indexed_log GROUP BY payer
  `);
}

function state() {
  const blocks = db.prepare("SELECT COUNT(*) AS n FROM indexed_block").get() as { n: number };
  const logs = db.prepare("SELECT COUNT(*) AS n FROM indexed_log").get() as { n: number };
  const players = db.prepare("SELECT COUNT(*) AS n FROM player_activity").get() as { n: number };
  const checkpoint = db.prepare("SELECT last_block FROM checkpoint WHERE id = 1").get() as
    | { last_block: number }
    | undefined;
  return `${blocks.n} blocks, ${logs.n} logs, ${players.n} players, checkpoint ${checkpoint?.last_block ?? 0}`;
}

// ---------------------------------------------------------------------------
// Ingest real blocks.
// ---------------------------------------------------------------------------

// This level walks block by block, so it makes more sequential RPC calls than
// any other — hence the larger retry budget on every read.
const ATTEMPTS = 8;

const head = await withRetry(() => client.getBlockNumber(), ATTEMPTS);
const from = head - 6n;

console.log(`indexing blocks ${from}–${head} from Amoy\n`);

/** Index a closed range: one getLogs for the whole span, one getBlock each. */
async function indexRange(fromBlock: bigint, toBlock: bigint): Promise<void> {
  // One call for the range rather than one per block. Both are correct; this
  // one is what you would actually run, and it is far kinder to the provider.
  const logs = await withRetry(() =>
    client.getLogs({ address: NATIVE, fromBlock, toBlock }),
    ATTEMPTS,
  );

  for (let height = fromBlock; height <= toBlock; height += 1n) {
    const block = await withRetry(() => client.getBlock({ blockNumber: height }), ATTEMPTS);
    insertBlock.run(Number(block.number), block.hash, block.parentHash);
    setCheckpoint.run(Number(height));
  }

  for (const log of logs) {
    insertLog.run(
      Number(log.blockNumber),
      log.blockHash,
      log.transactionHash,
      log.logIndex,
      log.topics[2] ?? "unknown",
    );
  }
}

await indexRange(from, head);
rebuildDerivedState();

console.log("--- after a clean run ---");
console.log(state());

// ---------------------------------------------------------------------------
// The detector.
// ---------------------------------------------------------------------------

/**
 * Walk backwards from the checkpoint comparing each stored block hash against
 * the hash the chain reports for that height. Return the last height where
 * they still agree — everything after it is on a dead branch.
 *
 * The naive version of this compares only the tip. That is not enough: a reorg
 * can be several blocks deep, and the tip check tells you only that something
 * is wrong, not where it started.
 */
async function findCommonAncestor(tip: number, floor: number): Promise<number> {
  for (let height = tip; height >= floor; height -= 1) {
    const stored = db
      .prepare("SELECT block_hash FROM indexed_block WHERE block_number = ?")
      .get(height) as { block_hash: Hex } | undefined;
    if (!stored) continue;

    const live = await withRetry(() => client.getBlock({ blockNumber: BigInt(height) }), ATTEMPTS);
    if (live.hash === stored.block_hash) return height;
  }
  return floor - 1;
}

/** Delete everything strictly after `height`, then rebuild derived state. */
function rollbackTo(height: number): { blocks: number; logs: number } {
  db.exec("BEGIN");
  const logs = db.prepare("DELETE FROM indexed_log WHERE block_number > ?").run(height);
  const blocks = db.prepare("DELETE FROM indexed_block WHERE block_number > ?").run(height);
  setCheckpoint.run(height);
  rebuildDerivedState();
  db.exec("COMMIT");
  return { blocks: Number(blocks.changes), logs: Number(logs.changes) };
}

// ---------------------------------------------------------------------------
// Break it on purpose: rewrite our own history four blocks deep.
// ---------------------------------------------------------------------------

console.log("\n--- simulating a three-block reorg ---");

const forkPoint = Number(head) - 3;
const poisoned: Hex = `0x${"de".repeat(32)}`;
for (let height = forkPoint + 1; height <= Number(head); height += 1) {
  db.prepare("UPDATE indexed_block SET block_hash = ? WHERE block_number = ?").run(poisoned, height);
  db.prepare("UPDATE indexed_log SET block_hash = ? WHERE block_number = ?").run(poisoned, height);
}

console.log(
  `rewrote our stored hashes for blocks ${forkPoint + 1}–${head}, as if those four\n` +
    "blocks had been produced by a branch that subsequently lost.\n",
);

const tipStored = db
  .prepare("SELECT block_hash FROM indexed_block WHERE block_number = ?")
  .get(Number(head)) as { block_hash: Hex };
const tipLive = await withRetry(() => client.getBlock({ blockNumber: head }), ATTEMPTS);

console.log("stored tip hash :", tipStored.block_hash.slice(0, 18) + "…");
console.log("live tip hash   :", tipLive.hash?.slice(0, 18) + "…");
console.log("agree           :", tipStored.block_hash === tipLive.hash);

const ancestor = await findCommonAncestor(Number(head), Number(from));
console.log(`\ncommon ancestor : block ${ancestor}`);
console.log(`depth of reorg  : ${Number(head) - ancestor} blocks`);

const before = state();
const removed = rollbackTo(ancestor);
console.log(`\nrolled back     : ${removed.blocks} blocks, ${removed.logs} logs deleted`);
console.log(`before rollback : ${before}`);
console.log(`after rollback  : ${state()}`);

console.log(
  "\nThe checkpoint moved BACKWARDS, which is the part people find uncomfortable\n" +
    "and the part that makes the design correct. A checkpoint is not a high-water\n" +
    "mark of progress; it is a claim about which history you have processed, and\n" +
    "when that history turns out to be wrong the honest response is to withdraw\n" +
    "the claim. The next polling cycle will re-fetch those heights from the\n" +
    "winning branch and re-insert whatever really happened — and because ingestion\n" +
    "is idempotent (level 7), re-inserting is free.\n",
);

// ---------------------------------------------------------------------------
// Re-index the true chain and show convergence.
// ---------------------------------------------------------------------------

await indexRange(BigInt(ancestor) + 1n, head);
rebuildDerivedState();

console.log("--- after re-indexing the winning branch ---");
console.log(state());

const ancestorAfter = await findCommonAncestor(Number(head), Number(from));
console.log(`detector now reports common ancestor at the tip: ${ancestorAfter === Number(head)}`);

console.log(
  "\nThree design decisions made all of this possible, and they are the three\n" +
    "things to say if you are asked about reorg handling:\n\n" +
    "  1. Store block hashes. Without them there is nothing to compare and the\n" +
    "     corruption is undetectable — you would simply serve wrong data forever.\n" +
    "  2. Make derived state rebuildable. player_activity is recomputed from the\n" +
    "     log table, never incremented in place. An inventory counter that was\n" +
    "     incremented as events arrived cannot be rolled back, because the inputs\n" +
    "     that produced it are gone.\n" +
    "  3. Let the checkpoint move backwards, inside the same transaction as the\n" +
    "     deletes. Anything else leaves the database claiming to have processed a\n" +
    "     history it has just thrown away.\n\n" +
    "And the operational judgement that sits on top: how far back to keep hashes\n" +
    "and how deep to search. On Polygon after Rio the finalized tag runs a couple\n" +
    "of blocks behind the head, so a handful is ample; on a chain with probabilistic\n" +
    "finality you would keep more. The cheapest safe policy of all is to index only\n" +
    "up to the finalized tag and accept the delay — and for anything that converts\n" +
    "into real value, that is the policy I would argue for.",
);

db.close();
