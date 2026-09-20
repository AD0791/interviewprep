# The Python path: FastAPI and web3.py, and exactly where it runs out

Metaspace's advert says Node and TypeScript, so that is what this track builds in. But you are a
Python engineer, they will probably ask what you would reach for, and "I'd use whatever you use"
is a weaker answer than the true one — which is that **most of this system does not care what
language it is written in, and the places where it does care are specific and nameable.**

This article is that list. Everything in it was run against Polygon Amoy with **web3.py 8.0.0**
and **eth-account 0.14.0**, and the four Python counterparts to the ladder live in
[exercises/python/](../exercises/python/).

---

## The argument that settles it

Here is the fact that makes the whole language question smaller than it sounds.

The EIP-712 type hash for the voucher struct is
`0xc97be41af9816514648878b03f762e694f0de1ef1c55a9f7cd5a230e9166f849`. That value was computed
three ways while writing this track: by viem in
[level 10](../exercises/solutions/10_voucher_eip712.ts), by `eth_utils.keccak` in
[the Python voucher service](../exercises/python/10_voucher_fastapi.py), and by `solc`, which
embedded it as a constant in
[ItemLedgerV3](../exercises/contracts/src/03_ItemLedgerV3.sol) — where level 10 finds it by
searching the compiled bytecode.

Three languages, one set of bytes. **The contract cannot tell what signed its voucher**, because
what it verifies is a signature over a hash, and a hash has no opinion about programming
languages. The same is true of every other boundary in the system: JSON-RPC is JSON over HTTP,
an ABI encoding is bytes, a log is bytes.

So the question is never "can Python do this." It is "where is Python more work," and there are
exactly four places.

## Where Python is more work

### One: the chain has to be explained to the library

This is the first hour of Python on Polygon and it is not in most tutorials. Ask web3.py for a
Polygon block with a default client and you get an exception rather than a block:

```text
web3.exceptions.ExtraDataLengthError: The field extraData is 105 bytes, but should be 32.
It is quite likely that you are connected to a POA chain.
```

Polygon — like BSC and most proof-of-authority chains — puts more than 32 bytes in a block's
`extraData`, and web3.py validates that field against the Ethereum mainnet rule. The fix is one
line, injecting `ExtraDataToPOAMiddleware`, and then everything works. But you have to know it,
and you discover it by failing.

There is a second, smaller edge behind the first: once that middleware is installed it *renames*
the field, so code reading `block["extraData"]` now raises `KeyError` and must read
`proofOfAuthorityData` instead.

viem has no equivalent step, because its `polygonAmoy` chain definition already encodes what
kind of chain it is. That is the difference in miniature: **TypeScript's libraries know more
about the specific chain; Python's expect you to.**

### Two: no static typing from the ABI

This is the real one, and it is the reason the exercises in this track are TypeScript.

In viem, declaring an event with `parseAbiItem` gives you `log.args.from` as a typed, named,
checked field — the compiler knows the ABI's shape and will reject a misspelling or a wrong
type before the code runs. It is honest about uncertainty too: as
[level 7](../exercises/solutions/07_indexer.ts) discovered, it insists that a decoded argument
may be absent, which caught a wrong assumption I had written by hand.

In web3.py, a block is an `AttributeDict` and a decoded log is a dictionary. A mistyped key is a
`KeyError` at runtime, on some log, in production, at three in the morning. You can layer
Pydantic models over the boundary and you should, but you are re-deriving by hand what the
TypeScript toolchain infers from the ABI automatically.

If someone asks why a Web3 backend would choose TypeScript over Python, this is the honest
answer, and it is worth more than any performance claim.

### Three: the contract toolchain

Foundry and Hardhat are where contract development happens — testing, fuzzing, deployment
scripting, invariant checks. Python has options, but a team writing serious contracts ends up
running one of those two regardless of what their backend is written in. So the Python question
is really only about the *backend*, and framing it that way in an interview shows you understand
where the boundary sits.

### Four: the ecosystem's centre of gravity

Wallet SDKs, account-abstraction bundlers, indexing frameworks and the examples in every
vendor's documentation are TypeScript-first. Python is a first-class citizen for talking to a
chain and a second-class one for the surrounding product infrastructure. That is a statement
about libraries and momentum, not about the language.

## Where Python is better

Two things, and one of them is not a small point.

**Integers.** Python's integers are arbitrary precision natively, so `uint256` values are just
numbers. The entire class of `bigint` hazards from
[article 09](09_nodejs_typescript_for_web3.md) — `Cannot mix BigInt and other types`,
`JSON.stringify` refusing to serialise, and the genuinely dangerous one where someone wraps a
value in `Number()` and silently loses precision — does not exist. In a system whose whole
purpose is keeping balances correct, that is a real advantage and worth saying plainly.

**ETL.** The indexer is a checkpointed pipeline that ingests from an unreliable source,
deduplicates on a natural key, and reconciles. Python has been the right language for that for
twenty years, and [the Python indexer](../exercises/python/07_indexer.py) shows it: the crash
safety that took explicit `BEGIN`/`COMMIT` in TypeScript is just `with conn:`, which commits on
success and rolls back on an exception. Same guarantee, less ceremony — and it produces a
database with the identical fingerprint after a mid-batch crash, exactly as the TypeScript does.

