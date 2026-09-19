# metaspace-prep

Interview preparation for the Metaspace technical interview (30 September 2026).

This is a working demonstration of **the integration layer between a game backend
and an EVM chain** — the part of a Web3 game that is actually backend engineering.
It exists so that when you're asked "how much blockchain have you done?", the
answer is a repository rather than an adjective.

Everything here compiles and the tests pass. Verify it yourself before the
interview — see *Verify* below.

---

## What's in it

```
contracts/src/
  GameItems.sol      ERC-1155 game assets, minted from backend-signed EIP-712
                     vouchers. THE most important file — read this one closely.
  ItemStaking.sol    O(1) reward accrual (the accumulator / MasterChef pattern).
  LordToken.sol      Capped ERC-20 reward currency with EIP-2612 permit.

backend/src/
  indexer.ts         Reorg-safe, checkpointed, idempotent event indexer.
                     The other file to know cold.
  relayer.ts         Nonce management, EIP-1559 fees, stuck-tx replacement,
                     outbox reconciliation.
  voucher.ts         EIP-712 voucher issuance with business-level idempotency.
  auth-siwe.ts       Sign-In With Ethereum (EIP-4361) with atomic nonce burn.
  server.ts          The HTTP surface — deliberately boring, and that's the point.
  voucher.test.ts    Cross-language test: proves the TS signer and the Solidity
                     verifier agree on the typehash.
  schema.sql         Postgres schema. Every constraint has a comment explaining
                     the failure mode it prevents.

notes/
  qa-drill.md        ~60 questions with model answers, scored 🟢🟡🔴.
  positioning.md     How to pitch this. The 60-second answer, the logistics,
                     the email to send the recruiter.
```

The code comments are written for *you*, not for a reviewer — they say what to
claim in the interview and why. Strip them before showing this to anyone if you
publish it publicly.

---

## The two files that matter most

**`GameItems.sol`** — the signed-voucher (lazy mint) pattern. This is how every
Web3 game hands a player an on-chain reward that was earned off-chain. If the
Tech Lead asks one architecture question, it's some version of this.

**`indexer.ts`** — keeping the game database in sync with the chain. Most
candidates answer this with `contract.on("Transfer", handler)`, which is wrong in
four ways at once. The correct answer is a checkpointed polling loop with reorg
detection, and being able to explain *why* is the differentiator.

---

## Verify

```bash
# Contracts compile (three contracts, no warnings, all well under EIP-170)
cd contracts && npm install && node compile.mjs

# Backend typechecks under strict mode
cd ../backend && npm install && npx tsc --noEmit

# EIP-712 cross-language tests pass (5 tests)
node --experimental-strip-types --test src/voucher.test.ts
```

Last verified: all three clean. `GameItems` 10,646 bytes, `ItemStaking` 5,375,
`LordToken` 6,219 — the EIP-170 limit is 24,576.

---

## Running it for real (optional, if you have time after Day 7)

Nothing below is required to discuss the code, but deploying once makes the
answers concrete.

1. Get testnet MATIC from a Polygon Amoy faucet.
2. Deploy with Foundry (`forge create`) or Remix — Remix in the browser is the
   fastest path and needs no local toolchain.
3. `psql -f backend/schema.sql`
4. Set `RPC_URL`, `GAME_ITEMS_ADDRESS`, `DEPLOY_BLOCK`, `SIGNER_PRIVATE_KEY`,
   `DATABASE_URL`.
5. `npm run indexer` in one terminal, `npm run server` in another.

**Use a throwaway wallet with testnet funds only.** Never put a key holding real
value into an env var, and never connect a wallet you actually use to anything
sent to you during a hiring process.

---

## Known gaps — name these yourself before they're found

Volunteering a weakness in your own code is a strong move in an interview. Three
real ones:

1. **`persistLog` calls `getBlock` per log** — an N+1 against the RPC provider.
   Fix: cache block metadata per batch.
2. **Nonce allocation is an in-process promise chain.** Correct for one instance,
   broken across replicas. Fix: `SELECT ... FOR UPDATE` on a per-sender row.
3. **`rebuildInventory` handles `TransferSingle` only.** `TransferBatch` needs
   array unnesting. Deliberate — say so rather than letting it look like an
   oversight.

There are no contract unit tests here (no Foundry in the build environment). If
you get the toolchain installed, the first test to write is the reentrancy case
on `mintWithVoucher`, and the second is a fuzz test on the staking accumulator.
