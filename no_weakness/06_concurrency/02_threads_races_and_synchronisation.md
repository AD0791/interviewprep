# Threads, races, and synchronisation

*A deadlock reproduced in twelve lines, the lock that deadlocks against itself, and why the best fix is usually not a lock.*

**Level:** L4 · **Prerequisites:** [`01` the GIL](01_the_gil_what_it_protects_and_when_it_lets_go.md)
**Syllabus:** [`CONC-06`–`CONC-10`](00_knowledge_graph.md) · **Roles:** DE ● FS ●
**Measurement:** `Measured` — CPython 3.14.6, arm64, 8 cores, macOS 26.5.2. Every output below came out of a terminal on this machine, including a genuine deadlock and its fix.

---

## 1. The thing you already do

A background worker that pulls jobs and updates a shared counter, which is roughly every batch process you have written:

```python
# Gist: worker.py
import threading

processed = 0
failed = 0

def worker(jobs: list[Job]):
    global processed, failed
    for job in jobs:
        try:
            handle(job)
            processed += 1
        except Exception:
            failed += 1

threads = [threading.Thread(target=worker, args=(chunk,)) for chunk in chunks]
for t in threads: t.start()
for t in threads: t.join()

print(f"processed {processed}, failed {failed}")
```

And somewhere else, a transfer between two accounts that each need locking:

```python
# Gist: transfer.py
def transfer(src: Account, dst: Account, amount: Decimal):
    with src.lock:
        with dst.lock:
            src.balance -= amount
            dst.balance += amount
```

Both look reasonable. The first has a bug that will not show up in testing and may not show up in production either — which is worse. The second has a bug that will hang your service completely, and it will do so only when two transfers happen to run in opposite directions at the same moment.

---

## 2. The questions you cannot answer about it

**Is that counter safe?** [Module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md) measured `+=` losing zero updates across sixteen threads — and then losing 59% once a property was involved. So "is it safe" now has a genuinely complicated answer, and you need to be able to say which case you are in.

**What is the difference between `Lock` and `RLock`?** "RLock can be acquired twice" is the memorised answer. By whom, and what happens if a plain `Lock` is acquired twice by the same thread? The answer to the second half is the more useful one.

**Can you reproduce a deadlock on demand?** Not describe one — reproduce it, in a few lines, and then fix it. Being able to do that at a whiteboard is a materially different signal from reciting the four Coffman conditions.

**And the one that should bother you.** Everyone reaches for a lock. But a lock has a measured cost, and there is a standard-library object that solves most producer-consumer problems with **no explicit locking at all**, gives you back-pressure for free, and makes shutdown expressible. Most people who can explain mutexes have never reached for it.

If you can answer all four, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: the single-key bathroom

A lock is a bathroom with one key hanging outside. You take the key, you go in, you come out, you hang the key back. Anyone arriving while the key is gone waits.

Two properties of this arrangement explain almost everything that follows. If you go in and come out without hanging the key back, nobody ever gets in again — that is a lock leaked by an exception path, and it is why `with` matters. And if there are two bathrooms and two people each holding the other's key while waiting for the one they lack, nobody moves, ever — that is deadlock, and it needs no bug in either person's logic, only the two of them taking the keys in different orders.

### 3.2 What a race actually is

A race condition is any situation where the result depends on the interleaving of operations that you did not control. The specific case worth naming is the **lost update**: read a value, compute from it, write it back — and have another thread complete the same sequence between your read and your write. Your write is based on a value that is now stale, and their update vanishes.

The critical section is not the write. It is the **whole read-modify-write sequence**, and the mistake people make is locking only the assignment.

Module 01 established the surprising empirical shape of this on CPython 3.14. A bare `+=` on a global, an attribute, or a dict item lost nothing across four hundred thousand increments, because no eval-breaker checkpoint falls inside the instruction sequence. The moment a Python-level function call enters that sequence — most commonly a `@property` — 59% of updates disappeared.

Which means the practical rule cannot be "`+=` is safe." It has to be: **you cannot tell by looking.** `account.balance += 1` is safe or catastrophic depending on whether `balance` is a plain attribute or a property, and the two are syntactically identical at the call site. Anything you cannot determine by reading the line in front of you is something you should protect explicitly.

### 3.3 What a lock costs

```python
# Gist: t2_lockcost.py
lk = threading.Lock(); n = 0
def no_lock():
    global n; n += 1
def with_lock():
    global n
    with lk: n += 1
```

```text
  2M increments: unlocked 0.077s   locked 0.201s   (2.6x)
```

