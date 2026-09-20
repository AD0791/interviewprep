/**
 * Level 5 — Sign-In With Ethereum as an Express endpoint.
 *
 * Use case:  A player connects a wallet. There is no password and no account
 *            row yet, and the address alone proves nothing — anyone can type
 *            anyone's address. The server has to turn a signature into a
 *            session without ever seeing a key.
 * Purpose:   Build the real thing (EIP-4361), then attack it twice: once by
 *            replaying a used signature, and once by racing two requests
 *            through a check-then-delete nonce store.
 * Key facts: viem ships SIWE support in `viem/siwe` — generateSiweNonce,
 *            createSiweMessage, verifySiweMessage — so no extra dependency.
 *            The security lives in the nonce store, not in the crypto.
 *
 * Run: npm run l5   (no network, no chain, no key with value: this file boots
 *                    the server, plays the client against it, and exits)
 */

import express from "express";
import { createSiweMessage, generateSiweNonce, verifySiweMessage } from "viem/siwe";
import { createPublicClient, http, type Address } from "viem";
import { polygonAmoy } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import { randomUUID } from "node:crypto";

const DOMAIN = "metaspace.example";
const ORIGIN = `https://${DOMAIN}`;
const CHAIN_ID = polygonAmoy.id; // 80002

// verifySiweMessage needs a client for one reason only: an address may be a
// smart contract wallet, in which case the signature is validated on-chain via
// ERC-1271 instead of by recovery. For a plain EOA nothing is fetched.
const client = createPublicClient({
  chain: polygonAmoy,
  transport: http(process.env.RPC_URL ?? "https://polygon-amoy.drpc.org"),
});

// ---------------------------------------------------------------------------
// The nonce store — two versions, and the difference is the whole exercise.
// ---------------------------------------------------------------------------

type NonceStore = {
  readonly name: string;
  issue(): string;
  /** Consume the nonce. Returns true only if THIS call removed it. */
  consume(nonce: string): Promise<boolean>;
};

/**
 * The version most people write first. It reads, then awaits something, then
 * deletes. In between those two steps another request can read the same nonce
 * and also find it present. Both requests then succeed.
 */
function naiveStore(): NonceStore {
  const nonces = new Set<string>();
  return {
    name: "naive check-then-delete",
    issue() {
      const nonce = generateSiweNonce();
      nonces.add(nonce);
      return nonce;
    },
    async consume(nonce) {
      if (!nonces.has(nonce)) return false;
      // The window. In real code this is the latency of the SELECT and the
      // DELETE being two separate round trips to Postgres; here it is ten
      // milliseconds of the event loop being free to run the other request,
      // which is exactly what a database round trip buys an attacker.
      await new Promise((resolve) => setTimeout(resolve, 10));
      nonces.delete(nonce);
      return true;
    },
  };
}

/**
 * The correct version: test and remove in a single step with no await between
 * them. `Set.prototype.delete` returns whether it removed anything, which is
 * exactly the answer we need. In Postgres the equivalent is one statement —
 * DELETE FROM siwe_nonce WHERE nonce = $1 RETURNING nonce — and you trust the
 * row count, not a prior SELECT.
 */
function atomicStore(): NonceStore {
  const nonces = new Set<string>();
  return {
    name: "atomic delete-returning",
    issue() {
      const nonce = generateSiweNonce();
      nonces.add(nonce);
      return nonce;
    },
    async consume(nonce) {
      return nonces.delete(nonce);
    },
  };
}

// ---------------------------------------------------------------------------
// The server.
// ---------------------------------------------------------------------------

const sessions = new Map<string, Address>();

function buildApp(store: NonceStore) {
  const app = express();
  app.use(express.json());

  app.get("/auth/nonce", (_request, response) => {
    response.json({ nonce: store.issue() });
  });

  app.post("/auth/verify", async (request, response) => {
    const { message, signature } = request.body as { message: string; signature: `0x${string}` };

    // 1. Is the signature real, and does it match the address the message
    //    claims? verifySiweMessage also enforces the fields we pin here: a
    //    message for another domain, another chain, or an expired one fails.
    const valid = await verifySiweMessage(client, {
      message,
      signature,
      domain: DOMAIN,
    });
    if (!valid) return response.status(401).json({ error: "bad signature" });

    // 2. Was this nonce issued by us, and is this the first time it is used?
    //    Everything above is reusable by an attacker who saw it once; this is
    //    the only step that makes a login single-use.
    const nonce = /\nNonce: (\S+)/.exec(message)?.[1];
    if (!nonce) return response.status(400).json({ error: "no nonce in message" });
    if (!(await store.consume(nonce))) {
      return response.status(401).json({ error: "nonce unknown or already used" });
    }

    const address = /\n(0x[0-9a-fA-F]{40})\n/.exec(message)?.[1] as Address;
    const token = randomUUID();
    sessions.set(token, address);
    response.json({ token, address });
  });

  // An ordinary authenticated route. Note that from here on there is nothing
  // web3 about this service at all — it is a session token like any other.
  app.get("/me", (request, response) => {
    const token = request.header("authorization")?.replace("Bearer ", "") ?? "";
    const address = sessions.get(token);
    if (!address) return response.status(401).json({ error: "not logged in" });
    response.json({ address });
  });

  return app;
}

