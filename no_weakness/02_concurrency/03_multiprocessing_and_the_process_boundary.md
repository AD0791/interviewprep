# Multiprocessing and the process boundary

*The pool that ran 300× slower than serial, the counter that silently stayed zero, and why your module ran four extra times.*

**Level:** L4 · **Prerequisites:** [`01` the GIL](01_the_gil_what_it_protects_and_when_it_lets_go.md), [`01_python/08` imports](../01_python/00_syllabus.md)
**Syllabus:** [`CONC-11`–`CONC-15`](00_syllabus.md) · **Roles:** DE ●● FS ●
**Measurement:** `Measured` — CPython 3.14.6, arm64, 8 cores, macOS 26.5.2. Every output below came out of a terminal on this machine, including one result I did not plan: a script that accidentally demonstrated the `spawn` re-import problem by printing its own header five times.

---

## 1. The thing you already do

[Module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md) established the rule: threads for I/O, processes for CPU. So having found a CPU-bound loop, you do the obvious thing:

```python
# Gist: reconcile_pool.py
from multiprocessing import Pool

def fx_convert(tx: Transaction) -> Decimal:
    return tx.amount * rate_for(tx.currency, tx.date)

with Pool(4) as pool:
    converted = pool.map(fx_convert, transactions)
```

Four processes, four cores, one line changed. This is presented everywhere as the happy ending of the GIL story.

It is not, quite. That code has three separate ways to disappoint you, and the first one is that it can be **hundreds of times slower** than the serial loop it replaced.

---

## 2. The questions you cannot answer about it

**Why does your worker's update to a global vanish?** You set a counter in a child process, the child reports it incremented, and the parent reads zero. No exception, no warning. Explain where the write went.

**Why does the same script behave differently on your Mac and your colleague's Linux box?** There is a platform default that differs, and it changes what your module does at import time. If you have never hit this, it is because you have not yet written a `multiprocessing` script with a side effect at module level.

**What can't cross the boundary, and why?** You know lambdas fail. Name the mechanism, then predict whether an open file handle or a database connection can cross.

**And the one that should bother you.** Take a trivially parallel workload — squaring two hundred thousand integers — and run it four ways. Serial takes **0.01s**. A four-process pool with `chunksize=1` takes **3.01s**.

**The parallel version is three hundred times slower than the serial one**, on a machine with eight idle cores. Same work, same function, four processes doing it at once.

If you can explain all four, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: a branch office, not a colleague

A thread is a colleague at the next desk. You share filing cabinets; anything you put down, they can pick up. That sharing is why threads need locks and why they are cheap.

A process is a **branch office in another city**. It has its own copies of everything. To send it work you photocopy the documents and post them; to get an answer back it photocopies and posts in return. Nothing you write on your desk appears on theirs, ever.

Two consequences follow, and they are the whole module. There is no shared state to corrupt — so no locks, no data races, real parallelism. And **everything that crosses must be copied**, which is the cost that makes §2's 300× slowdown possible.

### 3.2 Own address space, own interpreter, own GIL

A process gets its own memory, its own Python interpreter and therefore its own GIL. That is precisely why it achieves genuine parallelism where threads cannot — measured at 3.47× on eight cores in [module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md).

The price is that objects cannot be shared by reference. Anything sent to a worker is **pickled** in the parent, transmitted over a pipe, and unpickled in the child, producing an object that is equal to but not identical with the original. Return values make the same journey back.

### 3.3 `fork`, `spawn`, `forkserver` — and the platform default that bites

```text
default start method on this platform: spawn
available: ['spawn', 'fork', 'forkserver']
```

**macOS defaults to `spawn`** ([`CONC-MP-01`](../MEASUREMENTS.md)). Linux historically defaulted to `fork` and has been moving to `spawn` as the default too, because `fork` in a multi-threaded process is genuinely unsafe.

The three differ in how the child comes into existence, and the difference is not academic.