**2.6× on the uncontended path** ([`CONC-THR-01`](../MEASUREMENTS.md)) — and that is the *cheap* case, with a single thread and no waiting at all. Under contention the cost is unbounded, because threads serialise on the lock and any parallelism you were pursuing evaporates.

This is the number that should shape your instinct. A lock is not free insurance you sprinkle over shared state; it is a serialisation point you are inserting deliberately. Locking a hot counter in eight threads means eight threads taking turns, which is the performance profile you were trying to escape.

### 3.4 The lock family, and what each is for

**`Lock`** is the primitive: acquired or not, and **the thread that acquired it is not tracked**. That last part is the source of §4.2's failure.

**`RLock`** is re-entrant *by the owning thread*, keeping an owner and a recursion count. It exists for the case where a locked method calls another locked method on the same object.

**`Semaphore`** permits N holders rather than one — the right tool for bounding concurrent access to a resource with a capacity, like a connection pool or an API rate limit.

**`Event`** is a one-to-many signal: threads wait, one sets, all proceed. It carries no data and does not reset itself.

**`Condition`** is for waiting on a state change you cannot poll, pairing a lock with a wait/notify protocol. It is the most error-prone of the five, and needing one is often a sign that a queue would serve better.

### 3.5 The deadlock, reproduced

Four conditions must hold simultaneously for deadlock: mutual exclusion, hold-and-wait, no preemption, and circular wait. Only the last is usually under your control, which is why it is the one to attack.

```python
# Gist: t1_deadlock.py
lock_a, lock_b = threading.Lock(), threading.Lock()

def transfer_ab():
    with lock_a:
        time.sleep(0.05)
        got = lock_b.acquire(timeout=1.5)
        print(f"    thread AB: acquired B? {got}")
        if got: lock_b.release()

def transfer_ba():
    with lock_b:                      # opposite order
        time.sleep(0.05)
        got = lock_a.acquire(timeout=1.5)
        print(f"    thread BA: acquired A? {got}")
        if got: lock_a.release()
```

```text
    thread AB: acquired B? False
    thread BA: acquired A? False
  -> both timed out: circular wait. Neither could proceed.
```

A genuine deadlock in twelve lines ([`CONC-THR-02`](../MEASUREMENTS.md)). Both threads held one lock and waited forever for the other. Without the timeouts this program hangs permanently, and in a service it means the request never returns and the connection is never released.

Note what is *not* wrong here. Neither function has a bug. Each acquires two locks and releases them properly, uses `with` for the first, and does nothing exotic. **The bug exists only in the relationship between them** — which is why deadlocks survive code review, since reviewing either function alone reveals nothing.

The fix attacks circular wait by imposing a consistent global order:

```text
=== Same code, CONSISTENT ordering (always a before b) ===
  both succeeded: [True, True]  -> no cycle possible
```

If every thread acquires locks in the same order, a cycle cannot form — the thread holding the lower-ordered lock is always the one that can proceed. For the `transfer` example in §1 that means ordering by account id, so `transfer(A, B)` and `transfer(B, A)` both lock the lower id first.

Timeouts are a safety net rather than a fix. They convert a permanent hang into an error you can log and retry, which is genuinely valuable in production — but the circular wait is still there, and under load you will see the errors.

### 3.6 The lock that deadlocks against itself

```python
# Gist: t1_deadlock.py (part 3)
lk = threading.Lock()
lk.acquire()
print(lk.acquire(timeout=0.5))     # same thread, again

rl = threading.RLock()
rl.acquire()
print(rl.acquire(timeout=0.5))     # same thread, again
```

```text
  Lock re-acquire by same thread (timeout 0.5): False  <- SELF-DEADLOCK
  RLock re-acquire by same thread:              True  <- allowed
```

A plain `Lock` does not track its owner, so a thread that already holds it and tries again **blocks waiting for itself** ([`CONC-THR-03`](../MEASUREMENTS.md)). Without the timeout that is a permanent hang caused by a single thread.

This happens more easily than it sounds. A locked public method calls another locked public method on the same object — perfectly natural refactoring — and the service hangs. `RLock` fixes it by counting recursion depth for the owning thread.

But reaching for `RLock` is worth a moment's thought, because needing re-entrancy usually means the locking is at the wrong granularity. The tidier design is a private unlocked implementation and thin public methods that acquire the lock once:

```python
# Gist: no_reentrancy.py
class Ledger:
    def __init__(self): self._lock = threading.Lock()
    def _post_unlocked(self, tx): ...            # assumes lock held
    def post(self, tx):
        with self._lock: self._post_unlocked(tx)
    def post_batch(self, txs):
        with self._lock:
            for tx in txs: self._post_unlocked(tx)   # no re-acquire
```

