# asyncio internals

*A function call that executes nothing, one blocking line that cost 10× across every request, and the difference between `gather` and `TaskGroup` measured in cancelled siblings.*

**Level:** L4–L5 · **Prerequisites:** [`01` the GIL](01_the_gil_what_it_protects_and_when_it_lets_go.md), [`01_python/07` generators](../01_python/00_syllabus.md)
**Syllabus:** [`CONC-16`–`CONC-21`](00_syllabus.md) · **Roles:** DE ● FS ●●
**Measurement:** `Measured` — CPython 3.14.6, arm64, 8 cores, macOS 26.5.2. Every figure below came out of a terminal on this machine. **One failure would not reproduce**, and §4.3 reports it as a negative result rather than inventing one.

---

## 1. The thing you already do

This is your stack, more or less exactly:

```python
# Gist: routes.py
@router.get("/accounts/{account_id}/summary")
async def account_summary(account_id: int, session: AsyncSession = Depends(get_session)):
    account = await session.get(Account, account_id)
    transactions = await session.scalars(
        select(Transaction).where(Transaction.account_id == account_id).limit(50)
    )
    rate = await fx_client.get_rate(account.currency)          # external HTTP call
    return summarise(account, transactions, rate)
```

You have written dozens of these. It works, it is fast enough, and `async` is simply the shape FastAPI wants.

Now three variations, all of which look equally reasonable:

```python
rates = [await fx_client.get_rate(c) for c in currencies]      # A
```

```python
rate = requests.get(f"{FX}/rate/{cur}").json()["rate"]         # B — sync client, no await
```

```python
asyncio.create_task(audit_log.write(account_id))               # C — fire and forget
```

Variation A is twenty times slower than it needs to be. Variation B is ten times slower **and it slows down every other request in the process**, including ones that never touch that endpoint. Variation C may silently never run.

None of them raises. None of them fails a test.

---

## 2. The questions you cannot answer about it

**What does calling an `async def` actually do?** Not what `await` does — what the *call* does. There is a precise answer, and it differs from JavaScript in a way that catches people who move between the two.

**Why does one slow endpoint make unrelated endpoints slow?** You may have observed this. The explanation is one sentence about a single thread, and it is the most useful diagnostic signature in this module.

**What is the difference between `gather` and `TaskGroup`?** "TaskGroup is newer" is not an answer. There is a behavioural difference on failure that you can measure by watching which sibling tasks finish.

**And the one that should bother you.** Take your `async def` endpoint and make one blocking call inside it — a `requests.get`, a `time.sleep`, a synchronous database driver. Ten concurrent requests go from **202ms to 2039ms**.

Ten times slower. And not because the blocking call is slow — it takes exactly the same 200ms it always did. The other nine requests are now *waiting in line* for a runtime that was specifically designed so they would not have to.

If you can explain all four, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: a bookmark in a function

A coroutine is a **bookmark in a function**. When execution hits an `await` that cannot complete immediately, the interpreter closes the book at that exact page — keeping every local variable, the position in the loop, everything — and hands the book back to a librarian. The librarian keeps a shelf of paused books and a list of what each is waiting for. When a reply arrives, the librarian finds the matching book, opens it at the bookmark, and resumes the sentence.

Two things follow. Resuming is cheap, because nothing was torn down — no OS thread, no stack unwind, just a frame that was set aside. And there is **exactly one librarian**. If you hand the librarian a job that takes two hundred milliseconds of actual work rather than waiting, every other book on the shelf sits there, unopened.

### 3.2 Calling an `async def` executes nothing at all

Start with the call itself, because the answer surprises people who came from JavaScript.

```python
# Gist: a1_async.py
side_effects = []
async def work():
    side_effects.append("ran")
    return 42

coro = work()
print(f"  after calling work(): {type(coro).__name__}, side_effects={side_effects}")
coro.send(None)
```

```text
  after calling work(): coroutine, side_effects=[]
  ^ JavaScript would have run the body up to the first await. Python ran nothing.
  driving it manually with .send(None) -> StopIteration(42), side_effects=['ran']
```

Calling it produced a **coroutine object and executed zero lines of the body** ([`CONC-ASY-01`](../MEASUREMENTS.md)). The `side_effects` list is empty. The function did not begin.