**`fork`** clones the parent process — memory, file descriptors, everything — using copy-on-write. It is fast and the child inherits all state automatically. It is also dangerous: if any thread held a lock at the moment of the fork, the child inherits the *locked* lock and the thread that would have released it does not exist in the child. That is an unrecoverable hang, and it is why the default is moving away.

**`spawn`** starts a fresh interpreter and **re-imports your module** in the child, then unpickles the target function and arguments. It is slower and it inherits nothing, which is safe but means module-level side effects run again.

**`forkserver`** forks from a small clean server process started early, giving fork's speed without inheriting the main process's threads and locks.

The re-import in `spawn` is not a footnote. Here is what happened when I ran a script with two `print` calls at module level:

```text
=== 1. children mutate COPIES — silently ===
default start method on this platform: spawn
available: ['spawn', 'fork', 'forkserver']
default start method on this platform: spawn
available: ['spawn', 'fork', 'forkserver']
  children reported: [(15700, 1), (15699, 1), (15700, 2), (15699, 2)]
```

Those repeated lines are not a copy-paste error. **Each child process re-imported the module and re-executed the module-level prints** ([`CONC-MP-02`](../MEASUREMENTS.md)). Across the whole script the header printed thirteen times for one invocation.

I did not plan that demonstration; the script produced it by accident, which is exactly how this bites people in production. Now substitute something with consequences for a `print` — opening a database connection, starting a scheduler, sending a metric, writing a file — and every child does it too.

This is why `if __name__ == "__main__":` is **mandatory** rather than stylistic under `spawn`. In the child, the module is imported under its real name rather than as `__main__`, so the guarded block does not run. Without the guard, the child re-executes the code that creates the pool, which creates more children, which re-execute it — and the standard library raises rather than let you fork-bomb yourself.

### 3.4 Children mutate copies, and it fails silently

```python
# Gist: p1_procs.py
counter = 0
def child_mutates(_):
    global counter
    counter += 1
    return (os.getpid(), counter)

with mp.Pool(2) as p: res = p.map(child_mutates, range(4))
print("  children reported:", res)
print(f"  parent counter is still: {counter}")
```

```text
  children reported: [(15700, 1), (15699, 1), (15700, 2), (15699, 2)]
  parent counter is still: 0   <- no error, no warning
```

Read the child output first ([`CONC-MP-03`](../MEASUREMENTS.md)). Two distinct process ids, each counting to 2 — so each child had its own `counter`, starting from its own copy of the module state, and incremented it correctly within itself.

And the parent's counter is **0**. Not wrong-by-one, not partially updated. Untouched, because the children were writing to different memory in different processes.

**No exception. No warning. The code looks like it works.** This is the failure mode people find hardest to debug because there is nothing to catch — a log aggregation counter, a progress tally, a cache populated by workers, all quietly discarded.

For genuinely shared state there are three options, in increasing order of capability and decreasing order of speed. `Value` and `Array` give real shared memory but **not atomicity** — they still need `get_lock()` around read-modify-write, for exactly the reasons in [module 02](02_threads_races_and_synchronisation.md). `shared_memory` gives a raw zero-copy buffer, which is the right tool for large arrays. And `Manager` runs a separate server process holding the objects and hands out proxies, which supports rich types like dicts and lists at the cost of a round trip through IPC on **every single access**.

### 3.5 What cannot cross the boundary

Everything crossing is pickled, so the question "can this be pickled?" is the question "can this go to a worker?"

```python
# Gist: p1_procs.py (part 2)
for name, obj in [("lambda", lambda x: x), ("open file", open(__file__)),
                  ("local closure", (lambda: (lambda: 1))())]:
    pickle.dumps(obj)
```

```text
  lambda          PicklingError: Can't pickle <function <lambda> at 0x10a5c35e0>: it's not
  open file       TypeError: cannot pickle 'TextIOWrapper' instances
  local closure   PicklingError: Can't pickle local object <function <lambda>.<locals>.<lam
```

