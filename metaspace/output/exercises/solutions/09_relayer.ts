/**
 * Level 9 — The write path: nonces, fees, and a stuck transaction.
 *
 * Use case:  Your backend has to send transactions — minting, sponsoring gas,
 *            settling a marketplace trade. Sending one is easy. Sending
 *            thousands, concurrently, without duplicating or losing any, is
 *            the job.
 * Purpose:   Meet the three things that actually go wrong: two requests
 *            claiming the same nonce, a transaction priced too low to be
 *            mined, and the fact that there is no way to cancel one.
 * Key facts: The nonce is a per-account sequence; the chain accepts N only
 *            after N-1. Replacement means re-sending the SAME nonce at a
 *            higher price. An underpriced transaction does not fail — it waits.
 *
 * Funds:     Parts 1–3 sign locally and broadcast nothing, so they need no
 *            POL and no funded key. Part 4 broadcasts only if you set
 *            PRIVATE_KEY to a throwaway Amoy key that holds testnet POL;
 *            without it the file says so and skips. Never put a key with real
 *            value in an environment variable.
 *
 * Run: npm run l9
 */

import { createPublicClient, http, formatGwei, parseGwei, parseEther, keccak256 } from "viem";
import { polygonAmoy } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import { withRetry } from "./_rpc.ts";

const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

// Anvil account #0: published everywhere, holds nothing, safe in a source file.
// Part 4 uses process.env.PRIVATE_KEY instead, if you provide one.
const relayer = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);

const RECIPIENT = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" as const;

// ---------------------------------------------------------------------------
// Part 1 — two requests, one nonce.
// ---------------------------------------------------------------------------

console.log("--- Part 1: the nonce race ---");

/** The allocator almost everyone writes first. */
async function naiveNonce(): Promise<number> {
  return withRetry(() => client.getTransactionCount({ address: relayer.address }));
}

const [nonceA, nonceB] = await Promise.all([naiveNonce(), naiveNonce()]);
console.log(`two concurrent requests asked the node for the next nonce: ${nonceA} and ${nonceB}`);
console.log(`they got the same answer: ${nonceA === nonceB}`);

console.log(
  "\nBoth handlers will now build a transaction numbered " + nonceA + ". The chain\n" +
    "will accept exactly one of them and treat the other as a replacement — and\n" +
    "which one survives is decided by price, not by which request arrived first.\n" +
    "So one player's mint silently vanishes. Worse, if the two transactions differ\n" +
    "only in their recipient, the one that wins may be the wrong one.\n\n" +
    "The node cannot help you here. It reports how many transactions it has SEEN\n" +
    "confirmed (or pending, if you ask for that tag), which is a fact about the\n" +
    "past, not a reservation for the future. Allocation has to be yours.\n",
);

/**
 * The fix: a single authority hands out nonces, and hands each one out once.
 * In one process that is an atomic counter. Across replicas — which you will
 * have — it is a row in Postgres updated in one statement:
 *
 *   UPDATE relayer_nonce SET next = next + 1 WHERE sender = $1 RETURNING next - 1
 *
 * Same shape as the SIWE nonce burn in level 5: the database adjudicates, in
 * one statement, and the answer it returns IS the reservation.
 */
class NonceAllocator {
  private next: number | null = null;
  private readonly address: `0x${string}`;

  // Written out longhand rather than as a constructor parameter property,
  // because Node runs this file by *erasing* types rather than compiling them:
  // `constructor(private readonly address: …)` emits an assignment, which is
  // code, not a type, so type-stripping rejects it. The same applies to `enum`
  // and `namespace`. It is a useful thing to know before a live coding exercise.
  constructor(address: `0x${string}`) {
    this.address = address;
  }

  async allocate(): Promise<number> {
    if (this.next === null) {
      // Seed from the pending count, once, at startup — "pending" rather than
      // "latest" so that transactions we sent but that are not yet mined are
      // counted. Getting this wrong means colliding with your own in-flight work.
      this.next = await withRetry(() =>
        client.getTransactionCount({ address: this.address, blockTag: "pending" }),
      );
    }
    return this.next++;
  }
}