This is a genuine difference from JavaScript, where calling an `async function` runs the body synchronously up to the first `await` and only then returns a promise. In Python nothing happens until something *drives* the coroutine.

And the last line shows what driving means, stripped of all machinery: `coro.send(None)` advances it, the body runs, and the return value arrives inside `StopIteration`. That is the entire protocol. A coroutine is a generator with a different `await`-flavoured syntax, and the event loop is fundamentally a thing that calls `.send()` on a lot of them.

The practical consequence is the forgotten-`await` bug: writing `work()` without awaiting creates a coroutine, does nothing, and produces a `RuntimeWarning: coroutine 'work' was never awaited` — which is easy to miss in a busy log and means a function you believe you called never ran.

### 3.3 The loop, and what `await` does to a frame

The event loop is a single thread running a queue of callbacks. Its cycle is: run everything currently ready, then ask the OS which of the registered file descriptors have become readable or writable, wake the coroutines waiting on those, and go round again.

When your code hits `await client.get(...)`:

1. The coroutine runs until it needs data that is not there.
2. It **yields control back to the loop**, with its frame preserved — locals, loop position, everything.
3. The loop registers interest in the socket with the OS selector (`kqueue` here, `epoll` on Linux) and moves on to other ready work.
4. The OS reports the socket readable.
5. The loop finds the `Future` associated with that socket, sets its result, and schedules the waiting coroutine.
6. The coroutine resumes **on the same line** and continues with all its locals intact.

The gain is entirely in step 3. One thread serves thousands of connections because waiting costs a registration in a kernel data structure rather than an OS thread with its own stack.

The measured effect of doing this properly:

```text
  20 x sleep(0.1): sequential 2022ms   gather 102ms   (19.9x)
```

Twenty operations of 100ms each: sequentially 2022ms, concurrently 102ms — **19.9×**, essentially perfect ([`CONC-ASY-02`](../MEASUREMENTS.md)). The concurrent version takes as long as the *slowest single* operation, because all twenty waits overlap.

This is variation A from §1. `[await f(c) for c in currencies]` awaits each one to completion before starting the next. It is a sequential loop wearing async syntax.

### 3.4 One blocking call stalls everything

Now the failure that matters most, because it is the one you will actually meet in production.

```python
# Gist: a1_async.py (part 3)
async def good(): await asyncio.sleep(0.2); return "good"
async def bad():  time.sleep(0.2); return "bad"        # blocking!

await asyncio.gather(*(good() for _ in range(10)))
await asyncio.gather(*(bad()  for _ in range(10)))
```

```text
  10 concurrent: await asyncio.sleep 202ms   time.sleep 2039ms  (10.1x)
```

**202ms against 2039ms** ([`CONC-ASY-03`](../MEASUREMENTS.md)). Ten times worse, from changing `await asyncio.sleep` to `time.sleep` — two calls that do the same thing conceptually.

`await asyncio.sleep(0.2)` tells the loop "wake me in 200ms" and yields. Ten of those overlap and the whole batch takes 202ms.

`time.sleep(0.2)` does not yield. It occupies the single thread for 200ms, during which the loop cannot run *anything* — not the other nine coroutines, not a health check, not an unrelated endpoint. Ten of them serialise to 2039ms.

**This is the most important diagnostic signature in the module.** When unrelated endpoints slow down *together*, the loop is blocked. A slow dependency makes the endpoints that use it slow; a blocked loop makes everything slow, and the difference tells you where to look. Any synchronous library call in an `async def` — `requests`, `psycopg2`, `time.sleep`, `open().read()` on a slow disk, a CPU-heavy loop — does this.

The rescue is to move the blocking work to a thread:

```text
  10 concurrent via to_thread: 212ms
```

`asyncio.to_thread` runs the blocking call in a worker thread and awaits the result, restoring 212ms ([`CONC-ASY-04`](../MEASUREMENTS.md)). The loop stays free.

This is also the mechanism behind the counterintuitive result recorded from the v1 material: in FastAPI, a plain `def` endpoint is **automatically** offloaded to a threadpool by Starlette, while an `async def` endpoint is trusted to never block. So declaring an endpoint `async def` and then blocking inside it is *worse* than not declaring it async at all — `async def` is not "the fast option," it is **a promise you make to the runtime** that you will yield.

