# The async execution model

*Coroutines, the event loop, and the GIL — what actually runs your FastAPI endpoint.*

**Level: L3–L4.** Every measurement in this module was produced by running the code shown, on CPython 3.10.12, four cores, FastAPI 0.141.1 under uvicorn. Where a number appears, it came out of a terminal.

---

## 1. The thing you already do

```python
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/accounts/{account_id}/balance")
async def get_balance(account_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Account.balance).where(Account.id == account_id)
    )
    return {"balance": result.scalar_one()}
```

You have written this endpoint, or one close enough. It works. It handles concurrent requests. You did not have to think about threads.

---

## 2. The question you cannot answer about it

Here are four, and they get progressively worse.

When Python evaluates `get_balance(42)`, what object comes back? Not the balance — the function body has not run. So what is it, and who runs the body?

You wrote `async def`. Why does that keyword make the endpoint handle concurrent requests, given that there is exactly one thread and no parallelism anywhere in the process?

Now suppose that one day, in one endpoint, someone replaces the SQLAlchemy call with `requests.get("https://api.bank.example/rates")` — a perfectly ordinary, perfectly working HTTP call. Why does the latency of *every other endpoint in the application* collapse, including the ones nobody touched?

And the one that catches almost everybody: if you delete the word `async` from that broken endpoint and make it a plain `def`, throughput goes back to normal. **The synchronous version is ten times faster than the asynchronous one.** Why?

If you can answer all four cleanly, skip to section 6 and rehearse the spoken answers. If the third or fourth made you hesitate, that hesitation is worth an hour.

---

## 3. What the machine actually does

### 3.1 `async def` does not define a function that runs

The first thing to unlearn is that `async def` defines "a function that runs in the background." It does not. It defines **a function that builds an object and hands it to you, having executed none of its body.**

```python
import asyncio, inspect

async def get_balance(account_id):
    await asyncio.sleep(0)
    return 1500

c = get_balance(42)
print("type:", type(c).__name__)
print("is coroutine:", inspect.iscoroutine(c))
print("frame state:", inspect.getcoroutinestate(c))
```

```
type: coroutine
is coroutine: True
frame state: CORO_CREATED
```

Nothing has run. `CORO_CREATED` means the function's frame exists — its local variables, its instruction pointer parked at line one — and is waiting for someone to start it. The coroutine object is a **paused, resumable stack frame**.

This is why forgetting `await` produces a warning rather than an error, and why the bug is so quiet. `get_balance(42)` on its own is a valid expression that allocates an object and discards it. No database was queried. Nothing failed. The endpoint just silently did nothing.

### 3.2 A coroutine is driven by `send`, and that is the whole protocol

The machinery underneath is the generator protocol, which you already know. A coroutine is resumed by calling `.send()` on it. You can drive one by hand, with no event loop anywhere:

```python
c = get_balance(42)
try:
    out = c.send(None)          # run until the first suspension point
    print("suspended, yielded:", repr(out))
    print("frame state:", inspect.getcoroutinestate(c))
    c.send(None)                # resume it
except StopIteration as e:
    print("returned:", e.value)
    print("frame state:", inspect.getcoroutinestate(c))
```

```
suspended, yielded: None
frame state: CORO_SUSPENDED
returned: 1500
frame state: CORO_CLOSED
```

Read that output carefully, because it contains the entire model.

The first `send(None)` runs the body until it hits `await`, at which point the frame **suspends** and control returns to the caller. The frame is not destroyed — its locals and its instruction pointer are intact, sitting in `CORO_SUSPENDED`. The second `send(None)` resumes from exactly that instruction. When the body finally returns, the return value does not come back normally; it is **carried out inside a `StopIteration` exception** — `e.value` is your 1500.

That is not an analogy for how coroutines work. That is how they work. `await` is a suspension point and `StopIteration` is the return channel.

The mental model worth carrying: **a coroutine is a bookmark in a function.** The event loop's entire job is deciding which bookmark to pick up next.

### 3.3 The event loop is a `while` loop you could have written

There is no magic and no threading. Stripped of error handling and edge cases, `asyncio`'s loop is this:

```python
while True:
    timeout = time_until_earliest_scheduled_timer()
    events = selector.select(timeout)        # epoll on Linux -- the only place we sleep
    for fd, callback in events:
        ready.append(callback)
    move_expired_timers_into(ready)

    for callback in drain(ready):
        callback()                           # a plain, synchronous function call
```

Three observations, each of which explains a real production failure later in this module.

