/**
 * Level 1 — Hashes, chains of hashes, and where an address comes from.
 *
 * Use case:  The two primitives every later level rests on. A block "chain" is
 *            a linked list whose links are hashes, and an Ethereum address is
 *            nothing but the tail of a hash of a public key.
 * Purpose:   Prove to yourself that neither of these is magic, by computing
 *            both by hand and checking your answer against the library.
 * Key facts: keccak256 is Ethereum's hash (NOT the SHA-3 the NIST standard
 *            settled on — it is the original Keccak submission, which differs
 *            in its padding byte). An address is the last 20 bytes of
 *            keccak256 of the 64-byte uncompressed public key.
 *
 * Run: npm run l1        (no network, no key with value, nothing to install
 *                         beyond this folder's own dependencies)
 */

import { keccak256, toHex, stringToHex, getAddress, type Hex } from "viem";
import { privateKeyToAccount, publicKeyToAddress } from "viem/accounts";

// ---------------------------------------------------------------------------
// Part 1 — a hash is a deterministic fingerprint with no visible structure.
// ---------------------------------------------------------------------------

console.log("--- Part 1: the fingerprint ---");
console.log("keccak256('gold sword')  =", keccak256(stringToHex("gold sword")));
console.log("keccak256('gold sworb')  =", keccak256(stringToHex("gold sworb")));
console.log(
  "Same length, one letter apart, and not one nibble in common. That is the\n" +
    "avalanche property, and it is the whole reason a hash can stand in for the\n" +
    "data it summarises.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — a chain is a linked list whose pointers are hashes.
// ---------------------------------------------------------------------------

type Block = {
  readonly height: number;
  readonly parentHash: Hex;
  readonly payload: string;
};

/**
 * Hash a block the way a real one is hashed: over its *header*, which includes
 * the parent's hash. That inclusion is what makes the structure tamper-evident
 * rather than merely ordered.
 */
function hashBlock(block: Block): Hex {
  const header = `${block.height}|${block.parentHash}|${block.payload}`;
  return keccak256(stringToHex(header));
}

const GENESIS_PARENT: Hex = `0x${"00".repeat(32)}`;

function buildChain(payloads: readonly string[]): Block[] {
  const chain: Block[] = [];
  let parentHash: Hex = GENESIS_PARENT;
  for (const [index, payload] of payloads.entries()) {
    const block: Block = { height: index, parentHash, payload };
    chain.push(block);
    parentHash = hashBlock(block);
  }
  return chain;
}

/** Walk the chain forward, checking each block points at the real parent. */
function findBreak(chain: readonly Block[]): number | null {
  let expectedParent: Hex = GENESIS_PARENT;
  for (const block of chain) {
    if (block.parentHash !== expectedParent) return block.height;
    expectedParent = hashBlock(block);
  }
  return null;
}

console.log("--- Part 2: why you cannot quietly edit history ---");

const chain = buildChain([
  "alice mints sword #1",
  "alice transfers sword #1 to bob",
  "bob stakes sword #1",
]);

console.log("honest chain, first broken height:", findBreak(chain)); // null

// Break it on purpose: rewrite block 1 so the sword goes to mallory instead.
const tampered: Block[] = chain.map((block) =>
  block.height === 1
    ? { ...block, payload: "alice transfers sword #1 to mallory" }
    : block,
);

console.log("tampered chain, first broken height:", findBreak(tampered)); // 2
console.log(
  "Editing block 1 did not corrupt block 1 — it is perfectly well-formed. It\n" +
    "corrupted block 2, whose parentHash still names the block 1 that used to\n" +
    "exist. To make the lie hold you must re-hash every block after it, which is\n" +
    "exactly the work that proof-of-work or a staked validator set makes\n" +
    "expensive. That cost is the entire security argument.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — where an address comes from.
// ---------------------------------------------------------------------------

console.log("--- Part 3: deriving an address by hand ---");

// A throwaway key. It is the standard Hardhat/Anvil account #0 — published in
// documentation everywhere, holding nothing, and safe to print. Never put a key
// you care about in a source file, an env var on a shared box, or a chat window.
const TEST_PRIVATE_KEY: Hex =
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";

const account = privateKeyToAccount(TEST_PRIVATE_KEY);

// account.publicKey is the 65-byte uncompressed SEC1 encoding: a 0x04 prefix
// byte followed by the 32-byte X and 32-byte Y coordinates of the curve point.
// Ethereum hashes the 64 coordinate bytes only, so the prefix is stripped.
const publicKey = account.publicKey;
const coordinates: Hex = `0x${publicKey.slice(4)}`; // drop "0x" and the "04"
const hashOfPublicKey = keccak256(coordinates);
const derived = getAddress(`0x${hashOfPublicKey.slice(-40)}`); // last 20 bytes

console.log("public key (65 bytes):", publicKey);
console.log("keccak256 of X||Y     :", hashOfPublicKey);
console.log("last 20 bytes         :", derived);
console.log("library's answer      :", account.address);
console.log("viem publicKeyToAddress:", publicKeyToAddress(publicKey));
console.log("hand derivation matches:", derived === account.address);

console.log(
  "\nThe mixed case in the address is not decoration. EIP-55 encodes a checksum\n" +
    "in the choice of upper- and lower-case hex letters, which is why a wallet\n" +
    "can reject a mistyped address without asking the network anything. viem's\n" +
    "getAddress() applies it; passing a wrongly-cased address to a viem function\n" +
    "throws rather than silently sending funds into a void.",
);

console.log(
  "\nNotice what never happened here: nothing was registered anywhere. The\n" +
    "address existed the moment the key did, offline, and the chain learns of it\n" +
    "only when it first appears in a transaction. Accounts are not created; they\n" +
    "are discovered. " + toHex(0) + " ← and yes, hex zero is just '0x0'.",
);
