/**
 * Level 3 — Reading a contract: what an ABI is, and what a call really sends.
 *
 * Use case:  Your game backend needs to answer "does this player own item 42?"
 *            That is a contract read, and it is the cheapest, most common
 *            on-chain operation there is — free, instant, and off the record.
 * Purpose:   Take the mystery out of `readContract` by building the same call
 *            by hand out of a function selector, then letting viem do it.
 * Key facts: A function selector is the first four bytes of the keccak256 hash
 *            of the canonical signature, e.g. keccak256("totalSupply()")[0..4].
 *            eth_call executes against a node's local state and changes
 *            nothing, so it costs no gas and needs no key.
 *
 * Target:    WPOL on Polygon Amoy, 0x360ad4f9a9A8EFe9A8DCB5f461c4Cc1047E1Dcf9.
 *            Wrapped POL is an ordinary ERC-20 that exists because the native
 *            gas token is not itself a token and therefore has no transferFrom.
 *
 * Run: npm run l3        (network required; read-only; no key involved)
 */

import {
  createPublicClient,
  http,
  erc20Abi,
  keccak256,
  stringToHex,
  slice,
  formatUnits,
  getAddress,
  isAddress,
  type Address,
} from "viem";
import { polygonAmoy } from "viem/chains";
import { withRetry } from "./_rpc.ts";

const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

const WPOL: Address = "0x360ad4f9a9A8EFe9A8DCB5f461c4Cc1047E1Dcf9";

// ---------------------------------------------------------------------------
// Part 1 — the raw call, by hand.
// ---------------------------------------------------------------------------

console.log("--- Part 1: a contract call is four bytes and some arguments ---");

const selector = slice(keccak256(stringToHex("totalSupply()")), 0, 4);
console.log("keccak256('totalSupply()')[0:4] =", selector);

const raw = await withRetry(() => client.call({ to: WPOL, data: selector }));
console.log("eth_call returned               =", raw.data);
console.log("as a bigint                     =", BigInt(raw.data ?? "0x0"));

console.log(
  "\nThat is the entire protocol. There is no method table, no reflection, no\n" +
    "registry: the contract's dispatcher compares the first four bytes of the\n" +
    "calldata against the selectors it knows and jumps. Arguments follow, each\n" +
    "padded to 32 bytes. An ABI file is not something the chain has — it is a\n" +
    "description *you* keep so you can build those bytes and decode the answer.\n" +
    "Lose the ABI and the contract still works; you just cannot talk to it.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — the same call, typed.
// ---------------------------------------------------------------------------

console.log("--- Part 2: the same thing, with the types doing the work ---");

const [name, symbol, decimals, totalSupply] = await withRetry(() =>
  Promise.all([
    client.readContract({ address: WPOL, abi: erc20Abi, functionName: "name" }),
    client.readContract({ address: WPOL, abi: erc20Abi, functionName: "symbol" }),
    client.readContract({ address: WPOL, abi: erc20Abi, functionName: "decimals" }),
    client.readContract({ address: WPOL, abi: erc20Abi, functionName: "totalSupply" }),
  ]),
);

console.log("name        :", name);
console.log("symbol      :", symbol);
console.log("decimals    :", decimals);
console.log("totalSupply :", totalSupply, "(raw)");
console.log("totalSupply :", formatUnits(totalSupply, decimals), symbol);

console.log(
  "\nThe raw number is not a quantity of tokens; it is a count of the smallest\n" +
    "indivisible unit. Dividing by 10**decimals is a display concern and belongs\n" +
    "at the very edge of your system. Store the bigint. Every rounding bug in\n" +
    "every token ledger starts with someone putting a float in a database column.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — break it on purpose, twice.
// ---------------------------------------------------------------------------

console.log("--- Part 3: two failures worth having seen before the interview ---");

// (a) A mistyped address: the real WPOL address with its final 9 changed to 8.
//     EIP-55 hides a checksum in the *casing* of the hex letters, so this is
//     catchable locally, with no network round trip — but only if you ask.
const mistyped = "0x360ad4f9a9A8EFe9A8DCB5f461c4Cc1047E1Dcf8";
console.log("(a) isAddress(mistyped, { strict: true }) =", isAddress(mistyped, { strict: true }));
console.log("(a) getAddress(mistyped)                  =", getAddress(mistyped));
console.log(
  "    Look carefully: getAddress did NOT throw. It re-cased the string into a\n" +
    "    valid-looking checksummed address and handed it back. getAddress\n" +
    "    normalises; isAddress(x, { strict: true }) is the one that verifies.\n" +
    "    Confusing the two is how a typo reaches production wearing a costume.",
);

// (b) Calling a function the contract does not have. The selector matches
//     nothing, the dispatcher falls through, and the call reverts.
const fakeAbi = [
  {
    type: "function",
    name: "ownerOfEverything",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "address" }],
  },
] as const;

try {
  await client.readContract({ address: WPOL, abi: fakeAbi, functionName: "ownerOfEverything" });
} catch (error) {
  console.log("(b) wrong selector ->", (error as Error).message.split("\n")[0]);
}

console.log(
  "\nThe second failure is the one that bites in production. There is no such\n" +
    "thing as a 404 on chain: a call to a function that does not exist looks\n" +
    "exactly like a call to a function that reverted, and a call to an address\n" +
    "holding no code at all returns empty data that naive decoders read as zero.\n" +
    "If your backend is 'reading a balance' from a mistyped address, it will\n" +
    "cheerfully report zero forever. Check getCode() once at startup.\n",
);

// ---------------------------------------------------------------------------
// Part 4 — one round trip instead of four.
// ---------------------------------------------------------------------------

console.log("--- Part 4: multicall ---");

const results = await withRetry(() =>
  client.multicall({
    contracts: [
      { address: WPOL, abi: erc20Abi, functionName: "name" },
      { address: WPOL, abi: erc20Abi, functionName: "symbol" },
      { address: WPOL, abi: erc20Abi, functionName: "decimals" },
    ],
  }),
);

console.log(results.map((r) => `${r.status}:${String(r.result)}`).join("  "));
console.log(
  "One HTTP request, three reads, all at the same block height — which is the\n" +
    "point that matters more than the speed. Four separate reads can straddle a\n" +
    "block boundary and hand you an inconsistent snapshot. Multicall3 is deployed\n" +
    "at the same address on nearly every EVM chain and viem uses it automatically\n" +
    "when the chain config declares it.",
);