**Every callback is an ordinary blocking call.** The loop calls it and waits for it to return. There is no preemption, no timer, nothing that can interrupt a callback that decides to take five seconds. The loop is *cooperative*: it depends entirely on callbacks giving control back voluntarily.

**The loop is asleep almost all the time**, parked in `selector.select()`, which is a kernel call that blocks until a socket becomes readable or a timer expires. A well-behaved async application spends most of its wall-clock time in that one line.

**It is one thread.** There is no second thread anywhere in this picture. Concurrency here means *interleaving*, not *parallelism* — many operations in flight, one instruction executing.

### 3.4 What `await` compiles to, and how a Future closes the circuit

`await x` requires `x` to be awaitable, meaning it implements `__await__` returning an iterator. The `await` expression **delegates** to that iterator: whatever the inner object yields travels up through every enclosing coroutine frame, unchanged, until it reaches the thing driving the outermost coroutine — which is a `Task`.

A `Future` is the join between the two worlds. It is a small object holding a result-that-does-not-exist-yet plus a list of callbacks. Its `__await__` yields itself and stops. So when you `await` something that reaches a Future, the Task receives that Future and does one thing: it registers `Task.__step` as a done-callback on it, and then returns control to the loop.

Now the circuit is complete. Trace one request end to end:

Uvicorn receives bytes on a socket. The loop wakes from `select()`, sees the readable descriptor, and calls the protocol's callback. That callback creates a `Task` wrapping your `get_balance` coroutine and schedules `Task.__step`. The loop drains its ready queue and calls `__step`, which calls `coro.send(None)`. Your function body finally begins executing. It reaches `await session.execute(...)`, which issues the query, gets back a socket that is not yet readable, and yields a Future. That Future travels up through the frames to `__step`, which attaches itself as a callback and returns. **Your frame is now suspended and the loop is free.** It goes back to `select()` and immediately starts servicing other requests. Some milliseconds later Postgres replies, the socket becomes readable, the loop wakes, the driver sets the Future's result, which schedules `__step`, which calls `coro.send(result)` — and your function resumes on the exact line it stopped at, with `result` as the value of the `await` expression. It returns; `StopIteration` carries the response out; uvicorn writes bytes to the socket.

That is the whole mechanism. Every piece of it is a plain function call on a single thread.

### 3.5 Where the GIL fits, and where it does not

The GIL gets attached to async discussions constantly and usually wrongly, so be precise about this in an interview.

The Global Interpreter Lock is a mutex protecting CPython's internal state — most importantly reference counts, which are not atomic. One thread executes Python bytecode at a time. It is released in two circumstances: around blocking I/O syscalls, so a thread waiting on a socket does not hold it; and periodically, every 5 milliseconds by default (`sys.getswitchinterval()`), so CPU-bound threads take turns.

Here is the point most candidates miss. **The GIL and asyncio are not competing solutions to the same problem, and asyncio does not "avoid" the GIL.** asyncio is single-threaded. There is only ever one thread, so the GIL is never contended — it is irrelevant, not defeated.

What follows is the practically important part: since asyncio gives you one thread, **it provides exactly zero benefit for CPU-bound work.** And since the GIL prevents Python bytecode from running in parallel across threads, threads do not help CPU-bound work either. Measured, four identical CPU-bound jobs on a four-core machine:

```python
def checksum(n=6_000_000):
    return sum(i*i % 7 for i in range(n))
```

```
1 run, serial            : 0.42s
4 runs, asyncio.to_thread: 1.64s
4 runs, ThreadPool       : 1.66s
4 runs, ProcessPool      : 0.52s
```

Four threads took 1.64 seconds to do what one thread does in 0.42 — which is 3.9×, meaning **no parallelism whatsoever**, just the serial total plus overhead. Four processes took 0.52 seconds, near-linear speedup, because each process has its own interpreter and its own GIL.

That table is the honest answer to "how do you handle CPU-bound work in Python," and having measured it yourself is worth more than having read it.

*One caveat to verify before quoting it: free-threaded CPython builds without the GIL (PEP 703) were experimental as of 3.13, and the status has likely moved. Check the current state before making claims about it in an interview — it is exactly the kind of detail an interviewer who follows the language will probe.*

---

## 4. Break it on purpose

Four failures. The first is the one that will actually happen to you.

### 4.1 The blocked event loop

Section 3.3 said the loop cannot preempt a callback. Here is what that costs.