### 3.7 The answer that avoids locks entirely

Most shared state between threads is a producer-consumer pipeline, and for that, `queue.Queue` is a better answer than any arrangement of locks.

```python
# Gist: pipeline.py
import queue, threading

jobs: queue.Queue = queue.Queue(maxsize=100)
results: queue.Queue = queue.Queue()
SENTINEL = object()

def worker():
    while True:
        job = jobs.get()
        if job is SENTINEL:
            jobs.task_done()
            break
        try:
            results.put(handle(job))
        finally:
            jobs.task_done()

threads = [threading.Thread(target=worker) for _ in range(8)]
for t in threads: t.start()
for job in all_jobs: jobs.put(job)          # blocks when 100 are queued
for _ in threads: jobs.put(SENTINEL)
for t in threads: t.join()
```

There is no lock in that code and no shared counter, yet it is correct. Three things are being bought.

**The synchronisation moved into a tested primitive.** `Queue` handles its own locking internally, and it has been exercised far more thoroughly than a lock you wrote this afternoon.

**Back-pressure comes free.** `maxsize` means a fast producer blocks rather than growing an unbounded list until the process is killed:

```text
  Queue(maxsize=10) gives back-pressure: full=False after 10 puts -> True | put would now block
```

That is the property most hand-rolled pipelines lack ([`CONC-THR-04`](../MEASUREMENTS.md)), and it is why a "fast" producer feeding a slow consumer is a memory leak in disguise.

**Shutdown becomes expressible.** A sentinel per worker terminates them deterministically, which is otherwise surprisingly fiddly to get right.

The underlying principle is Go's, and it applies cleanly here: **do not communicate by sharing memory; share memory by communicating.** When you find yourself designing a lock protocol, ask first whether the threads could pass messages instead.

### 3.8 Thread-local state, and the async trap

`threading.local()` gives each thread its own copy of an attribute — the standard answer for per-thread database connections or request context.

It has one failure mode worth knowing, and it is not obvious: **it does not work under `asyncio`.** Many coroutines share a single thread, so they all see the same thread-local storage and overwrite each other's "per-request" context.

The async-safe equivalent is `contextvars.ContextVar`, which is scoped to the logical execution context rather than the OS thread and follows a coroutine across suspension points. Any request-scoped context in an async framework — request ids, the current user, tracing spans — is built on `contextvars` for exactly this reason.

---

## 4. Break it on purpose

### 4.1 The counter that lost 59% of its updates

The failure from module 01, restated because it is this module's central case.

```text
  obj.balance += 1        lost        0 of 400,000  (0.00%)
  obj.prop_balance += 1   lost  236,574 of 400,000  (59.14%)
```

Same syntax, same threads, same interval. The property version lost 236,574 deposits.

The critical section is the read-modify-write, and the property inserted a Python function call inside it, which is an eval-breaker checkpoint. The correct fix locks the whole sequence:

```python
# Gist: fixed_counter.py
class Account:
    def __init__(self):
        self._p = 0
        self._lock = threading.Lock()
    def deposit(self, amount):
        with self._lock:                  # covers read AND write
            self._p += amount
```

Note what is being locked. Putting the lock inside the property setter would not help, because the read happened before the setter was ever called. **A lock around only the write is a lock around the wrong thing** — a mistake that produces code which looks synchronised and is not.

The cost is 2.6× on the uncontended path and serialisation under contention. Which is the argument for §3.7: if this counter is hot, do not share it. Give each thread its own and sum at the end.

### 4.2 The lock released by the wrong thread

`Lock` does not track ownership, and that has a second consequence beyond §3.6.

```python
# Gist: wrong_release.py
lk = threading.Lock()
lk.acquire()

def releaser():
    lk.release()          # a thread that never acquired it

threading.Thread(target=releaser).start()
time.sleep(0.1)
print("lock is now free:", not lk.locked())
```

```text
lock is now free: True
```

A thread that never acquired the lock released it, and Python permitted it silently. The critical section is now unprotected while the original holder still believes it holds the lock.

This is why acquiring in one function and releasing in another is a design to avoid, and why `with` is not merely stylistic — it guarantees the release happens on the same frame that acquired, including on the exception path. `RLock` does raise `RuntimeError` for a foreign release, which is a second, smaller reason to prefer it when locks cross function boundaries.

### 4.3 The unbounded queue that ate the memory

The failure hiding in every hand-rolled pipeline.