Three failures with two distinct causes ([`CONC-MP-04`](../MEASUREMENTS.md)).

**Lambdas and local closures fail because pickle stores functions by qualified name**, not by code. It writes down "the function called `square` in module `p1_procs`" and expects the child to find it by importing. A lambda has no importable name, and a closure defined inside another function is not reachable at module level. This is also why the target of a `Pool.map` must be defined at module top level — a method or nested function will not resolve in the child.

**Open files, sockets and database connections fail for a deeper reason**: they are handles to kernel resources belonging to this process. There is nothing meaningful to copy. A file descriptor number is only valid in the process that owns it.

That last point generalises into the most damaging version of this problem. Under `fork`, a database connection **is** inherited — the file descriptor is cloned — and now two processes are interleaving bytes on one socket. The server sees a corrupted protocol stream, and the errors are bizarre: results delivered to the wrong query, connections dropped, occasional corruption. The rule is to **create connection pools inside the worker after the fork**, which is why frameworks like Gunicorn and Celery expose a post-fork hook.

### 3.6 The measurement that should change your instinct

Now §2's result in full.

```python
# Gist: p1_procs.py (part 3)
data = range(200_000)
for cs in (1, 100, 10_000):
    with mp.Pool(4) as p: p.map(square, data, chunksize=cs)
```

```text
  chunksize      1: 3.01s
  chunksize    100: 0.09s
  chunksize  10000: 0.05s
  serial (no pool) : 0.01s
```

Four numbers, and every one of them is instructive ([`CONC-MP-05`](../MEASUREMENTS.md)).

**`chunksize=1` took 3.01 seconds against serial's 0.01 — the parallel version is 300× slower.** Each of the two hundred thousand integers was pickled individually, sent through a pipe, unpickled, squared in about a nanosecond, pickled again, and sent back. The coordination cost is thousands of times the work.

**Raising `chunksize` to 100 cut it to 0.09s** — a 33× improvement from a single keyword argument, because the per-item overhead is now amortised over a hundred items per message.

**And even the best pool configuration, 0.05s, is five times slower than the serial loop.** For this workload multiprocessing can never win. The work per item is too small for any amount of tuning to overcome the boundary cost.

The general shape: **parallelism pays only when the work per item substantially exceeds the cost of shipping the item across.** Squaring an integer does not qualify. Parsing a document, resizing an image, running an FX conversion against a rate table, computing a statistical model — those do.

This is also the strongest argument for the [module 01](01_the_gil_what_it_protects_and_when_it_lets_go.md) recommendation to vectorise first. A NumPy expression over these two hundred thousand integers releases the GIL, runs in C, and copies nothing.

---

## 4. Break it on purpose

### 4.1 The pool that made it 300× slower

Covered in §3.6 as a measurement; worth restating as the failure it is, because it is so common.

Somebody profiles a loop, sees it is CPU-bound, wraps it in `Pool.map`, observes the code is now slower, and concludes that "multiprocessing doesn't work" or that "Python is slow." Both conclusions are wrong. The pool worked exactly as designed; the workload was unsuitable and the default chunking made it pathological.

The diagnostic is a ratio, and you can estimate it without a profiler: **how long does one item take, and how big is one item?** Nanoseconds of work on a small object means the boundary dominates. Milliseconds of work means it will pay.

The fixes in order of effectiveness are: do not parallelise this at all; vectorise it; raise `chunksize` substantially; batch at the application level so each task is genuinely large.

### 4.2 The progress counter that stayed at zero

```python
# Gist: silent_counter.py
processed = 0

def work(item):
    global processed
    processed += 1              # increments a copy
    return transform(item)

with Pool(4) as pool:
    results = pool.map(work, items)

print(f"processed {processed} items")     # prints 0
```

```text
  parent counter is still: 0   <- no error, no warning
```

Ten thousand items processed correctly, results returned correctly, and the report says zero.

