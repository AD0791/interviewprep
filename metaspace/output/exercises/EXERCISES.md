# The ladder — twelve levels, one application

Every level here is a step in building the same thing: the path a game item takes from being
earned inside your game to existing on Polygon, and back into your database. That is precisely
the system Metaspace is hiring for, so the ladder is not a set of puzzles — it is the job,
disassembled into pieces small enough to hold one at a time.

The rule of the ladder is that **nothing depends on code you have not already written**. Level
7's indexer uses the log reading from level 6, which uses the client from level 2, which uses
the address derivation from level 1. If a level feels like it appeared from nowhere, you
skipped one.

## How to work a level

Read the statement, try it before reading the solution, and then read the solution file even if
your version worked — the comments in it are written for you, and they say what to claim about
this in the room. Each level closes with **what they will ask**, which is the actual point.

Setup is one command in this directory:

```bash
npm install          # viem 2, Express 5, TypeScript — nothing global, nothing on-chain
npm run l1           # and l2, l3, … as you go
npm run typecheck    # strict mode, the same settings a real backend would use
```

Levels 1, 4, 5 and 10 need no network at all. The rest read a public Polygon Amoy RPC, and that
endpoint rate-limits: run several levels back to back and one of them will be refused, sometimes
with an error that misdescribes why. That is not a flaw in the exercises, it is the first thing
you learn about depending on an RPC provider, and it is why every genuine read in the ladder
goes through the small backing-off retry in [solutions/_rpc.ts](solutions/_rpc.ts). The
*deliberate* failures — level 3's mistyped address and missing function, level 6's oversized
queries — pointedly do not retry, because those are the point. Set `RPC_URL` to your own
provider key if you have one.

Nothing in the ladder broadcasts a transaction unless you ask it to. Level 9 signs its
transactions locally and shows you the bytes; it sends one only if you set `PRIVATE_KEY`, and
then it must be **a throwaway key holding testnet POL and nothing else** — the reason is in
[positioning.md](../../input/metaspace-prep/notes/positioning.md) and it is not negotiable.
Level 10 is entirely offline, including its cross-language proof against the contract.

A note on the stack. These solutions use **Express 5 and viem 2**, deliberately, because the
job advert names Node and because Express is what most of these backends actually run. The
reference repo in [../../input/metaspace-prep](../../input/metaspace-prep) uses **Fastify and
ethers v6** instead. That is not an inconsistency to hide; it is useful, because you end up
having written both, and "I used viem here and ethers there, and here is the difference" is a
much better answer than loyalty to one library. Article
[09](../articles/09_nodejs_typescript_for_web3.md) covers the differences.

---

## Level 1 — Hashes, chains of hashes, and where an address comes from

**Statement.** Without touching a network, do three things. Hash two nearly identical strings
and look at how little the outputs have in common. Then build a three-block "chain" in memory
where each block's header contains the hash of its parent, tamper with the middle block, and
write the function that detects it — noting *which* block your detector flags. Finally, take a
known test private key, pull its uncompressed public key, and derive the address yourself with
`keccak256` and a slice, then check your answer against the library's.

**Hint.** The address is the last twenty bytes of the hash of the public key's X and Y
coordinates. The `0x04` prefix byte on the uncompressed key is not part of what gets hashed.

**Solution.** [solutions/01_hash_and_address.ts](solutions/01_hash_and_address.ts) — `npm run l1`

The tamper detector flags block **2**, not the block you edited. That is the whole idea of a
hash chain and it is worth sitting with for a moment: editing block 1 leaves block 1 perfectly
well-formed and breaks its *child*, because the child carries a pointer to a parent that no
longer exists. To make the edit stick you must re-hash every block after it, forever, faster
than everyone else — and the cost of doing that is the entire security argument of every
blockchain ever built. Proof-of-work makes it expensive in electricity; proof-of-stake makes it
expensive in slashable deposits. Neither makes it impossible.

The derivation half of the exercise is there to kill a specific piece of mystique. An address
is not an account the network created for you. It is a hash of a number you picked at random,
computed on your own machine, and the chain has no idea it exists until it appears in a
transaction. The mixed-case spelling is EIP-55, a checksum hidden in the choice of upper- and
lower-case hex letters.

**What they will ask.** *"What actually stops someone rewriting history?"* and *"Where does an
address come from?"* Both are warm-up questions and both are places where a candidate who has
only read about it produces a vague answer about "cryptography" while a candidate who has done
this produces the mechanism.

