# The event loop, microtasks, and async

*A thousand microtasks ahead of a zero-millisecond timer, a 20× penalty for one misplaced `await`, and a timer that fired a full second late.*

**Level:** L4–L5 · **Prerequisites:** [`01` scope and closures](00_knowledge_graph.md)
**Syllabus:** [`JS-12`–`JS-17`](00_knowledge_graph.md) · **Roles:** FS ●●● DE ●
**Measurement:** `Measured` — Node **v20.20.2** on `ENV-A`, arm64, macOS 26.5.2. Every figure below came out of a terminal. Browser-specific behaviour (render steps, `requestAnimationFrame`) is tagged `documented` inline.

---

## 1. The thing you already do

A handler that fetches a few things and returns a payload:

```javascript
// Gist: summary.js
async function accountSummary(accountId) {
  const account = await db.accounts.findById(accountId);
  const txns    = await db.transactions.forAccount(accountId, { limit: 50 });
  const rate    = await fx.getRate(account.currency);
  return { account, txns, rate };
}
```

And somewhere in a report generator:

```javascript
// Gist: report.js
const rates = [];
for (const currency of currencies) {
  rates.push(await fx.getRate(currency));
}
```

The first is fine as written — each step needs the previous one, except the third, which does not. The second is **twenty times slower than it needs to be**, and I measured exactly that.

Neither errors. Both look like idiomatic modern JavaScript.

---

## 2. The questions you cannot answer about it

**In what order do these run?** A `setTimeout(fn, 0)`, a `process.nextTick`, a `Promise.resolve().then`, a `queueMicrotask`, and a plain synchronous statement. There is a total order and it is not obvious.

**What does `await` compile to?** Not "it waits" — what does the runtime actually schedule, and on which queue?

**Can a promise chain starve a timer?** If microtasks and macrotasks both queue up, does the loop alternate fairly between them?

**And the two that should bother you.** First: a chain of promises that each schedule another promise. A `setTimeout(fn, 0)` was registered *before* the chain started. **One thousand microtasks ran before that timer fired.** Not a few — the entire chain, to exhaustion.

Second: a timer set for **0 ms fired at 1001 ms**, and its output appeared *after* several `console.log`s that came later in the source.

If you can explain both, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: one chef, two order rails

There is exactly one chef. Above the pass are two rails of order tickets.

The **microtask rail** holds tickets the chef must clear completely — every one, plus any new ticket added while clearing — before touching the other rail at all. Promise callbacks go here.

The **macrotask rail** holds tickets the chef takes **one at a time**, and after each one they go back and empty the microtask rail again. Timers, I/O callbacks and events go here.

Two things follow, and they are the whole module. A microtask that schedules another microtask can keep the chef at the first rail indefinitely, so the macrotask rail starves. And there is **one chef** — a ticket that takes a second of actual cooking blocks every other ticket on both rails.

### 3.2 The total order, measured

```javascript
// Gist: j1_loop.js
setTimeout(()   => order.push("setTimeout(0) [macrotask]"), 0);
setImmediate(() => order.push("setImmediate [check]"));
Promise.resolve().then(() => order.push("promise.then [microtask]"));
queueMicrotask(()   => order.push("queueMicrotask [microtask]"));
process.nextTick(() => order.push("process.nextTick [FIRST]"));
order.push("synchronous");
```

```text
  1. synchronous
  2. process.nextTick [FIRST]
  3. promise.then [microtask]
  4. queueMicrotask [microtask]
  5. setTimeout(0) [macrotask]
  6. setImmediate [check]
```

The complete ordering ([`JS-LOOP-01`](../MEASUREMENTS.md)), and every position is explicable.

**Synchronous code first**, always. The loop is not involved; this is just the current call stack running to completion. Nothing queued can run while the stack is non-empty.

**`process.nextTick` before promises.** Node keeps a separate queue that is drained before the promise microtask queue. It is Node-specific and higher priority than everything, which is why using it for anything but internal library work is a good way to starve the rest of the loop.

**Promise callbacks and `queueMicrotask` together**, in registration order — the same queue.

**Then one macrotask.** `setTimeout(0)` is really `setTimeout(1)` — the HTML spec clamps zero to one millisecond — and it lands in the timers phase.