This is worse than a crash because it is *plausible*. A progress counter reading zero looks like a logging bug, so people spend an afternoon on the logging. The actual cause is that `processed += 1` ran in four separate address spaces, none of which was the parent's.

The fix depends on what you actually need. If you want a count, `len(results)` is free and correct — derive it from the returned data rather than accumulating shared state. If you need live progress, use a `multiprocessing.Queue` that workers write to and the parent drains, or a `Value` with `get_lock()`. The general principle: **let the return values carry the information.** The boundary already copies them for you.

### 4.3 The connection pool that corrupted itself

The most damaging failure in this module, and the least obvious.

```python
# Gist: forked_conn.py
engine = create_engine(DATABASE_URL)          # created at module level, in the parent

def work(item):
    with engine.connect() as conn:            # child uses the INHERITED pool
        return conn.execute(query, item).fetchone()

with Pool(4) as pool:                          # under fork, all four inherit `engine`
    results = pool.map(work, items)
```

Under `fork`, the pool's already-open sockets are inherited by every child. Four processes now write to and read from the same TCP connections with no coordination, interleaving their bytes mid-protocol.

The symptoms are genuinely strange: a query returning another query's results, `server closed the connection unexpectedly`, occasional decoding errors, and — the worst kind — data that is subtly wrong rather than absent. And it is **load-dependent and non-deterministic**, so it passes tests and fails in production.

The fix is to create the engine inside the worker, or to dispose the inherited pool at worker start:

```python
# Gist: forked_conn_fixed.py
def init_worker():
    engine.dispose()          # drop inherited connections; new ones are created per child

with Pool(4, initializer=init_worker) as pool:
    ...
```

The cost is a fresh connection per worker, which is exactly what you wanted anyway.

**Run this one yourself** only if you have a database you do not mind confusing. The reason to know it without running it is that the error messages point at the database, and you can lose a long time there before suspecting the fork.

### 4.4 The script that ran itself five times

The accidental discovery from §3.3, stated as the bug it becomes.

```python
# Gist: no_guard.py
import multiprocessing as mp

print("starting up")                 # module level — runs in every child under spawn
setup_logging()
metrics.increment("worker.boot")     # so does this

def work(x): return x * 2

with mp.Pool(4) as pool:             # NO __main__ guard
    print(pool.map(work, range(10)))
```

Under `spawn`, each child re-imports the module, so `setup_logging()` and the metric increment run five times rather than once. Worse, the unguarded pool creation is itself re-executed, and the standard library detects the recursion and raises rather than letting the machine fork-bomb.

My measurement script showed exactly this behaviour with harmless `print` calls, thirteen times over one run. The fix is mechanical:

```python
if __name__ == "__main__":
    with mp.Pool(4) as pool:
        print(pool.map(work, range(10)))
```

The deeper habit is to keep module level free of side effects entirely — no connections, no scheduler starts, no metric writes — which is good practice regardless of multiprocessing and becomes mandatory with it.

---

## 5. The judgment call

### The options, honestly costed

| Approach | Use when | Because | Real cost |
|---|---|---|---|
| **Serial** | Per-item work is small | No boundary to pay for; **measured 0.01s versus the pool's best 0.05s** | Uses one core |
| **Vectorise** | Numeric work over arrays | C speed *and* the GIL released — no copying at all | A dependency and a conversion boundary |
| **`Pool` + large `chunksize`** | Per-item work substantially exceeds pickling cost | Amortises the boundary; **`chunksize` 1 → 100 was a 33× improvement** | Everything must pickle; tuning required |
| **`ProcessPoolExecutor`** | Same, with a nicer API and futures | Cleaner cancellation and exception propagation | Same boundary costs |
| **`shared_memory`** | Large numeric buffers several workers read | Zero-copy; no pickling of the payload | Manual lifecycle; you unlink it yourself |
| **`Value` / `Array`** | One or two shared scalars | Genuine shared memory | **Not atomic** — still needs `get_lock()` |
| **`Manager`** | Shared rich types (dict, list) | Supports arbitrary objects | A proxy round trip on **every access**; much slower than it looks |
| **Task queue (Celery/RQ)** | Work outlives a request, or must survive a restart | Durability, retries, monitoring, scaling across machines | Real infrastructure — broker, workers, deployment |

