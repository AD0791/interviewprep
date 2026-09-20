# Metaspace — Blockchain Engineer technical interview

The track for the thirty-minute technical interview with Metaspace's Tech Lead, **booked for
Wednesday 30 September 2026 at 16:00**. Everything here is sized for the days between now and
then rather than for completeness: the field is larger than any eleven-day plan, and a plan you
finish beats a syllabus you abandon.

> **Confirm which time zone that 16:00 is in before you rely on it.** Haiti is UTC-4 in
> September and the UAE is UTC+4, an eight-hour gap, so 16:00 in Dubai is 08:00 in
> Port-au-Prince and 16:00 in Port-au-Prince is midnight in Dubai. Calendly normally shows
> times in *your* local zone, but the invitation is the thing to check, and it is worth having
> the event in a calendar that displays both.

This folder is the study track. The folder beside it,
[../input/metaspace-prep](../input/metaspace-prep), is the working repository from an earlier
session — compiling contracts, a Fastify/ethers backend, a sixty-question drill and a
positioning note. It is not superseded; the articles here link into it, and its
[positioning.md](../input/metaspace-prep/notes/positioning.md) remains the authority on how to
pitch yourself honestly.

---

## Start here

1. **[KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md)** — the sixteen topics from
   [../metaspace.md](../metaspace.md) arranged as the dependency graph they actually form,
   marked for what earns its place in a thirty-minute conversation.
2. **[facts.md](facts.md)** — the memorisation layer: chain IDs, EIP numbers, gas costs,
   function selectors, current library versions. All verified on 19 September 2026.
3. **[sources.md](sources.md)** — where each claim comes from and, more usefully, which popular
   sources are now wrong and in what way.
4. **[exercises/EXERCISES.md](exercises/EXERCISES.md)** — twelve levels that build one
   application: a player earns an item off chain, claims it on Polygon, and your database stays
   in sync.
5. The **[articles/](articles/)**, in numbered order, which is prerequisite order.

## Reading order and the eleven days

Each day pairs reading with building, because the two halves teach different things and the
interview will test both. The exercise levels are in
[exercises/EXERCISES.md](exercises/EXERCISES.md); run them from the `exercises/` directory
after one `npm install`.

| Day | Read | Build | Why this pairing |
|---|---|---|---|
| 1 | [01 What a blockchain engineer is](articles/01_what_is_a_blockchain_engineer_2026.md), [02 Blockchain from zero](articles/02_blockchain_from_zero.md) | Level 1 | The map first, then hashes and addresses by hand |
| 2 | [03 Ethereum, the EVM, accounts and gas](articles/03_ethereum_evm_accounts_gas.md) | Levels 2–3 | Read a live chain and a live contract while the theory is fresh |
| 3 | [04 Polygon and EVM networks](articles/04_polygon_and_evm_networks.md) | Level 3 again, on a second chain | Chain choice is an architecture answer, not trivia |
| 4 | [05 Wallets, keys and signatures](articles/05_wallets_keys_signatures.md) | Level 4 | Signing and recovery, and the replay bug that motivates SIWE |
| 5 | [06 Solidity from zero](articles/06_solidity_from_zero.md) | Level 5 | Contract literacy plus the login endpoint |
| 6 | [07 Token standards and digital assets](articles/07_token_standards_digital_assets.md) | Level 6 | ERC-1155 is the game inventory standard; events are how you read it |
| 7 | [08 Smart contract security](articles/08_smart_contract_security.md) | Levels 7–8 | The indexer and its reorg rollback — your strongest ground |
| 8 | [09 Node, TypeScript and the client libraries](articles/09_nodejs_typescript_for_web3.md) | Level 9 | Drill TS under time pressure; the relayer write path |
| 9 | [10 Backend architecture for a Web3 game](articles/10_backend_architecture_web3_game.md) | Levels 10–11 | Vouchers and the contract that accepts them |
| 10 | [11 Frontend wallet integration](articles/11_frontend_wallet_integration.md), [12 The Python path](articles/12_python_path_fastapi_web3py.md) | Level 12 | The whole loop, end to end |
| 11 | [mock_interviews.md](mock_interviews.md) and [facts.md](facts.md) | — | Timed rehearsal only; no new material |

