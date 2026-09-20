# Node, TypeScript and the client libraries: the gap to drill hardest

Every other article in this track is about a subject you can discuss. This one is about a skill
you may have to *perform*, live, while someone watches — and the brief for this whole track
starts from a previous interview lost on basics rather than on depth.

So this article is organised differently. It is the short list of things that actually go wrong
when an experienced Python backend engineer writes TypeScript against a chain, in the order they
go wrong, with the failure shown each time. Everything here is verified output, not recollection.

---

## Life as a Python engineer writing TypeScript

The syntax is not the problem. You will guess `const`, `async`, `await`, arrow functions, and
template strings correctly on the first try, and TypeScript's type annotations will feel
familiar if you have used Pydantic.

Four things are genuinely different, and all four have bitten someone in production this week.

## One: single-threaded does not mean safe

The most dangerous belief a Python engineer can bring to Node is that the event loop makes
concurrency someone else's problem. Node runs your JavaScript on one thread, so two lines of
your code never execute *simultaneously* — and people conclude that races are impossible.

They are not. **Every `await` is a yield point.** Your function stops, other work runs to
completion, and then your function resumes into a world that changed while it was gone.

You built exactly this bug in [level 5](../exercises/solutions/05_siwe_express.ts):

```ts
async consume(nonce) {
  if (!nonces.has(nonce)) return false;   // request A checks: present
  await somethingSlow();                   // ← A suspends; B runs and also checks: present
  nonces.delete(nonce);                    // both proceed
  return true;
}
```

Raced directly, that store accepts the same nonce twice, every time. The fix is not a mutex —
there is nothing to lock against in one thread, and a mutex would not survive the second replica
anyway. The fix is to make the check and the act **one operation that cannot be interleaved**:
in memory that is `Set.delete`, which returns whether it removed anything; in Postgres it is
`DELETE … RETURNING`, and you trust the row count rather than a prior `SELECT`.

The same shape returns in [level 9](../exercises/solutions/09_relayer.ts): two concurrent
requests both ask the node for the next nonce, both get the same answer, and both build a
transaction that cannot both be mined.

Say this crisply if asked about concurrency in Node: the thread is single, the *interleaving* is
real, and the unit of atomicity is the stretch of code between two awaits.

## Two: everything is a `bigint`, and JavaScript will not let you forget

A `uint256` does not fit in a JavaScript number. Numbers are IEEE-754 doubles, exact only to
about 2^53, and token amounts routinely exceed that — the WPOL supply you read in
[level 3](../exercises/solutions/03_read_a_contract.ts) is a 24-digit integer.

So viem and ethers both return `bigint`, and the language enforces the boundary rudely:

```text
> 1n + 1
TypeError: Cannot mix BigInt and other types, use explicit conversions

> JSON.stringify({ balance: 1n })
TypeError: Do not know how to serialize a BigInt

> Number("144899711026285645594950")
1.4489971102628564e+23      ← silently wrong, no error at all

> 10n / 3n
3n                          ← integer division, truncated, no warning
```

The first two throw, which is merciful. The third and fourth do not, and they are how balances
quietly become wrong.

Three rules cover it. **Keep `bigint` all the way through your domain logic** — convert only at
the display boundary, with `formatUnits`. **Store it as text or numeric**, never a float, in
Postgres. And **serialise deliberately**: an API returning token amounts needs a `bigint`
replacer in `JSON.stringify`, or amounts as strings in the response type, because the default
throws and a hastily added `Number()` is worse than the crash it silences.

## Three: the TypeScript settings that actually catch things

