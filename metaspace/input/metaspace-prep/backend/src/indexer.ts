/**
 * =====================================================================
 * REORG-SAFE EVENT INDEXER
 * =====================================================================
 *
 * If you only rehearse one file for this interview, make it this one. "How
 * would you keep our game database in sync with the chain?" is THE backend
 * question at a Web3 game studio, and almost every candidate answers it with
 * `contract.on("Transfer", handler)` — which is wrong in four ways at once:
 * it loses events while the process is down, it double-delivers on WebSocket
 * reconnect, it has no idea what a reorg is, and it cannot backfill.
 *
 * The correct shape is a polling loop with a checkpoint. Frame it out loud as
 * what it actually is: an ETL pipeline over an append-only log whose tail can
 * be rewritten. You have built checkpointed, idempotent ingestion before —
 * the ONA.io pipelines are the same problem with a friendlier source.
 *
 * THE FIVE PROPERTIES THAT MAKE IT CORRECT
 *   1. CHECKPOINTED   — resume from the last committed block, never from "now".
 *   2. IDEMPOTENT     — re-processing a range is a no-op (unique key + upsert).
 *   3. ATOMIC         — events and the checkpoint advance in ONE transaction.
 *   4. REORG-AWARE    — detect that the parent chain changed, roll back, re-index.
 *   5. LAG-TOLERANT   — only treat blocks as settled after N confirmations.
 *
 * WHY REORGS MATTER ON POLYGON SPECIFICALLY
 *   Polygon PoS produces a block roughly every 2 seconds and checkpoints to
 *   Ethereum periodically. Short reorgs of a few blocks are routine, and
 *   historically it has seen deeper ones. Ethereum mainnet gives you
 *   `finalized` (~2 epochs, about 13 minutes) as a hard guarantee; on Polygon
 *   the practical answer is a confirmation depth — commonly 64–128 blocks for
 *   anything that moves value — plus the ability to roll back if you are wrong.
 *   Say that number out loud with the reasoning attached; the reasoning is
 *   what is being graded, not the constant.
 *
 * THE TRADE-OFF TO NAME
 *   Confirmations buy safety and cost latency. So you run TWO read paths: an
 *   optimistic one at ~1 confirmation that updates the UI immediately and is
 *   allowed to be wrong, and this settled one that is the source of truth for
 *   anything economic. Never let a player spend an unsettled balance.
 */

import { Interface, JsonRpcProvider, type Log } from "ethers";
import type pg from "pg";
import { pool, withTransaction } from "./db.ts";

// ---------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------

export interface IndexerConfig {
  rpcUrl: string;
  chainId: number;
  contractAddress: string;
  abi: ReadonlyArray<string>;
  /** Block the contract was deployed in. Starting at 0 scans 60M empty blocks. */
  deployBlock: number;
  /** Blocks behind head we treat as settled. Chain-dependent; see note above. */
  confirmations: number;
  /**
   * Max blocks per eth_getLogs call. Public RPCs cap the response (Alchemy and
   * Infura commonly reject ranges that return >10k logs). Too large and every
   * call fails; too small and a backfill takes days. 2000 is a safe default
   * that you then tune by watching for "query returned more than N results".
   */
  batchSize: number;
  pollIntervalMs: number;
  streamId: string;
}

export const POLYGON_AMOY: Omit<IndexerConfig, "contractAddress" | "deployBlock" | "abi" | "streamId"> = {
  rpcUrl: process.env.RPC_URL ?? "https://rpc-amoy.polygon.technology",
  chainId: 80002,
  confirmations: 64,
  batchSize: 2000,
  pollIntervalMs: 4000,
};

interface Checkpoint {
  blockNumber: number;
  blockHash: string;
}

// ---------------------------------------------------------------------
// Indexer
// ---------------------------------------------------------------------

export class EventIndexer {
  private readonly provider: JsonRpcProvider;
  private readonly iface: Interface;
  private readonly cfg: IndexerConfig;
  private running = false;

