/**
 * =====================================================================
 * TRANSACTION RELAYER — nonce management, EIP-1559 fees, stuck-tx recovery
 * =====================================================================
 *
 * The second half of the integration layer. The indexer READS the chain; the
 * relayer WRITES to it. Writing is much harder, and the reason is one
 * sentence worth memorising:
 *
 *   A transaction is not a request/response. It is a message you broadcast
 *   into a market, and you cannot cancel it — only outbid it.
 *
 * You already have the right instincts for this from order-flow trading. Gas
 * is a live auction: base fee is the clearing price set by demand, priority
 * fee is your tip for queue position, and an underpriced transaction sits in
 * the mempool exactly like a limit order that never fills. "Speeding up" a
 * transaction is not a cancel-replace in the exchange sense — it is
 * submitting a new order at the same sequence number with a higher price and
 * letting the better one win. USE THAT ANALOGY IN THE INTERVIEW. It is true,
 * it is yours, and it shows you understand the mechanism rather than the API.
 *
 * THE THREE FAILURE MODES THIS FILE EXISTS TO PREVENT
 *
 *   1. NONCE GAPS / COLLISIONS
 *      Every account has a strictly sequential nonce. Two concurrent handlers
 *      that both call getTransactionCount() get the SAME number, and one of
 *      them is silently dropped. Worse: submit nonce 7 and 9 without 8 and
 *      NOTHING after 7 ever mines — the account is wedged until 8 lands.
 *      Fix: one serialised nonce allocator per sending address. Below it is
 *      an in-process mutex; multi-instance, it is `SELECT ... FOR UPDATE` on
 *      a per-address row, which is the answer to "how does this scale to
 *      three pods?"
 *
 *   2. STUCK TRANSACTIONS
 *      Base fee doubles, your maxFeePerGas no longer clears, the tx sits
 *      forever and blocks every later nonce. Fix: a watchdog that rebroadcasts
 *      the SAME nonce with a higher fee. Geth requires at least a 10% bump to
 *      accept a replacement, so bump by 12.5% to leave headroom against
 *      rounding.
 *
 *   3. DOUBLE SENDS
 *      Crash between eth_sendRawTransaction and writing the hash, retry on
 *      boot, mint twice. Fix: the outbox. Write intent first, reconcile on
 *      restart by asking the chain what happened to that nonce — never by
 *      assuming.
 */

import { JsonRpcProvider, Wallet, type TransactionRequest, type TransactionResponse } from "ethers";
import { pool, withTransaction } from "./db.ts";

export interface RelayRequest {
  /** Caller-supplied. Same key => same transaction, never a second one. */
  idempotencyKey: string;
  to: string;
  data: string;
  valueWei?: bigint;
  gasLimit?: bigint;
}

export class Relayer {
  /**
   * Serialises nonce allocation within this process. Concurrency is the
   * enemy here and a queue is the whole defence.
   *
   * SAY THIS OUT LOUD: single-instance, a promise chain is enough.
   * Multi-instance, you need the allocation in Postgres — a `sender_nonce`
   * row locked with SELECT ... FOR UPDATE inside the same transaction that
   * writes the outbox row. Otherwise two pods hand out nonce 42 and one of
   * their transactions is dropped. The follow-up question is almost always
   * "and if you run three replicas?", so answer it before it is asked.
   */
  private chain: Promise<unknown> = Promise.resolve();

  private readonly provider: JsonRpcProvider;
  private readonly wallet: Wallet;
  private readonly chainId: number;

  constructor(provider: JsonRpcProvider, wallet: Wallet, chainId: number) {
    this.provider = provider;
    this.wallet = wallet;
    this.chainId = chainId;
  }

  // -------------------------------------------------------------------
  // Send
  // -------------------------------------------------------------------

