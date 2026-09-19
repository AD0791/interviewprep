/**
 * =====================================================================
 * THE API SURFACE
 * =====================================================================
 *
 * Deliberately boring, and that is the point to make in the room: once the
 * chain-specific machinery is isolated into the indexer, relayer, and voucher
 * service, the HTTP layer is an ordinary backend. Auth, validation, rate
 * limits, idempotency keys, clean errors. Nothing here is "web3".
 *
 * That framing is your strongest card. You are not asking them to believe you
 * are a blockchain expert. You are pointing out that 80% of the job is
 * backend architecture you have done for years, and the remaining 20% is a
 * bounded, learnable domain you can already talk about precisely.
 *
 * If they ask why Fastify over Express: schema-based validation and
 * serialisation compiled ahead of time, which is roughly the Pydantic
 * relationship FastAPI has — declare the shape once, get validation, coercion
 * and docs from it. Coming from FastAPI you will find it the closest thing in
 * the Node ecosystem.
 */

import Fastify from "fastify";
import { JsonRpcProvider, Wallet, getAddress } from "ethers";
import { SiweService, AuthError } from "./auth-siwe.ts";
import { VoucherService } from "./voucher.ts";
import { Relayer } from "./relayer.ts";
import { pool } from "./db.ts";

const CHAIN_ID = Number(process.env.CHAIN_ID ?? 80002);
const RPC_URL = process.env.RPC_URL ?? "https://rpc-amoy.polygon.technology";
const GAME_ITEMS = process.env.GAME_ITEMS_ADDRESS ?? "0x0000000000000000000000000000000000000000";

const provider = new JsonRpcProvider(RPC_URL, CHAIN_ID, { staticNetwork: true });

// In production this key comes from KMS and is never in process memory.
// An env var is fine for a local demo — but say the production answer aloud
// before anyone has to ask you for it.
const signerKey = process.env.SIGNER_PRIVATE_KEY ?? Wallet.createRandom().privateKey;
const signer = new Wallet(signerKey, provider);

const siwe = new SiweService(
  process.env.APP_DOMAIN ?? "localhost:3000",
  process.env.APP_URI ?? "http://localhost:3000",
  CHAIN_ID
);
const vouchers = new VoucherService(signer, CHAIN_ID, GAME_ITEMS);
const relayer = new Relayer(provider, signer, CHAIN_ID);

const app = Fastify({ logger: true });

// ---------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------

app.post<{ Body: { address: string } }>("/auth/challenge", {
  schema: {
    body: {
      type: "object",
      required: ["address"],
      properties: { address: { type: "string", pattern: "^0x[a-fA-F0-9]{40}$" } },
    },
  },
}, async (req) => {
  return siwe.createChallenge(req.body.address);
});

app.post<{ Body: { message: string; signature: string } }>("/auth/verify", async (req, reply) => {
  try {
    const { address } = await siwe.verify(req.body.message, req.body.signature);
    // Issue a short-lived JWT here in a real service. Kept out so the file
    // stays about the chain-specific parts.
    return { address, token: `demo-session-for-${address}` };
  } catch (err) {
    if (err instanceof AuthError) return reply.code(401).send({ error: err.message });
    throw err;
  }
});

// ---------------------------------------------------------------------
// Rewards
// ---------------------------------------------------------------------

/**
 * The authorisation boundary lives HERE, not in the contract.
 *
 * The contract only knows "a key with SIGNER_ROLE approved this". Whether the
 * player actually finished mission 1042 is a question only the game server
 * can answer, and it must answer it before signing. A client that can ask for
 * an arbitrary itemId is a client that mints legendaries. Say that plainly if
 * you are asked how you stop cheating: the server is authoritative, the chain
 * is settlement.
 */
