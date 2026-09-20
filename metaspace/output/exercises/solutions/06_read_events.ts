/**
 * Level 6 — Reading events: getLogs, provider limits, and the loop that survives them.
 *
 * Use case:  Your game database needs to know what happened on chain. Events
 *            are how a contract tells the outside world, and getLogs is the
 *            only way to ask for them after the fact.
 * Purpose:   Learn the query, then meet the two limits every provider imposes
 *            — a block-range cap and a result cap — and write the chunked,
 *            self-halving, retrying loop that an indexer actually needs.
 * Key facts: Indexed event parameters become `topics` and are filterable at
 *            the node; everything else is packed into `data` and can only be
 *            decoded afterwards. topic0 is the hash of the event signature.
 *
 * Target:    0x0000000000000000000000000000000000001010 — Polygon's native
 *            token precompile. It emits LogFeeTransfer on essentially every
 *            transaction, so unlike a quiet test token it is always busy.
 *
 * Run: npm run l6        (network required; read-only; no key involved)
 */

import { createPublicClient, http, parseAbiItem, formatEther, type Address } from "viem";
import { polygonAmoy } from "viem/chains";
import { withRetry } from "./_rpc.ts";

const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

const NATIVE: Address = "0x0000000000000000000000000000000000001010";

// Declaring the event this way gives viem everything it needs to build the
// topic filter AND to decode the result into named, typed fields. Note which
// parameters are `indexed`: those three are the only ones you can filter on.
const logFeeTransfer = parseAbiItem(
  "event LogFeeTransfer(address indexed token, address indexed from, address indexed to, uint256 amount, uint256 input1, uint256 input2, uint256 output1, uint256 output2)",
);

const head = await withRetry(() => client.getBlockNumber());
console.log("head block:", head, "\n");

// ---------------------------------------------------------------------------
// Part 1 — a small, well-behaved query.
// ---------------------------------------------------------------------------

console.log("--- Part 1: ten blocks of fee transfers ---");

const logs = await withRetry(() =>
  client.getLogs({ address: NATIVE, event: logFeeTransfer, fromBlock: head - 10n, toBlock: head }),
);

console.log(`${logs.length} logs in 10 blocks`);
for (const log of logs.slice(0, 3)) {
  console.log(
    `  block ${log.blockNumber} logIndex ${log.logIndex}: ${log.args.from} paid ` +
      `${formatEther(log.args.amount ?? 0n)} POL in fees to ${log.args.to}`,
  );
}