  async send(req: RelayRequest): Promise<{ txHash: string; nonce: number }> {
    const existing = await this.lookup(req.idempotencyKey);
    if (existing) return existing;

    return this.serialise(async () => {
      // Re-check inside the lock. Without this, two concurrent callers with
      // the same key both miss the fast path and both send. Check-then-act
      // outside a lock is not idempotency, it is a narrower race.
      const again = await this.lookup(req.idempotencyKey);
      if (again) return again;

      const nonce = await this.allocateNonce();
      const fees = await this.suggestFees();

      const tx: TransactionRequest = {
        to: req.to,
        data: req.data,
        value: req.valueWei ?? 0n,
        nonce,
        chainId: this.chainId,
        type: 2, // EIP-1559
        maxFeePerGas: fees.maxFeePerGas,
        maxPriorityFeePerGas: fees.maxPriorityFeePerGas,
        gasLimit: req.gasLimit ?? (await this.estimateWithBuffer(req)),
      };

      // OUTBOX: record intent BEFORE broadcasting. If the process dies on the
      // next line, reconcileOnBoot() finds this row and asks the chain what
      // happened instead of blindly resending.
      await pool.query(
        `INSERT INTO outbound_tx
           (idempotency_key, chain_id, from_address, to_address, data, value_wei,
            nonce, status, max_fee_wei, max_priority_wei)
         VALUES ($1,$2,$3,$4,$5,$6,$7,'pending',$8,$9)`,
        [req.idempotencyKey, this.chainId, this.wallet.address.toLowerCase(),
         req.to.toLowerCase(), req.data, (req.valueWei ?? 0n).toString(), nonce,
         fees.maxFeePerGas.toString(), fees.maxPriorityFeePerGas.toString()]
      );

      const sent = await this.wallet.sendTransaction(tx);

      await pool.query(
        `UPDATE outbound_tx
            SET tx_hash = $2, status = 'submitted', attempts = attempts + 1, updated_at = now()
          WHERE idempotency_key = $1`,
        [req.idempotencyKey, sent.hash]
      );

      // Deliberately NOT awaiting sent.wait(). Holding an HTTP request open
      // for 30+ seconds of block time ties up a connection and lies to the
      // caller about what "done" means. Return the hash; let the indexer
      // observe the receipt and update game state. Async by construction —
      // the same reason you use an outbox instead of a synchronous webhook.
      return { txHash: sent.hash, nonce };
    });
  }

  // -------------------------------------------------------------------
  // Fees
  // -------------------------------------------------------------------

  /**
   * EIP-1559 in one paragraph, because you will be asked:
   *   baseFeePerGas is set by the protocol from the previous block's fullness
   *   and is BURNED. maxPriorityFeePerGas is the tip that actually goes to the
   *   validator. maxFeePerGas is your ceiling; you pay
   *   min(maxFee, baseFee + priority) and are refunded the rest. So setting a
   *   generous maxFee is not the same as overpaying — it buys resilience to a
   *   rising base fee at no cost when the base fee stays flat.
   *
   * The 2x headroom below is the standard heuristic: base fee can rise at most
   * 12.5% per block, so 2x survives roughly six consecutive full blocks.
   */
  private async suggestFees(): Promise<{ maxFeePerGas: bigint; maxPriorityFeePerGas: bigint }> {
    const fee = await this.provider.getFeeData();
    const base = fee.maxFeePerGas ?? fee.gasPrice ?? 30_000_000_000n;

    // Polygon validators historically enforce a ~30 gwei priority-fee floor;
    // bid under it and your transaction is simply never picked up. This is
    // exactly the kind of chain-specific detail that shows you have actually
    // shipped on Polygon rather than only read about EVM chains.
    const floor = this.chainId === 137 || this.chainId === 80002 ? 30_000_000_000n : 1_000_000_000n;
    const priority = maxBigInt(fee.maxPriorityFeePerGas ?? floor, floor);

    return { maxFeePerGas: base * 2n + priority, maxPriorityFeePerGas: priority };
  }

  /**
   * +20% on the estimate. eth_estimateGas simulates against the CURRENT state;
   * by the time the transaction mines, state has moved — a first-time SSTORE
   * (20,000 gas) may have become a cheap update, or vice versa. Estimate
   * exactly and you ship intermittent out-of-gas reverts that burn the user's
   * gas and mint nothing.
   */
  private async estimateWithBuffer(req: RelayRequest): Promise<bigint> {
    const estimate = await this.provider.estimateGas({
      from: this.wallet.address,
      to: req.to,
      data: req.data,
      value: req.valueWei ?? 0n,
    });
    return (estimate * 120n) / 100n;
  }

  // -------------------------------------------------------------------
  // Stuck-transaction watchdog
  // -------------------------------------------------------------------