### 3.5 `gather` versus `TaskGroup`: what happens to the siblings

Both run coroutines concurrently. They differ on failure, and the difference is visible.

```python
# Gist: a2_tasks.py
async def ok(n): await asyncio.sleep(0.3); print(f"    sibling {n} COMPLETED"); return n
async def boom(): await asyncio.sleep(0.05); raise ValueError("boom")

# gather
try: await asyncio.gather(boom(), ok(1), ok(2))
except ValueError as e: print(f"    caught {e!r}")

# TaskGroup
async with asyncio.TaskGroup() as tg:
    tg.create_task(boom()); tg.create_task(ok(3)); tg.create_task(ok(4))
```

```text
  asyncio.gather:
    caught ValueError('boom')
    sibling 1 COMPLETED
    sibling 2 COMPLETED
  ^ siblings kept running after the failure

  asyncio.TaskGroup:
    caught ExceptionGroup (ValueError('boom'),)
  ^ siblings were CANCELLED — nothing printed COMPLETED
```

There it is ([`CONC-ASY-05`](../MEASUREMENTS.md)). With `gather`, the exception propagated immediately **and siblings 1 and 2 carried on and completed** — after the error had already been handled, in code that has moved on. With `TaskGroup`, the siblings were cancelled and never printed.

That difference is the whole argument for **structured concurrency**. `gather`'s behaviour means a request handler can return an error response while three tasks it started are still running, still holding connections, still writing to a database. Nobody is waiting for them and nobody will notice if they fail. `TaskGroup` makes task lifetime lexically scoped: **no task outlives the block that created it**, so the failure of one cancels the rest and the block does not exit until all children are done.

`TaskGroup` raises an `ExceptionGroup`, which is why the handler is `except*` — several children can fail simultaneously and all of their exceptions are preserved rather than only the first.

This is the trio "nursery" idea, arrived in the standard library in 3.11. Prefer `TaskGroup` for new code; `gather(return_exceptions=True)` remains useful when you genuinely want every result regardless of individual failures.

### 3.6 Bounding concurrency, and cancellation

Unbounded concurrency is its own failure. `gather` over ten thousand items opens ten thousand connections, and you will exhaust file descriptors or be rate-limited.

```python
# Gist: a2_tasks.py (part 3)
sem = asyncio.Semaphore(5)
async def limited():
    async with sem:
        ...
await asyncio.gather(*(limited() for _ in range(50)))
```

```text
  50 tasks, Semaphore(5): peak in-flight=5, elapsed 514ms
```

Peak in-flight never exceeded 5 ([`CONC-ASY-06`](../MEASUREMENTS.md)), and 50 tasks of 50ms took 514ms — ten batches of five. That is the shape you want: concurrent, but bounded to something the downstream service has agreed to.

Cancellation is the other half of control, and it is cooperative:

```text
  TimeoutError raised; inner task saw CancelledError: True
```

`asyncio.timeout` cancels the inner task, which observes a `CancelledError` **raised at its current await point** ([`CONC-ASY-07`](../MEASUREMENTS.md)). Two consequences follow. A coroutine that never awaits cannot be cancelled, because there is no point at which to deliver the exception. And a `try/except Exception` that swallows everything will swallow cancellation too — `CancelledError` inherits from `BaseException` in modern Python specifically to make that harder, and if you catch it deliberately you must re-raise.

---

## 4. Break it on purpose

### 4.1 The async loop that was sequential

```python
# Gist: sequential_await.py
rates = [await fx_client.get_rate(c) for c in currencies]
```

```text
  20 x sleep(0.1): sequential 2022ms   gather 102ms   (19.9x)
```

Twenty times slower than necessary, in code that is fully `async`, passes review, and uses `await` correctly on every line.

`await` means "wait here for this to finish." A loop of awaits is a sequence of waits. The async machinery is present and buying nothing, which makes this the async equivalent of the pointless thread pool in [module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md).

The fix is `gather` or a `TaskGroup`, plus a semaphore if the count is large. The cost of fixing it is that twenty requests now hit the downstream service simultaneously, which is exactly why the bound matters.