---

## Level 2 — Reading a live chain: blocks, balances, fees, finality

**Statement.** Point a read-only client at Polygon Amoy. Assert the chain ID before you trust
anything else. Read the head block and print its number, timestamp, parent hash, transaction
count, gas used against gas limit, and base fee. Then read the block tagged `finalized` and
print the gap between it and the head. Finish by reading an account's balance and nonce, and
the current fee estimates.

**Hint.** `createPublicClient`, a `http()` transport, and the `polygonAmoy` chain from
`viem/chains`. Every numeric value comes back as a `bigint`.

**Solution.** [solutions/02_read_the_chain.ts](solutions/02_read_the_chain.ts) — `npm run l2`

The gap between `latest` and `finalized` is the number this exercise exists for. Everything
above the finalized height is provisional: valid now, possibly gone in a moment. When it was
run on 19 September 2026 the gap was two blocks on Amoy, at roughly one second per block. That
is a small window, and it is still a window, and a game that credits an item the instant it
sees an event at the head is a game that occasionally creates items out of nothing.

The other thing to absorb here is that everything is a `bigint`. Not a number. The first time
you write `latest.timestamp * 1000` you will get `Cannot mix BigInt and other types`, and the
correct reflex is to convert at the display boundary and nowhere else.

**What they will ask.** *"How do you know a transaction really happened?"* The answer that
separates candidates is that confirmation is a risk decision, not a boolean — how many blocks
you wait depends on what the transaction is worth, and on a chain with fast finality you can
often simply wait for the finalized tag.

---

## Level 3 — Reading a contract: what an ABI is, and what a call really sends

**Statement.** Against the WPOL token on Amoy, call `totalSupply()` twice. First by hand:
compute the four-byte selector from the function signature yourself, send it as raw `data` in
an `eth_call`, and decode the 32-byte answer. Then do it properly with a typed ABI, and read
name, symbol, decimals and supply, formatting the supply correctly. Then break it twice: pass a
mistyped address and see what your tooling does about it, and call a function the contract does
not have. Finish by batching three reads into one round trip.

**Hint.** The selector is `keccak256("totalSupply()")` sliced to four bytes. `formatUnits`
turns the raw `bigint` into a human number; never do that division by hand.

**Solution.** [solutions/03_read_a_contract.ts](solutions/03_read_a_contract.ts) — `npm run l3`

Two discoveries here are worth more than the exercise. The first is that a contract call is
nothing but four bytes of selector followed by padded arguments; the chain has no method table
and no reflection, and an ABI is a file *you* keep so you can construct those bytes. Lose it
and the contract still works — you just cannot speak to it.

The second is the failure mode. There is no 404 on a blockchain. Calling a function that does
not exist, calling a contract that was never deployed, and calling a contract that reverted all
look similar from the outside, and the empty response `0x` decodes to zero in careless code. A
backend reading balances from a mistyped address will report zero forever, cheerfully. Note
also what the solution shows about `getAddress`: it *normalises* casing rather than validating
it, so the function that actually catches a typo is `isAddress(x, { strict: true })`.

**What they will ask.** *"How would you check whether a player owns an item?"* and, if they are
probing depth, *"what is an ABI, really?"*

---

## Level 4 — Signing off-chain, verifying on the server

**Statement.** With a throwaway key, sign a plain message and recover the signer's address from
the signature alone. Split the signature into its `r`, `s` and `v` components. Then reconstruct
what was actually signed — the EIP-191 prefixed hash — by hand, and confirm it matches the
library's `hashMessage`. Then write the naive login check that verifies a signature against an
address, and demonstrate, explicitly, that the same signature logs you in forever.

**Hint.** `signMessage` on the account, `recoverMessageAddress` and `verifyMessage` from
`viem`. The prefix is `"\x19Ethereum Signed Message:\n"` followed by the message's byte length.

**Solution.** [solutions/04_sign_and_recover.ts](solutions/04_sign_and_recover.ts) — `npm run l4`

The prefix is not bureaucracy. A raw Ethereum transaction is RLP-encoded and can never begin
with `0x19`, so prefixing guarantees that a signature you gave a website to prove your identity
is structurally incapable of being replayed as a transfer of your funds. Any interface asking
you to sign unprefixed bytes is asking for a blank cheque.