const allocator = new NonceAllocator(relayer.address);
const allocated = await Promise.all([allocator.allocate(), allocator.allocate(), allocator.allocate()]);
console.log("one allocator, three concurrent requests ->", allocated.join(", "));
console.log(
  "\nDistinct, in order, with no gaps. A gap matters as much as a duplicate: the\n" +
    "chain will not accept nonce N+1 until it has accepted N, so a single lost\n" +
    "nonce stalls every transaction behind it. That is why a failed send has to\n" +
    "either return its nonce to the allocator or be replaced with a no-op\n" +
    "transaction to fill the hole.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — pricing, and what "stuck" means.
// ---------------------------------------------------------------------------

console.log("--- Part 2: pricing a transaction ---");

const block = await withRetry(() => client.getBlock({ blockTag: "latest" }));
const fees = await withRetry(() => client.estimateFeesPerGas());

console.log("current base fee        :", formatGwei(block.baseFeePerGas ?? 0n), "gwei");
console.log("suggested maxFeePerGas  :", formatGwei(fees.maxFeePerGas), "gwei");
console.log("suggested priority fee  :", formatGwei(fees.maxPriorityFeePerGas), "gwei");

// The standard headroom rule: allow the base fee to double a few times before
// your ceiling binds. Base fee can rise at most 12.5% per block, so 2x buys
// roughly six blocks of protection, and you are refunded the difference anyway.
const safeMaxFee = (block.baseFeePerGas ?? 0n) * 2n + fees.maxPriorityFeePerGas;
console.log("headroom ceiling (2x+tip):", formatGwei(safeMaxFee), "gwei");

console.log(
  "\nYou are charged base fee plus your tip and refunded the rest, so a generous\n" +
    "maxFeePerGas costs nothing when the market is calm and saves you when it is\n" +
    "not. Setting it tight is the false economy that produces stuck transactions.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — sign the stuck one, then sign its replacement. No broadcast.
// ---------------------------------------------------------------------------

console.log("--- Part 3: replacement, signed locally ---");

const nonce = await allocator.allocate();

const underpriced = await relayer.signTransaction({
  to: RECIPIENT,
  value: parseEther("0.001"),
  chainId: polygonAmoy.id,
  nonce,
  gas: 21_000n,
  maxFeePerGas: parseGwei("0.0001"),
  maxPriorityFeePerGas: parseGwei("0.00001"),
  type: "eip1559",
});

const replacement = await relayer.signTransaction({
  to: RECIPIENT,
  value: parseEther("0.001"),
  chainId: polygonAmoy.id,
  nonce, // THE SAME NONCE. This is what makes it a replacement.
  gas: 21_000n,
  maxFeePerGas: safeMaxFee * 2n,
  maxPriorityFeePerGas: fees.maxPriorityFeePerGas * 2n,
  type: "eip1559",
});

console.log(`nonce used for both : ${nonce}`);
console.log(`underpriced tx hash : ${keccak256(underpriced)}`);
console.log(`replacement tx hash : ${keccak256(replacement)}`);
console.log(`different hashes    : ${keccak256(underpriced) !== keccak256(replacement)}`);

console.log(
  "\nTwo different transactions competing for one slot in one account's sequence.\n" +
    "Only one can ever be mined. That is the entire mechanism of 'speeding up' a\n" +
    "transaction, and notice what it is NOT: there is no cancel. The chain has no\n" +
    "concept of withdrawing a broadcast transaction — you can only outbid it, and\n" +
    "if you want it to do nothing you replace it with a zero-value transfer to\n" +
    "yourself. A resting order you cannot pull, only improve.\n\n" +
    "One operational detail that catches people: most nodes require a replacement\n" +
    "to beat the original by a margin (commonly 10%) on BOTH fee fields, not to\n" +
    "merely equal it. A bump that is too timid is rejected as a duplicate and you\n" +
    "are left thinking you retried when you did not. So bump decisively, record\n" +
    "every hash you have signed for that nonce, and treat all of them as the same\n" +
    "business operation — because exactly one will land, and your outbox needs to\n" +
    "recognise it whichever one it is.\n",
);

// ---------------------------------------------------------------------------
// Part 4 — actually broadcast, only if a funded throwaway key is present.
// ---------------------------------------------------------------------------

console.log("--- Part 4: broadcasting for real ---");

const key = process.env.PRIVATE_KEY as `0x${string}` | undefined;

if (!key) {
  console.log(
    "PRIVATE_KEY is not set, so nothing was broadcast — everything above ran\n" +
      "offline and proved itself without spending anything.\n\n" +
      "To run this part: create a FRESH key that has never held anything else, fund\n" +
      "it from a Polygon Amoy faucet (linked from the Polygon docs), and run\n" +
      "  PRIVATE_KEY=0x… npm run l9\n" +
      "Then watch the transaction on https://amoy.polygonscan.com. Never use a key\n" +
      "that holds real value, and never paste one into anything that arrives during\n" +
      "a hiring process.",
  );
} else {
  const sender = privateKeyToAccount(key);
  const balance = await withRetry(() => client.getBalance({ address: sender.address }));
  console.log(`sender  : ${sender.address}`);
  console.log(`balance : ${balance} wei`);

  if (balance === 0n) {
    console.log("balance is zero — fund it from an Amoy faucet first. Nothing broadcast.");
  } else {
    const { createWalletClient } = await import("viem");
    const wallet = createWalletClient({
      account: sender,
      chain: polygonAmoy,
      transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
    });

    const liveNonce = await withRetry(() =>
      client.getTransactionCount({ address: sender.address, blockTag: "pending" }),
    );
    const hash = await wallet.sendTransaction({
      to: sender.address, // to yourself: costs only gas
      value: 0n,
      nonce: liveNonce,
      maxFeePerGas: safeMaxFee * 2n,
      maxPriorityFeePerGas: fees.maxPriorityFeePerGas * 2n,
    });
    console.log(`broadcast: ${hash}`);

    const receipt = await client.waitForTransactionReceipt({ hash });
    console.log(`status   : ${receipt.status}, block ${receipt.blockNumber}, gas ${receipt.gasUsed}`);
    console.log(
      "\nNote what the receipt does and does not tell you. It says the EVM executed\n" +
        "the transaction without reverting. It does NOT say your business operation\n" +
        "succeeded, and it is attached to a block that could still be reorganised.\n" +
        "That is why the outbox pattern exists: record the hash before you send,\n" +
        "and let the indexer's events — not the receipt — mark the work complete.",
    );
  }
}