### 4.2 The blocking call that slowed down the whole service

```python
# Gist: blocking_endpoint.py
@router.get("/rate/{currency}")
async def rate(currency: str):
    return requests.get(f"{FX}/rate/{currency}").json()      # sync client in async def
```

```text
  10 concurrent: await asyncio.sleep 202ms   time.sleep 2039ms  (10.1x)
```

The endpoint itself is only mildly slow. What makes this a serious incident is that **every other endpoint in the process degrades at the same time** — the health check times out, the metrics endpoint hangs, and an operator concludes the whole service is failing rather than one route.

The signature to memorise: *unrelated endpoints slowing together means a blocked loop, not a slow dependency.*

Three fixes, in order of preference. Use an async client — `httpx.AsyncClient` instead of `requests`, `asyncpg` instead of `psycopg2`. If no async client exists, wrap the call in `asyncio.to_thread`, measured back at 212ms. And if the blocking thing is CPU-bound rather than I/O, a thread will not help under the GIL — that needs a process pool, per [module 03](03_multiprocessing_and_the_process_boundary.md).

**Run this one yourself.** Start a FastAPI app with one blocking endpoint and hit an *unrelated* endpoint while it runs. Watching a route you did not touch time out is what makes the single-thread model concrete.

### 4.3 The orphaned task — a negative result

`asyncio.create_task` schedules a coroutine, but the loop keeps only a **weak** reference. The documented hazard is that a task with no strong reference elsewhere can be garbage-collected before it finishes.

I tried to reproduce it:

```python
# Gist: a2_tasks.py (part 2)
done = []
async def bg(): await asyncio.sleep(0.05); done.append(1)
for _ in range(5): asyncio.create_task(bg())      # no reference kept
gc.collect()
await asyncio.sleep(0.3)
```

```text
  5 unreferenced tasks, forced gc: 5/5 completed
  -> could NOT force the failure; it is nondeterministic, not absent
```

**All five completed.** Five unreferenced tasks and a forced collection, and nothing was lost ([`CONC-ASY-08`](../MEASUREMENTS.md)).

I am reporting that rather than manufacturing a failure, and the honest reading matters: **this is not evidence the pattern is safe.** It is evidence the failure is *nondeterministic*, which is precisely what makes it dangerous. A bug that appears under memory pressure, at high task counts, or on a different interpreter — and never in testing — is worse than one that fails immediately.

The documented remedy costs nothing, so take it regardless:

```python
# Gist: keep_reference.py
_background: set[asyncio.Task] = set()

def spawn(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _background.add(task)
    task.add_done_callback(_background.discard)
    return task
```

The stronger answer is a `TaskGroup`, which owns its children by construction, so the question of who holds the reference does not arise.

### 4.4 The exception nobody saw

```python
# Gist: swallowed.py
async def audit(account_id: int):
    await write_audit_row(account_id)          # raises when the DB is down

asyncio.create_task(audit(account_id))          # nobody awaits this
return {"ok": True}
```

The handler returns 200. The audit row was never written. The exception is stored on the task object, and because nothing ever awaits the task, nothing retrieves it — you get a `Task exception was never retrieved` message at some later point, usually at garbage collection, detached from the request that caused it.

In a banking context that is a compliance failure that reports success.

`gather` has a related trap: `return_exceptions=True` puts exceptions in the results list instead of raising, so code that does not inspect each result treats an exception object as data. Both are avoided by `TaskGroup`, where an unhandled child exception propagates out of the block as an `ExceptionGroup` and cannot be ignored.

---

## 5. The judgment call

### The options, honestly costed

