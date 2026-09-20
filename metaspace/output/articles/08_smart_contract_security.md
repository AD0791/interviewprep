# Smart contract security: the failure classes, and the honest limit of your claim

Every other kind of bug you have shipped was recoverable. A bad deploy gets rolled back; a
corrupt row gets repaired from a backup; a leaked credential gets rotated. The cost is a bad
afternoon.

Contract bugs are different in three specific ways, and the difference is the reason this
discipline exists as a separate profession. The code is **public**, so anyone can read it
looking for a mistake. It is **immutable by default**, so a mistake cannot be patched — only
migrated away from, while the broken version keeps running forever. And it **holds value
directly**, so finding a mistake pays, immediately and anonymously.

That combination means your adversary is not a bored script kiddie. It is a competent engineer
with a financial incentive proportional to your contract's balance, working from your source.

You are not going to become an auditor before this interview, and you should not pretend to be
one. What you can do — and what is genuinely expected of a backend engineer at a game studio —
is recognise the standard failure classes, know the patterns that prevent them, and be precise
about where your competence stops.

---

## The method: how to read a contract for bugs

Before the catalogue, the procedure, because in a live review the procedure is what they are
actually watching. Work outward in a fixed order so nothing is missed and the interviewer can
follow your reasoning.

Start with **authority**: for every function that changes state, who can call it? Then
**ordering**: within each function, are all the checks before all the effects, and does anything
call out to an untrusted address before the state is settled? Then **arithmetic**, which since
Solidity 0.8 mostly means finding anything wrapped in `unchecked` and asking why. Then
**external calls**: what happens if the thing you called reverts, or re-enters, or lies? Then,
hardest and most valuable, **what is missing**: no event on a state change, no deadline on a
signed message, no replay key on a voucher, no cap on a mint.

## Class one: reentrancy

The famous one, still the most asked, and still shipped.

The mechanism is simple once seen. When your contract calls another address, that address is
code, and that code runs *before* your function finishes. If it calls back into you, it finds
your contract in whatever half-updated state you left it in.

```solidity
// Broken: the classic shape.
function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");   // they get control HERE
    require(ok);
    balances[msg.sender] = 0;                            // too late
}
```

The recipient's fallback function calls `withdraw` again. The balance has not been zeroed yet,
so the check passes again, and again, until the contract is empty. One function, drained.