```python
# Gist: unbounded.py
results = []                      # or queue.Queue() with no maxsize
def producer():
    for row in read_10_million_rows():
        results.append(transform(row))     # never blocks
```

Nothing raises. The producer reads from a database cursor at tens of thousands of rows a second; the consumer writes to an API at hundreds. The gap accumulates in memory until the process is killed by the OOM killer — and the traceback, if you get one at all, points at whatever happened to allocate last rather than at the producer.

`queue.Queue(maxsize=N)` fixes this by making `put` block when full, which propagates the slowness backwards to the producer where it belongs. **A pipeline without back-pressure is not a pipeline, it is a memory leak with extra steps.**

The cost of back-pressure is that a slow consumer now visibly slows the producer, which some people experience as a regression. It is not — it is the system telling you the truth about its throughput instead of hiding it in RAM.

**Run this one yourself**, with a `time.sleep` in the consumer and a memory monitor open. Watching RSS climb steadily while the program reports no errors is the fastest way to internalise why `maxsize` is not optional.

---

## 5. The judgment call

### The options, honestly costed

| Approach | Use when | Because | Real cost |
|---|---|---|---|
| **No sharing** | Each thread can own its data and results combine at the end | No locks, no races, nothing to reason about | Needs a combinable result; not always possible |
| **`queue.Queue`** | Producer-consumer of any shape | Synchronisation is inside a tested primitive; **back-pressure via `maxsize`**; clean shutdown via sentinels | Items are copied by reference — the objects are still shared |
| **`Lock`** | A genuine read-modify-write on shared state | Simplest correct protection | **Measured 2.6× uncontended**; serialises under contention; self-deadlocks if re-acquired |
| **`RLock`** | Locked methods call other locked methods | Re-entrant for the owner; raises on foreign release | Slightly slower; usually a sign the granularity is wrong |
| **`Semaphore`** | Bounding concurrent access to a capacity-limited resource | Expresses "at most N" directly | Does not protect data, only limits concurrency |
| **`contextvars`** | Per-request context in async code | Follows a coroutine across `await` | `threading.local` is the wrong tool here and fails silently |
| **Atomic-by-C-call** | Simple `append`/`popleft` on a built-in | Single C call, no checkpoint inside | **By accident, not contract** — breaks on free-threading and on refactors |

### When you would not do this

**Do not reach for a lock first.** The instinct on seeing shared mutable state should be to remove the sharing, not to protect it. Per-thread accumulators summed at the end have no critical section at all, and a `queue.Queue` moves the problem into code that is already correct. Locks are the answer when threads genuinely must mutate the same object, which is rarer than it appears.

**Do not lock at the wrong granularity.** §4.1's mistake — locking the write and not the read — produces code that passes review and does not work. The critical section is the whole sequence whose intermediate states are invalid, and identifying it is the actual skill; adding the `with` is trivial.

**Do not use timeouts as a deadlock fix.** They are a good safety net and a bad solution. A timeout converts a hang into an error, which is genuinely better for availability, but the circular wait remains and under load you will simply see errors instead. Fix the ordering.

**Do not use `threading.local` in async code.** It will appear to work in development with one request at a time and produce cross-request data bleed under concurrency — arguably the worst failure mode in this module, because in a banking context it means one customer seeing another's context. `contextvars` is the correct tool and the fix is mechanical.

**Do not assume built-in atomicity survives your next refactor.** Module 01 measured a plain attribute losing nothing and the same attribute-turned-property losing 59%. If correctness depends on atomicity, make it explicit — the free-threaded build is coming and it removes the accident entirely.

---

## 6. Interview angles

**"How do you prevent deadlock?"**

> The honest short answer is: impose a consistent lock ordering. Four conditions have to hold at once — mutual exclusion, hold-and-wait, no preemption, and circular wait — and circular wait is the only one you usually control, so that's the one to attack. I reproduced this to make sure I could rather than just reciting it: two locks, two threads, one taking A then B and the other taking B then A, with a sleep in between to make the window reliable. Both timed out, neither could proceed. Then the same code with both threads taking A before B — both succeeded, because a cycle can't form when everyone agrees on the order. For something like a transfer between two accounts, that means locking by account id, so `transfer(A, B)` and `transfer(B, A)` both grab the lower id first. The thing I'd emphasise is that neither of those functions had a bug in isolation. Each acquired and released properly. The bug only existed in the relationship between them, which is exactly why deadlocks get through code review — you review one function and there's nothing to see. And I'd say explicitly that timeouts aren't the fix. They turn a permanent hang into an error you can retry, which is worth having in production, but the circular wait is still there and under load you just get errors instead of hangs.