console.log(
  "\nThose field names came from the ABI item, not from you counting array\n" +
    "positions. Underneath, `from` and `to` were topics[2] and topics[3] — 32-byte\n" +
    "left-padded words — and `amount` was the first 32 bytes of the data blob. The\n" +
    "reason to care is that only indexed parameters are filterable: asking the node\n" +
    "for 'every fee paid by this address' is cheap, while 'every fee over 1 POL'\n" +
    "means downloading everything and filtering locally.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — break it on purpose, twice.
// ---------------------------------------------------------------------------

console.log("--- Part 2: the two limits ---");

async function attempt(span: bigint, filtered: boolean): Promise<string> {
  try {
    const result = filtered
      ? await client.getLogs({ address: NATIVE, event: logFeeTransfer, fromBlock: head - span, toBlock: head })
      : await client.getLogs({ fromBlock: head - span, toBlock: head });
    return `ok, ${result.length} logs`;
  } catch (error) {
    const cause = (error as { cause?: { message?: string } }).cause;
    return `FAILED: ${cause?.message ?? (error as Error).message.split("\n")[0]}`;
  }
}

console.log("  50,000 blocks, filtered  ->", await attempt(50_000n, true));
console.log("     500 blocks, unfiltered ->", await attempt(500n, false));

console.log(
  "\nTwo different failures, and look closely at what came back. The first is a\n" +
    "genuine block-range cap. The second asked for only 500 blocks — well inside\n" +
    "that cap — and failed because it omitted the address filter and matched far\n" +
    "too many results, yet the provider reported it with the same range message,\n" +
    "which in that case is simply false. Run it again and you may instead get a\n" +
    "generic internal error with a trace id.\n\n" +
    "The operational conclusion is important and it is the reason part 3 looks the\n" +
    "way it does: DO NOT PARSE THE ERROR MESSAGE. It is not a stable interface, it\n" +
    "differs between Alchemy, Infura, QuickNode and drpc, and it sometimes lies.\n" +
    "Treat any failure as 'that was too much' and ask for less.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — the loop that survives both limits.
// ---------------------------------------------------------------------------

console.log("--- Part 3: chunked, self-halving, retrying ---");

type Chunk = { from: bigint; to: bigint; count: number };

async function getLogsChunked(
  fromBlock: bigint,
  toBlock: bigint,
  initialSpan: bigint,
): Promise<{ total: number; chunks: Chunk[] }> {
  const chunks: Chunk[] = [];
  let total = 0;
  let cursor = fromBlock;
  let span = initialSpan;

  while (cursor <= toBlock) {
    const end = cursor + span - 1n > toBlock ? toBlock : cursor + span - 1n;
    try {
      const batch = await client.getLogs({
        address: NATIVE,
        event: logFeeTransfer,
        fromBlock: cursor,
        toBlock: end,
      }); // deliberately NOT wrapped: this loop does its own halving and retrying
      chunks.push({ from: cursor, to: end, count: batch.length });
      total += batch.length;
      cursor = end + 1n;
      // Creep back up after a success, so one bad patch does not permanently
      // cripple throughput. Halve on failure, grow gently on success — the
      // same additive-increase shape as a congestion window.
      if (span < initialSpan) span = span * 2n;
    } catch {
      if (span === 1n) {
        // A single block that will not come back is a provider problem, not a
        // size problem. Wait and retry rather than skipping: skipping a block
        // silently loses events, which is the one outcome an indexer must
        // never produce.
        await new Promise((resolve) => setTimeout(resolve, 1_000));
        continue;
      }
      span = span / 2n;
      console.log(`    (chunk failed, halving span to ${span})`);
    }
  }

  return { total, chunks };
}

const { total, chunks } = await getLogsChunked(head - 200n, head, 250n);
console.log(`  fetched ${total} logs across ${chunks.length} chunk(s)`);
for (const chunk of chunks.slice(0, 5)) {
  console.log(`    blocks ${chunk.from}-${chunk.to}: ${chunk.count} logs`);
}

// ---------------------------------------------------------------------------
// Part 4 — ordering, and the key that level 7 is built on.
// ---------------------------------------------------------------------------

console.log("\n--- Part 4: what identifies a log ---");

const recent = await withRetry(() =>
  client.getLogs({ address: NATIVE, event: logFeeTransfer, fromBlock: head - 5n, toBlock: head }),
);

const sorted = [...recent].sort((a, b) =>
  a.blockNumber === b.blockNumber
    ? (a.logIndex ?? 0) - (b.logIndex ?? 0)
    : Number(a.blockNumber! - b.blockNumber!),
);

for (const log of sorted.slice(0, 4)) {
  console.log(
    `  ${log.blockHash?.slice(0, 10)}… / ${log.transactionHash?.slice(0, 10)}… / logIndex ${log.logIndex}`,
  );
}

console.log(
  "\nThree identifiers, and you need all three. Block number alone is not unique\n" +
    "— a block holds many logs. Transaction hash alone is not unique — one\n" +
    "transaction emits several. Block NUMBER plus log index is not safe either,\n" +
    "because after a reorg a different block can occupy the same height and reuse\n" +
    "the same indices.\n\n" +
    "So the natural key is (blockHash, transactionHash, logIndex). Put a unique\n" +
    "constraint on that triple and 'have I already processed this log?' stops being\n" +
    "a question your code has to answer and becomes an invariant the database\n" +
    "enforces. That is the foundation of level 7, and the reason the indexer there\n" +
    "can be interrupted at any moment without consequence.",
);