**`setImmediate` last here**, but this is the one that is *not* stable. Node's loop runs phases in order — timers, pending callbacks, poll, check, close — and `setImmediate` fires in the check phase, after poll. From the main module, whether a 0 ms timer or a `setImmediate` fires first depends on how long process startup took, so **it is genuinely racy**. From inside an I/O callback it is deterministic: `setImmediate` always wins, because you are already past the timers phase when the poll callback runs.

The browser has no `setImmediate` and no `process.nextTick`; it has the same microtask queue plus render steps, where the browser attempts to paint between macrotasks and `requestAnimationFrame` callbacks run just before paint. *(`documented`.)*

### 3.3 Microtasks drain to exhaustion — and can starve a timer

The rule that makes the two rails behave differently:

```javascript
// Gist: j1_loop.js (part 2)
let n = 0;
setTimeout(() => { timerFired = true; }, 0);
function chain() { if (++n < 1000) Promise.resolve().then(chain); }
Promise.resolve().then(chain);
```

```text
  microtasks run before the 0ms timer: 1000
```

**All one thousand** ([`JS-LOOP-02`](../MEASUREMENTS.md)). The timer was registered first and still waited for the entire chain.

The microtask queue is drained **to exhaustion**, including tasks added *during* the drain. A microtask that schedules another microtask extends the drain, and the loop cannot proceed to the macrotask queue until it empties. An infinite chain hangs the process while looking completely idle — no CPU-bound loop to find in a profile, just a queue that never empties.

This is also why promise resolution feels synchronous-but-not. A `.then` on an already-resolved promise does not run inline; it is queued and runs after the current synchronous block finishes. So this prints `A`, `C`, `B`:

```javascript
console.log("A");
Promise.resolve().then(() => console.log("B"));
console.log("C");
```

### 3.4 What `await` actually compiles to

`async`/`await` is syntax over the same machinery. An `async` function returns a promise. `await x` means: suspend this function, and schedule its **continuation as a microtask** to run when `x` settles.

Three consequences follow from "the continuation is a microtask."

**The function suspends but the caller continues.** Calling an `async` function runs its body synchronously up to the first `await`, then returns a pending promise. (Python differs here — calling an `async def` runs *nothing*, as measured in [`06_concurrency/04`](../06_concurrency/04_asyncio_internals.md). That contrast is worth having ready.)

**Resumption is a microtask, not a macrotask.** So an `await` on an already-resolved value still yields — it does not continue inline — but it resumes before any pending timer.

**`await` in a loop is sequential.** Each iteration suspends until its promise settles before the next begins:

```text
  20 x sleep(100): sequential 2022ms   Promise.all 101ms   (20.0x)
```

**Twenty times** ([`JS-LOOP-03`](../MEASUREMENTS.md)). Twenty independent 100 ms operations took 2022 ms sequentially and 101 ms concurrently — the concurrent version taking as long as the slowest single operation, which is the theoretical optimum.

This is §1's report generator. `await` inside a `for` loop is a sequential loop with async syntax, and it is the most common performance defect in async JavaScript.

The fix is `Promise.all` when you need every result and want to fail fast, `Promise.allSettled` when partial failure is acceptable, and a bounded pool when the count is large — because `Promise.all` over ten thousand items opens ten thousand connections at once.

### 3.5 One blocking call stops everything

```javascript
// Gist: j1_loop.js (part 4)
const t = Date.now();
setTimeout(() => console.log(`timer set for 0ms actually fired at ${Date.now()-t}ms`), 0);
const end = Date.now() + 1000; while (Date.now() < end);   // block 1s
console.log("0.1 + 0.2 =", 0.1 + 0.2);
```

```text
  0.1 + 0.2 = 0.30000000000000004
  (1.005).toFixed(2) = "1.00"
  0.1+0.2 === 0.3 -> false
  timer set for 0ms actually fired at 1001ms
```

Two things to read here ([`JS-LOOP-04`](../MEASUREMENTS.md)).

The timer fired at **1001 ms** instead of 0. And its output appears **last** — after three `console.log` calls that come later in the source — because those ran synchronously while the loop was blocked, and the timer callback could not run until the stack cleared.

`setTimeout` does not promise to run in N milliseconds. It promises **not to run before** N milliseconds, and to run as soon as possible after that, once the loop is free. A busy synchronous loop, a large `JSON.parse`, a synchronous `fs.readFileSync`, or a heavy template render all do this.

The production signature is the one to memorise: **when unrelated endpoints slow down together, the loop is blocked**, not the dependency. A slow database makes the endpoints that query it slow. A blocked loop makes the health check slow too — which is the fastest way to tell them apart.

