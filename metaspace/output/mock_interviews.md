# Mock interviews — three simulations, thirty minutes each

The constraint you are preparing for is not ignorance. It is **thirty minutes**, which is
roughly five to seven substantive questions, which means a four-minute answer has cost you a
whole question and the impression of not being able to stop.

So run these against a clock, out loud, from the first word. Reading them silently trains
nothing you will need in the room.

Scoring is the same three-colour scheme as the existing
[qa-drill](../input/metaspace-prep/notes/qa-drill.md), which remains worth rereading and is not
replaced by this file:

- 🟢 **Answered cleanly** — you got there in under ninety seconds without groping.
- 🟡 **Got there** — but slowly, or you needed a second run at it.
- 🔴 **Missed** — go back to the article named beside the question.

---

## Before any of them: the opening ninety seconds

Every simulation starts the same way, because every real interview will. Rehearse this until it
is boring.

> **"So, tell me about yourself and how much blockchain you've actually done."**

The answer is in [article 01](articles/01_what_is_a_blockchain_engineer_2026.md) and in
[positioning.md](../input/metaspace-prep/notes/positioning.md), and its shape is: backend and
data engineer, a decade of keeping systems correct against sources you do not control, the
observation that a Web3 game backend is mostly that same problem, the repository you built to
check yourself, and the explicit limit — not a contract security expert, would not want to be
the only reviewer of a contract holding real value.

Two things to time yourself on. It should take **sixty seconds, not three minutes**. And it
should end with an offer — "happy to walk through any of it" — rather than trailing off.

---

## Simulation one — the architecture conversation

The most likely shape of the call: a Tech Lead finding out whether you can hold a design
discussion. This is the one you should be best at, because it is your actual job.

| # | Question | Where it is answered |
| --- | --- | --- |
| 1 | How much blockchain have you done? | [01](articles/01_what_is_a_blockchain_engineer_2026.md) |
| 2 | Walk me through what happens when a player claims a reward. | [10](articles/10_backend_architecture_web3_game.md), [level 12](exercises/solutions/12_full_loop.ts) |
| 3 | Why not just subscribe to events with `contract.on`? | [10](articles/10_backend_architecture_web3_game.md), [level 7](exercises/solutions/07_indexer.ts) |
| 4 | What happens to your database when the chain reorganises? | [02](articles/02_blockchain_from_zero.md), [level 8](exercises/solutions/08_reorg.ts) |
| 5 | How many confirmations do you wait before crediting a player? | [02](articles/02_blockchain_from_zero.md), [04](articles/04_polygon_and_evm_networks.md) |
| 6 | Our relayer sometimes sends duplicate transactions. Where would you look? | [10](articles/10_backend_architecture_web3_game.md), [level 9](exercises/solutions/09_relayer.ts) |
| 7 | Why are we on Polygon rather than mainnet? | [04](articles/04_polygon_and_evm_networks.md) |

**What a strong answer sounds like here**, as opposed to a correct one: you name the *defence*
at each step of the claim path rather than just the step. "The claim is idempotent on the reward
ID" is worth more than "then the backend issues a voucher." And on question 5 you refuse the
number — confirmation depth is a risk decision, and on Polygon after Rio the finalized tag is a
couple of blocks behind, which you measured.

**The trap in this set** is question 3. It is easy to answer "because it's unreliable" and stop.
The full answer is that a subscription has no memory: restart the process and the events that
arrived meanwhile are not delayed, they are gone, with nothing in the API to tell you they
existed — so a routine deploy becomes silent data loss.

---

## Simulation two — the contract conversation

Harder, shorter, and the one where the discipline is knowing where to stop.

| # | Question | Where it is answered |
| --- | --- | --- |
| 1 | Read `mintWithVoucher` and tell me what's wrong with it. | [06](articles/06_solidity_from_zero.md), [08](articles/08_smart_contract_security.md) |
| 2 | Explain reentrancy, and where it could appear in our contracts. | [08](articles/08_smart_contract_security.md), [level 11](exercises/solutions/11_reentrancy.ts) |
| 3 | What is EIP-712 and why not just sign a string? | [05](articles/05_wallets_keys_signatures.md), [level 10](exercises/solutions/10_voucher_eip712.ts) |
| 4 | Why ERC-1155 rather than ERC-721 for game items? | [07](articles/07_token_standards_digital_assets.md) |
| 5 | How would you do loot boxes on chain? | [08](articles/08_smart_contract_security.md) |
| 6 | How much smart contract security do you know? | [08](articles/08_smart_contract_security.md) |
| 7 | What's the difference between storage, memory and calldata? | [06](articles/06_solidity_from_zero.md) |

