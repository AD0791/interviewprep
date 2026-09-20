/**
 * Level 12 — The whole loop.
 *
 * Use case:  Everything the previous eleven levels built, wired into one
 *            system: a player logs in with a wallet, claims a reward earned
 *            off chain, mints it on chain, and reads an inventory served from
 *            a database that an indexer keeps in sync with events.
 * Purpose:   Be able to narrate this path in thirty seconds, from having built
 *            it rather than from having read about it.
 * Key facts: The chain is the source of truth for OWNERSHIP. The database is
 *            the source of truth for SPEED. The indexer is the one-way bridge.
 *            The inventory endpoint never calls an RPC.
 *
 * Requires:  cd ../contracts && npm install && node compile.mjs
 *
 * Run: npm run l12       (no network, no funds — local EVM, in-memory SQLite)
 */

import express from "express";
import { DatabaseSync } from "node:sqlite";
import { createEVM } from "@ethereumjs/evm";
import { createAddressFromString, hexToBytes, bytesToHex, type Address } from "@ethereumjs/util";
import {
  createSiweMessage,
  generateSiweNonce,
  verifySiweMessage,
} from "viem/siwe";
import {
  createPublicClient,
  http,
  encodeDeployData,
  encodeFunctionData,
  decodeFunctionResult,
  decodeEventLog,
  type Abi,
  type Hex,
} from "viem";
import { polygonAmoy } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";

// ---------------------------------------------------------------------------
// The chain. A local EVM stands in for Polygon so the whole loop runs offline;
// every line below would be identical against Amoy, with viem's wallet client
// in place of `evm.runCall`.
// ---------------------------------------------------------------------------

function requireArtifacts(): Record<string, { abi: Abi; bytecode: Hex; deployedBytecode: Hex }> {
  const path = join(import.meta.dirname, "..", "contracts", "artifacts.json");
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    console.error(
      "No compiled contracts found.\n\n" +
        "This level executes real Solidity in a local EVM, so it needs the\n" +
        "artifacts first. They are build output and are not committed:\n\n" +
        "  cd ../contracts && npm install && node compile.mjs\n",
    );
    process.exit(1);
  }
}

const artifacts = requireArtifacts();

const CONTRACT = "GameItemsFixed";
const abi = artifacts[CONTRACT]!.abi;

const backendSigner = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);
const player = privateKeyToAccount(
  "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
);

const SENDER = createAddressFromString(player.address);
const evm = await createEVM();

const deployResult = await evm.runCall({
  caller: SENDER,
  origin: SENDER,
  gasLimit: 10_000_000n,
  data: hexToBytes(
    encodeDeployData({ abi, bytecode: artifacts[CONTRACT]!.bytecode, args: [backendSigner.address] }),
  ),
});
const tokenAddress: Address = deployResult.createdAddress!;
console.log(`contract deployed at ${tokenAddress.toString()} (local EVM)\n`);

// ---------------------------------------------------------------------------
// The database: sessions, rewards, indexed logs, inventory.
// ---------------------------------------------------------------------------

const db = new DatabaseSync(":memory:");
db.exec(`
CREATE TABLE siwe_nonce (nonce TEXT PRIMARY KEY);
CREATE TABLE session (token TEXT PRIMARY KEY, address TEXT NOT NULL);

-- One row per reward the game has granted. The UNIQUE on reward_id is what
-- makes claiming idempotent: a retry finds the row and returns the SAME
-- voucher rather than minting a second one.
CREATE TABLE reward (
  reward_id  TEXT PRIMARY KEY,
  player     TEXT    NOT NULL,
  item_id    INTEGER NOT NULL,
  amount     INTEGER NOT NULL,
  voucher_id INTEGER NOT NULL UNIQUE,
  signature  TEXT,
  deadline   INTEGER NOT NULL
);

-- What the indexer has seen. Keyed on the log's natural identity, so
-- reprocessing is free (level 7).
CREATE TABLE indexed_log (
  tx_id     TEXT    NOT NULL,
  log_index INTEGER NOT NULL,
  player    TEXT    NOT NULL,
  item_id   INTEGER NOT NULL,
  amount    INTEGER NOT NULL,
  PRIMARY KEY (tx_id, log_index)
);

-- Derived, and therefore rebuilt rather than incremented (level 8).
CREATE TABLE inventory (
  player  TEXT    NOT NULL,
  item_id INTEGER NOT NULL,
  amount  INTEGER NOT NULL,
  PRIMARY KEY (player, item_id)
);
`);