The fix is to get the work off the loop: `worker_threads` for CPU-bound work, which are genuinely parallel isolated V8 heaps with no shared interpreter state and therefore no GIL-equivalent; or chunking the work across macrotasks so the loop can breathe between pieces.

### 3.6 The promise state machine, and rejection handling

A promise is a small state machine: **pending** → **fulfilled** or **rejected**, once, irreversibly. Settled promises never change, which is why a `.then` attached after settlement still fires — it is queued immediately rather than lost.

`.catch(fn)` is `.then(undefined, fn)`. `.finally(fn)` runs on both paths and, importantly, **passes the value or rejection through unchanged** — so a `.finally` that returns something does not alter the result, but one that *throws* does replace the rejection.

Rejection handling differs sharply by environment. In Node ≥ 15 an unhandled rejection **terminates the process with exit code 1**. In a browser it fires an `unhandledrejection` event and the page survives. That difference has caught out plenty of code moved from browser to server.

The subtle part is what "unhandled" means: it is evaluated at the moment of settlement plus a microtask turn. Attaching a `.catch` later — in a subsequent macrotask — is too late, and the process has already been marked as having an unhandled rejection.

`Promise.all` rejects on the **first** failure while the other promises keep running — nothing cancels them, so their work continues and their own rejections may become unhandled. `Promise.allSettled` always fulfils with a result array of `{status, value|reason}` objects, which is what you want when partial failure is tolerable.

Cancellation is not built into promises at all. `AbortController` is the convention: pass `controller.signal` into `fetch` or your own function, call `controller.abort()`, and the operation rejects with an `AbortError`. The promise itself is not cancelled — the underlying operation is asked to stop, and the promise rejects as a result.

---

## 4. Break it on purpose

### 4.1 The loop that was twenty times slower

```text
  20 x sleep(100): sequential 2022ms   Promise.all 101ms   (20.0x)
```

The code is fully `async`, every `await` is correct, and it passes review. It is also serial.

This ships because `await` reads as "get this value" rather than "stop here until this finishes." In a loop over twenty currencies, or a hundred user records, or every row of a report, the cost is linear in the item count while the correct version is constant.

The diagnostic is a question rather than a tool: **does iteration N need the result of iteration N−1?** If not, the loop should be a `Promise.all`. If yes, it genuinely must be sequential and the fix is elsewhere.

**Run this one yourself** with twenty real HTTP calls. Watching 2 seconds become 100 ms from one refactor is the fastest way to make the habit stick.

### 4.2 The timer that fired a second late — and printed out of order

```text
  0.1 + 0.2 = 0.30000000000000004
  ...
  timer set for 0ms actually fired at 1001ms
```

The output order is the tell. Three logs that appear *later* in the source printed *first*, because they were synchronous and the timer callback had to wait for the stack.

In a server this is the incident where the health check times out and an operator restarts a process that was working perfectly, just busy. And it is invisible in most APM tooling, which reports the slow endpoint rather than the one that blocked the loop.

The fix depends on the work. CPU-bound goes to a `worker_thread`. A large synchronous parse gets chunked or streamed. A synchronous filesystem call becomes its async equivalent — the async version exists precisely so the loop stays free.

### 4.3 The microtask chain that hung a healthy process

```text
  microtasks run before the 0ms timer: 1000
```

A thousand is deliberate. Remove the bound and the process hangs — permanently, with a queue that never empties.

What makes this hard to diagnose is that it does not look like a busy loop. There is CPU usage, but the stack is shallow and constantly changing; a profiler shows the promise machinery rather than a culprit function. Timers never fire, I/O callbacks never run, and the process appears alive and idle while doing nothing useful.

Any recursive promise chain without a terminating condition does this — a retry that always retries, a polling function that re-queues itself with `Promise.resolve()` rather than a timer, a stream pump with no backpressure check. The rule: **recursion through microtasks needs a bound; recursion through `setTimeout` yields to the loop and does not.**

### 4.4 The rejection that killed the process

```javascript
// Gist: late_catch.js
const p = doSomethingThatRejects();
setTimeout(() => p.catch(handleIt), 0);     // attached one macrotask too late
```

The `.catch` looks like it handles the rejection. It does not — by the time the timer runs, the runtime has already fired `unhandledRejection`, and on Node ≥ 15 the process is exiting with code 1.

