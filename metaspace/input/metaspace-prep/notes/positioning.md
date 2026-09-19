# Positioning — how to pitch this without overclaiming

## The problem you're solving in the room

They found you through a Kotlin course on GitHub. The outreach email asks for
Solidity, ethers.js, EVM. You've told me the role you're actually interviewing
for is backend with some frontend. So the Tech Lead will probably open with some
version of *"so, how much blockchain have you actually done?"*

There are three ways to answer, and only one works.

**Overclaim** — "I've worked with Solidity" — and the first follow-up question
exposes you. In a small studio where the Tech Lead is likely the person who wrote
the contracts, this is fatal, and it's unrecoverable within a single interview.

**Underclaim** — "I'm new to blockchain but I learn fast" — and you've handed
them a reason to say no. It's also just inaccurate about what you bring.

**Reframe.** This is the one. The claim is not that you're a blockchain engineer.
The claim is that **most of what a Web3 game backend does is not blockchain, and
the part that is, is a data-consistency problem you've been solving for a
decade.**

---

## The 60-second answer — rehearse this until it's natural

> "I'm a backend and data engineer — Python and FastAPI mostly, async SQLAlchemy,
> pipelines, a lot of systems that have to stay correct against a data source I
> don't control and can't fully trust.
>
> When I looked at what a Web3 game backend actually has to do, most of it is
> that same problem. You're keeping a database in sync with an append-only log
> whose tail can be rewritten underneath you, you need idempotent ingestion
> because delivery is at-least-once, and you need a write path that handles
> retries without double-spending. I've built checkpointed, reorg-equivalent
> pipelines before — the source was survey data arriving in unreliable batches
> rather than a chain, but the failure modes are the same ones.
>
> So I built the integration layer to check myself: an indexer with reorg
> rollback, an EIP-712 voucher service for server-authorised minting, and a
> relayer with proper nonce management and fee bumping. Happy to walk through any
> of it.
>
> What I'm not is a contract security expert. I've written ERC-1155 and staking
> contracts and I understand reentrancy and the standard patterns, but I wouldn't
> want to be the only pair of eyes on a contract holding real value."

Why this works: it's true, it's specific, it ends with a concrete offer, and the
last sentence makes everything before it more credible rather than less. Senior
engineers trust people who know the edge of their own competence.

---

## The bridge — what actually transfers

| What they need | What you already have |
|---|---|
| Idempotent event ingestion | ONA.io / KoboToolbox pipelines, bulk upserts, dedup on natural keys |
| Checkpointing and resumability | Every ETL job you've written that had to survive a dropped connection |
| Reconciling against a source of truth you don't own | mWater, ONA, survey backends — the whole M&E job |
| Async backend architecture | FastAPI, async SQLAlchemy — same event-loop model as Node |
| Postgres depth: constraints, indexes, transactions | Years of it, plus SQL scripting for bulk operations |
| Realtime | Socket.io work in your interview prep |
| Docker, DigitalOcean, Linux | Arch/Manjaro sysadmin, deployments |
| Designing for bad connectivity | Building for Haiti. Not a metaphor — a real design constraint you've lived with |
| Token economy analysis | Applied Economics degree. Nobody else in their pipeline has this |

**Two of these are genuinely differentiating and you should make sure they land:**

**The trading angle.** You trade YM futures with order-flow tools. Gas markets are
order books: base fee is the clearing price, priority fee is your position in the
queue, an underpriced transaction is a limit order that never fills, and
"speeding up" a transaction is a price improvement on a resting order — not a
cancel, because you can't cancel, you can only outbid. Most backend engineers
learn this vocabulary painfully from documentation. You already think in it. Use
the analogy when fee mechanics come up; it will land, and it's memorable.

**The economics degree.** A play-to-earn game with two tokens has an inflation
problem the day it launches. When F8 comes up (token economy), you're the only
candidate who can talk about sinks, faucets and velocity as an economist rather
than as someone repeating a blog post.

---

## What not to do

- **Don't lead with the Kotlin course.** It's why they found you, but it's not why
  they should hire you, and it points away from backend.
- **Don't say "I've been following crypto for years"** unless asked. Every
  candidate says it and it's worth nothing.
- **Don't bluff a number.** If you don't know how many confirmations Polygon
  needs, say "it's a risk-versus-latency decision — what depth do you use?" and
  you've turned a gap into a conversation.
- **Don't apologise for your background.** You're not a blockchain engineer
  applying down; you're a backend engineer with ten years of experience applying
  across. Those are different postures and they're audible.
- **Don't demo code you can't explain line by line.** Only open the repo on
  parts you've actually read closely.

---

## Logistics — get these settled before the 30th

- **Book the Calendly slot now.** It's first-come, and slots with a Tech Lead in
  a different time zone go fast.
- **Check the time zone carefully.** Haiti is UTC-4 in September; the UAE is
  UTC+4. That's an 8-hour gap. Calendly normally shows times in *your* local zone
  — confirm which zone "4pm" is in before you rely on it, and add the event to a
  calendar that shows both.
- **They asked for a PC or laptop, not a phone.** They almost certainly intend a
  screen share or a live coding exercise. Test the camera, mic and screen sharing
  in whatever tool the invite names, from the actual machine, at least a day
  before.
- **Power and connectivity.** Have a backup: charged laptop, a mobile hotspot
  ready, and a plan if the power goes. If it does go, message them immediately —
  handled well, that's a non-event; handled by disappearing, it isn't.
- **Have the repo open in an editor**, not just on GitHub, so you can navigate it
  quickly if asked to show something.
- **Push the practice repo to GitHub before the interview.** They already
  recruited you off your GitHub, so they will look again.

---

## Two things worth verifying, calmly

The company checks out on the public record: Metaspace is licensed by RAK DAO in
Ras Al Khaimah as a gaming studio, builds a Polygon-based mobile RPG with $LORD
and $MLD tokens, and metaspacechain.org redirects to their main site. So this
looks like a real company, not an impersonation.

Two things are still worth doing, because they cost nothing:

**The scheduling link is a personal Calendly handle**, not a company-branded one.
That's common at small studios, but on the call it's reasonable to confirm you're
speaking to who you think you are — ask their name and role at the start, which
is normal interview behaviour anyway.

**Do not run take-home code on your main machine, and never connect a real
wallet.** There is a well-documented, ongoing campaign that targets developers
with fake or compromised "technical interview" repositories containing malware,
aimed specifically at people with crypto on their machines. This is standard
hygiene regardless of how legitimate the employer is: if they send a repo, read
it first, then run it in a container or a throwaway VM. For anything on-chain,
use a fresh testnet wallet with no real funds. Nobody legitimate will object —
and if someone does object, that's your answer.

---

## Email to send the recruiter now

Short, useful, and it makes you look organised. Send it when you book the slot.

> Subject: Re: Metaspace technical interview — quick question before we meet
>
> Hello,
>
> Thank you — I've booked the technical interview for 30 September.
>
> So I can come prepared, could you confirm two things?
>
> 1. Which stack the role centres on day to day — is the backend in
>    Node/TypeScript, and how much of the work is smart contracts versus backend
>    services and integration?
> 2. Whether there will be a live coding exercise, and in which language.
>
> I'll join from a laptop as requested.
>
> Best regards,
> Alexandro Disla

The second question is the valuable one. If there's a live exercise in
TypeScript, that changes what you drill in the last three days — and asking is
completely normal.