**"What's the difference between `Lock` and `RLock`?"**

> `RLock` is re-entrant by the owning thread — it keeps an owner and a recursion count, so the same thread can acquire it repeatedly and has to release it the same number of times. The more interesting half is what happens with a plain `Lock`, which doesn't track ownership at all: a thread that already holds it and acquires it again **blocks waiting for itself**. I tested it and got exactly that — a half-second timeout returning False. Without the timeout that's a permanent hang caused by one thread. And it happens really easily; a locked public method calling another locked public method on the same object, which is an entirely natural thing to write. The other consequence of no ownership tracking is that any thread can release a `Lock`, even one that never acquired it — I checked, and Python allows it silently, which leaves your critical section unprotected while the real holder thinks it's still safe. `RLock` at least raises on a foreign release. But I'd add that reaching for `RLock` is often a smell. If you need re-entrancy, usually the locking is at the wrong granularity, and the cleaner fix is a private unlocked implementation with thin public wrappers that take the lock exactly once.

**"You've got a producer-consumer pipeline. How would you build it?"**

> With `queue.Queue`, and specifically with a `maxsize`. The reason I wouldn't hand-roll it with a list and a lock is that the queue gives me three things I'd otherwise have to get right myself. The synchronisation is inside a primitive that's far better tested than anything I'd write. Shutdown becomes expressible — a sentinel per worker terminates them deterministically, which is fiddlier than it sounds otherwise. And most importantly, `maxsize` gives back-pressure: a fast producer blocks instead of growing an unbounded list. That last one is the failure I'd actually be designing against, because a producer reading rows from a cursor at tens of thousands a second feeding a consumer that writes to an API at hundreds isn't a slow pipeline, it's a memory leak — RSS climbs until the OOM killer arrives and nothing ever raises. People sometimes push back that back-pressure makes the producer slower, and I'd argue it's just the system telling you the truth about throughput rather than hiding it in RAM. The general principle I'd cite is the Go one — don't communicate by sharing memory, share memory by communicating. When I find myself designing a lock protocol, that's my cue to ask whether the threads could pass messages instead.

**"Your service intermittently returns another user's data. Where do you look?"**

> Cross-request data bleed points at shared mutable state that should be per-request, and in an async service the specific thing I'd check first is `threading.local`. It's the standard answer for per-thread context — connections, current user, request id — and it's wrong under asyncio, because many coroutines share one thread, so they all see the same thread-local storage and overwrite each other. What makes it nasty is that it works perfectly in development when you're handling one request at a time, and only bleeds under concurrency. The fix is `contextvars.ContextVar`, which is scoped to the logical execution context and follows a coroutine across `await` points — that's what request-scoped context in async frameworks is built on. After that I'd look for module-level mutable defaults and any cache keyed on something that isn't actually unique per request. I should be straight that my concurrency experience is the I/O side inside FastAPI rather than running threaded workers in production, so I've built these cases deliberately to understand them rather than having debugged this exact incident at three in the morning. But I'd know where to look and I'd reach for `contextvars` first.

---

## 7. To add to `RECALL.md`

- The critical section is the **whole read-modify-write**, not the write. Locking only the assignment protects nothing
- **You cannot tell by looking**: `account.balance += 1` is safe as an attribute, loses **59%** as a property. Same syntax
- Lock cost measured: **2M increments unlocked 0.077s vs locked 0.201s — 2.6×**, and that is *uncontended*
- Under contention a lock **serialises**, removing the parallelism you added threads to get
- Four Coffman conditions; **circular wait is the one you control**
- **Deadlock reproduced**: two locks taken in opposite orders → both threads timed out, neither proceeded
- **Fix: consistent global lock ordering** (e.g. by account id) → both succeeded. Timeouts are a safety net, not a fix
- Neither deadlocking function had a bug alone — **the bug was in the relationship**, which is why review misses it
- A plain `Lock` re-acquired by its **own** thread **blocks on itself** — measured `False` on a 0.5s timeout
- `Lock` tracks **no owner**, so **any** thread can release it, silently. `RLock` raises on foreign release
- Needing `RLock` usually means wrong granularity → private unlocked impl + thin locking public methods
- `queue.Queue` buys: tested synchronisation, **back-pressure via `maxsize`** (measured: full after 10 puts), sentinel shutdown
- **A pipeline without back-pressure is a memory leak with extra steps**
- *Do not communicate by sharing memory; share memory by communicating*
- `threading.local` **breaks under asyncio** — many coroutines, one thread → cross-request bleed. Use **`contextvars`**

---

← [Concurrency knowledge graph](00_knowledge_graph.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