The related trap is `Promise.all` with a failure: it rejects on the first error, and the remaining promises **keep running**. They still hold connections, still write to databases, and if any of them also rejects, that rejection has no handler either.

Attach handlers synchronously, in the same turn the promise is created. Use `allSettled` when you want every outcome. And treat `unhandledRejection` as a crash rather than a warning, because on the server it is one.

---

## 5. The judgment call

### The options, honestly costed

| Choice | Use when | Because | Real cost |
|---|---|---|---|
| **Sequential `await`** | Step N needs step N−1's result | Correct by construction; easiest to read | **Measured 20× slower** when the steps were independent |
| **`Promise.all`** | Independent operations, all must succeed | Concurrent; fails fast; results in order | Siblings **keep running** after the first rejection; unbounded |
| **`Promise.allSettled`** | Partial failure is acceptable | Always fulfils; you inspect each outcome | You must check every `status` — an ignored rejection is invisible |
| **Bounded pool** | Fan-out over hundreds or thousands | Caps concurrent connections | Extra code, or a dependency like `p-limit` |
| **`queueMicrotask`** | Deferring to after the current stack, before any timer | Cheapest possible deferral | **Drains to exhaustion** — recursion here starves the loop |
| **`setTimeout(fn, 0)`** | Yielding to let timers and I/O run | Genuinely returns to the macrotask queue | Clamped to ~1 ms; not a precise scheduler |
| **`setImmediate`** | Yielding after the poll phase, in Node | Deterministic *inside* I/O callbacks | Node-only, and **racy against `setTimeout(0)`** from the main module |
| **`worker_threads`** | CPU-bound work | Real parallelism — isolated V8 heaps, no shared state | Structured-clone cost per message; startup |

### When you would not do this

**Do not `await` in a loop over independent work.** The measured 20× is the argument. The question to ask is whether iteration N needs iteration N−1's result, and if not it should be a `Promise.all`.

**Do not `Promise.all` an unbounded collection.** Ten thousand items means ten thousand simultaneous requests, and you will exhaust sockets or be rate-limited — having done it to someone else's service. Bound it to what the downstream tolerates.

**Do not recurse through microtasks.** §4.3 hangs a process in a way that looks like idleness. If a function re-queues itself, go through `setTimeout` or `setImmediate` so the loop gets a turn.

**Do not do CPU work on the loop.** JavaScript's concurrency is for *waiting*. A synchronous thousand-millisecond computation delays every timer, every I/O callback, and every request in the process — measured at 1001 ms on a timer set for zero. That is what `worker_threads` are for, and unlike Python's threads they achieve genuine parallelism because each worker is an isolated V8 heap with nothing shared to protect.

**Do not treat `unhandledRejection` as a warning.** On Node ≥ 15 it terminates the process. Attach handlers in the same turn the promise is created.

**Do not use `setTimeout` as a scheduler.** It guarantees a lower bound, not a time. If ordering matters, express it with promises rather than by guessing at delays — the classic `setTimeout(fn, 100)` "wait for the other thing to finish" is a race that passes locally and fails under load.

---

## 6. Interview angles

**"What logs first?"**

> Synchronous code, then `process.nextTick`, then promise callbacks and `queueMicrotask` together, then one macrotask like `setTimeout`, then `setImmediate` in the check phase. I ran exactly that and got that order. The two things I'd flag beyond the list: `nextTick` is Node-specific and drains before the promise queue, which is why it's a good way to starve everything else if you use it in application code. And `setImmediate` versus `setTimeout(0)` from the main module is genuinely **racy** — it depends on how long startup took — whereas from inside an I/O callback `setImmediate` always wins, because you're already past the timers phase. The mental model I'd offer is one chef and two rails of tickets: the microtask rail has to be cleared completely, including tickets added while clearing it, before the chef touches the macrotask rail at all — and then only one macrotask, before going back to drain microtasks again.

**"Can a promise chain starve a timer?"**

> Yes, completely, and I measured it. I registered a `setTimeout(fn, 0)` first, then started a chain where each promise callback scheduled another one. **A thousand microtasks ran before that timer fired.** The microtask queue is drained to exhaustion, and crucially that includes microtasks added *during* the drain — so a self-scheduling chain extends the drain indefinitely and the loop never reaches the macrotask queue. Remove the bound and the process hangs. What makes it genuinely nasty to diagnose is that it doesn't look like a busy loop: there's CPU usage but the stack is shallow and constantly changing, so a profiler shows you promise machinery rather than a culprit function, and the process looks alive and idle while doing nothing. The rule I'd take from it is that recursion through microtasks needs a bound, whereas recursion through `setTimeout` or `setImmediate` yields to the loop and is safe.