```python
import asyncio, time

async def good(i):
    await asyncio.sleep(0.5)      # yields control back to the loop
    return i

async def bad(i):
    time.sleep(0.5)               # holds the thread. Nothing else can run.
    return i

async def main():
    t = time.perf_counter()
    await asyncio.gather(*(good(i) for i in range(10)))
    print(f"10 x await asyncio.sleep(0.5) : {time.perf_counter()-t:.2f}s")

    t = time.perf_counter()
    await asyncio.gather(*(bad(i) for i in range(10)))
    print(f"10 x time.sleep(0.5)          : {time.perf_counter()-t:.2f}s")

asyncio.run(main())
```

```
10 x await asyncio.sleep(0.5) : 0.51s
10 x time.sleep(0.5)          : 5.04s
```

Ten times slower, and note that `gather` did not help at all — the ten coroutines ran strictly one after another. `time.sleep` is standing in for anything synchronous: `requests.get`, `psycopg2`, `open().read()`, `boto3`, a synchronous SQLAlchemy session, `bcrypt.hashpw`, a large `pandas` operation. Any of them, inside any `async def`, stops the entire process.

**Now the part that is genuinely counterintuitive.** Run the same three shapes as real FastAPI endpoints and hit each with ten concurrent requests:

```python
@app.get("/async-await")        # async def + awaitable I/O
async def a():
    await asyncio.sleep(0.5)
    return {"ok": 1}

@app.get("/async-blocking")     # async def + BLOCKING I/O  <-- the bug
async def b():
    time.sleep(0.5)
    return {"ok": 1}

@app.get("/sync-def")           # plain def -> Starlette threadpool
def c():
    time.sleep(0.5)
    return {"ok": 1}
```

```
/async-await       10 concurrent requests -> 0.53s
/async-blocking    10 concurrent requests -> 5.06s
/sync-def          10 concurrent requests -> 0.53s
```

**The plain `def` endpoint is ten times faster than the `async def` one running identical code.** Deleting the word `async` made it faster.

The reason is a design decision in Starlette that is worth knowing by name. When FastAPI sees a path operation declared `async def`, it awaits it directly on the event loop — it trusts you not to block. When it sees a plain `def`, it assumes the function may block and offloads it to a threadpool via `anyio.to_thread.run_sync`. Blocking a worker thread is survivable. Blocking the loop is not.

So `async def` is not "the fast option." It is a **promise you make to the runtime** that this function will not block. If you cannot keep that promise, plain `def` is not a fallback — it is the correct answer.

**Run this one yourself.** Reading the table is not the same as watching a server you wrote go ten times slower because of one keyword.

### 4.2 `await` inside a loop

The second failure is subtler because nothing blocks and nothing is wrong — it is simply slower than it looks.

```python
async def sequential():
    out = []
    for i in range(10):
        out.append(await fetch_account(i))    # 0.5s each
    return out

async def concurrent():
    return await asyncio.gather(*(fetch_account(i) for i in range(10)))
```

```
await in a loop : 5.05s
asyncio.gather  : 0.51s
```

`await` means *wait here until this finishes*. Ten of them in sequence is ten waits in sequence. The code is correctly async and completely serial — you paid the entire complexity cost of `asyncio` and received none of the benefit.

This is the single most common performance bug in real async codebases, and it is nearly invisible in review because every individual line is correct. Look for `await` inside `for`. When the iterations are independent, they belong in `gather`.

The caveat that makes this a senior answer rather than a memorised tip: `gather` over ten thousand items opens ten thousand simultaneous connections and will exhaust your database pool or get you rate-limited. Unbounded concurrency is its own outage. The mature version bounds it with a semaphore, or uses `asyncio.TaskGroup` on 3.11+ for structured concurrency and proper cancellation semantics.

### 4.3 Threadpool exhaustion

Section 4.1 made plain `def` look like a free win. It is not — it moves the ceiling rather than removing it. The AnyIO threadpool has a default capacity of 40 threads. Same `/sync-def` endpoint, increasing concurrency:

```
/sync-def   10 concurrent ->  0.54s
/sync-def   40 concurrent ->  0.57s
/sync-def   80 concurrent ->  1.16s
```

Flat to 40, then it doubles. Eighty requests against forty threads is two batches of half a second. The cliff is exactly at the limiter.

The reason this matters more than the arithmetic suggests is the **shape of the failure**. Latency is perfectly flat right up to the limit and then degrades in steps. In production that presents as an application that is fine in testing, fine at normal load, and falls over at a threshold nobody documented — and the metric that would show it is queue depth, which most teams do not graph.

### 4.4 The fire-and-forget task that vanishes

```python
asyncio.create_task(audit_log(f"transfer-{i}"))    # nobody holds a reference
```

The event loop keeps only a **weak** reference to a running task. If nothing else holds a strong reference, the task can be garbage-collected mid-flight and its work silently never completes. The `asyncio` documentation warns about this explicitly.