The deliberate breakage is the important half. A bare signature is a **bearer token with no
expiry**: anyone who finds it in a log file or a proxy can log in as that player for the rest of
time without ever touching the key. Fixing that needs three pieces of server-side state — a
random nonce the server issued, the domain and expiry inside the signed text, and deletion of
the nonce the instant it is used — and those three pieces, standardised, are Sign-In With
Ethereum. Level 5 builds it.

**What they will ask.** *"How does wallet login work, and what stops a replay?"* This is the
single most likely hands-on question for a backend engineer at a game studio, because it is the
one piece of wallet integration that lives entirely on the server.

---

## Level 5 — Sign-In With Ethereum, as an Express endpoint

**Statement.** Build two routes. `GET /auth/nonce` issues a cryptographically random nonce,
stores it against nothing in particular, and returns it. `POST /auth/verify` accepts an
EIP-4361 message and a signature, checks the domain, the chain ID, the expiry and the nonce,
recovers the signer, **deletes the nonce atomically**, and issues a session token. Then attack
your own endpoint: replay the same verify payload twice and prove the second attempt fails.

**Hint.** The atomicity is the exercise. `SELECT` then `DELETE` is a race; a single
`DELETE … RETURNING` is not. In memory, the equivalent is checking and removing in one
synchronous step before any `await`.

**Solution.** [solutions/05_siwe_express.ts](solutions/05_siwe_express.ts) — `npm run l5`.
Compare against [auth-siwe.ts](../../input/metaspace-prep/backend/src/auth-siwe.ts), which does
the same job with ethers and Fastify.

The solution boots the server, plays a client against it and exits, so there is nothing to leave
running. It races the nonce store two ways, and the pair of results is the lesson. Raced
directly, the naive check-then-delete store accepts the same nonce **twice, every time** — the
defect is deterministic once you remove the network. Raced through two concurrent HTTP requests,
it usually accepts only one, because signature verification takes long enough for the first
request to finish deleting. So the bug is present on every run and visible on some of them,
which is precisely why this class of defect survives code review and manual testing and then
appears in production under load. The fix is not a mutex — that protects one process and you
will run several — it is a single conditional statement the database adjudicates:
`DELETE FROM siwe_nonce WHERE nonce = $1 RETURNING nonce`.

**What they will ask.** *"Where is the race condition in that login flow?"*

---

## Level 6 — Reading events: `getLogs`, ranges, and provider limits

**Statement.** Fetch `Transfer` events from a token on Amoy over a range of blocks. Then
deliberately ask for a range so large the provider refuses, observe the error, and write the
loop that walks the range in chunks. Decode the logs into typed objects rather than reading
`topics[1]` by hand.

**Hint.** Indexed parameters live in `topics`, non-indexed ones in `data`. Public RPCs cap the
block span and the result count, and the caps differ per provider, so the chunk size must be a
parameter and the loop must survive being told "too many results."

**Solution.** [solutions/06_read_events.ts](solutions/06_read_events.ts) — `npm run l6`

It reads Polygon's native-token precompile at `0x…1010`, which emits `LogFeeTransfer` on
essentially every transaction and is therefore always busy — unlike a quiet test token, which
teaches you nothing because every query returns nothing. Two things in the output are worth
dwelling on. The self-halving loop really does halve, several times, against the live provider.
And the two deliberate failures come back with the *same* error message, one of which is plainly
false: a 500-block query is not a range "over 10000 blocks". That is why the loop treats any
failure as "ask for less" rather than parsing the message — provider error text is not an
interface, it differs between Alchemy, Infura, QuickNode and drpc, and it sometimes lies.

**What they will ask.** *"How do you get historical data off the chain?"* — where the wrong
answer is "loop over every block and read the transactions."

---

## Level 7 — A checkpointed, idempotent indexer

**Statement.** Take level 6's log reader and write the results into a database so that the game
can answer "what does this player own?" without ever touching an RPC. Keep a checkpoint row
recording the last block you processed. Make the ingestion idempotent, so that processing the
same log twice leaves the database unchanged — because you *will* process the same log twice.
Kill the process mid-batch and restart it, and prove the result is identical.

**Hint.** The natural key of a log is the triple of block hash, transaction hash and log index.
A unique constraint on that triple plus an upsert turns "did I already handle this?" from a
question into an invariant the database enforces.

**Solution.** [solutions/07_indexer.ts](solutions/07_indexer.ts) — `npm run l7`. Compare
against [indexer.ts](../../input/metaspace-prep/backend/src/indexer.ts).

