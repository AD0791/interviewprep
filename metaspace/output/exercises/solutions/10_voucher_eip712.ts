/**
 * Level 10 — EIP-712 vouchers, and proving both languages agree.
 *
 * Use case:  A player earned a sword inside your game. You want them to be
 *            able to mint it on chain, exactly once, without your server
 *            paying gas for rewards nobody claims and without holding a key
 *            that can mint anything at any time.
 * Purpose:   Sign the authorisation as typed structured data, then prove
 *            mechanically that the type hash your TypeScript computes is the
 *            same 32 bytes the Solidity compiler embedded in the contract.
 * Key facts: A signature over a plain string is valid on every chain and to
 *            every contract, forever. EIP-712 binds it to one contract, one
 *            chain, one application and one shape of data. The type string
 *            must match byte for byte on both sides — including the spaces.
 *
 * Requires:  cd ../contracts && npm install && node compile.mjs
 *            (that writes artifacts.json, which part 2 reads)
 *
 * Run: npm run l10       (no network, no funds, nothing broadcast)
 */

import {
  keccak256,
  stringToHex,
  encodeAbiParameters,
  parseAbiParameters,
  recoverTypedDataAddress,
  verifyTypedData,
  type Hex,
} from "viem";
import { polygonAmoy, polygon } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import { DatabaseSync } from "node:sqlite";
import { readFileSync } from "node:fs";
import { join } from "node:path";

// The backend's signing key. In production this lives in a KMS or an HSM and
// the signing service is the only thing that can reach it — because possession
// of this key is the authority to mint.
const backendSigner = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);

const PLAYER = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" as const;
// Stands in for the deployed ItemLedgerV3. The address is part of what gets
// signed, which is exactly the point of part 3.
const CONTRACT = "0x5FbDB2315678afecb367f032d93F642f64180aa3" as const;

// ---------------------------------------------------------------------------
// The typed data. These three objects are the whole protocol.
// ---------------------------------------------------------------------------

const domain = {
  name: "Metaspace Items",
  version: "1",
  chainId: polygonAmoy.id,
  verifyingContract: CONTRACT,
} as const;