### When you would not do this

**Do not parallelise before measuring the per-item cost.** §3.6 is the argument, and it is the strongest number in this module: a four-process pool ran 300× slower than a serial loop on eight idle cores. If one item takes microseconds, no configuration will make the boundary pay. Estimate the ratio of work-per-item to size-of-item before writing the pool.

**Do not share state across processes if the return value can carry it.** §4.2's counter should have been `len(results)`. The boundary already copies return values, so information travelling that way is free, correct, and needs no synchronisation. Reaching for `Manager` to share a dict is usually a sign the design should have been "workers return data, parent aggregates."

**Do not create connections, engines or clients at module level.** Under `fork` they are inherited and corrupted; under `spawn` they are recreated in every child. Both are bad and the second is merely wasteful. Create them inside the worker, or dispose them in an initialiser.

**Do not assume the parent's behaviour transfers.** Global configuration set at runtime — a logging level changed by a CLI flag, a mutated settings object, a monkeypatch — exists in the parent and does not reach a `spawn`ed child, which starts from a fresh import. State that matters must be passed explicitly as an argument.

**Prefer a task queue when the work is not compute.** `multiprocessing` is for using more cores in one program. If the real requirement is that work survives a crash, retries, runs on another machine, or outlives the request that scheduled it, that is a broker's job. I should be plain that this is a boundary in my own experience — the parallelism in my pipeline work was Beam's and the runner's rather than something I operated directly.

---

## 6. Interview angles

**"When would you use multiprocessing over threading?"**

> When the work is CPU-bound in pure Python, because each process gets its own interpreter and its own GIL, and that's the only way to get real parallelism. I measured it: eight CPU-bound jobs on eight cores took 1.88 seconds serial, 1.87 with eight threads — literally no change — and 0.54 with eight processes. But I'd immediately add the caveat, because the naive version of this advice caused the most surprising measurement I took. I ran a trivially parallel workload, squaring two hundred thousand integers, through a four-process pool with the default chunking, and it took **3.01 seconds against 0.01 serial**. Three hundred times slower, on a machine with eight idle cores. The reason is that every item gets pickled individually, sent down a pipe, unpickled, squared in about a nanosecond, and shipped back — the coordination costs thousands of times more than the work. Raising `chunksize` to 100 brought it to 0.09s, a 33× improvement from one keyword argument, but even the best pool config was still five times slower than the serial loop. So my actual rule is that parallelism pays only when work-per-item substantially exceeds the cost of shipping the item, and before reaching for processes at all I'd ask whether the loop should be vectorised — NumPy and Polars release the GIL around their C kernels, so you get parallelism and C speed with no copying.

**"A worker updates a global and the parent doesn't see the change. Explain."**

> Because the child mutated a copy. Processes have separate address spaces, so the child gets its own copy of module state and its writes go to its own memory. I ran it to see the shape clearly: two workers, four tasks, and the children reported their own counters incrementing to 2 each with distinct process ids — so each of them was counting correctly, internally. The parent's counter stayed at zero. And the thing I'd emphasise is that there's **no exception and no warning**. Nothing to catch. That makes it much harder to debug than a crash, because a progress counter reading zero looks like a logging bug and people go and investigate the logging. The fix I'd usually reach for isn't shared memory, it's to let the return values carry the information — `len(results)` is free and correct, and the boundary is already copying returns for you. If you genuinely need live progress, a `multiprocessing.Queue` the workers write to and the parent drains. `Value` and `Array` do give real shared memory but they're **not atomic**, so you still need `get_lock()` around read-modify-write, and `Manager` supports rich types but pays a proxy round trip on every single access, which is much slower than the API makes it look.

**"Your multiprocessing code works on Linux and misbehaves on macOS. What's happening?"**