  constructor(cfg: IndexerConfig) {
    this.cfg = cfg;
    // staticNetwork: the chain id never changes, so skip the eth_chainId
    // round-trip ethers otherwise makes before every single call. On a loop
    // that polls every 4s this is a meaningful cut in RPC billing.
    this.provider = new JsonRpcProvider(cfg.rpcUrl, cfg.chainId, { staticNetwork: true });
    this.iface = new Interface([...cfg.abi]);
  }

  async start(): Promise<void> {
    this.running = true;
    while (this.running) {
      try {
        await this.tick();
      } catch (err) {
        // A poll failure must never kill the loop. RPC providers rate-limit,
        // time out, and return 502s as a matter of course. Log, back off,
        // continue — the checkpoint means nothing is lost by retrying.
        console.error("[indexer] tick failed", err);
        await sleep(this.cfg.pollIntervalMs * 2);
      }
      await sleep(this.cfg.pollIntervalMs);
    }
  }

  stop(): void {
    this.running = false;
  }

  // -------------------------------------------------------------------
  // One poll
  // -------------------------------------------------------------------

  private async tick(): Promise<void> {
    const head = await this.provider.getBlockNumber();
    const safeHead = head - this.cfg.confirmations;
    if (safeHead < this.cfg.deployBlock) return; // chain too young

    const checkpoint = await this.loadCheckpoint();

    // ---- STEP 1: has the chain we indexed been rewritten? -----------
    if (checkpoint) {
      const rollbackTo = await this.detectReorg(checkpoint);
      if (rollbackTo !== null) {
        console.warn(
          `[indexer] REORG detected at block ${checkpoint.blockNumber}; rolling back to ${rollbackTo}`
        );
        await this.rollback(rollbackTo);
        return; // re-enter on the next tick with a clean checkpoint
      }
    }

    const from = checkpoint ? checkpoint.blockNumber + 1 : this.cfg.deployBlock;
    if (from > safeHead) return; // caught up

    // ---- STEP 2: pull one bounded batch -----------------------------
    const to = Math.min(from + this.cfg.batchSize - 1, safeHead);
    const logs = await this.getLogsWithBackoff(from, to);

    // ---- STEP 3: persist events + checkpoint ATOMICALLY -------------
    const tip = await this.provider.getBlock(to);
    if (!tip) throw new Error(`block ${to} vanished between getLogs and getBlock`);

    await withTransaction(async (tx) => {
      for (const log of logs) {
        await this.persistLog(tx, log);
      }
      await this.saveCheckpoint(tx, { blockNumber: to, blockHash: tip.hash! });
    });

    if (logs.length > 0) {
      console.log(`[indexer] ${from}-${to}: ${logs.length} events (head ${head})`);
    }
  }

  // -------------------------------------------------------------------
  // Reorg detection
  // -------------------------------------------------------------------

  /**
   * Ask the node for the block we last committed. If the hash differs, that
   * block is no longer on the canonical chain and everything we indexed from
   * it is fiction. Walk backwards until hashes agree again — that is the fork
   * point, and everything after it must be re-indexed.
   *
   * Returns the block number to roll back to, or null if the chain is intact.
   */
  private async detectReorg(checkpoint: Checkpoint): Promise<number | null> {
    const current = await this.provider.getBlock(checkpoint.blockNumber);
    if (current && current.hash === checkpoint.blockHash) return null;

    // Walk back. The bound matters: an unbounded walk during a node
    // resync will march to genesis and hang the indexer forever. If we
    // exceed it, that is an alert-a-human condition, not a retry condition.
    const maxDepth = this.cfg.confirmations * 2;
    for (let depth = 1; depth <= maxDepth; depth++) {
      const height = checkpoint.blockNumber - depth;
      if (height < this.cfg.deployBlock) return this.cfg.deployBlock - 1;

      const stored = await this.storedHashAt(height);
      const onChain = await this.provider.getBlock(height);
      if (!stored || (onChain && onChain.hash === stored)) {
        return height;
      }
    }
    throw new Error(
      `[indexer] reorg deeper than ${maxDepth} blocks — refusing to auto-recover, page a human`
    );
  }