const types = {
  Voucher: [
    { name: "to", type: "address" },
    { name: "itemId", type: "uint256" },
    { name: "amount", type: "uint256" },
    { name: "voucherId", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
} as const;

const voucher = {
  to: PLAYER,
  itemId: 42n,
  amount: 1n,
  voucherId: 9001n,
  deadline: BigInt(Math.floor(Date.now() / 1000) + 3600),
} as const;

// ---------------------------------------------------------------------------
// Part 1 — sign it, and recover the signer.
// ---------------------------------------------------------------------------

console.log("--- Part 1: issuing a voucher ---");

const signature = await backendSigner.signTypedData({
  domain,
  types,
  primaryType: "Voucher",
  message: voucher,
});

console.log("backend signer :", backendSigner.address);
console.log("signature      :", signature.slice(0, 26) + "…");

const recovered = await recoverTypedDataAddress({
  domain,
  types,
  primaryType: "Voucher",
  message: voucher,
  signature,
});
console.log("recovered      :", recovered);
console.log("matches        :", recovered === backendSigner.address);

console.log(
  "\nNothing has touched a chain. The player now holds a piece of data that the\n" +
    "contract will accept exactly once, and your server has paid nothing. If the\n" +
    "player never claims it, it costs nobody anything — which is why this pattern\n" +
    "exists rather than having the backend mint directly.\n",
);

// ---------------------------------------------------------------------------
// Part 2 — the hashes, by hand, and the cross-language proof.
// ---------------------------------------------------------------------------

console.log("--- Part 2: do TypeScript and Solidity agree? ---");

// The type string is built by a rule, not by taste: the struct name, then its
// fields as "type name", comma separated, in declaration order, no spaces
// anywhere except the one between each type and name.
const TYPE_STRING =
  "Voucher(address to,uint256 itemId,uint256 amount,uint256 voucherId,uint256 deadline)";
const typeHash = keccak256(stringToHex(TYPE_STRING));

const DOMAIN_TYPE_STRING =
  "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";
const domainSeparator = keccak256(
  encodeAbiParameters(parseAbiParameters("bytes32, bytes32, bytes32, uint256, address"), [
    keccak256(stringToHex(DOMAIN_TYPE_STRING)),
    keccak256(stringToHex(domain.name)),
    keccak256(stringToHex(domain.version)),
    BigInt(domain.chainId),
    domain.verifyingContract,
  ]),
);

console.log("type hash        :", typeHash);
console.log("domain separator :", domainSeparator);

// The proof. VOUCHER_TYPEHASH is a compile-time constant in ItemLedgerV3, so
// solc embeds those 32 bytes directly in the deployed bytecode as a PUSH32.
// If the two sides ever disagree, these bytes are simply not there.
const artifactPath = join(import.meta.dirname, "..", "contracts", "artifacts.json");

let bytecode: string | undefined;
try {
  const artifacts = JSON.parse(readFileSync(artifactPath, "utf8")) as Record<
    string,
    { deployedBytecode: string }
  >;
  bytecode = artifacts.ItemLedgerV3?.deployedBytecode;
} catch {
  bytecode = undefined;
}

if (!bytecode) {
  console.log(
    "\n(no artifacts.json — run `cd ../contracts && npm install && node compile.mjs`\n" +
      " to enable the cross-language check)",
  );
} else {
  const embedded = bytecode.includes(typeHash.slice(2));
  console.log("\ntype hash found in the compiled contract bytecode:", embedded);

  const wrongTypeString =
    "Voucher(address to, uint256 itemId, uint256 amount, uint256 voucherId, uint256 deadline)";
  const wrongTypeHash = keccak256(stringToHex(wrongTypeString));
  console.log("same string with spaces after the commas:", wrongTypeHash.slice(0, 26) + "…");
  console.log("that one found in the bytecode          :", bytecode.includes(wrongTypeHash.slice(2)));

  if (!embedded) {
    console.error("\nFAILED: the signer and the contract disagree about the type hash.");
    process.exitCode = 1;
  }
}

console.log(
  "\nThat is the test worth writing, and it is the one most teams do not have.\n" +
    "Four spaces — legal, readable, the kind of thing a formatter adds — produce a\n" +
    "completely different type hash, and therefore a digest the contract will never\n" +
    "recognise. The failure mode is the cruel one: nothing throws, no error\n" +
    "mentions the type string, the signature is perfectly valid, and the contract\n" +
    "simply recovers some other address and reverts with 'bad signature'. Teams\n" +
    "lose days to this. A test that hashes the string on both sides and compares\n" +
    "catches it in milliseconds.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — what the domain actually protects.
// ---------------------------------------------------------------------------

console.log("--- Part 3: change one field of the domain ---");

const mainnetDomain = { ...domain, chainId: polygon.id } as const;
const otherContractDomain = { ...domain, verifyingContract: PLAYER } as const;

for (const [label, candidate] of [
  ["the intended contract on Amoy", domain],
  ["the same contract on Polygon mainnet", mainnetDomain],
  ["a different contract on Amoy", otherContractDomain],
] as const) {
  const valid = await verifyTypedData({
    address: backendSigner.address,
    domain: candidate,
    types,
    primaryType: "Voucher",
    message: voucher,
    signature,
  });
  console.log(`  ${label.padEnd(38)} -> ${valid ? "ACCEPTED" : "rejected"}`);
}

console.log(
  "\nOne signature, three contexts, one acceptance. Compare that with level 4,\n" +
    "where a signature over the plain string 'mint item 42 to 0x…' was valid on\n" +
    "every chain and to every contract that happened to check the same words —\n" +
    "so a voucher issued on a testnet could be replayed on mainnet. The domain\n" +
    "separator is what closes that, and it costs one struct.\n",
);

// ---------------------------------------------------------------------------
// Part 4 — the part that is not cryptography at all.
// ---------------------------------------------------------------------------

console.log("--- Part 4: the voucher id, which is a database problem ---");

const db = new DatabaseSync(":memory:");
db.exec(`
CREATE TABLE reward (
  reward_id  TEXT PRIMARY KEY,   -- the in-game reward being claimed
  voucher_id INTEGER NOT NULL UNIQUE,
  player     TEXT NOT NULL
);
`);

/** Issue a voucher for a reward, at most once, ever. */
function issue(rewardId: string, player: string, voucherId: number): "issued" | "already issued" {
  const existing = db
    .prepare("SELECT voucher_id FROM reward WHERE reward_id = ?")
    .get(rewardId) as { voucher_id: number } | undefined;
  if (existing) return "already issued";
  try {
    db.prepare("INSERT INTO reward (reward_id, voucher_id, player) VALUES (?, ?, ?)").run(
      rewardId,
      voucherId,
      player,
    );
    return "issued";
  } catch {
    // The unique constraint fired: another request won the race between our
    // SELECT and our INSERT. This catch is not error handling, it IS the
    // concurrency control, and it is the only version that works across
    // replicas.
    return "already issued";
  }
}

console.log("first request  :", issue("dungeon-run-77", PLAYER, 9001));
console.log("retry, same id :", issue("dungeon-run-77", PLAYER, 9002));

const rows = db.prepare("SELECT COUNT(*) AS n FROM reward").get() as { n: number };
console.log("rows in reward :", rows.n);
db.close();

console.log(
  "\nThe cryptography in this file is the easy half. The half that decides whether\n" +
    "players can duplicate items is the ordinary database discipline in part 4:\n" +
    "one reward maps to one voucher id, forever, enforced by a constraint rather\n" +
    "than by a check the code performs and hopes to have performed first. A client\n" +
    "that retries a claim — because the network dropped, because the player tapped\n" +
    "twice, because a queue redelivered — must receive the SAME voucher back, not a\n" +
    "second one.\n\n" +
    "Notice that the contract already refuses to mint the same voucher id twice, so\n" +
    "a duplicate would be caught on chain. That is a backstop, not a design: it\n" +
    "wastes the player's gas on a transaction that reverts, and it means your own\n" +
    "records are wrong even though the chain is right. Correct on chain and wrong\n" +
    "in your database is still an incident, and it is the one your support team\n" +
    "sees.",
);