> Almost certainly the start method. macOS defaults to `spawn`, and Linux historically defaulted to `fork` — I confirmed `spawn` is the default here and all three are available. Under `fork` the child is a clone, so it inherits everything automatically. Under `spawn` you get a fresh interpreter that **re-imports your module**, so anything at module level runs again in every child. I actually demonstrated this to myself by accident: I'd left two `print` calls at module level in a measurement script, and the output showed the header repeated thirteen times for a single run, once per child. Harmless with prints, but substitute opening a database connection or starting a scheduler and every child does it too. That's why `if __name__ == "__main__":` is mandatory rather than stylistic under spawn — in the child the module is imported under its real name, so the guard is what stops the pool-creating code from running again and spawning more children. The nastier direction is `fork`, though. A forked child inherits open sockets, so an inherited database connection pool means several processes interleaving bytes on the same TCP connection — you get results delivered to the wrong query and connection errors that point at the database rather than at the fork. The fix is creating the pool inside the worker or disposing the inherited one in an initialiser, which is exactly what the post-fork hooks in Gunicorn and Celery are for.

**"You need to process a million records nightly and it currently takes six hours. Design it."**

> I'd want two numbers before designing anything: how long one record takes, and where that time goes. If it's waiting on a database or an API, more processes won't help much and I'd be looking at batching the queries and concurrency on the I/O — which is the shape of work I've actually done, on the pipeline side. If it's genuinely CPU-bound per record, then a process pool with a deliberately large chunk size, and I'd size chunks so each task is at least tens of milliseconds of work, because I've measured what happens when they're not. But I'd challenge the framing first. A six-hour nightly job that's one Python program is fragile — if it dies at hour five you've lost the run, and rerunning it needs the work to be idempotent. So I'd want it partitioned into independently retryable units keyed on something deterministic, so a failed partition can be reprocessed without touching the rest. That's the same idempotency argument as the pipeline work on my CV, where the sink had to tolerate a redelivered batch. And if the requirement is really "survives crashes, retries, runs across machines," that's a task queue or a managed runner rather than `multiprocessing` — I should be straight that in my own work Beam and its runner owned that parallelism rather than me operating a worker fleet directly, so I'd be reasoning from the design side rather than from having run one.

---

## 7. To add to `RECALL.md`

- Process = **own address space, own interpreter, own GIL** → real parallelism. Thread = shared heap, own stack → needs locks
- **macOS defaults to `spawn`**; Linux historically `fork` and moving to `spawn` because forking a threaded process is unsafe
- `fork` clones everything (fast, inherits locks — **a lock held at fork time is held forever in the child**); `spawn` re-imports the module; `forkserver` forks from a clean early process
- **Measured accidentally:** module-level prints ran once per child under `spawn` — the header appeared **13 times** in one run
- `if __name__ == "__main__":` is **mandatory** under spawn — without it the child re-runs pool creation
- **Children mutate copies, silently:** children reported their own counters at 2; **parent stayed 0. No exception, no warning**
- Pickle stores functions **by qualified name**, so lambdas, local closures and methods fail — target must be module-level
- Files, sockets and connections cannot pickle — they are **kernel handles valid only in the owning process**
- Under `fork` a connection pool **is** inherited → several processes interleave on one socket → wrong results and weird errors. **Create pools inside the worker**
- **The 300× result:** 200k squares, serial **0.01s** vs 4-process pool `chunksize=1` **3.01s**
- `chunksize` 1 → 100 gave **33×** (3.01s → 0.09s); best pool config 0.05s is **still 5× slower than serial**
- **Parallelism pays only when work-per-item exceeds the cost of shipping the item**
- `Value`/`Array` = shared memory but **not atomic** (needs `get_lock()`); `shared_memory` = zero-copy buffers; `Manager` = rich types at **a proxy round trip per access**
- Prefer **letting return values carry the data** — the boundary already copies them

---

← [Concurrency syllabus](00_syllabus.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