**What a strong answer sounds like**: on question 1, a *method* rather than a guess — authority
first, then ordering, then arithmetic, then what is missing — and a question rather than a
verdict where you are unsure. On question 2, the game-specific landing: ERC-1155 requires
notifying a contract recipient, so every mint is a call into untrusted code, which is why the
voucher is marked used before minting. You have watched that fail;
[level 11](exercises/solutions/11_reentrancy.ts) mints four items from one voucher against the
broken ordering and nothing against the fixed one.

**The trap in this set** is question 6, and it is a trap in both directions. Overclaim and the
next question exposes you, in front of someone who has probably written the contracts.
Underclaim and you have handed them a reason to say no. The calibrated answer names the classes
you know, the contracts you have written, and the specific limit: no professional-level formal
verification or invariant fuzzing, and not the only reviewer on anything holding real value.

---

## Simulation three — the live coding exercise

They asked you to join from a laptop rather than a phone, which usually means a shared editor.
Assume TypeScript. Thirty minutes total means the exercise is small — fifteen minutes of code at
most — and that **talking while you work matters more than finishing**.

Set a timer for fifteen minutes on each of these and type it, in the
[exercises](exercises/) folder, with the tests you would actually write.

**Exercise A — idempotent ingestion.** "Here are some log objects, some of them duplicates.
Write the function that stores them so that running it twice changes nothing." The whole answer
is the natural key `(blockHash, transactionHash, logIndex)` and an upsert; the mistake is
deduplicating in JavaScript with a `Set` instead of letting the database enforce it.
([level 7](exercises/solutions/07_indexer.ts))

**Exercise B — the async trap.** "This function saves every log but returns before they're
written. Fix it." `forEach` with an async callback, and the follow-up question is which of
`for…of` and `Promise.all` you would choose and why — sequential for database writes where
ordering matters and the pool is finite, concurrent for independent RPC reads.
([article 09](articles/09_nodejs_typescript_for_web3.md))

**Exercise C — the balance endpoint.** "Return a player's token balance as JSON." The trap is
`JSON.stringify` refusing to serialise a `bigint`, and the wrong fix under time pressure is
`Number()`, which silently loses precision above 2^53. Say that out loud as you avoid it.
([article 09](articles/09_nodejs_typescript_for_web3.md))

**Exercise D — verify a signature.** "Given a message and a signature, tell me who signed it."
Recovery rather than comparison, and the thing to volunteer unprompted is that without a nonce
and an expiry this is a bearer token that never dies.
([level 4](exercises/solutions/04_sign_and_recover.ts))

**What a strong performance looks like** has little to do with the code. Narrate as you go, say
what you are assuming, write the failing case first if there is time, and when you do not know
an API say so and move — "I'd check whether viem exposes that directly, but the shape is this"
costs nothing, while silence for ninety seconds is the thing that sinks live exercises. If you
finish early, add the test.

---

## Questions to ask them

Leave four or five minutes. These are not filler — the answers change how you would work, and
asking them is itself a signal.

The sharpest one is **"which part of the on-chain integration is currently painful?"** It is
specific, it invites a real answer, and whatever they say — indexer lag, stuck transactions,
gas costs, support tickets about missing items — is something you have now studied.

Then, in rough order of usefulness: whether the backend is Node or something else and how much
of the work is contracts versus services; whether players hold their own keys or the studio
custodies them, because that decides half the architecture; who holds the upgrade key on the
item contract and whether it is behind a multisig or timelock; when the contracts were last
audited and against which version; and what the split is between the game backend and the chain
integration in terms of people.

If there is time for only one more, ask **what the first ninety days would look like**. It is
the question that most reliably tells you whether the role is the one advertised.

---

## The night before

Reread [facts.md](facts.md) and nothing else. No new material.

Confirm the time zone in writing. The slot is booked for **30 September 2026 at 16:00**, but
Haiti is UTC-4 in September and the UAE is UTC+4 — an eight-hour gap — so 16:00 in one is 08:00
or midnight in the other. Check which zone the invitation quotes rather than assuming it is
yours. Test the camera, microphone and
screen sharing from the actual machine. Have the repository open in an editor rather than in a
browser, at [level 12](exercises/solutions/12_full_loop.ts) and
[GameItems.sol](../input/metaspace-prep/contracts/src/GameItems.sol), because those are the two
things you would want to show.

And keep the security rule from [positioning.md](../input/metaspace-prep/notes/positioning.md):
if they send a repository, read it before running it, run it in a container, and never connect a
wallet holding anything real.