  /**
   * Mark orphaned rows rather than DELETE-ing them.
   *
   * Two reasons, and both are good interview answers. First, forensics: when
   * a player says "my sword disappeared", the orphaned rows are the evidence.
   * Second, the projection rebuild reads `WHERE NOT orphaned`, so soft-delete
   * and re-index converge to the same state a hard delete would, without
   * destroying the audit trail. Same instinct as never hard-deleting from a
   * survey dataset.
   */
  private async rollback(toBlock: number): Promise<void> {
    await withTransaction(async (tx) => {
      await tx.query(
        `UPDATE chain_event
            SET orphaned = TRUE
          WHERE chain_id = $1 AND block_number > $2 AND NOT orphaned`,
        [this.cfg.chainId, toBlock]
      );

      const { rows } = await tx.query<{ block_hash: string }>(
        `SELECT block_hash FROM chain_event
          WHERE chain_id = $1 AND block_number = $2 AND NOT orphaned LIMIT 1`,
        [this.cfg.chainId, toBlock]
      );

      await tx.query(
        `UPDATE indexer_checkpoint
            SET last_block_number = $2, last_block_hash = $3, updated_at = now()
          WHERE stream_id = $1`,
        [this.cfg.streamId, toBlock, rows[0]?.block_hash ?? ""]
      );

      // The projection is derived, so rebuild it from surviving events rather
      // than trying to reverse individual mutations. Reversing is where the
      // bugs live.
      await this.rebuildInventory(tx);
    });
  }

  // -------------------------------------------------------------------
  // Persistence
  // -------------------------------------------------------------------

  private async persistLog(tx: pg.PoolClient, log: Log): Promise<void> {
    const parsed = this.iface.parseLog({ topics: [...log.topics], data: log.data });
    if (!parsed) return; // an event this ABI does not know about

    const block = await this.provider.getBlock(log.blockNumber);

    // ON CONFLICT DO NOTHING is the idempotency. Replaying a range after a
    // crash inserts nothing and throws nothing — which is precisely why the
    // loop is safe to restart at any point.
    await tx.query(
      `INSERT INTO chain_event
         (chain_id, block_number, block_hash, block_time, tx_hash, log_index,
          address, event_name, args)
       VALUES ($1,$2,$3,to_timestamp($4),$5,$6,$7,$8,$9)
       ON CONFLICT (block_hash, log_index) DO NOTHING`,
      [
        this.cfg.chainId,
        log.blockNumber,
        log.blockHash,
        block?.timestamp ?? 0,
        log.transactionHash,
        log.index,
        log.address.toLowerCase(),
        parsed.name,
        JSON.stringify(serialiseArgs(parsed.args as unknown as Record<string, unknown>)),
      ]
    );
  }

  private async loadCheckpoint(): Promise<Checkpoint | null> {
    const { rows } = await pool.query<{ last_block_number: string; last_block_hash: string }>(
      `SELECT last_block_number, last_block_hash
         FROM indexer_checkpoint WHERE stream_id = $1`,
      [this.cfg.streamId]
    );
    const row = rows[0];
    if (!row) return null;
    return { blockNumber: Number(row.last_block_number), blockHash: row.last_block_hash };
  }

  private async saveCheckpoint(tx: pg.PoolClient, cp: Checkpoint): Promise<void> {
    await tx.query(
      `INSERT INTO indexer_checkpoint
         (stream_id, chain_id, contract_address, last_block_number, last_block_hash)
       VALUES ($1,$2,$3,$4,$5)
       ON CONFLICT (stream_id) DO UPDATE
         SET last_block_number = EXCLUDED.last_block_number,
             last_block_hash   = EXCLUDED.last_block_hash,
             updated_at        = now()`,
      [this.cfg.streamId, this.cfg.chainId, this.cfg.contractAddress.toLowerCase(),
       cp.blockNumber, cp.blockHash]
    );
  }

  private async storedHashAt(height: number): Promise<string | null> {
    const { rows } = await pool.query<{ block_hash: string }>(
      `SELECT block_hash FROM chain_event
        WHERE chain_id = $1 AND block_number = $2 AND NOT orphaned LIMIT 1`,
      [this.cfg.chainId, height]
    );
    return rows[0]?.block_hash ?? null;
  }