| Approach | Use when | Because | Real cost |
|---|---|---|---|
| **Sequential `await`** | Each step genuinely needs the previous result | Simplest; correct by construction | **Measured 19.9× slower** when the steps were independent |
| **`gather`** | Independent operations, all results wanted | One line; returns results in order | Siblings **keep running after a failure**; unbounded by default |
| **`TaskGroup`** | Almost everything else | Structured — failure cancels siblings, no task outlives the block | Needs 3.11+; `except*` and `ExceptionGroup` are unfamiliar |
| **`Semaphore` bound** | Fanning out to a service with limits | Caps in-flight work; **measured peak exactly 5 of 50** | Adds latency by design — that is the point |
| **`asyncio.to_thread`** | A blocking **I/O** call with no async client | Frees the loop; **restored 2039ms → 212ms** | A real OS thread per call; useless for CPU-bound work |
| **Process pool** | CPU-bound work inside an async service | The GIL makes threads useless here | Pickling and startup, per [module 03](03_multiprocessing_and_the_process_boundary.md) |
| **Plain `def` endpoint** | The handler is unavoidably synchronous | Starlette offloads it to a threadpool automatically | Pool is finite (default 40); it is a fallback, not a design |

### When you would not do this

**Do not write `async def` unless you will actually yield.** This is the rule I would defend hardest, because §3.4 shows the counterintuitive consequence: a plain `def` endpoint that blocks is handled *better* by FastAPI than an `async def` one that blocks, because the framework can offload what it knows is synchronous. `async def` is a promise to the runtime. Making it and then breaking it is worse than never making it.

**Do not use asyncio for CPU-bound work.** It is concurrency for *waiting*. A coroutine doing arithmetic holds the single thread exactly as firmly as `time.sleep` does, and no amount of `async` syntax changes that. That is a process pool.

**Do not `gather` an unbounded collection.** Ten thousand coroutines is ten thousand simultaneous connections. The semaphore is not optional at scale, and the correct bound comes from what the downstream service will tolerate rather than from what your machine can open.

**Do not adopt asyncio for a handful of concurrent operations.** It is all-or-nothing: one synchronous call anywhere in the stack undermines it, so the whole call chain — driver, client, middleware — must be async. For eight parallel HTTP calls a `ThreadPoolExecutor` is simpler, has no colouring problem, and [module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md) measured it at 7.97× on I/O. Asyncio earns its complexity in the thousands, not the dozens.

**Prefer `TaskGroup` to `gather` in new code.** §3.5 measured the difference in cancelled siblings, and orphaned work holding database connections after its request has errored is a real production problem rather than a theoretical one.

---

## 6. Interview angles

**"What does calling an async function do?"**

> It returns a coroutine object and executes nothing — not one line of the body. I checked this because I wanted to be sure rather than assume: I put a side effect as the very first statement, called the function, and the side-effect list was still empty. The body only runs when something drives the coroutine, and if you strip away the machinery, driving it is literally `coro.send(None)` — it advances, runs, and the return value comes back inside `StopIteration`. Coroutines are generators with different syntax, and the event loop is fundamentally a thing that calls `send` on a lot of them. The reason I'd volunteer this is that it's a real difference from JavaScript, where calling an `async function` runs the body synchronously up to the first `await` and *then* hands you a promise. Python runs nothing. That's why a forgotten `await` in Python gives you a `RuntimeWarning: coroutine was never awaited` and a function that simply didn't happen — which is easy to lose in a busy log.

**"One endpoint got slow and now everything is slow. Where do you look?"**

> That specific signature — *unrelated* endpoints degrading together — tells me the event loop is blocked, not that a dependency is slow. If a dependency were slow, only the routes using it would suffer. Everything suffering at once means something is occupying the single thread. So I'd go looking for a synchronous call inside an `async def`: `requests` instead of `httpx`, `psycopg2` instead of `asyncpg`, a `time.sleep`, or a CPU-heavy loop. I measured how bad this gets — ten concurrent operations went from 202 milliseconds with `await asyncio.sleep` to 2039 milliseconds with `time.sleep`, so about ten times worse, and the blocking call itself hadn't got any slower. The other nine were just queued behind it. The fix in order of preference is an async client, or `asyncio.to_thread` if none exists — that brought it back to 212ms in my test — and if the blocking thing is CPU-bound rather than I/O then a thread won't help under the GIL and it needs a process pool. The bit I find genuinely counterintuitive and worth saying out loud is that in FastAPI a plain `def` endpoint that blocks is handled *better* than an `async def` one that blocks, because Starlette knows to offload a sync function to a threadpool. `async def` is a promise you make to the runtime that you'll yield, and breaking it is worse than never making it.

**"`gather` or `TaskGroup`?"**

