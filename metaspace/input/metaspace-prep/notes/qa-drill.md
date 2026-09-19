# Q&A Drill Sheet — Metaspace Technical Interview

**Format:** cover the answer, say yours out loud, then compare. Speaking it is the
point. Reading an answer you already know is the most comfortable and least useful
way to prepare.

**The 80/20 of this sheet:** sections A, B and D are where the interview will
actually be won. C is your real gap. E only needs to be credible, not deep — you
told the recruiter backend, and the role is backend-with-some-frontend. F is what
makes you sound like you understand *their* business rather than blockchain in
the abstract.

**Scoring yourself:** mark each question 🟢 (fluent), 🟡 (know it, stumble),
🔴 (blank). On the 29th, drill only the 🔴s and 🟡s. Anything still 🔴 on the 30th,
plan to say "I haven't worked with that" — a clean admission costs far less than
a bluff that collapses under one follow-up.

---

## A. Backend architecture — your home turf, play it confidently

**A1. Walk me through the architecture of a backend you built end to end.**
Pick HANWASH or the Tekkod work. Structure it: the problem, the constraint that
made it non-trivial (unreliable connectivity, data arriving in batches you don't
control, a source of truth you don't own), the design, and one thing you'd do
differently. Two minutes. Rehearse it until it fits, because this is usually the
opening question and it sets your level for everything after.

**A2. How do you make an API endpoint idempotent?**
Client supplies an idempotency key; a unique constraint in the database — not
application logic — enforces it; on conflict you return the *original* response
rather than erroring. The two subtleties worth adding: the key must cover the
business event, not the HTTP call, and the result must be stored so a retry after
a crash still returns the same answer. You implemented exactly this in the voucher
service.

**A3. At-least-once vs exactly-once delivery.**
Exactly-once delivery doesn't exist across a network; exactly-once *processing*
does, and you get it by making the consumer idempotent. The network guarantees
at-least-once, your unique key turns duplicates into no-ops. Anyone who claims
exactly-once delivery is describing at-least-once plus deduplication.

**A4. Outbox pattern — what and why.**
Writing to your database and publishing a message are two systems that can't
commit atomically. So you write the message into the same database in the same
transaction, and a separate process reads and publishes it. You lose atomicity
with the broker but gain the guarantee that the intent is never lost. See
`outbound_tx` in the schema.

**A5. Design rate limiting for a public API.**
Token bucket in Redis, keyed per account rather than per IP (NAT makes IP useless
on mobile). Return `429` with `Retry-After`. Distinguish *cost* tiers — a read is
not a write. Mention that on a game backend you also rate-limit by game action,
because the abuse you care about is reward farming, not bandwidth.

**A6. How do you handle a third-party API that is slow and unreliable?**
Timeouts on every call (no default-infinite), retries with exponential backoff
*and jitter*, a circuit breaker so you stop hammering a dead dependency, and a
bulkhead so its failure doesn't consume every worker. Then: degrade gracefully —
serve stale cached data and say it's stale. Your indexer's `getLogsWithBackoff`
is a worked example, including the detail that a rate-limit error and an
oversized-response error need *different* responses.

**A7. Sync vs async processing — where do you draw the line?**
If the caller needs the result to continue, sync. If it's slow, external, or
retryable, async with a job record the caller can poll. The relayer is the
canonical case: you never hold an HTTP connection open for a block confirmation.

**A8. How would you scale this backend from 1k to 250k daily players?**
Read replicas and a projection table before anything clever. Cache the hot read
path. Move the indexer and relayer to their own processes — they have completely
different scaling profiles from the API. Partition `chain_event` by block range.
Say explicitly that you'd measure before sharding.

**A9. What's in your health check?**
Not just 200. Indexer lag in blocks, relayer queue depth, hot-wallet balance, DB
pool saturation. Say the line: *"uptime tells you the process is alive, which you
already knew"*. Then the operational point — a silently stalled indexer is worse
than a crash, because nothing pages you.

**A10. Blue/green vs rolling deploys, and what breaks with a stateful indexer.**
Two indexer instances processing the same stream will race on the checkpoint. You
need either a leader election or an advisory lock on the stream id. Volunteering
this shows you've thought past the happy path.

**A11. How do you version an API?**
URL versioning for breaking changes, additive-only within a version. On a *mobile
game* this matters more than usual: you cannot force an update, so old clients
will call your v1 endpoint for years. Design for that from day one.

**A12. FastAPI vs Node — how do you think about the difference?**
Both are async, single-event-loop models; the concurrency model is the same and
the mistakes are the same (a blocking call in a handler stalls everything). The
real differences are ecosystem and typing discipline. Be honest that Python is
your stronger language and that the transferable part — async I/O, connection
pooling, dependency injection, schema validation — is most of it.

---

## B. Databases and data — your unfair advantage, use it

**B1. Why `(block_hash, log_index)` and not `(tx_hash, log_index)`?**
Because a reorg re-includes the same transaction in a different block, keeping
its hash. Key on tx_hash and the re-inclusion silently collides with the orphaned
row under `ON CONFLICT DO NOTHING`, and you lose the event. This is the single
best question in the whole sheet to nail — it proves you've thought about the
failure mode and not just read a tutorial.

**B2. How do you store a uint256 in Postgres?**
`NUMERIC(78,0)`. 2^256 is 78 digits. Not BIGINT (overflows at 2^63), not a JS
`number` (loses precision past 2^53). And the `pg` driver returns NUMERIC as a
string on purpose — convert to `BigInt`, never `Number`.

**B3. Transaction isolation levels — which do you use and when?**
Postgres defaults to READ COMMITTED. Use REPEATABLE READ or SERIALIZABLE when a
read-then-write decision must not see a changed world in between. In practice
prefer a single atomic statement (`INSERT ... ON CONFLICT`, `UPDATE ... RETURNING`)
over a higher isolation level — it's cheaper and it can't deadlock.

**B4. How does `UPDATE ... WHERE consumed_at IS NULL RETURNING` prevent replay?**
It's a compare-and-swap in one statement. Two concurrent requests race and exactly
one gets a row back. `SELECT` then `UPDATE` lets both through. Point at the SIWE
nonce burn.

**B5. Materialised view vs projection table.**
A projection you maintain incrementally can be updated per event; a materialised
view is refreshed wholesale. For inventory you want incremental with the option
to rebuild — which you get by keeping raw events forever and treating the chain
as the log.

**B6. Index design for the event table.**
Partial indexes on `WHERE NOT orphaned` so orphaned rows don't bloat them. GIN
with `jsonb_path_ops` for arg lookups. And the rule: index the query you actually
run, verify with `EXPLAIN ANALYZE`, don't index on instinct.

**B7. This query got slow. Walk me through diagnosing it.**
`EXPLAIN (ANALYZE, BUFFERS)`. Look for seq scans on big tables, a row-estimate
that's wildly off (stale statistics → `ANALYZE`), and nested loops over large
sets. Then: missing index, bad plan, or bad schema — in that order of likelihood.

**B8. N+1 — how do you spot it and fix it?**
Query count scaling with result-set size. Fix with a join, a batched `IN`, or a
dataloader. In your indexer, `getBlock` per log is an N+1 against the RPC
provider — say so before they spot it, and say the fix is caching by block number
within a batch. **Volunteering a weakness in your own code is a strong move.**

**B9. Would you use an ORM here?**
Raw SQL for the indexer's hot path because the queries are shaped and you want to
see the plan. An ORM is fine for CRUD. You've used async SQLAlchemy heavily —
mention that you know where the abstraction earns its keep and where it hides a
seq scan.

**B10. How do you do a zero-downtime migration on a hot table?**
Additive first: add nullable column, backfill in batches, dual-write, switch
reads, then drop. Never `ALTER TABLE` with a rewrite on a table under load.
`CREATE INDEX CONCURRENTLY`.

---

## C. Node and TypeScript — your real gap. Drill these hardest.

**C1. Event loop: what actually happens with `await`?**
`async`/`await` is syntax over promises. `await` yields to the event loop and
schedules the continuation as a microtask. Microtasks drain completely before the
next macrotask (timers, I/O), which is why a tight promise loop can starve timers.
Compare to Python's asyncio if you like — the model is genuinely the same.

**C2. `Promise.all` vs `allSettled` vs `race` vs `any`.**
`all` rejects on the first failure (and doesn't cancel the rest — they keep
running). `allSettled` always resolves with per-item outcomes. `race` settles on
the first to settle, including rejections. `any` resolves on the first *success*.
For fan-out to flaky RPC nodes you usually want `allSettled` or `any`.

**C3. What is an unhandled promise rejection and why does it matter?**
A rejected promise nobody caught. Node 15+ crashes the process by default. This
is why the relayer's `serialise` swallows rejections *on the chain* but still
returns the original promise to the caller — one failed send must not poison the
queue or kill the process.

**C4. CommonJS vs ESM.**
`require` is synchronous and dynamic; `import` is static, hoisted, and supports
top-level `await`. This repo is ESM (`"type": "module"`), which is why files are
imported with explicit extensions.

**C5. `interface` vs `type`.**
Interfaces are open (declaration merging) and preferred for object shapes; type
aliases do unions, intersections, mapped and conditional types. Practical rule:
interface for object contracts, type for everything else.

**C6. What does `strict` actually turn on, and what is `noUncheckedIndexedAccess`?**
`strictNullChecks`, `noImplicitAny`, `strictFunctionTypes` and friends.
`noUncheckedIndexedAccess` makes `arr[0]` typed as `T | undefined`, which catches
the empty-result bug — it's why the code is full of `rows[0]?.x ?? fallback`.
Turning it on is an opinion worth defending.

**C7. Why is `any` dangerous and what do you use instead?**
`any` disables checking and spreads silently. Use `unknown` and narrow it — you
must prove the shape before use. Relevant when parsing RPC responses.

**C8. Structured concurrency / cancellation in Node.**
`AbortController` and `AbortSignal`, passed into fetch and timers. Node has no
task groups; you compose with `Promise.all` and pass signals down. Worth saying
that Python's `asyncio.TaskGroup` is cleaner and you miss it.

**C9. How do you handle BigInt across a JSON boundary?**
`JSON.stringify` throws on BigInt. Serialise to string explicitly. This bites
everyone once — you've already handled it in `serialiseArgs`.

**C10. Worker threads vs cluster vs child process.**
`cluster` forks processes sharing a port for CPU parallelism across cores;
`worker_threads` shares memory and suits CPU-bound work in-process; child
processes for isolation. On this backend you'd scale with processes, not threads,
because the work is I/O bound.

---

## D. Web3 fundamentals — the credibility section

**D1. What happens between "user clicks buy" and "the item is theirs"?**
Wallet builds and signs a transaction → broadcast to a node → mempool → a
validator includes it in a block → executed by the EVM → receipt with logs →
your indexer sees it after N confirmations → your database updates → the game UI
reflects it. Being able to narrate this whole chain smoothly is worth more than
any single fact in this section.

**D2. What is a reorg and how does your system survive one?**
The canonical chain switches to a different branch, so blocks you already
processed are no longer real. Survive it by storing block hashes, re-checking
them on each poll, walking back to the fork point, marking orphaned rows, and
rebuilding the projection. Plus confirmations so it happens rarely.

**D3. How many confirmations, and why?**
It's a risk decision, not a constant: value at stake vs latency tolerated.
Ethereum gives you `finalized` as a hard guarantee (~13 min). Polygon PoS
checkpoints to Ethereum, and short reorgs are routine — so a depth of roughly
64–128 blocks for anything economic, with rollback capability because you might
still be wrong. **Say the reasoning; the number alone sounds memorised.**

**D4. EIP-1559 — base fee, priority fee, max fee.**
Base fee is protocol-set from the previous block's fullness and is *burned*.
Priority fee is the validator's tip. Max fee is your ceiling; you pay
`min(maxFee, baseFee + priority)` and are refunded the difference. So a generous
maxFee buys resilience at no cost when the base fee stays flat.

**D5. A transaction is stuck. What do you do?**
Rebroadcast with the *same nonce* and a higher fee — at least +10% for Geth to
accept the replacement. Never a new nonce: the old transaction is still live and
may mine, executing twice. **This is where your trading analogy lands:** it's a
price improvement on a resting order, not a cancel-replace.

**D6. Explain nonces.**
Per-account sequential counter preventing replay and fixing ordering. Gaps stall
everything behind them. Concurrency is the enemy — one serialised allocator per
sending address, and in Postgres with `SELECT ... FOR UPDATE` once you run more
than one instance. *Expect the follow-up "and with three pods?" — answer it
before it's asked.*

**D7. Custodial vs non-custodial wallets for a mobile game.**
Non-custodial is ideologically correct and terrible onboarding UX — a seed phrase
before the tutorial loses most players. Custodial or an embedded/smart-account
wallet converts far better but makes you a custodian with the legal and security
weight that implies. The honest answer names the trade-off and asks what they
chose, because it's a product decision, not a technical one.

**D8. ERC-20 vs 721 vs 1155 — when each?**
20 for fungible currency ($LORD). 721 for unique items where each token has its
own identity. 1155 for a mix — the same contract holds both fungible consumables
and unique gear, with batch transfers that are dramatically cheaper. **For a game,
1155 is almost always right**, and knowing *why* (batch ops, one contract for the
whole catalogue) is the answer they want.

**D9. Why Polygon rather than Ethereum mainnet for a game?**
Fees and block time. A game does thousands of low-value actions; mainnet gas
makes that impossible. Polygon PoS gives ~2s blocks and cheap transactions, full
EVM compatibility, and settles to Ethereum. The trade-off is a weaker security
model and reorg behaviour you have to engineer around — which you did.

**D10. What is MEV and does it affect a game?**
Validators and searchers reorder, insert or sandwich transactions for profit.
Relevant to a game at mint moments (a limited drop gets front-run) and on any
marketplace trade. Mitigations: commit-reveal, allowlists with signatures (your
voucher pattern), private mempools/Flashbots, or simply not putting price-sensitive
actions on-chain.

**D11. Gasless transactions — what are the options?**
`permit` (EIP-2612) for ERC-20 approvals; meta-transactions via a trusted
forwarder (ERC-2771); account abstraction (ERC-4337) with a paymaster sponsoring
gas. Know the names and the one-line difference; nobody expects you to have
implemented 4337.

**D12. Can you trust a block timestamp?**
Loosely. Validators have some latitude, so it's fine for hour-scale logic and
unsafe for anything finer, and it must never be a randomness source. On-chain
randomness needs a VRF (Chainlink) or commit-reveal — `block.timestamp` and
`blockhash` are manipulable by whoever builds the block.

---

## E. Solidity — be credible, don't overclaim

**E1. Reentrancy: what it is, and two defences.**
An external call hands control to attacker code that re-enters before your state
is updated. Defences: checks-effects-interactions (structural, always do this)
and a reentrancy guard (a mutex, the belt to CEI's braces). Point at
`nonceUsed[...] = true` *before* `_mint` in GameItems, and say exactly why ERC-1155
makes it necessary: `_mint` calls `onERC1155Received` on a contract recipient.

**E2. Why EIP-712 rather than signing a raw hash?**
Wallets render named typed fields so users see what they're signing; the domain
separator binds the signature to chain id and contract address; and
`abi.encodePacked` with two dynamic types is ambiguous while `abi.encode` is not.

**E3. Name the four replay defences in the voucher.**
chainId (cross-chain), verifyingContract (cross-deployment), nonce (same-voucher),
deadline (indefinite validity). Miss one and you've minted infinite items.

**E4. Why is looping over stakers to pay rewards a bug?**
Unbounded loop: gas grows with the user count until it exceeds the block limit and
*nobody* can claim. The fix is the accumulator — one global
`accRewardPerWeight`, per-user `rewardDebt`, O(1) claims. Being able to derive
this on a whiteboard is the single highest-value Solidity thing on this sheet.

**E5. Why `PRECISION = 1e18` and why the order of operations matters.**
Integer division truncates. Multiply before dividing, scale by 1e18 through the
accumulator, divide it out at the end. Divide first and you pay everyone zero.

**E6. `AccessControl` vs `Ownable`.**
Least privilege. The staking contract needs to mint; it does not need to upgrade
or withdraw. `Ownable` collapses every privilege into one key, so one compromise
is total. Roles let you put the signing key in KMS with `SIGNER_ROLE` only, and
rotate with grant/revoke and no redeploy.

**E7. What's the difference between `require`, custom errors, and `assert`?**
Custom errors are cheaper (4-byte selector vs a stored string) and are the modern
default. `require` with a reason string is still fine and readable. `assert` is
for invariants that should be unreachable — it consumed all gas pre-0.8, now it
panics.

**E8. How would you upgrade a deployed contract?**
Proxy patterns — UUPS is the current default, with the logic in an implementation
contract and storage in the proxy. The trap is storage layout: you may append but
never reorder or remove. Then state the governance question honestly — an
upgradeable contract means someone can change the rules, which for a game economy
is a trust decision, not a technical one.

---

## F. Game-backend specific — this is what makes you sound like a fit

**F1. What goes on-chain and what stays off?**
On-chain: ownership, scarcity, transfers, anything a player must be able to verify
or trade. Off-chain: game logic, matchmaking, progression, anti-cheat, anything
high-frequency or low-value. **One-liner worth memorising: the chain is a
settlement layer, not a rules engine.**

**F2. How do you stop a player minting rewards they didn't earn?**
The server is authoritative. It verifies the mission was completed before signing
a voucher. The contract only knows "a key with SIGNER_ROLE approved this" — the
authorisation decision lives in your backend, and a client that can name an
arbitrary itemId is a client that mints legendaries.

**F3. A player says an item vanished. How do you debug it?**
Chain first, because it's the source of truth: check the token balance at the
contract. Then your event log, then the projection. The most likely causes are a
reorg that orphaned the mint, an indexer that stalled, or a projection bug. This
is why events are soft-deleted rather than dropped — the orphaned rows are the
evidence.

**F4. Your RPC provider goes down. What happens to the game?**
Reads keep working, because you serve inventory from your projection rather than
from `eth_call` — that's the whole reason for the projection. Writes queue in the
outbox. The indexer stalls and catches up from its checkpoint when the provider
returns. Then: multiple providers with failover, because a single RPC vendor is a
single point of failure for the entire game economy.

**F5. How do you handle a mobile client on a bad connection?**
Idempotency keys on every mutating call, so a retry can't double-mint. Offline
queue on the client. Optimistic UI with reconciliation. *This is worth flagging as
personal experience:* building for intermittent connectivity in Haiti is a real
constraint you've designed around for years, and it's directly relevant to a
mobile game with players in emerging markets.

**F6. How would you test all this?**
Unit tests on the contracts (Foundry, including fuzz tests on the reward maths);
integration tests against a local chain (Anvil) with the full indexer running;
and a reorg test that forks the chain deliberately to prove rollback works. Say
that last one — almost nobody tests reorg handling, and saying you would is a
differentiator.

**F7. Unity talks to your backend. What does that interface look like?**
REST over HTTPS for state, WebSocket for realtime. The client never holds a
signing key or talks to the chain directly for anything authoritative. You've done
Socket.io realtime work — say so.

**F8. The token economy is inflating. What can the backend do?**
Mostly it's a design problem, not an engineering one, and saying that is the
right answer. Engineering gives you the levers: `setRewardPerSecond`, the supply
cap, sinks (crafting, repairs, fees), and the data to see it happening — which is
where your economics background is a genuine asset rather than a line on a CV.

---

## G. Behavioural and positioning

**G1. Why are you interested in this role?**
Don't say "blockchain is exciting". Say: the interesting problem is keeping two
systems consistent when one of them can rewrite its own history, and you've spent
years on checkpointed pipelines against sources you don't control. Then something
specific about *them* — a licensed studio with a shipped mobile title has real
users and real constraints, which is different from most of this industry.

**G2. You're a Python engineer. Why should we hire you for a Node/TS backend?**
Meet it head on. The async model is the same; the architecture is the same; the
language is a month, not a year. Then show the repo. **Having built something
before the interview is the whole answer to this question** — it converts a claim
into evidence.

**G3. What's your weakness here?**
Say the true one: you haven't shipped a production contract, and you wouldn't
want to be the sole author of one holding significant value without an audit and
a more experienced reviewer. Then say what you *are* confident owning: the
integration layer, the indexer, the API, the data. Naming your limits precisely
makes everything else you claim more believable.

**G4. Tell me about a production incident you handled.**
Pick something real. Structure: what broke, how you found out (be honest if
monitoring didn't catch it), what you did immediately, what the root cause was,
and what you changed so it couldn't recur. The last part is what's being graded.

**G5. How do you work in a fully remote team across time zones?**
Concrete, not platitudes: written-first, decisions in a document not a call,
overlapping hours protected for anything requiring discussion. You've done remote
US-client work at Tekkod for years — Haiti is UTC-4/-5, UAE is UTC+4, so there's
an 8–9 hour gap. **Volunteer your overlap window before they raise it as a
concern**, because they will be thinking about it.

**G6. Where do you want to be in two years?**
Owning a system end to end rather than a set of tickets. Honest and it matches
what a small studio needs.

---

## Questions to ask them

Ask these. Not asking questions reads as not caring, and the answers genuinely
change whether you want the job.

1. **"Is the backend already in Node/TypeScript, or is some of it something else?"**
   Tells you what the first month looks like.

2. **"Who owns the contracts today — is there an in-house Solidity engineer, and
   do you audit before deploying?"**
   Tells you whether you'd be expected to be solely responsible for contract
   security, which you should not accept.

3. **"How do you currently keep game state in sync with the chain — is there an
   indexer, or is it reading from RPC directly?"**
   This is a *senior* question. If the answer is "we call the contract directly",
   you have just found the problem you'd be hired to fix, and you can say so.

4. **"What broke most recently in production?"**
   The best question in any technical interview. You learn their real maturity
   level, and engineers enjoy answering it.

5. **"What does the team look like, and what are the working hours — how much
   overlap would you want with the UAE?"**
   Practical, and it signals you're thinking about actually doing the job.

6. **"What would a successful first three months look like for this person?"**
   If they can't answer, the role isn't well defined yet — useful to know before
   you negotiate.