It uses `node:sqlite`, built into Node 24, so there is no database to install; every statement is
ordinary SQL and the Postgres differences are noted inline. The run proves two things. Indexing
the same range twice inserts nothing the second time and raises no error, because the primary key
on `(block_hash, tx_hash, log_index)` makes reprocessing free. And a crash halfway through a
batch leaves **zero** rows and a checkpoint of zero rather than half a batch — then the restart
converges on a database with the same fingerprint as a clean run. That equality is the whole
exercise: it means a deploy, an OOM kill or a provider outage is a non-event rather than an
incident.

**What they will ask.** *"Why not just use `contract.on('Transfer', …)`?"* This is the question
the README of your own repo already calls the differentiator, and the answer is that an
event subscription has no memory, no checkpoint, no replay and no reorg handling: restart the
process and you have a hole in your data you will never know about.

---

## Level 8 — Reorg handling: detect it, then unwrite it

**Statement.** Extend the indexer so that before processing a batch it checks that the parent
hash of the first new block matches the hash it recorded for the previous block. When they
disagree, walk backwards to the last block whose hash still matches the chain, delete
everything after it, and resume from there. Simulate the condition rather than waiting for one
to happen.

**Hint.** You cannot roll back what you did not record, so the indexer must store block hashes
alongside the data, and derived state — a player's inventory — must be rebuildable from the log
table rather than incremented in place.

**Solution.** [solutions/08_reorg.ts](solutions/08_reorg.ts) — `npm run l8`

Real reorgs on Polygon after Rio are rare, which is the point of an elected block producer, so
the solution indexes real Amoy blocks and then rewrites **its own** stored hashes four blocks
deep. The detector cannot tell the difference: all it does is compare what it stored against
what the chain now reports. It finds the common ancestor, deletes everything after it, moves the
checkpoint *backwards*, rebuilds derived state, re-indexes the winning branch and converges.

The uncomfortable part is the checkpoint going backwards, and it is the part that makes the
design correct: a checkpoint is a claim about which history you processed, not a high-water mark
of progress, so when that history turns out to be wrong the honest response is to withdraw the
claim.

**What they will ask.** *"What happens to your database when the chain reorganises?"* This is
the senior question in the whole ladder, and it is the one where your ten years of reconciling
against sources you do not control is the answer, not a liability.

---

## Level 9 — The write path: nonces, fees, and a stuck transaction

**Statement.** Send a transaction from a throwaway funded account on Amoy. Manage the nonce
explicitly rather than letting the library guess. Set EIP-1559 fees deliberately. Then send one
with a maximum fee low enough that it sits unmined, observe that it neither fails nor confirms,
and replace it by re-sending the **same nonce** with a higher fee.

**Hint.** Replacement is not cancellation — the chain has no cancel. You are outbidding your
own earlier order. Most nodes require the replacement to beat the original by a margin, not
merely tie it.

**Solution.** [solutions/09_relayer.ts](solutions/09_relayer.ts) — `npm run l9`. Compare
against [relayer.ts](../../input/metaspace-prep/backend/src/relayer.ts).

Parts 1 to 3 need **no funds and no funded key**: transactions are signed locally and nothing is
broadcast, which is enough to demonstrate everything that matters. Part 4 broadcasts only if you
set `PRIVATE_KEY` to a throwaway Amoy key, and says so clearly when you have not.

The nonce race is shown live: two concurrent calls to `getTransactionCount` return the same
number, because the node is reporting a fact about the past rather than issuing a reservation.
Then the replacement — two different transaction hashes signed against the *same* nonce, only
one of which can ever be mined. There is no cancel on a blockchain; there is only outbidding
your own resting order, and most nodes require the bump to beat the original by a margin rather
than merely equal it.

**What they will ask.** *"Two requests come in at once and your relayer sends two transactions
with the same nonce. What happens, and how do you prevent it?"*

---

## Level 10 — EIP-712 vouchers, and proving both languages agree

**Statement.** Build the voucher service: given a player and an item, the backend signs a typed
struct — not a string — binding the mint to a contract, a chain ID, a recipient, an item, an
amount and a unique voucher ID. Then write the test that matters: compute the type hash in
TypeScript and compare it against the one the Solidity contract computes, and watch the test
fail when you change a single space in the type string.

**Hint.** The domain separator pins name, version, `chainId` and `verifyingContract`. Getting
any of them wrong produces a signature that verifies nowhere, with no useful error.