Strict mode is table stakes. Two flags beyond it earn their keep in this domain, and both are on
in [the exercises' tsconfig](../exercises/tsconfig.json).

`noUncheckedIndexedAccess` makes `array[0]` have type `T | undefined`, which is the truth. Log
topics are the canonical case: `log.topics[2]` may not exist, and code that assumes it does
crashes on the first log with fewer topics than you expected.

`exactOptionalPropertyTypes` distinguishes "absent" from "present and undefined", which matters
when you are building RPC parameters where a present-but-undefined field is not the same as an
omitted one.

Then the thing that makes viem worth choosing at all: **types inferred from the ABI**. Declare
an event with `parseAbiItem` and `log.args.from` is typed `0x${string}`, named, and checked —
no array indexing, no casting. That inference is also honest about uncertainty, which produced a
real compiler error in [level 7](../exercises/solutions/07_indexer.ts): I hand-wrote a row type
claiming `args.from` is always present, and the compiler refused, because a log whose topics do
not decode really can arrive with missing args. Letting the library's inference define the shape
— `type FeeLog = Awaited<ReturnType<typeof fetchRange>>[number]` — is both less typing and more
correct.

One more that catches people in interviews: **`catch (error)` gives you `unknown`**, not `Error`,
because JavaScript can throw anything. You must narrow before using it.

## Four: the runtime is not the compiler

Node can run TypeScript directly, which is new enough that its limits surprise people. It does
it by **erasing types**, not by compiling them, so any TypeScript construct that *emits code*
is rejected. Level 9 hit this for real:

```text
SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]:
  TypeScript parameter property is not supported in strip-only mode
```

`constructor(private readonly address: string)` emits an assignment, which is code. The same
applies to `enum` and `namespace`. Write the field out longhand and it runs. Worth knowing before
someone hands you a shared editor.

Two smaller runtime facts that matter in a live exercise: this is ESM, so there is no `require`
and top-level `await` works; and Express 5 finally forwards rejected promises from async route
handlers to the error middleware, which Express 4 did not — in Express 4 an unhandled rejection
in a route hung the request until it timed out.

## Break it on purpose: the loop that does not wait

The single most common async bug in JavaScript, and a favourite live-coding trap:

```ts
logs.forEach(async (log) => {
  await saveToDatabase(log);
});
console.log("all saved");        // prints immediately; nothing is saved yet
```

`forEach` ignores the promise each callback returns — it returns `undefined`, always — so the
loop finishes instantly, the log line prints, and the writes complete later, in an order nobody
controls, with any rejection becoming an unhandled rejection that can take the process down.

The corrections are two, and choosing between them is the actual question:

```ts
for (const log of logs) await saveToDatabase(log);   // sequential, ordered, slow
await Promise.all(logs.map(saveToDatabase));         // concurrent, unordered, fast
```

For an indexer writing to a database, `for…of` is usually right, because ordering matters and
because `Promise.all` over ten thousand logs opens ten thousand concurrent operations and
exhausts the connection pool. For independent RPC reads, `Promise.all` is right. And when you
need concurrency with a ceiling, the answer is a small worker pool or a batching library, not a
bigger `Promise.all` — which is a good thing to volunteer, because it is the answer of someone
who has run this at scale.

## The library landscape in 2026

The advert says "ethers.js/Web3.js". Here is the accurate picture, and stating it precisely is a
cheap, verifiable signal of currency.

**web3.js** carries an official sunset notice. It is still installed in a great many codebases
and you should be able to read it, but nothing new should start on it.

**ethers v6** is what most production backends run today, including
[the reference repo](../../input/metaspace-prep/backend/src). It is mature, complete, and
organised around `Provider`, `Wallet` and `Contract` objects. Version 6 moved from `BigNumber` to
native `bigint` and flattened the namespaces, so v5 code and v5 answers are visibly dated.

**viem** is the modern alternative and what the exercises in this track use: functional rather
than object-oriented, tree-shakeable, and typed from the ABI upward. **wagmi** is the React hook
layer built on it, covered in [article 11](11_frontend_wallet_integration.md).

The same three operations in both, all verified against Amoy while writing this:

| Operation | ethers v6 | viem 2 |
| --- | --- | --- |
| Connect | `new JsonRpcProvider(url)` | `createPublicClient({ chain, transport: http(url) })` |
| Read a contract | `new Contract(addr, abi, provider).name()` | `client.readContract({ address, abi, functionName: "name" })` |
| Sign a message | `new Wallet(key).signMessage(m)` | `privateKeyToAccount(key).signMessage({ message: m })` |
| Recover a signer | `verifyMessage(m, sig)` | `recoverMessageAddress({ message: m, signature })` |
| Selector | `id("totalSupply()").slice(0,10)` | `toFunctionSelector("totalSupply()")` |

Both return `0x18160ddd` for that selector and both recover the same address, because underneath
they are doing the identical arithmetic on the identical JSON-RPC. **The library is the least
important choice in this stack**, and being relaxed about that is more convincing than advocacy:
the concepts — nonces, gas, logs, reorgs, idempotency — transfer completely, and learning the
other one is an afternoon.

## Trace one request through a Node backend

`GET /inventory/:address`, so the shape is concrete.

The request arrives and Express matches the route. Your handler is `async`, so calling it returns
a promise immediately and the event loop is free; nothing blocks.

You `await` a Postgres query. Your function suspends at that `await`, and the loop runs other
requests — this is where the interleaving from section one lives, and why any check-then-act in
this handler is a race.

The rows come back with amounts as strings, because that is how a 256-bit integer survives a
database. You convert to `bigint` for any arithmetic, and to a decimal string with `formatUnits`
for display.

You serialise the response. If a `bigint` reached this point unconverted, `JSON.stringify` throws
and Express 5 forwards it to your error middleware — which is the good outcome, because it fails
loudly rather than sending a wrong number.

Note what never happened: no RPC call. The inventory came from the database the indexer fills.
The chain is consulted when you need to *write*, not when you need to *read* —
[article 10](10_backend_architecture_web3_game.md) is about that division.

## Interview Angles

**"Node is single-threaded. Can you still have race conditions?"**

Yes, and it is worth being emphatic because a lot of people answer no. Only one line of my
JavaScript runs at a time, but every `await` is a suspension point: the function stops, the event
loop runs other work to completion, and the function resumes into state that may have changed.
So any check-then-act sequence with an `await` between the check and the act is a race. I built
this deliberately in a Sign-In With Ethereum endpoint — a nonce store that checked the nonce
existed, awaited the signature verification, then deleted it, which lets two concurrent requests
both pass. The fix is not a lock, because a lock only protects one process and you will run
several; it is to collapse the check and the act into a single statement the database
adjudicates, like `DELETE … RETURNING`, and trust the row count. The same pattern covers
allocating relayer nonces and issuing mint vouchers, where losing the race means a duplicate
transaction or a duplicate item rather than a duplicate session.

**"Why does everything come back as a BigInt, and what do you do about it?"**

Because a `uint256` does not fit in a JavaScript number — doubles are exact only to about 2^53,
and token amounts routinely exceed that, so a naive conversion loses precision silently rather
than throwing. Both viem and ethers v6 return native `bigint` for this reason. What I do about
it is keep `bigint` through the whole domain layer and convert only at the edges: `formatUnits`
for display, text or numeric columns in Postgres, never a float. The two traps are that mixing a
`bigint` with a number throws `Cannot mix BigInt and other types`, which is fine because it is
loud, and that `JSON.stringify` refuses to serialise one at all — so an API returning amounts
needs either a replacer or amounts typed as strings in the response contract. The dangerous one
is the fix people reach for under time pressure, wrapping it in `Number()`, which turns a crash
into a wrong balance.

**"We use ethers here — you've been writing viem. Is that a problem?"**

No, and I would rather show why than assert it. They are the same JSON-RPC underneath and the
same arithmetic: computing a function selector gives `0x18160ddd` in both, recovering a signer
from a message gives the same address in both, and both return native `bigint` since ethers v6.
The differences are ergonomic — ethers is object-oriented around Provider, Wallet and Contract,
viem is functional and infers types from the ABI, which I like because it removes a class of
mistakes where you index into `topics` by hand. I have used both deliberately for that reason:
the exercises I wrote are viem, and the reference backend is ethers with Fastify. What does not
transfer between libraries is nothing, really — nonce management, fee strategy, log ranges,
reorgs and idempotency are all properties of the chain, not of the client. The one thing I would
check on arrival is whether any of the codebase is still on ethers v5 or web3.js, because v5 has
`BigNumber` rather than `bigint` and web3.js is formally sunset, and both change what a safe
change looks like.