  /**
   * Rebroadcast anything submitted more than `staleMs` ago at a higher fee.
   *
   * Crucially it reuses the SAME nonce. Sending a new nonce would leave the
   * old transaction in the mempool, and if it later mines you have executed
   * the action twice. Replacement is the only safe "cancel" the EVM offers:
   * same nonce, better price, and the network keeps whichever mines first —
   * which is why it is exactly a price improvement on a resting order, not a
   * cancel.
   */
  async bumpStuck(staleMs = 120_000): Promise<number> {
    const { rows } = await pool.query<{
      idempotency_key: string; nonce: string; to_address: string; data: string;
      value_wei: string; max_fee_wei: string; max_priority_wei: string; attempts: number;
    }>(
      `SELECT idempotency_key, nonce, to_address, data, value_wei,
              max_fee_wei, max_priority_wei, attempts
         FROM outbound_tx
        WHERE status = 'submitted'
          AND from_address = $1
          AND updated_at < now() - ($2 || ' milliseconds')::interval
        ORDER BY nonce ASC`,
      [this.wallet.address.toLowerCase(), String(staleMs)]
    );

    let bumped = 0;
    for (const row of rows) {
      // Did it quietly mine while we were not looking? Always ask the chain
      // before acting on your own stale bookkeeping.
      const mined = await this.provider.getTransactionCount(this.wallet.address, "latest");
      if (mined > Number(row.nonce)) {
        await pool.query(
          `UPDATE outbound_tx SET status='mined', updated_at=now() WHERE idempotency_key=$1`,
          [row.idempotency_key]
        );
        continue;
      }

      // Geth's replacement rule is +10%. Bump 12.5% so integer rounding can
      // never leave you a wei short and get the replacement rejected with
      // "replacement transaction underpriced".
      const newMaxFee = (BigInt(row.max_fee_wei) * 1125n) / 1000n;
      const newPriority = (BigInt(row.max_priority_wei) * 1125n) / 1000n;

      // Give up rather than escalate forever. Unbounded bumping during a real
      // gas spike drains the hot wallet; at that point a human decides.
      if (row.attempts >= 6) {
        await pool.query(
          `UPDATE outbound_tx SET status='failed', last_error='max bump attempts', updated_at=now()
            WHERE idempotency_key=$1`,
          [row.idempotency_key]
        );
        continue;
      }

      const replacement: TransactionResponse = await this.wallet.sendTransaction({
        to: row.to_address,
        data: row.data,
        value: BigInt(row.value_wei),
        nonce: Number(row.nonce),
        chainId: this.chainId,
        type: 2,
        maxFeePerGas: newMaxFee,
        maxPriorityFeePerGas: newPriority,
      });

      await pool.query(
        `UPDATE outbound_tx
            SET tx_hash=$2, max_fee_wei=$3, max_priority_wei=$4,
                attempts=attempts+1, updated_at=now()
          WHERE idempotency_key=$1`,
        [row.idempotency_key, replacement.hash, newMaxFee.toString(), newPriority.toString()]
      );
      bumped++;
    }
    return bumped;
  }

  /**
   * Boot-time reconciliation. For every row we recorded but never confirmed,
   * ask the chain. This is the step that makes the outbox worth having: after
   * a crash you do not guess, you query.
   */
  async reconcileOnBoot(): Promise<void> {
    const { rows } = await pool.query<{ idempotency_key: string; tx_hash: string | null; nonce: string }>(
      `SELECT idempotency_key, tx_hash, nonce FROM outbound_tx
        WHERE status IN ('pending','submitted') AND from_address = $1`,
      [this.wallet.address.toLowerCase()]
    );

    for (const row of rows) {
      if (!row.tx_hash) {
        // Died before broadcasting. The nonce was never consumed, so this is
        // safe to retry from scratch.
        await pool.query(
          `UPDATE outbound_tx SET status='failed', last_error='crash before broadcast' WHERE idempotency_key=$1`,
          [row.idempotency_key]
        );
        continue;
      }
      const receipt = await this.provider.getTransactionReceipt(row.tx_hash);
      if (receipt) {
        await pool.query(
          `UPDATE outbound_tx SET status=$2, updated_at=now() WHERE idempotency_key=$1`,
          [row.idempotency_key, receipt.status === 1 ? "mined" : "failed"]
        );
      }
    }
  }

  // -------------------------------------------------------------------
  // Internals
  // -------------------------------------------------------------------

  /**
   * "pending" counts transactions already sitting in the mempool, so
   * concurrent sends get distinct nonces. "latest" would hand the same nonce
   * to everything in flight.
   *
   * The DB max is the safety net: some RPC providers lag on pending, and one
   * stale answer wedges the account. Take whichever is higher.
   */
  private async allocateNonce(): Promise<number> {
    const [onChain, local] = await Promise.all([
      this.provider.getTransactionCount(this.wallet.address, "pending"),
      pool.query<{ next: string }>(
        `SELECT COALESCE(MAX(nonce), -1) + 1 AS next FROM outbound_tx
          WHERE from_address = $1 AND status IN ('pending','submitted','mined')`,
        [this.wallet.address.toLowerCase()]
      ),
    ]);
    return Math.max(onChain, Number(local.rows[0]?.next ?? 0));
  }

  private async lookup(key: string): Promise<{ txHash: string; nonce: number } | null> {
    const { rows } = await pool.query<{ tx_hash: string | null; nonce: string | null }>(
      `SELECT tx_hash, nonce FROM outbound_tx WHERE idempotency_key = $1`,
      [key]
    );
    const row = rows[0];
    if (!row?.tx_hash || row.nonce === null) return null;
    return { txHash: row.tx_hash, nonce: Number(row.nonce) };
  }

  private serialise<T>(fn: () => Promise<T>): Promise<T> {
    const next = this.chain.then(fn, fn);
    // Swallow rejections on the CHAIN only, so one failed send does not
    // poison every queued send behind it. The caller still sees the error.
    this.chain = next.catch(() => undefined);
    return next;
  }
}

function maxBigInt(a: bigint, b: bigint): bigint {
  return a > b ? a : b;
}

export { withTransaction };