**Honesty about this one:** I could not make it fail on demand. Five unreferenced tasks, a forced `gc.collect()`, and all five completed normally. That is not evidence it is safe — it is evidence the failure is **nondeterministic**, which is precisely what makes it dangerous. It will not appear in your tests. It will appear once a month in production as an audit record that was never written, and you will not be able to reproduce it.

The fix costs three lines and you should apply it unconditionally:

```python
_background = set()

def spawn(coro):
    task = asyncio.create_task(coro)
    _background.add(task)
    task.add_done_callback(_background.discard)
    return task
```

This is a good thing to have an opinion about in an interview, because "I could not reproduce it, so I apply the fix anyway" is a more senior position than either ignoring it or claiming to have seen it.

---

## 5. The judgment call

### 5.1 Choosing a concurrency model

| | Use when | Because | Real cost |
|---|---|---|---|
| **asyncio** | Many concurrent I/O-bound operations — HTTP, database, queues | Thousands of suspended coroutines cost a few KB each; no thread stacks, no context switches | Colours your whole codebase; one blocking call poisons everything; harder to debug |
| **Threads** | I/O-bound work where the library is synchronous and has no async equivalent | The GIL is released around blocking syscalls, so threads genuinely overlap on I/O | Each thread costs ~8MB of stack; hundreds is a lot; locking bugs |
| **Processes** | CPU-bound work | Each process has its own interpreter and its own GIL — actual parallelism | Startup cost, no shared memory, everything crosses a pickle boundary |
| **Nothing** | Low concurrency, simple service | Sync code is easier to write, read, test and debug | You will be told this is unfashionable. It is still often right. |

The measured evidence for row three is in section 3.5: four processes did in 0.52s what four threads took 1.64s to do.

### 5.2 "Async all the way down" is a real constraint, not a slogan

An async application is only as async as its *most synchronous dependency*. If your HTTP client is `requests`, your database driver is `psycopg2`, or your ORM session is the synchronous SQLAlchemy one, you have an application that pays the full complexity cost of async and delivers sequential throughput — exactly the 5.06s row in section 4.1.

The practical implication when you adopt async is that you are committing to an ecosystem, not a keyword: `httpx` or `aiohttp` instead of `requests`, `asyncpg` instead of `psycopg2`, SQLAlchemy 2.0's `AsyncSession` instead of `Session`, and an audit of every library that touches the network.

If any dependency has no async equivalent — and there is always one — the escape hatch is `asyncio.to_thread(...)` (or `run_in_executor`), which pushes the blocking call onto a thread and gives you back an awaitable. That is the correct, boring answer and it is much better than pretending the call is fast enough not to matter.

### 5.3 When you should not use async at all

Three cases, and being able to argue *against* async is a stronger signal than advocating for it.

If the work is **CPU-bound**, async is not merely useless — it is actively harmful, because it adds complexity while delivering nothing. Section 3.5 is the proof.

If **concurrency is genuinely low** — an internal tool, a scheduled job, a service with a handful of users — the synchronous version is easier to write, easier to test, and easier for the next person. FastAPI with plain `def` endpoints on a threadpool serves real traffic perfectly well, as the 40-concurrent measurement shows.

If the **ecosystem you must use is synchronous**, you will spend more time bridging than you save. Many data-stack libraries, `pandas` prominent among them, have no async story at all.

### 5.4 Diagnosing it in production

Two things worth knowing by name, because "how would you find this" is a standard follow-up.

`asyncio` debug mode — `asyncio.run(main(), debug=True)`, or `PYTHONASYNCIODEBUG=1` — logs a warning whenever a callback occupies the loop for longer than `loop.slow_callback_duration` (100ms by default). That is a direct detector for section 4.1, and it should be on in staging.

Beyond that, the signature of a blocked loop in your metrics is distinctive and worth being able to describe: **latency across unrelated endpoints rising together**, in lockstep, including endpoints that do nothing. Endpoint-level tracing sends you hunting through the slow endpoint. The blocked-loop signature is that the *fast* ones got slow too.

---

## 6. Interview angles

Spoken answers. Say them aloud; do not memorise the words.

### "Explain how async works in Python."

