/**
 * Level 2 — Reading a live chain: blocks, balances, fees, and finality.
 *
 * Use case:  Everything a game backend does starts here. Before you can index
 *            events or send a transaction you need a client, and you need to
 *            know what the numbers it returns actually mean.
 * Purpose:   Replace "the blockchain" with five concrete quantities you have
 *            read yourself from Polygon Amoy.
 * Key facts: Polygon PoS mainnet is chain ID 137 and Amoy testnet is 80002,
 *            both with POL as the gas token (Polygon docs, "Network
 *            information"). A public client is read-only: it holds no key and
 *            can sign nothing.
 *
 * Run: npm run l2        (network required; read-only; no key involved)
 */

import { createPublicClient, http, formatEther, formatGwei } from "viem";
import { polygonAmoy } from "viem/chains";
import { withRetry } from "./_rpc.ts";

// A Transport is *how* you talk to a node; a Chain is *which* node you expect
// to be on. Separating them is viem's central design decision, and it is why
// pointing this file at a paid Alchemy or Infura URL is a one-line change.
const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

const chainId = await withRetry(() => client.getChainId());
console.log("--- who am I talking to ---");
console.log("chain id          :", chainId, chainId === 80002 ? "(Amoy)" : "(NOT Amoy!)");
console.log(
  "Always assert this. Every EVM chain speaks the same JSON-RPC, so an RPC URL\n" +
    "pointing at the wrong network fails silently — you read plausible numbers\n" +
    "from a chain nobody is playing on.\n",
);

// ---------------------------------------------------------------------------
// The head of the chain.
// ---------------------------------------------------------------------------

const latest = await withRetry(() => client.getBlock({ blockTag: "latest" }));

console.log("--- the head block ---");
console.log("number            :", latest.number);
console.log("timestamp         :", new Date(Number(latest.timestamp) * 1000).toISOString());
console.log("parentHash        :", latest.parentHash);
console.log("transactions      :", latest.transactions.length);
console.log("gasUsed / gasLimit:", latest.gasUsed, "/", latest.gasLimit);
console.log(
  "baseFeePerGas     :",
  latest.baseFeePerGas === null ? "none" : `${formatGwei(latest.baseFeePerGas)} gwei`,
);
console.log(
  "\nThat parentHash is the same link you built by hand in level 1, except this\n" +
    "one is real. Every number here arrived as a hex string over HTTP and viem\n" +
    "parsed it into a JavaScript bigint — never a number. Timestamps, balances,\n" +
    "gas: all bigint. This is the single most common source of `Cannot mix BigInt\n" +
    "and other types` errors in a first web3 backend.\n",
);

// ---------------------------------------------------------------------------
// Finality: "latest" is a claim, "finalized" is a commitment.
// ---------------------------------------------------------------------------

const finalized = await withRetry(() => client.getBlock({ blockTag: "finalized" }));
const lag = latest.number - finalized.number;

console.log("--- finality ---");
console.log("latest    :", latest.number);
console.log("finalized :", finalized.number);
console.log("lag       :", lag, "blocks");
console.log(
  "Those two numbers are the whole reason an indexer is hard. Blocks between\n" +
    "finalized and latest can still disappear in a reorganisation. If your game\n" +
    "credits a player an item the instant it sees the event at the head, and the\n" +
    "chain then reorganises, you have created an item out of nothing. Level 8\n" +
    "deals with this properly; for now, notice that the risk is measurable and\n" +
    "you just measured it.\n",
);

// ---------------------------------------------------------------------------
// Balances and fees.
// ---------------------------------------------------------------------------

// Vitalik's address — a public, well-known account, used here only as something
// guaranteed to exist. On Amoy it will almost certainly hold nothing.
const someone = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" as const;
const balance = await withRetry(() => client.getBalance({ address: someone }));

console.log("--- an account ---");
console.log("address :", someone);
console.log("balance :", formatEther(balance), "POL");
console.log("nonce   :", await withRetry(() => client.getTransactionCount({ address: someone })));
console.log(
  "The nonce is the count of transactions this account has already sent, and it\n" +
    "is the account's write cursor: the chain will only accept nonce N when it\n" +
    "has accepted N-1. Level 9 is entirely about respecting that.\n",
);

const fees = await withRetry(() => client.estimateFeesPerGas());
console.log("--- fee market ---");
console.log("maxFeePerGas         :", formatGwei(fees.maxFeePerGas), "gwei");
console.log("maxPriorityFeePerGas :", formatGwei(fees.maxPriorityFeePerGas), "gwei");
console.log(
  "Read these as an order book, because that is what they are. The base fee is\n" +
    "the clearing price the protocol sets by itself and then burns (EIP-1559);\n" +
    "the priority fee is your bid for position in the builder's queue. maxFeePerGas\n" +
    "is the highest total you will tolerate — set it too low and your transaction\n" +
    "is a limit order that never fills, and it will sit in the mempool, not fail.",
);