> `TaskGroup` for new code, and the reason is what happens to the siblings when one task fails. I set this up to watch it: one task that raises quickly and two slow ones that print when they complete. With `gather`, the exception propagated, I caught it — and then both siblings carried on and printed COMPLETED afterwards, after the error had already been handled and the code had moved on. With `TaskGroup`, the siblings were cancelled and never printed. That difference is the whole case for structured concurrency. `gather`'s behaviour means a request handler can return a 500 while three tasks it started are still running, still holding database connections, and nobody's waiting on them or will notice if they fail. `TaskGroup` makes lifetime lexical — no task outlives the block that created it. The practical wrinkle is that it raises an `ExceptionGroup` and you handle it with `except*`, because multiple children can fail at once and it preserves all of them rather than just the first. I'd still use `gather` with `return_exceptions=True` when I genuinely want every result regardless of individual failures, but I'd treat that as the special case now.

**"You need to call an API for ten thousand records. How do you write it?"**

> Not with a bare `gather`, and not with `await` in a loop either — those are the two failure modes and they're opposite. A loop of awaits is sequential; I measured twenty operations at 2022ms that way versus 102ms concurrent, so about twenty times slower with all the async machinery present and buying nothing. But an unbounded `gather` over ten thousand items opens ten thousand connections, and you'll exhaust file descriptors or get rate-limited, and you'll have done it to someone else's service. So: a semaphore sized to whatever the downstream will actually tolerate, and a `TaskGroup` around it. I tested the bound holds — fifty tasks through a `Semaphore(5)` never exceeded five in flight and took 514ms, which is ten neat batches. I'd also want a timeout per call so one hung request can't pin a slot forever, and I'd remember that cancellation is cooperative — `asyncio.timeout` delivers `CancelledError` at the current await point, so a coroutine that never awaits can't be cancelled, and a broad `except Exception` that swallows everything will swallow cancellation too. One honest caveat: my own concurrency work has been I/O concurrency inside FastAPI, and on the pipeline side Beam and its runner owned the parallelism rather than me. So I've built these cases deliberately to understand the mechanism, and I'd be validating my choices with measurements rather than from having tuned a ten-thousand-task fan-out in production.

---

## 7. To add to `RECALL.md`

- Calling an `async def` returns a **coroutine object and executes nothing** — measured with a side effect on line 1, list stayed empty
- **JS runs the body to the first `await`; Python runs nothing.** The clean cross-language contrast
- Driving it is `coro.send(None)`; the return value arrives inside **`StopIteration`**. Coroutines are generators with different syntax
- Forgotten `await` → `RuntimeWarning: coroutine was never awaited`, and the function silently never ran
- `await` yields to the loop with the **frame preserved**; it resumes on the same line with locals intact
- Measured: 20 × 100ms — **sequential 2022ms vs gather 102ms (19.9×)**. `await` in a loop is a sequential loop in async clothing
- **Measured: blocking in `async def` — 202ms → 2039ms (10.1×)** for 10 concurrent. `asyncio.to_thread` restored **212ms**
- **The diagnostic signature: unrelated endpoints slowing *together* = blocked loop**, not a slow dependency
- FastAPI offloads plain `def` to a threadpool (default 40). **`async def` is a promise to yield** — breaking it is worse than not making it
- Measured: on failure `gather` let **siblings run to completion**; `TaskGroup` **cancelled them**
- `TaskGroup` raises **`ExceptionGroup`**, handled with `except*` — preserves all simultaneous failures
- Measured: 50 tasks through `Semaphore(5)` → **peak in-flight exactly 5**, 514ms
- Cancellation is **cooperative** — `CancelledError` is delivered at the current await point; a coroutine that never awaits cannot be cancelled
- `CancelledError` inherits **`BaseException`**; a broad `except Exception` swallowing it breaks cancellation
- **Negative result:** 5 unreferenced `create_task`s plus forced `gc.collect()` → **5/5 completed**. Not proof it is safe — proof the failure is **nondeterministic**
- Keep a strong reference set with `add_done_callback(discard)`, or use `TaskGroup` which owns its children
- asyncio is concurrency for **waiting**. CPU-bound work holds the single thread exactly as `time.sleep` does

---

← [Concurrency syllabus](00_syllabus.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