> "When you write `async def`, you're not defining a function that runs in the background — you're defining a function that returns a coroutine object without executing any of its body. That object is essentially a paused stack frame, with its locals and its instruction pointer preserved, waiting for something to drive it.
>
> The thing that drives it is the event loop, which is single-threaded and much simpler than people expect — it's a `while` loop that asks the kernel which sockets are ready, turns those into callbacks, and calls them one at a time. When your coroutine hits an `await` on something that isn't ready yet, the frame suspends and control goes back to the loop, which is then free to run someone else's request. When the socket becomes readable the loop resumes your frame on exactly the line it stopped on.
>
> So the mental model I use is that a coroutine is a bookmark in a function, and the event loop's whole job is choosing which bookmark to pick up next. And the important consequence is that it's cooperative — there's no preemption. The loop can't interrupt a callback that decides to take five seconds, which is why one blocking call anywhere takes down the throughput of the entire process."

### "What's the GIL, and does asyncio solve it?"

> "The GIL is a mutex protecting CPython's internal state, mainly reference counts, which aren't atomic. It means one thread executes Python bytecode at a time. It's released around blocking I/O syscalls and periodically, about every five milliseconds, so CPU-bound threads take turns.
>
> And no, asyncio doesn't solve it — I'd push back a little on the premise, because they're not solutions to the same problem. asyncio is single-threaded, so the GIL is never contended; it's irrelevant rather than defeated. What that means practically is that asyncio buys you nothing at all for CPU-bound work.
>
> I actually measured this recently. Four identical CPU-bound jobs on a four-core machine: one alone takes 0.42 seconds, four across a thread pool take 1.64 — which is 3.9 times, so no parallelism at all, just the serial total. Four across a process pool take 0.52. So the rule I work to is processes for CPU, asyncio for I/O concurrency, and threads for I/O when the library I need is synchronous."

### "Your API is slow under load. Walk me through diagnosing it."

> "The first thing I'd look at is the shape of the slowness rather than the magnitude, because that tells you which class of problem you have. If latency is rising across *unrelated* endpoints together — including ones that barely do anything — that's the signature of a blocked event loop, and I'd go looking for a synchronous call inside an `async def`. That's the most common version of this bug I've seen: someone uses `requests` instead of `httpx`, or a sync database session, and the whole process serialises. asyncio's debug mode catches it directly, since it warns whenever a callback holds the loop for more than a hundred milliseconds.
>
> If instead it's one endpoint and the rest are fine, I'd look for `await` inside a `for` loop, which is correct code that's completely serial — ten sequential awaits at half a second each is five seconds when it should be half. The fix is `gather`, bounded with a semaphore so you don't open ten thousand connections and cause a different outage.
>
> If latency is flat and then steps up sharply at a particular concurrency, that's queueing rather than either of those — for FastAPI that's usually the threadpool that synchronous endpoints run on, which defaults to forty threads. I measured that recently: flat to forty, then it doubles at eighty. And underneath all of it I'd want to rule out the database, because the honest answer is that it's usually the database — which is where I'd want to look at the query plan rather than the application."

### "When would you not use async?"

> "Three cases. If the work is CPU-bound, async adds complexity and delivers nothing, because it's one thread — that needs processes. If concurrency is genuinely low, like an internal tool, the synchronous version is easier to write, test and hand over, and FastAPI with plain `def` endpoints handles real traffic fine on the threadpool. And if the libraries I need are synchronous — a lot of the data stack is, pandas has no async story — I'd spend more time bridging than I'd save.
>
> The framing I'd add is that `async def` isn't the fast option, it's a promise to the runtime that the function won't block. If I can't keep that promise, a plain `def` isn't a fallback, it's the correct answer — FastAPI will offload it to a thread pool. I've measured a case where deleting the word `async` made an endpoint ten times faster, because the async version was blocking the loop and the sync version was safely on a worker thread."

---

## 7. To add to `RECALL.md`

- Calling an `async def` returns a coroutine object; **nothing has executed**
- Coroutines are driven by `.send()`; the return value arrives inside `StopIteration`
- The loop is one thread, cooperative, **cannot preempt** a callback
- `await` suspends the frame and hands control back; the frame resumes on the same line
- GIL: released around blocking syscalls and every ~5ms; **irrelevant under asyncio, not defeated**
- CPU-bound measured: 1 job 0.42s · 4 threads 1.64s (no parallelism) · 4 processes 0.52s
- Blocking call in `async def`: 0.53s → 5.06s for 10 concurrent requests
- `def` endpoint → Starlette threadpool, default **40** threads; cliff measured at 40
- `await` in a loop = serial; `gather` = concurrent; bound it with a semaphore
- `create_task` without a strong reference can be garbage-collected mid-flight
- Blocked-loop signature: **unrelated endpoints slow down together**
- `asyncio.run(..., debug=True)` warns above `slow_callback_duration` (100ms)

---

← [Python index](README.md) · [repo plan](../README.md)
