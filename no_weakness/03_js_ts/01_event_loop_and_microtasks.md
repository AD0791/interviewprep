# The event loop, microtasks, and the single thread

*What order things run in, why `await` in a loop is slow, and where the second thread actually lives.*

**Level: L3–L4.** Every output below was produced by running the code on **Node.js v22.22.3**, four cores. Browser differences are flagged where they matter. Read alongside [Python's async execution model](../01_python/01_async_execution_model.md) — the two languages solve the same problem and the comparison is section 5.4.

---

## 1. The thing you already do

```js
async function loadDashboard(accountId) {
  const account = await api.getAccount(accountId);
  const txns    = await api.getTransactions(accountId);
  return { account, txns };
}
```

Two awaits, a rendered dashboard, no threads to think about.

---

## 2. The question you cannot answer about it

Four callbacks are pending: a `setTimeout` with a delay of zero, a `setImmediate`, a `process.nextTick`, and a `.then` on an already-resolved promise. Put them in execution order. Then justify the order — not from memory, from the mechanism.

Those two awaits above are independent. How much time did the second one cost you, and why does nothing in the syntax warn you?

JavaScript is single-threaded, which everyone says. So what exactly is a Web Worker, and what is `worker_threads`? Are they lying, or is "single-threaded" a claim about something narrower than it sounds?

And: an unhandled promise rejection. Does your Node process survive it?

---

## 3. What the machine actually does

### 3.1 The pieces

**One call stack.** Function calls push, returns pop. When it is non-empty, JavaScript is executing, and nothing else can.

**The task queue** (macrotasks): timer callbacks, I/O completions, `setImmediate`.

**The microtask queue**: promise reactions, `queueMicrotask`, and in Node a separate, higher-priority `process.nextTick` queue.

**The event loop**: when the call stack empties, drain the microtask queue **completely**, then take one macrotask, run it to completion, drain microtasks again, repeat.

That word *completely* is doing enormous work, and section 4.5 shows what it costs.

### 3.2 The ordering, measured

```js
console.log('1 sync start');
setTimeout(()      => console.log('6 setTimeout 0'), 0);
setImmediate(()    => console.log('7 setImmediate'));
Promise.resolve().then(() => console.log('5 promise.then'));
queueMicrotask(()  => console.log('5b queueMicrotask'));
process.nextTick(()=> console.log('4 process.nextTick'));
console.log('2 sync end');
```

```
1 sync start
2 sync end
4 process.nextTick
5 promise.then
5b queueMicrotask
7 setImmediate
6 setTimeout 0
```

Reason it out rather than memorising it.

**All synchronous code first**, because the loop does not get a turn until the stack empties. Registering a callback is not running it.

**`process.nextTick` before promises.** Node keeps two microtask queues and drains the nextTick one first. This is Node-only; there is no `nextTick` in a browser.

**Promise reactions and `queueMicrotask` next**, in registration order — they share one queue.

**Then macrotasks.** `setImmediate` beat `setTimeout(…, 0)` here. That ordering is genuinely the interesting bit: `setTimeout(fn, 0)` is clamped to a minimum of 1ms and lands in the timers phase, while `setImmediate` runs in the check phase, which follows poll. From inside an I/O callback `setImmediate` is *always* first; from the main module the result depends on how long startup took, so it can flip. **A question whose honest answer is "it's deterministic from an I/O callback and racy from the main module" is a better answer than a confident wrong one.**

The one-line model: **microtasks are drained to exhaustion between every pair of macrotasks.**

### 3.3 What `await` compiles to

`await` is not a pause. The function returns immediately, suspending itself, and the remainder becomes a callback attached to the promise as a **microtask**.

So `await x` means: return control to the event loop, and resume the rest of this function once `x` settles and the microtask queue reaches me. The stack frame is preserved; execution continues on the exact line.

That is the same shape as a Python coroutine — a bookmark in a function — with one significant difference covered in section 5.4: Python makes you start the loop yourself, JavaScript has one running always.

### 3.4 Closures capture variables, not values

A closure keeps a reference to the *binding*, not a copy of the value at creation time. `var` is function-scoped, so one binding is shared by every iteration of a loop. `let` is block-scoped, and the specification creates a **fresh binding per iteration**.

```js
for (var i = 0; i < 3; i++) setTimeout(() => out.push(`var:${i}`), 0);
for (let j = 0; j < 3; j++) setTimeout(() => out.push(`let:${j}`), 0);
```

```
var:3  var:3  var:3  let:0  let:1  let:2
```

All three `var` callbacks print 3 — by the time they run, the shared `i` has finished counting. The `let` version captures three separate bindings.

This is not trivia. It is exactly the mechanism behind the React "stale closure" bug: a callback captured a binding from an earlier render and is still reading it after the state has moved on.

### 3.5 `this` is decided at the call site

`this` is not a property of the function. It is determined by **how the function is called**.

```js
const account = { balance: 1500, show(){ return this?.balance; } };
const detached = account.show;
```

```
method call   : 1500
detached      : undefined
bind          : 1500
call          : 1500
arrow wrapper : 1500
```

`account.show()` — called *as a member of* `account`, so `this` is `account`. `detached()` — the exact same function, called bare, so `this` is `undefined` under strict mode and ES modules. Nothing about the function changed; only the call site did.

Arrow functions are the exception that proves the rule: they have no `this` of their own and close over the enclosing lexical scope, which is why the arrow wrapper works and why arrows are the modern fix.

### 3.6 Property lookup walks the prototype chain

```js
class Account { constructor(b){this.balance=b;} show(){return this.balance;} }
class Savings extends Account { }
```

```
own property?  false
lookup walks : Savings -> Account -> Object
toString found on: Object.prototype
```

`show` is not an own property of the instance. On a miss, the engine follows the internal prototype link and looks again, repeating until it finds the property or reaches `null`. `class` is syntax over this; there is no separate class system underneath.

---

## 4. Break it on purpose

### 4.1 `await` in a loop

```js
async function sequential(){
  const o=[];
  for (let i=0;i<10;i++) o.push(await fetchAccount(i));   // 500ms each
  return o;
}
async function concurrent(){
  return Promise.all([...Array(10)].map((_,i)=>fetchAccount(i)));
}
```

```
await in a loop : 5052 ms
Promise.all     : 503 ms
```

**Ten times slower**, and every individual line is correct. `await` means *stop here until this settles*; ten in sequence is ten stops in sequence.

This is the most common async performance bug in real codebases and it survives code review because there is nothing to point at. Look for `await` inside `for`. When iterations are independent, they belong in `Promise.all`.

The senior caveat, same as in Python: `Promise.all` over ten thousand items opens ten thousand sockets at once and will exhaust a connection pool or trip a rate limit. Bound it — `p-limit`, a semaphore, or batching. And know that `Promise.all` rejects on the first failure while `Promise.allSettled` waits for all of them; choosing the wrong one turns a partial failure into a total one.

### 4.2 Blocking the only thread

```js
const t0=Date.now();
setTimeout(()=>console.log(`timer scheduled for 0ms fired at ${Date.now()-t0} ms`),0);
const end=Date.now()+1000; while(Date.now()<end);   // synchronous CPU work
```

```
sync work finished at        1000 ms
timer scheduled for 0ms fired at 1002 ms
```

A timer set for zero milliseconds fired after **1002**. The loop cannot preempt running code — it gets a turn only when the stack empties.

In a browser that is a frozen page: no rendering, no clicks, no scrolling, because the render step is a task on the same loop. In a Node server it is every concurrent request stalled behind one — the same failure as blocking Python's event loop, and it has the same fix: get the work off the loop, either into a worker or out of the request cycle.

`JSON.parse` on a large payload, synchronous crypto, a big `.sort()`, and image processing are all real-world versions of that `while` loop.

### 4.3 The unhandled rejection kills the process

```js
process.on('exit', c => console.log('exit code:', c));
Promise.reject(new Error('transfer failed'));
setTimeout(()=>console.log('this line never prints'), 50);
```

```
exit code: 1
Error: transfer failed
```

The last line never printed. Since Node 15 the default for an unhandled rejection is `throw` — **the process dies.** In a browser it is far gentler: an `unhandledrejection` event and a console error, and the page carries on.

The practical consequence is that a floating promise in a Node service is a crash waiting for the right input. `promise.catch(...)`, or `void promise` with a handler attached, or make sure something awaits it. This is a place where a Node-versus-browser distinction is a genuine signal in an interview.

### 4.4 Money

```
0.1+0.2 = 0.30000000000000004
=== 0.3? false
cents  : 0.3
toFixed lies: 1.00
```

IEEE-754 doubles cannot represent 0.1 exactly, and every language using them has this. Two things worth having ready.

Integer minor units — store and compute in cents, divide only when formatting — is the standard fix, and the third line shows it working.

And `toFixed` is not a rounding function you can trust: `(1.005).toFixed(2)` returned **`1.00`**, not `1.01`, because the stored double is fractionally below 1.005. Rounding *display* is not the same as rounding *money*, and financial code should be doing arithmetic in integers or a decimal library long before it reaches formatting.

### 4.5 Microtasks can starve the loop

```js
let n = 0;
setTimeout(() => console.log(`timer finally ran after ${n} microtasks`), 0);
function spin(){ if (++n < 1000) queueMicrotask(spin); }
queueMicrotask(spin);
```

```
timer finally ran after 1000 microtasks
```

Because the microtask queue is drained *to exhaustion* before the next macrotask, a microtask that schedules another microtask can hold the loop indefinitely. Timers never fire, I/O never completes, the page never repaints — and no individual piece of code looks slow.

Recursive promise chains and `process.nextTick` loops are the realistic versions. The distinction to hold: **macrotask starvation is a slow callback; microtask starvation is a livelock.**

---

## 5. The judgment call

### 5.1 So where *is* the second thread?

"JavaScript is single-threaded" is a claim about **one JavaScript execution context**, not about the process. Your code has one stack, one heap, one loop. The runtime around it has plenty of threads — libuv's pool doing file I/O and DNS, and the browser doing network and rendering.

And you can have more contexts. Measured, four CPU-bound jobs:

```
1 run, main thread       :  2996 ms
4 runs, main thread      : 12012 ms
4 runs, 4 worker_threads :  3280 ms
```

**Real parallelism** — 12,012ms down to 3,280ms on four cores.

Worth pausing on, because this is where JavaScript and Python genuinely differ. Node's `worker_threads` are OS threads each running an **isolated V8 instance** with its own heap and its own event loop. There is no shared interpreter state, so there is no need for a GIL, so CPU-bound work actually parallelises across threads. Python threads on the identical benchmark gave [zero speedup](../01_python/02_concurrency_threads_processes.md#34-measured-cpu-bound).

The cost is the mirror image: because heaps are isolated, communication is by message-passing and structured cloning, which is a copy — the same "pickle boundary" tax that Python's processes pay. `SharedArrayBuffer` is the escape hatch, and it brings real shared-memory data races with it.

### 5.2 Choosing a Node concurrency primitive

| | What it is | Use for |
|---|---|---|
| **async/await** | One thread, interleaved | I/O — the default, and right almost always |
| **worker_threads** | OS threads, isolated V8 heaps, message passing | CPU-bound work inside one process |
| **cluster** | Multiple processes sharing a listening socket | Using all cores to serve HTTP |
| **child_process** | A separate program | Shelling out; isolation from crashes |

The rule to state: **async for waiting, workers for computing, cluster for serving.** And in a browser the same split is Web Workers, with `postMessage` and the same cloning cost.

### 5.3 When the answer is not concurrency

Before reaching for a worker, check whether the work needs to happen in the request at all. Most "we need threads" problems in Node are actually a large synchronous `JSON.parse`, an unbounded `.sort()`, or an N+1 against the database — and the fix is streaming, pagination, or one better query. A worker adds a serialisation boundary and a lifecycle to manage; it is worth it for genuine computation and rarely worth it for a slow query.

### 5.4 Against Python, since you use both

| | JavaScript | Python |
|---|---|---|
| Event loop | Always running, built into the runtime | You start it: `asyncio.run()` |
| Colouring | `async`/`await`, same problem | `async`/`await`, same problem |
| Calling an async function | Starts executing immediately, returns a promise | Returns a coroutine, **runs nothing** |
| Blocking the loop | Same disaster | Same disaster |
| CPU on threads | **Real parallelism** (isolated heaps, no GIL) | **None** (GIL) |
| Cross-context sharing | Structured clone; `SharedArrayBuffer` opt-in | Pickle; `mp.Value`/`shared_memory` opt-in |

The third row is the one that catches people who move between the languages. `foo()` on a JS async function begins running the body synchronously until the first `await`; `foo()` on a Python `async def` returns an object having executed nothing. Forgetting `await` in JavaScript usually still does the work; forgetting it in Python silently does nothing at all.

---

## 6. Interview angles

### "Explain the event loop."

> "There's one call stack, and while it's non-empty nothing else runs. When it empties, the loop drains the microtask queue completely — that's promise callbacks and `queueMicrotask`, plus `process.nextTick` first in Node, which has its own higher-priority queue. Then it takes *one* macrotask, a timer or an I/O callback, runs it to completion, and drains microtasks again.
>
> The word that matters is 'completely'. Microtasks are exhausted between every pair of macrotasks, which is why a promise always beats a `setTimeout(0)` — and also why a microtask that schedules another microtask can livelock the loop. I tested that: a self-scheduling microtask ran a thousand times before a zero-millisecond timer got a turn.
>
> And `await` fits into that picture as a microtask. It's not a pause — the function returns and suspends, and the rest of it becomes a callback on the promise. The stack frame is preserved, so it resumes on the same line."

### "Is JavaScript single-threaded?"

> "The execution context is — one stack, one heap, one loop, and while my code is running nothing else can. But the runtime around it isn't: libuv has a thread pool doing file I/O and DNS, and the browser handles network and rendering elsewhere.
>
> And you can have more than one context. Node's `worker_threads` are OS threads each running an isolated V8 instance with its own heap and its own loop, so there's no shared interpreter state and no need for a global lock — which means CPU work genuinely parallelises. I measured four CPU-bound jobs: twelve seconds on the main thread, 3.3 seconds across four workers, on four cores.
>
> That's actually where JavaScript and Python differ most. The same benchmark in Python across four threads gives no speedup at all, because of the GIL — you need processes. Node gets the parallelism from threads, but pays the same price for it: isolated heaps mean communication is by structured clone, which is a copy, exactly like Python's pickle boundary. So the trade-off is identical, it just sits in a different place."

### "Your Node service freezes under load."

> "The first thing I'd suspect is that something is blocking the loop, because there's only one thread and nothing can preempt it. I'd look for synchronous work in a request path — a big `JSON.parse`, a synchronous crypto call, an unbounded sort. The signature is that *every* endpoint gets slow together, including ones that do nothing, because they're all queued behind the same stack. I measured a trivial version: a timer set for zero milliseconds fired after 1002, behind a one-second synchronous loop.
>
> Second thing I'd look for is `await` inside a `for` loop, which is correct code and completely serial. Ten awaits at half a second each is five seconds when `Promise.all` makes it half — I've measured 5052 against 503. Though I'd bound the parallel version, because unbounded `Promise.all` over ten thousand items just moves the outage to the connection pool.
>
> And I'd check for unhandled rejections, because since Node 15 that's a process crash by default, not a warning. If the symptom is a service that disappears rather than slows, that's where I'd start — a floating promise somewhere with no `.catch`."

### "Why does `0.1 + 0.2` not equal `0.3`, and what do you do about it?"

> "Doubles are binary floating point and 0.1 isn't exactly representable in binary, the same way a third isn't in decimal. So the sum comes out as 0.30000000000000004 and the equality check is false. Every language using IEEE-754 has this; it isn't a JavaScript flaw.
>
> For money I don't store floats at all — I work in integer minor units, cents, and divide only at the point of display. And I'd add that `toFixed` isn't a safe rounding function: `(1.005).toFixed(2)` gives `1.00`, not `1.01`, because the stored double is a hair below 1.005. So rounding for display isn't the same as rounding money — the arithmetic needs to be integers or a decimal library long before it reaches formatting."

---

## 7. To add to `RECALL.md`

- Order: **sync → nextTick → promises/queueMicrotask → macrotasks**; microtasks drained **to exhaustion** between macrotasks
- `setImmediate` vs `setTimeout(0)`: deterministic from an I/O callback, **racy from the main module**
- `await` = suspend + resume as a **microtask**; the frame is preserved
- `await` in a loop **5052ms** vs `Promise.all` **503ms**; bound the parallel version
- `Promise.all` rejects on first failure; `allSettled` waits for all
- Closures capture **bindings**: `var` → `3 3 3`, `let` → `0 1 2` (fresh binding per iteration) — this is the stale-closure bug
- `this` is set by the **call site**: detached method → `undefined`. Arrows have no own `this`.
- Blocking: timer for 0ms fired at **1002ms**. Signature = **all endpoints slow together**
- Unhandled rejection in Node ≥15 → **process exits(1)**; in a browser → an event, page survives
- `0.1+0.2 = 0.30000000000000004`; `(1.005).toFixed(2) = "1.00"` — use integer cents
- Microtask livelock: **1000 microtasks before a 0ms timer**
- `worker_threads`: **12012ms → 3280ms** on 4 cores. Isolated V8 heaps, **no GIL**, cost is structured clone
- async for waiting · workers for computing · cluster for serving

---

← [JS/TS index](README.md) · [Python's event loop](../01_python/01_async_execution_model.md) · [repo plan](../README.md)