**"What does `await` compile to?"**

> The function suspends and its continuation is scheduled as a **microtask** when the awaited value settles. Which means three things. Calling an async function runs the body synchronously up to the first `await` and then returns a pending promise — worth contrasting with Python, where calling an `async def` runs *nothing* at all and just hands you a coroutine object; I've measured both and that's a clean difference to have ready. Second, `await` on an already-resolved value still yields rather than continuing inline, but it resumes before any pending timer, because microtasks beat macrotasks. And third, the practical one: `await` in a loop is sequential. I measured twenty 100-millisecond operations at **2022ms sequentially versus 101ms with `Promise.all`** — twenty times, with the concurrent version taking as long as the single slowest operation, which is the optimum. That's the most common performance defect in async JavaScript and it ships constantly because `await` reads as "get this value" rather than "stop here."

**"Your API's endpoints all got slow at once. Walk me through it."**

> The fact that it's *all* of them is the diagnosis. If a dependency were slow, only the routes touching it would suffer — everything degrading together, including the health check, means the event loop itself is blocked. So I'd be looking for synchronous work on the loop: a `readFileSync`, a big `JSON.parse`, a heavy synchronous render, a CPU-bound loop, or a crypto call that isn't using the async form. I built the case to see how bad it gets: a timer set for **0 milliseconds fired at 1001** behind a one-second blocking loop, and the giveaway in the output was that three `console.log`s appearing *later* in the source printed *first*, because they were synchronous and the callback had to wait for the stack to clear. `setTimeout` never promised to run in N milliseconds — it promises not to run *before* N, and then as soon as the loop is free. For fixes: CPU-bound work goes to a `worker_thread`, and those are genuinely parallel because each worker is an isolated V8 heap with no shared state — which is a real difference from Python threads, where the GIL means you get no CPU speedup at all. If it's a large parse or serialization I'd chunk or stream it. And I'd add that this is often invisible in APM, which reports the slow endpoint rather than the one that blocked the loop, so I'd want event-loop lag as an explicit metric.

---

## 7. To add to `RECALL.md`

- **Measured order:** synchronous → `process.nextTick` → promise `.then` / `queueMicrotask` → one macrotask (`setTimeout`) → `setImmediate` (check)
- `process.nextTick` has its **own queue, drained before promises** — Node-only, easy to starve the loop with
- `setTimeout(0)` is clamped to **~1 ms**; vs `setImmediate` it is **racy from the main module**, deterministic inside an I/O callback
- **Microtasks drain to exhaustion, including ones added during the drain.** Measured: **1000 microtasks ran before a 0 ms timer**
- Unbounded microtask recursion **hangs the process while looking idle** — shallow shifting stack, no culprit in a profile
- `Promise.resolve().then(f)` does **not** run inline — prints `A, C, B`
- `await` = suspend + resume as a **microtask**; resumes before any timer
- **JS runs an async body to the first `await`; Python runs nothing.** The clean cross-language contrast
- **Measured: 20 × sleep(100) — sequential 2022ms vs `Promise.all` 101ms (20.0×)**
- **Measured: a 0 ms timer fired at 1001 ms** behind a blocking loop, and its output printed *after* later synchronous logs
- `setTimeout` guarantees a **lower bound**, not a time
- **Signature: unrelated endpoints slowing together = blocked loop**, not a slow dependency. Track event-loop lag as a metric
- Promise: **pending → settled once, irreversibly**. `.finally` passes the value through but a throw inside it replaces the rejection
- Unhandled rejection: Node ≥ 15 **exits(1)**; browser fires an event and survives. A `.catch` attached in a later macrotask is **too late**
- `Promise.all` rejects on first failure and **siblings keep running**; `allSettled` always fulfils with `{status, value|reason}`
- Promises have **no cancellation** — `AbortController` asks the operation to stop; the promise then rejects with `AbortError`
- `worker_threads` are **isolated V8 heaps, no shared state, real parallelism** — unlike Python threads under the GIL

---

← [JavaScript knowledge graph](00_knowledge_graph.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