function rebuildInventory(): void {
  db.exec("DELETE FROM inventory");
  db.exec(`
    INSERT INTO inventory (player, item_id, amount)
    SELECT player, item_id, SUM(amount) FROM indexed_log GROUP BY player, item_id
  `);
}

// ---------------------------------------------------------------------------
// The indexer. Given the logs a transaction produced, write them down once.
// ---------------------------------------------------------------------------

type RawLog = [Uint8Array, Uint8Array[], Uint8Array];

function indexLogs(txId: string, logs: readonly RawLog[]): number {
  const insert = db.prepare(
    `INSERT OR IGNORE INTO indexed_log (tx_id, log_index, player, item_id, amount)
     VALUES (?, ?, ?, ?, ?)`,
  );

  let inserted = 0;
  db.exec("BEGIN");
  try {
    logs.forEach((log, logIndex) => {
      const [, topics, data] = log;
      const decoded = decodeEventLog({
        abi,
        topics: topics.map((t) => bytesToHex(t)) as [Hex, ...Hex[]],
        data: bytesToHex(data) as Hex,
      });
      if (decoded.eventName !== "ItemMinted") return;

      const args = decoded.args as unknown as { to: Hex; itemId: bigint; amount: bigint };
      const result = insert.run(
        txId,
        logIndex,
        args.to.toLowerCase(),
        Number(args.itemId),
        Number(args.amount),
      );
      if (result.changes > 0) inserted += 1;
    });
    rebuildInventory();
    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
  return inserted;
}

// ---------------------------------------------------------------------------
// The API.
// ---------------------------------------------------------------------------

const DOMAIN = "metaspace.example";
const app = express();
app.use(express.json());

app.get("/auth/nonce", (_request, response) => {
  const nonce = generateSiweNonce();
  db.prepare("INSERT INTO siwe_nonce (nonce) VALUES (?)").run(nonce);
  response.json({ nonce });
});

app.post("/auth/verify", async (request, response) => {
  const { message, signature } = request.body as { message: string; signature: Hex };

  const valid = await verifySiweMessage(
    createPublicClient({ chain: polygonAmoy, transport: http("http://127.0.0.1:1") }),
    { message, signature, domain: DOMAIN },
  ).catch(() => false);
  if (!valid) return response.status(401).json({ error: "bad signature" });

  const nonce = /\nNonce: (\S+)/.exec(message)?.[1] ?? "";
  // Single statement, so two concurrent requests cannot both win (level 5).
  const burned = db.prepare("DELETE FROM siwe_nonce WHERE nonce = ?").run(nonce);
  if (burned.changes === 0) return response.status(401).json({ error: "nonce unknown or used" });

  const address = (/\n(0x[0-9a-fA-F]{40})\n/.exec(message)?.[1] ?? "").toLowerCase();
  const token = randomUUID();
  db.prepare("INSERT INTO session (token, address) VALUES (?, ?)").run(token, address);
  response.json({ token, address });
});

function authenticate(request: express.Request): string | null {
  const token = request.header("authorization")?.replace("Bearer ", "") ?? "";
  const row = db.prepare("SELECT address FROM session WHERE token = ?").get(token) as
    | { address: string }
    | undefined;
  return row?.address ?? null;
}

/** Issue (or re-issue) the voucher for one reward. Idempotent by construction. */
app.post("/rewards/:rewardId/claim", async (request, response) => {
  const address = authenticate(request);
  if (!address) return response.status(401).json({ error: "not logged in" });

  const rewardId = request.params.rewardId;
  const existing = db.prepare("SELECT * FROM reward WHERE reward_id = ?").get(rewardId) as
    | { voucher_id: number; item_id: number; amount: number; deadline: number; signature: string }
    | undefined;

  if (existing) {
    // The retry path. Same voucher, same signature, same id — the player can
    // call this as many times as they like and can never obtain two.
    return response.json({
      reused: true,
      voucher: {
        to: address,
        itemId: String(existing.item_id),
        amount: String(existing.amount),
        voucherId: String(existing.voucher_id),
        deadline: String(existing.deadline),
      },
      signature: existing.signature,
    });
  }

  const voucherId = Date.now();
  const deadline = Math.floor(Date.now() / 1000) + 3600;
  const voucher = {
    to: address as Hex,
    itemId: 42n,
    amount: 1n,
    voucherId: BigInt(voucherId),
    deadline: BigInt(deadline),
  };

  const signature = await backendSigner.signTypedData({
    domain: {
      name: "Metaspace Items",
      version: "1",
      chainId: 1,
      verifyingContract: tokenAddress.toString() as Hex,
    },
    types: {
      Voucher: [
        { name: "to", type: "address" },
        { name: "itemId", type: "uint256" },
        { name: "amount", type: "uint256" },
        { name: "voucherId", type: "uint256" },
        { name: "deadline", type: "uint256" },
      ],
    },
    primaryType: "Voucher",
    message: voucher,
  });

  db.prepare(
    `INSERT INTO reward (reward_id, player, item_id, amount, voucher_id, signature, deadline)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
  ).run(rewardId, address, 42, 1, voucherId, signature, deadline);

  response.json({
    reused: false,
    voucher: {
      to: address,
      itemId: "42",
      amount: "1",
      voucherId: String(voucherId),
      deadline: String(deadline),
    },
    signature,
  });
});

/**
 * Stands in for the player's wallet submitting the transaction. On a real
 * chain this endpoint would not exist — the player broadcasts it themselves,
 * or a relayer does (level 9).
 */
app.post("/chain/submit", async (request, response) => {
  const { voucher, signature } = request.body as {
    voucher: { to: Hex; itemId: string; amount: string; voucherId: string; deadline: string };
    signature: Hex;
  };

  const result = await evm.runCall({
    caller: SENDER,
    origin: SENDER,
    to: tokenAddress,
    gasLimit: 5_000_000n,
    data: hexToBytes(
      encodeFunctionData({
        abi,
        functionName: "mintWithVoucher",
        args: [
          {
            to: voucher.to,
            itemId: BigInt(voucher.itemId),
            amount: BigInt(voucher.amount),
            voucherId: BigInt(voucher.voucherId),
            deadline: BigInt(voucher.deadline),
          },
          signature,
        ],
      }),
    ),
  });

  if (result.execResult.exceptionError) {
    return response.status(400).json({ status: "reverted" });
  }

  // The indexer runs. On a real chain this is a separate process polling from
  // its checkpoint (level 7); here it is called inline so the flow is legible.
  const txId = randomUUID();
  const indexed = indexLogs(txId, result.execResult.logs ?? []);
  response.json({ status: "success", logs: (result.execResult.logs ?? []).length, indexed });
});

app.get("/inventory", (request, response) => {
  const address = authenticate(request);
  if (!address) return response.status(401).json({ error: "not logged in" });

  // No RPC. No contract call. Just Postgres — SQLite here — answering the
  // question the game actually asks, thousands of times a second.
  const items = db
    .prepare("SELECT item_id, amount FROM inventory WHERE player = ?")
    .all(address) as { item_id: number; amount: number }[];
  response.json({ address, items });
});

// ---------------------------------------------------------------------------
// Drive the whole thing.
// ---------------------------------------------------------------------------

const server = app.listen(0);
const port = (server.address() as { port: number }).port;
const base = `http://127.0.0.1:${port}`;

async function post(path: string, body: unknown, token?: string) {
  const response = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
  return { status: response.status, body: (await response.json()) as Record<string, unknown> };
}

// 1. Log in.
const { nonce } = (await (await fetch(`${base}/auth/nonce`)).json()) as { nonce: string };
const message = createSiweMessage({
  address: player.address,
  chainId: polygonAmoy.id,
  domain: DOMAIN,
  nonce,
  uri: `https://${DOMAIN}`,
  version: "1",
  expirationTime: new Date(Date.now() + 300_000),
});
const login = await post("/auth/verify", {
  message,
  signature: await player.signMessage({ message }),
});
const token = login.body.token as string;
console.log("1. SIWE login              ->", login.status, `session for ${login.body.address}`);

// 2. Inventory before anything happens.
const empty = await (
  await fetch(`${base}/inventory`, { headers: { authorization: `Bearer ${token}` } })
).json();
console.log("2. inventory (before)      ->", JSON.stringify(empty));

// 3. Claim the reward: the backend signs a voucher.
const claim = await post("/rewards/dungeon-run-77/claim", {}, token);
console.log("3. claim reward            -> voucher", (claim.body.voucher as { voucherId: string }).voucherId, `(reused: ${claim.body.reused})`);

// 4. Claim it again — the retry a flaky network or an impatient player causes.
const claimAgain = await post("/rewards/dungeon-run-77/claim", {}, token);
const sameVoucher =
  (claim.body.voucher as { voucherId: string }).voucherId ===
  (claimAgain.body.voucher as { voucherId: string }).voucherId;
console.log("4. claim again             -> same voucher:", sameVoucher, `(reused: ${claimAgain.body.reused})`);

// 5. Submit it on chain.
const mint = await post("/chain/submit", { voucher: claim.body.voucher, signature: claim.body.signature });
console.log("5. submit to chain         ->", mint.body.status, `| ${mint.body.logs} log(s), ${mint.body.indexed} indexed`);

// 6. Submit the very same voucher a second time.
const mintAgain = await post("/chain/submit", { voucher: claim.body.voucher, signature: claim.body.signature });
console.log("6. submit the same voucher ->", mintAgain.body.status, "(contract refused: voucher already used)");

// 7. Inventory after.
const after = await (
  await fetch(`${base}/inventory`, { headers: { authorization: `Bearer ${token}` } })
).json();
console.log("7. inventory (after)       ->", JSON.stringify(after));

server.close();
db.close();

const items = (after as { items: { amount: number }[] }).items;
if (items.length !== 1 || items[0]!.amount !== 1) {
  console.error("\nFAILED: expected exactly one item of amount 1.");
  process.exitCode = 1;
}

console.log(
  "\n" +
    "That is the entire system, and it is worth noticing how little of it is\n" +
    "blockchain. Steps 1, 2, 3, 4 and 7 are ordinary backend engineering:\n" +
    "sessions, idempotent writes, a database read. Step 5 is the only line that\n" +
    "touches a chain, and step 6 is the chain doing what your database already\n" +
    "did — refusing a duplicate.\n\n" +
    "Three defences stopped the player getting two swords, at three different\n" +
    "layers, and a good answer names all three. The database refused to issue a\n" +
    "second voucher for the same reward. The contract refused to honour the same\n" +
    "voucher id twice. And the indexer's primary key means that even if the same\n" +
    "event were delivered to it repeatedly, the inventory would not move. You\n" +
    "want all three: the first is correctness, the second is trustlessness, and\n" +
    "the third is what keeps your own records honest when the network misbehaves.\n\n" +
    "Say the last part out loud in the interview, because it is the sentence that\n" +
    "distinguishes an integration engineer from someone who has read a tutorial:\n" +
    "the chain is the source of truth for ownership, the database is the source\n" +
    "of truth for speed, and the indexer is the one-way bridge between them. The\n" +
    "inventory endpoint above never called an RPC — and in production, under\n" +
    "load, that is the difference between a game that responds in milliseconds\n" +
    "and a game that falls over when its provider rate-limits you.",
);