// ---------------------------------------------------------------------------
// The client, exercising the flow.
// ---------------------------------------------------------------------------

const player = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);

async function login(base: string) {
  const { nonce } = (await (await fetch(`${base}/auth/nonce`)).json()) as { nonce: string };

  const message = createSiweMessage({
    address: player.address,
    chainId: CHAIN_ID,
    domain: DOMAIN,
    nonce,
    uri: ORIGIN,
    version: "1",
    statement: "Sign in to Metaspace. This does not cost gas and moves no funds.",
    expirationTime: new Date(Date.now() + 5 * 60_000),
  });

  const signature = await player.signMessage({ message });
  const response = await fetch(`${base}/auth/verify`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, signature }),
  });
  return { message, signature, status: response.status, body: await response.json() };
}

async function replay(base: string, message: string, signature: `0x${string}`) {
  const response = await fetch(`${base}/auth/verify`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, signature }),
  });
  return { status: response.status, body: await response.json() };
}

function listen(app: express.Express): Promise<{ base: string; close: () => void }> {
  return new Promise((resolve) => {
    const server = app.listen(0, () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 0;
      resolve({ base: `http://127.0.0.1:${port}`, close: () => server.close() });
    });
  });
}

// ---------------------------------------------------------------------------
// Part 1 — the happy path, then the replay.
// ---------------------------------------------------------------------------

{
  const { base, close } = await listen(buildApp(atomicStore()));

  console.log("--- Part 1: login, then replay the same signature ---");
  const first = await login(base);
  console.log("first login        :", first.status, JSON.stringify(first.body));

  const session = (first.body as { token: string }).token;
  const me = await fetch(`${base}/me`, { headers: { authorization: `Bearer ${session}` } });
  console.log("GET /me with token :", me.status, JSON.stringify(await me.json()));

  const second = await replay(base, first.message, first.signature);
  console.log("replayed signature :", second.status, JSON.stringify(second.body));
  console.log(
    "\nThe signature is still perfectly valid — cryptographically nothing changed.\n" +
      "What changed is that the nonce it names no longer exists on the server. That\n" +
      "is the only thing standing between a stolen log line and a permanent account\n" +
      "takeover, and it lives in your database, not in the wallet.\n",
  );
  close();
}

// ---------------------------------------------------------------------------
// Part 2 — the race. Same payload, twice, concurrently.
// ---------------------------------------------------------------------------

console.log("--- Part 2a: the store itself, raced directly ---");

for (const store of [naiveStore(), atomicStore()]) {
  const nonce = store.issue();
  const [first, second] = await Promise.all([store.consume(nonce), store.consume(nonce)]);
  const accepted = [first, second].filter(Boolean).length;
  console.log(
    `${store.name.padEnd(26)} -> ${accepted} of 2 concurrent consumes succeeded`,
    accepted === 1 ? "(correct)" : "(BUG: the nonce was consumed twice)",
  );
}

console.log(
  "\nThat is the defect in isolation, and it is deterministic: the naive store\n" +
    "answers 'yes, it exists' to both callers because neither has deleted it yet.\n" +
    "Now watch the same defect through HTTP, where it is not deterministic at all.\n",
);

console.log("--- Part 2b: the same race through two concurrent HTTP requests ---");

for (const store of [naiveStore(), atomicStore()]) {
  const { base, close } = await listen(buildApp(store));

  const { nonce } = (await (await fetch(`${base}/auth/nonce`)).json()) as { nonce: string };
  const message = createSiweMessage({
    address: player.address,
    chainId: CHAIN_ID,
    domain: DOMAIN,
    nonce,
    uri: ORIGIN,
    version: "1",
    expirationTime: new Date(Date.now() + 5 * 60_000),
  });
  const signature = await player.signMessage({ message });

  const [a, b] = await Promise.all([
    replay(base, message, signature),
    replay(base, message, signature),
  ]);
  const accepted = [a, b].filter((r) => r.status === 200).length;

  console.log(
    `${store.name.padEnd(26)} -> ${accepted} of 2 requests accepted`,
    accepted === 1 ? "(this run: no double login)" : "(BUG reproduced: two sessions)",
  );
  close();
}

console.log(
  "\nRun that a few times. The atomic store always accepts exactly one. The naive\n" +
    "store accepts two only when the second request happens to reach its check\n" +
    "before the first reaches its delete — and whether it does depends on how long\n" +
    "signature verification took, which depends on the network. So the bug is\n" +
    "present on every run and *visible* on some of them.\n\n" +
    "That is the real lesson, and it is worth saying in exactly these terms in an\n" +
    "interview: a check-then-act race does not fail your tests, it fails your\n" +
    "users, intermittently, in production, under load. You cannot test your way to\n" +
    "confidence here; you have to remove the window. The fix is not a mutex — that\n" +
    "only works inside one process, and you will run several. It is to make the\n" +
    "database adjudicate in a single statement: DELETE FROM siwe_nonce WHERE nonce\n" +
    "= $1 RETURNING nonce, and trust the row count. The same shape returns in level\n" +
    "9 for nonce allocation and in level 10 for voucher issuance, where the cost of\n" +
    "losing the race is not a duplicate session but a duplicate mint.",
);