Add to that FastAPI, Pydantic validation, async SQLAlchemy and pandas for the economic analysis
a token-based game will eventually want, and the Python side of this stack is not a compromise.

## The straight comparison

| Concern | TypeScript (viem/ethers) | Python (web3.py 8) |
| --- | --- | --- |
| Talking to a chain | Native | Native, plus a middleware line for Polygon |
| 256-bit integers | `bigint`, with serialisation traps | Plain `int`, no traps |
| Types from the ABI | Inferred and checked at compile time | Runtime dicts; Pydantic by hand |
| Signing, EIP-712 | viem | eth-account, equally mature |
| Async | Native to the runtime | `AsyncWeb3` exists; ecosystem less uniform |
| Web framework | Express, Fastify | FastAPI, arguably nicer |
| Indexing / ETL | Fine | Its natural home |
| Contract toolchain | Foundry / Hardhat | Use Foundry / Hardhat anyway |
| Wallet and AA vendor SDKs | First-class | Thin or absent |
| Data analysis of on-chain data | Awkward | pandas |

## Trace the same claim, in Python

The [FastAPI voucher service](../exercises/python/10_voucher_fastapi.py) is the Express endpoint
from [level 10](../exercises/solutions/10_voucher_eip712.ts), line for line in intent.

A claim arrives for a reward ID. The service looks for an existing row; if there is one it
returns **the same voucher and the same signature**, because retries are normal and a second
voucher would be a second item. Otherwise it allocates a voucher ID, signs the typed struct with
`eth_account`, and inserts under a unique constraint — and if the insert raises
`IntegrityError`, that is not an error to log and swallow, it is a race another request won, and
the correct response is a 409.

Running its self-test shows the retry returning a byte-identical signature, and the type hash
matching the TypeScript and the contract.

The point to take from that: if Metaspace asked you to build the voucher service in Python
tomorrow, nothing about the contract, the chain or the player's wallet would change. Only the
file extension.

## What I would actually recommend

Be decisive here, because "either is fine" sounds like avoidance.

For **this** job: use TypeScript, because the team does, because the ABI typing is a genuine
safety benefit in code that moves assets, and because a backend engineer who insists on their
own language in a small studio is a cost rather than an asset.

For a team that is **already** Python: keep the backend in Python and do not let anyone tell you
the chain requires otherwise. Put the ABI boundary behind Pydantic models, pin the POA
middleware in one place, and use Foundry for the contracts regardless.

And in both cases, the same architecture: an indexer with a checkpoint, a relayer with an
outbox, vouchers signed as typed data, and a database that is the source of truth for speed
while the chain is the source of truth for ownership.

## Interview Angles

**"You're a Python engineer. How much of a problem is that here?"**

Small and specific, which I can show rather than assert. I built this track's exercises in
TypeScript with viem and Express, and I built four of them again in Python with web3.py and
FastAPI, and the interesting result is that the EIP-712 type hash comes out as the same 32 bytes
in viem, in `eth_utils`, and in the constant solc embedded in the contract — so the contract
cannot tell what signed its voucher. The interoperability is at the protocol, not the library.
Where TypeScript genuinely wins is the typing: viem infers types from the ABI, so a misspelled
event field is a compile error, whereas web3.py hands you dictionaries and you find out at
runtime. In code that moves assets I think that is worth having, which is why I would write it
in TypeScript here even though Python is my first language. What does not change either way is
the part that actually decides whether the system is correct — idempotent ingestion,
checkpointing, nonce allocation, reorg handling — because those are properties of the chain.

**"What would you have to be careful about using web3.py with Polygon?"**

The first thing is concrete and it bites immediately: web3.py validates a block's `extraData`
against the Ethereum mainnet rule of 32 bytes, and Polygon puts more than that in it, so
`get_block` raises `ExtraDataLengthError` until you inject `ExtraDataToPOAMiddleware`. It is one
line, but you discover it by failing, and once it is installed the field is renamed to
`proofOfAuthorityData`, so anything reading `extraData` then breaks. Beyond that I would put
Pydantic models at the ABI boundary so that decoded logs are validated once rather than trusted
everywhere, and I would be careful about async — `AsyncWeb3` exists and works, but the
surrounding ecosystem is less uniformly async than Node's, so it is worth checking each
dependency rather than assuming.

**"Would you build the indexer in Python or Node?"**

For the indexer specifically I would be happy either way, and if the team had no preference I
would lean Python, because it is a checkpointed ETL pipeline reconciling against an unreliable
source and that is Python's home ground — the crash-safety that needs explicit transaction
handling in the TypeScript version is just a `with conn:` block, and I verified both converge on
an identical database after a mid-batch crash. What would actually decide it for me is
operational rather than linguistic: whatever the rest of the backend is written in, because an
indexer that shares the team's deployment pipeline, logging, connection pooling and on-call
habits is worth more than a marginally nicer language. A second runtime in a small studio is a
real cost.