The fix is an ordering discipline rather than a library: **checks, effects, interactions**.
Validate first, update your own state second, call out last. Write it that way and the
re-entrant call finds a balance of zero and does nothing.

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;                            // effect first
    (bool ok, ) = msg.sender.call{value: amount}("");     // interaction last
    require(ok);
}
```

A `nonReentrant` guard — a flag set on entry and cleared on exit, cheap since transient storage
— is a belt to that pair of braces, and worth having on anything holding value. It is not a
substitute for the ordering, because it only protects one function at a time: two different
functions that share state can still be played against each other, which is the "cross-function
reentrancy" a good interviewer will push you toward.

**Where this lives in a game contract**, and this is the specific thing to say: ERC-1155's mint
and transfer call `onERC1155Received` on the recipient if it is a contract. That is required by
the standard — it exists so tokens cannot be sent to a contract that will never be able to move
them — and it means **every mint is an external call to untrusted code**. So in
[the voucher mint](../exercises/contracts/src/03_ItemLedgerV3.sol), marking the voucher used
before minting is not stylistic caution. Do it the other way around and a contract recipient can
re-enter `mintWithVoucher` with the same voucher and mint repeatedly.

## Class two: access control

Less famous, more common, and usually more expensive: a function that changes state and never
asks who is calling. [Article 06](06_solidity_from_zero.md) shipped exactly this in
`ItemLedgerV1`, where `mint` was `external` and unguarded.

The subtleties are where the real bugs are. **`tx.origin` is not `msg.sender`**: `msg.sender` is
the immediate caller, `tx.origin` is the externally owned account that began the whole call
chain. Authorising on `tx.origin` means any contract a user can be tricked into calling can turn
around and impersonate them to you. It is always wrong for authorisation.

**Initialisation is a function too.** A proxy-based contract has no constructor in the usual
sense; it has an `initialize` function, and if that function is not itself protected, anyone can
call it and become the owner. This has happened, repeatedly, to real projects.

And **ownership transfer should be two-step**. A single-step `transferOwnership` to a mistyped
address is unrecoverable; the two-step version, where the new owner must accept, makes the typo
harmless. OpenZeppelin ships `Ownable2Step` for this reason.

For a game, the authority question to ask is narrower and sharper: *what can the minting key do
if it leaks?* If the answer is "mint anything, unlimited, forever," the design is wrong
regardless of how well the key is stored. The voucher pattern narrows it — a leaked signing key
can still authorise mints, but each one is a specific, expiring, single-use authorisation, and
rotating the signer address on the contract cuts off all of them at once.

## Class three: signature and replay bugs

You have already built the defences in [level 4](../exercises/solutions/04_sign_and_recover.ts),
[level 5](../exercises/EXERCISES.md) and
[level 10](../exercises/solutions/10_voucher_eip712.ts), so this is mostly naming what each one
prevents.

A signature with **no nonce or single-use key** is a bearer token forever. A signature with **no
deadline** is valid years later, under circumstances nobody anticipated. A signature with **no
domain separator** is valid on every chain and to every contract that checks the same bytes — so
a testnet voucher works on mainnet. A design that keys replay protection on **the signature
hash** rather than a business ID is broken by malleability, because EIP-2 constrains `s` to the
lower half of the curve order precisely so that flipping it is invalid — but only if you check,
which is why the recovery helper in the reference contract rejects a high `s` explicitly.

And `ecrecover` **returns the zero address on failure rather than reverting**. Compare its
result against your expected signer and you are fine; compare it against something that might
itself be zero — an uninitialised storage variable, say — and any garbage signature passes. This
is a genuine, exploited bug class, and it is the reason to use OpenZeppelin's `ECDSA` library
rather than raw `ecrecover`.

## Class four: the mempool is public

Everything waiting to be mined is visible to everyone, which makes two things possible.

**Front-running**: someone sees your transaction and submits the same action with a higher
priority fee so theirs executes first. In a game, that is whoever is buying the last rare item
from a marketplace listing.

**Sandwiching**: a trade is surrounded by two transactions that profit from the price movement
it causes. This is a DeFi concern more than a game one, but knowing the word costs nothing.

The general name is MEV — the value extractable by whoever orders transactions in a block. For a
game the practical mitigations are unglamorous: a commit-reveal scheme where the intent is
hashed first and revealed later, deadlines and slippage limits on anything priced, and — most
often — simply not putting the contested decision on chain. Matchmaking, loot rolls and auction
resolution can live in your backend, where ordering is yours to decide.

## Class five: randomness, which does not exist

A game wants loot rolls. The EVM has no randomness, and everything that looks like a source of
it is either public or controllable.

`block.timestamp` is set by the block producer within a tolerance, so a producer with a stake in
the outcome can nudge it. `blockhash` of a recent block is public. Any value derivable from
on-chain state is known to the caller *before* they call, which means a contract can compute the
outcome of your loot roll and revert if it dislikes the result — a free reroll, repeated until
the player wins.

The real options are a verifiable randomness oracle such as Chainlink VRF, which delivers a
random value with a proof in a later transaction, or a commit-reveal scheme, or keeping the roll
off chain and having the backend sign the outcome as a voucher. For a game studio the last of
these is usually right: the roll happens on your server, where it always happened, and the chain
records only the result. It also keeps the loot table private, which the other two do not.

## Class six: upgradeability, and the bugs it adds

Immutability is a feature until you need to fix something, which is why proxies exist: a small
contract holding the storage and delegating all calls to an implementation contract whose
address can be changed.

`delegatecall` is the mechanism, and the thing to understand about it is that the implementation
runs **in the proxy's storage context**. Slot 3 in the implementation is slot 3 in the proxy,
regardless of what either contract calls that variable. So if an upgrade reorders, inserts or
removes a state variable, the new code reads the old data at the wrong offsets — a storage
collision, which corrupts everything silently.

The discipline is strict: new variables are appended, never inserted; nothing is reordered;
nothing is deleted; and gaps are reserved in advance for inheritance. Constructors do not run
for the proxy, so initialisers replace them and must be protected against being called twice.

Worth saying plainly in an interview, because it shows judgement rather than recall: an
upgradeable contract is also a contract someone can change, so it trades one risk for another.
For a game's item contract I would want to know who holds the upgrade key and whether it is
behind a multisig and a timelock, because "the studio can rewrite the rules of the asset you
bought, instantly" is a different product from the one players think they are buying.

## What I would actually check in this codebase

If asked what you would do first with their contracts, an honest and useful answer is a short
list rather than a promise to audit.

Read the mint path end to end, because that is where new assets come from and therefore where
the economic damage is. Check every state-changing function's access control. Check the
checks-effects-interactions ordering everywhere ERC-1155 calls back into a recipient. Check that
every signed message has a domain, a deadline and a single-use key, and that the type hash is
tested against the backend's — the test in
[level 10](../exercises/solutions/10_voucher_eip712.ts). Check that events are emitted on every
state change, because a missing event is an indexing bug that becomes a data-integrity bug.
Confirm there is a pause mechanism for the day something is discovered, and that someone
specific is on the other end of it. Then ask when they last had an external audit, and of which
version.

None of that requires claiming to be an auditor, and all of it is the reading a competent
backend engineer should do before integrating.

## Interview Angles

**"Explain reentrancy, and where it could appear in our contracts."**

Reentrancy is what happens when your contract calls an external address before it has finished
updating its own state: the call transfers control to code the caller controls, and that code
can call back in and find your contract mid-update. The classic case is a withdraw function that
sends funds before zeroing the balance, so the recipient's fallback re-enters and drains it. The
fix is checks-effects-interactions — validate, then update your own state, then make the
external call — with a `nonReentrant` guard as a backstop, though a guard alone does not cover
two functions sharing state. The reason it matters for a game specifically is that ERC-1155
mints and transfers call `onERC1155Received` on a contract recipient, which the standard
requires, so every mint is an external call into untrusted code. That is exactly why a voucher
mint has to mark the voucher used before minting rather than after — otherwise a contract
recipient can re-enter with the same voucher and mint it repeatedly.

**"How much smart contract security do you know?"**

Answer it as a scope rather than a level, and put the boundary in explicitly, because the
boundary is what makes the rest credible. Something like: I know the standard failure classes
well enough to review a contract and to avoid writing them — reentrancy and CEI ordering, access
control including the `tx.origin` trap and unprotected initialisers, signature replay across
nonces, deadlines, domains and malleability, the fact that on-chain randomness does not exist,
and storage collisions in upgradeable proxies. I have written ERC-1155 and staking contracts and
I would be comfortable being a second reviewer on a change. What I am not is an auditor: I do
not do formal verification or invariant fuzzing at a professional level, and I would not want to
be the only pair of eyes on a contract holding real value. For anything with money in it I would
expect an external audit, and my own contribution would be on the integration side — making sure
the backend does not become the weak point through a leaked signing key, a non-idempotent
voucher, or an indexer that credits items from a block that gets reorganised.

**"How would you do loot boxes on chain?"**

Start by saying that the EVM has no randomness, because that is the whole question. Anything
derivable from chain state — `block.timestamp`, `blockhash`, a hash of storage — is either
influenced by the block producer or known to the caller before they call, and if the caller can
compute the outcome in advance they can wrap the call in a contract that reverts on a bad roll,
giving themselves unlimited free rerolls. So the options are a verifiable randomness oracle like
Chainlink VRF, which returns a value plus a proof in a second transaction, a commit-reveal
scheme, or generating the roll off chain and having the backend sign the result as a mint
voucher. For a game studio I would usually argue for the last: the roll happens on the server
where it already happens, the chain records only the outcome, the player still gets a real
on-chain asset, and the loot table stays private — which the on-chain options give away. The
trade to state honestly is that players are then trusting the studio's fairness rather than
verifying it, so if provable fairness is a product promise, VRF is the answer and the extra
transaction is its price.