**Solution.** [solutions/10_voucher_eip712.ts](solutions/10_voucher_eip712.ts) — `npm run l10`.
Compare against [voucher.ts](../../input/metaspace-prep/backend/src/voucher.ts) and
[voucher.test.ts](../../input/metaspace-prep/backend/src/voucher.test.ts).

The cross-language check is real rather than illustrative, and it needs no deployment. Because
`VOUCHER_TYPEHASH` is a compile-time constant, solc embeds those exact 32 bytes in the deployed
bytecode, so the solution computes the type hash in TypeScript and asserts the bytes appear in
the compiled artifact of
[03_ItemLedgerV3.sol](contracts/src/03_ItemLedgerV3.sol) — run
`cd contracts && npm install && node compile.mjs` first to generate it. Then it does the same
with the type string rewritten with spaces after the commas, which a formatter might add: a
different hash, absent from the bytecode, and a signature the contract would silently refuse.

Part 3 shows the domain separator earning its place — one signature checked against three
contexts, accepted in exactly one. Part 4 is the half nobody expects: the voucher ID is an
ordinary database uniqueness problem, and the contract's own replay check is a backstop, not a
design, because a duplicate caught on chain still wastes the player's gas and still leaves your
records wrong.

**What they will ask.** *"How does a player claim a reward they earned in the game?"* For a game
studio minting assets, this is the architecture question, and the signed-voucher pattern is the
answer.

---

## Level 11 — The contract side: `mintWithVoucher` on ERC-1155

**Statement.** Write the contract that accepts level 10's voucher: recover the signer, check it
against the authorised backend signer, mark the voucher ID used *before* minting, and mint.
Then examine what happens if you mark it used afterwards instead.

**Hint.** Checks, effects, interactions — in that order, always. ERC-1155's `_mint` calls back
into the recipient if it is a contract, and that callback is an opportunity for it to call you
again.

**Solution.** [solutions/11_reentrancy.ts](solutions/11_reentrancy.ts) — `npm run l11`. Compare
against [GameItems.sol](../../input/metaspace-prep/contracts/src/GameItems.sol).

This one does not describe the attack, it **runs** it. The solution spins up a local EVM
(`@ethereumjs/evm`), deploys
[04_GameItemsBroken.sol](contracts/src/04_GameItemsBroken.sol) and
[05_GameItemsFixed.sol](contracts/src/05_GameItemsFixed.sol), and attacks each with
[06_ReentrantReceiver.sol](contracts/src/06_ReentrantReceiver.sol). No testnet, no funds, no
deployment.

Against the broken ordering, one voucher for one item mints **four items**. Against the fixed
ordering the same voucher mints nothing, and a third run proves an honest contract recipient
still receives its one item — otherwise the "fix" would be a denial of service wearing a
security costume. The two contracts differ by the order of three lines and by two bytes of
compiled bytecode.

What did *not* save the broken version is the part worth remembering: the signature was verified,
the deadline was checked, and the voucher-used mapping existed and was written to. Every control
was present. A control that runs after control has left the building is not a control.

**What they will ask.** *"Where is the reentrancy in this contract?"*

---

## Level 12 — The whole loop

**Statement.** Put it together. A React page connects a wallet with wagmi, logs in through your
level 5 endpoint, requests a voucher, submits the claim, and polls its own inventory — which is
served from the database your level 7 indexer fills from the events the level 11 contract
emits. Nothing in the frontend reads the chain to know what the player owns.

**Hint.** That last sentence is the design. The chain is the source of truth for *ownership*;
your database is the source of truth for *everything the game needs to be fast about*, and the
indexer is the one-way bridge between them.

**Solution.** [solutions/12_full_loop.ts](solutions/12_full_loop.ts) — `npm run l12`

The whole system in one runnable file, offline: a local EVM holding the contract, an Express API,
SQLite, and a client that plays the seven steps in order. Log in with SIWE, read an empty
inventory, claim a reward, claim it **again** and receive the same voucher, submit the mint,
submit the identical voucher a second time and watch the contract refuse it, then read an
inventory containing exactly one sword.

Three defences stopped a duplicate item at three layers, and naming all three is the answer to
the question below: the database refused to issue a second voucher for the same reward, the
contract refused to honour the same voucher id twice, and the indexer's primary key means
redelivery moves nothing. The first is correctness, the second is trustlessness, the third keeps
your own records honest when the network misbehaves.

**What they will ask.** *"Walk me through what happens when a player claims a reward."* Thirty
seconds, whiteboard optional. If you can do that cleanly, the interview is largely over and you
have been the one talking about architecture.