Day 11 is 30 September, the day itself: deliberately empty of new learning. The failure being
prepared against is not ignorance — it is knowing the material and being unable to say it
inside thirty minutes.

## What is written so far

**The track is complete.** Every article is written, all twelve exercise levels have runnable
solutions that pass, and the mock interviews are ready to run against a clock.

| Piece | Status |
|---|---|
| [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md), [facts.md](facts.md), [sources.md](sources.md) | written |
| [exercises/EXERCISES.md](exercises/EXERCISES.md) — all twelve statements | written |
| Exercise solutions, levels 1–12 | written, run clean, typecheck under strict mode |
| Articles [01](articles/01_what_is_a_blockchain_engineer_2026.md), [02](articles/02_blockchain_from_zero.md), [03](articles/03_ethereum_evm_accounts_gas.md) | written |
| Articles [04](articles/04_polygon_and_evm_networks.md), [05](articles/05_wallets_keys_signatures.md), [06](articles/06_solidity_from_zero.md) | written |
| The three progressive contracts in [exercises/contracts/](exercises/contracts/) | written, compile clean under solc 0.8.37 |
| Articles [07](articles/07_token_standards_digital_assets.md), [08](articles/08_smart_contract_security.md), [09](articles/09_nodejs_typescript_for_web3.md) | written |
| Articles [10](articles/10_backend_architecture_web3_game.md), [11](articles/11_frontend_wallet_integration.md), [12](articles/12_python_path_fastapi_web3py.md) | written |
| [mock_interviews.md](mock_interviews.md) — three timed simulations | written |
| [exercises/python/](exercises/python/) — the Python counterparts | written, run against web3.py 8 |

## Running the exercises

```bash
cd exercises
npm install        # viem 2, Express 5, TypeScript — nothing global
npm run l1         # hashes, a tamper-evident chain, address derivation (offline)
npm run l2         # a live read of Polygon Amoy
npm run l3         # a contract read, by hand and then typed
npm run l4         # signing, recovery, and the replay bug (offline)
npm run l5         # SIWE login over Express, and a nonce race (offline)
npm run l6         # getLogs, provider limits, and a self-halving loop
npm run l7         # a checkpointed, crash-safe indexer (node:sqlite, no install)
npm run l8         # reorg detection and rollback
npm run l9         # nonce races, fees and replacement (signs locally, broadcasts nothing)
npm run l10        # EIP-712 vouchers + the cross-language type-hash proof (offline)
npm run l11        # a real reentrancy attack in a local EVM (offline)
npm run l12        # the whole loop: SIWE -> voucher -> mint -> indexer -> inventory (offline)
npm run typecheck  # strict mode

cd contracts && npm install && node compile.mjs   # the three contracts from article 06
```

Levels 1, 4, 5 and 10 need no network, and level 9 needs one only to read. Levels 2, 3, 6, 7 and
8 read a public Amoy RPC. Nothing in the ladder broadcasts a transaction unless you opt in by
setting `PRIVATE_KEY` in level 9 — and that must be **a throwaway key holding testnet POL and
nothing else**. Never connect a wallet with real value to anything that arrives during a hiring
process; the reasoning is in
[positioning.md](../input/metaspace-prep/notes/positioning.md).

## The two things this track will not do

It will not help you claim to be a smart contract security specialist. You have written
ERC-1155 and staking contracts and you can discuss reentrancy and the standard patterns, and
the honest limit — that you would not want to be the only reviewer of a contract holding real
value — is what makes the rest of your claims credible to a Tech Lead who has shipped audited
code.

It will not organise your preparation around your CV. The subject is the organising principle.
What you have done is settled elsewhere — the source of truth is
[alexandrodislaResume.tex](../../../curiculum-vitae-and-letter/alexandrodislaResume.tex), and
the framing is in [positioning.md](../input/metaspace-prep/notes/positioning.md).