app.post<{ Body: { wallet: string; missionId: number } }>("/rewards/claim", async (req, reply) => {
  const { wallet, missionId } = req.body;

  const completed = await verifyMissionCompleted(wallet, missionId);
  if (!completed) return reply.code(403).send({ error: "mission not completed" });

  const { itemId, amount } = rewardTableFor(missionId);
  const signed = await vouchers.issue(wallet, itemId, amount, `mission:${missionId}`);

  return {
    voucher: {
      to: signed.voucher.to,
      id: signed.voucher.id.toString(),
      amount: signed.voucher.amount.toString(),
      nonce: signed.voucher.nonce.toString(),
      deadline: signed.voucher.deadline.toString(),
    },
    signature: signed.signature,
    // The player redeems this themselves and pays their own gas. Set
    // sponsored:true and route through the relayer if the studio absorbs it.
    sponsored: false,
  };
});

// ---------------------------------------------------------------------
// Inventory (served from the projection, never from the chain)
// ---------------------------------------------------------------------

/**
 * Reading balances straight from the contract via eth_call looks simpler and
 * is wrong at scale: one RPC round-trip per item per player, rate limits, and
 * an outage whenever the node has a bad day. The indexer already maintains
 * this projection, so serving it is a single indexed Postgres query — and the
 * game keeps working when the RPC provider does not.
 *
 * The honest caveat, which you should volunteer: the projection is eventually
 * consistent, lagging by the confirmation depth. That is a feature for
 * anything economic (unsettled balances must not be spendable) and needs an
 * optimistic overlay for UI responsiveness.
 */
app.get<{ Params: { wallet: string } }>("/inventory/:wallet", async (req, reply) => {
  let wallet: string;
  try {
    wallet = getAddress(req.params.wallet).toLowerCase();
  } catch {
    return reply.code(400).send({ error: "invalid address" });
  }

  const { rows } = await pool.query<{ item_id: string; balance: string; updated_at: Date }>(
    `SELECT item_id, balance, updated_at
       FROM player_inventory WHERE wallet = $1 AND balance > 0
      ORDER BY item_id`,
    [wallet]
  );

  const { rows: cp } = await pool.query<{ last_block_number: string; updated_at: Date }>(
    `SELECT last_block_number, updated_at FROM indexer_checkpoint LIMIT 1`
  );

  return {
    wallet,
    items: rows.map((r) => ({ itemId: r.item_id, balance: r.balance })),
    // Expose the lag. A client that knows the data is 64 blocks behind can
    // render "pending" states honestly instead of appearing broken.
    syncedToBlock: cp[0]?.last_block_number ?? null,
    syncedAt: cp[0]?.updated_at ?? null,
  };
});

// ---------------------------------------------------------------------
// Sponsored transactions
// ---------------------------------------------------------------------

app.post<{ Body: { to: string; data: string; idempotencyKey: string } }>(
  "/relay/send",
  async (req) => relayer.send({
    idempotencyKey: req.body.idempotencyKey,
    to: req.body.to,
    data: req.body.data,
  })
);

// ---------------------------------------------------------------------
// Ops
// ---------------------------------------------------------------------

/**
 * A health check that only returns 200 tells you the process is alive, which
 * you already knew. What matters operationally is indexer LAG: if the
 * checkpoint stops advancing, inventories silently freeze and nobody notices
 * until players complain. Alert on this number, not on uptime.
 */
app.get("/health", async () => {
  const head = await provider.getBlockNumber();
  const { rows } = await pool.query<{ last_block_number: string }>(
    `SELECT last_block_number FROM indexer_checkpoint LIMIT 1`
  );
  const indexed = Number(rows[0]?.last_block_number ?? 0);
  const lag = head - indexed;
  return { ok: lag < 200, head, indexed, lagBlocks: lag };
});

// ---------------------------------------------------------------------
// Stubs — the game-logic side, which is not what this repo is about
// ---------------------------------------------------------------------

async function verifyMissionCompleted(_wallet: string, _missionId: number): Promise<boolean> {
  return true;
}

function rewardTableFor(missionId: number): { itemId: bigint; amount: bigint } {
  return { itemId: BigInt(missionId % 10), amount: 1n };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  await relayer.reconcileOnBoot();
  // The watchdog runs on a timer, not in the request path.
  setInterval(() => void relayer.bumpStuck().catch((e) => app.log.error(e)), 30_000);
  await app.listen({ port: Number(process.env.PORT ?? 3000), host: "0.0.0.0" });
}

export { app };