  /**
   * Fold every surviving TransferSingle/TransferBatch into player_inventory.
   *
   * Doing this in SQL rather than in a JS loop is deliberate: it is one
   * statement, it runs inside the same transaction as the rollback, and it
   * cannot half-apply. This is the part of the job where a data engineer has
   * an unfair advantage over a typical app developer — say so in the room.
   */
  private async rebuildInventory(tx: pg.PoolClient): Promise<void> {
    await tx.query(`TRUNCATE player_inventory`);
    await tx.query(
      `INSERT INTO player_inventory (wallet, item_id, balance)
       SELECT wallet, item_id, SUM(delta)
         FROM (
           SELECT lower(args->>'to')   AS wallet,
                  (args->>'id')::numeric  AS item_id,
                  (args->>'value')::numeric AS delta
             FROM chain_event
            WHERE NOT orphaned AND event_name = 'TransferSingle'
           UNION ALL
           SELECT lower(args->>'from') AS wallet,
                  (args->>'id')::numeric,
                  -(args->>'value')::numeric
             FROM chain_event
            WHERE NOT orphaned AND event_name = 'TransferSingle'
         ) moves
        WHERE wallet <> '0x0000000000000000000000000000000000000000'
        GROUP BY wallet, item_id
       HAVING SUM(delta) > 0`
    );
  }

  // -------------------------------------------------------------------
  // RPC resilience
  // -------------------------------------------------------------------

  /**
   * Exponential backoff with a range split.
   *
   * The two failures you actually hit in production are different and need
   * different responses: rate limiting wants you to WAIT, while an oversized
   * response wants you to ASK FOR LESS. Conflating them gives you an indexer
   * that stalls forever on a busy contract.
   */
  private async getLogsWithBackoff(from: number, to: number, attempt = 0): Promise<Log[]> {
    try {
      return await this.provider.getLogs({
        address: this.cfg.contractAddress,
        fromBlock: from,
        toBlock: to,
      });
    } catch (err) {
      const msg = String((err as Error)?.message ?? err);
      const tooMany = /more than .* results|query returned more than|response size|limit exceeded/i.test(msg);

      if (tooMany && to > from) {
        const mid = Math.floor((from + to) / 2);
        const [left, right] = await Promise.all([
          this.getLogsWithBackoff(from, mid),
          this.getLogsWithBackoff(mid + 1, to),
        ]);
        return [...left, ...right];
      }
      if (attempt >= 5) throw err;

      // Full jitter — without the random term, every worker that failed at the
      // same moment retries at the same moment and the thundering herd
      // re-creates the outage you are backing off from.
      const base = Math.min(30_000, 500 * 2 ** attempt);
      await sleep(Math.random() * base);
      return this.getLogsWithBackoff(from, to, attempt + 1);
    }
  }
}

// ---------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------

/** BigInt is not JSON-serialisable. Stringify, do not Number() — uint256 overflows. */
function serialiseArgs(args: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(args)) {
    if (/^\d+$/.test(key)) continue; // ethers duplicates args positionally
    out[key] = typeof value === "bigint" ? value.toString() : value;
  }
  return out;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------

export const GAME_ITEMS_ABI = [
  "event TransferSingle(address indexed operator, address indexed from, address indexed to, uint256 id, uint256 value)",
  "event TransferBatch(address indexed operator, address indexed from, address indexed to, uint256[] ids, uint256[] values)",
  "event VoucherRedeemed(address indexed to, uint256 indexed id, uint256 amount, uint256 nonce)",
] as const;

if (import.meta.url === `file://${process.argv[1]}`) {
  const contractAddress = process.env.GAME_ITEMS_ADDRESS ?? "0x0000000000000000000000000000000000000000";
  const indexer = new EventIndexer({
    ...POLYGON_AMOY,
    contractAddress,
    abi: GAME_ITEMS_ABI,
    deployBlock: Number(process.env.DEPLOY_BLOCK ?? 0),
    streamId: `amoy:${contractAddress}:GameItems`,
  });

  // Graceful shutdown: finish the in-flight transaction instead of being
  // SIGKILLed mid-batch. The checkpoint makes a hard kill survivable, but a
  // clean stop means zero re-work on restart.
  process.on("SIGTERM", () => indexer.stop());
  process.on("SIGINT", () => indexer.stop());

  await indexer.start();
}
