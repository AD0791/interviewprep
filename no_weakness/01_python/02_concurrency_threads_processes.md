# Concurrency — threads, processes, and the GIL

*What actually runs in parallel, what only appears to, and how to choose.*

**Level: L3–L4.** Every number below came out of a terminal: CPython 3.10.12, four cores, Linux, default `fork` start method. Read [01 — the async execution model](01_async_execution_model.md) first if you have not; this module assumes the event loop material and extends it outward to threads and processes.

---

## 1. The thing you already do

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_rate(currency):
    return requests.get(f"https://api.bank.example/fx/{currency}").json()

with ThreadPoolExecutor(max_workers=10) as pool:
    rates = list(pool.map(fetch_rate, ["USD", "EUR", "HTG", "CAD"]))
```

Ten workers, four requests, done in the time of the slowest one. You have written this. It works.

---

## 2. The question you cannot answer about it

Python has a Global Interpreter Lock. One thread executes bytecode at a time. So why did that code get faster at all?

Now change `fetch_rate` to a function that computes a checksum over ten million rows instead of calling an API — same pool, same shape, same ten workers. It gets **slower than running it serially**. Why does the identical structure help in one case and hurt in the other?

And the one that separates people who have read about the GIL from people who have debugged around it: two threads incrementing the same integer. The GIL guarantees only one of them executes bytecode at a time. Does that make `balance += 1` safe?

If your instinct is "yes, the GIL protects it" — that instinct is wrong, and section 4.1 loses 74% of the deposits to prove it.

---

## 3. What the machine actually does

### 3.1 Process and thread, at the level the OS sees

A **process** owns an address space. Its memory is its own; another process cannot reach into it. It has its own file descriptors, its own copy of the Python interpreter, and — the part that matters here — **its own GIL**.

A **thread** is a schedulable execution context *inside* a process. Threads of one process share the address space: same heap, same globals, same module objects. Each has only its own stack and registers. Creating one is cheap relative to a process because there is nothing to copy.

Everything else in this module follows from that single distinction. Shared memory is why threads are fast to start and dangerous to reason about. Separate memory is why processes are safe and expensive to talk to.

### 3.2 The GIL, precisely

The Global Interpreter Lock is a mutex inside CPython protecting interpreter state — most importantly reference counts, which are ordinary non-atomic integers. Without it, two threads decrementing the same refcount concurrently would corrupt memory and crash the interpreter.

A thread must hold the GIL to execute Python bytecode. It releases it in two situations:

**Around blocking I/O.** When a thread calls into the kernel to read a socket or a file, it drops the GIL first and reacquires it on return. This is the entire reason your `ThreadPoolExecutor` above worked — the threads spend their time inside `recv()` with the GIL released, so they genuinely overlap.

**Periodically, so CPU-bound threads take turns.** Every 5 milliseconds by default (`sys.getswitchinterval()`), the interpreter asks the running thread to drop the GIL so another can run. This produces *interleaving*, not parallelism — it is time-slicing on one core.

The consequence is a clean rule with one sharp edge. Threads help I/O-bound work because the GIL is released during the wait. Threads do nothing for CPU-bound work because the GIL is held the whole time. The sharp edge is in section 4.1.

### 3.3 Measured: I/O-bound

Twenty operations, each a half-second wait:

```
serial            : 10.09s
20 threads        :  0.51s
8 processes       :  1.54s
20 coroutines     :  0.50s
```

Threads gave a 20× speedup on a language that "can't do parallelism," because the GIL is not held during the wait. Coroutines matched them. Processes helped but were capped by the pool size — eight workers doing twenty jobs is three rounds — and paid startup cost on top.

### 3.4 Measured: CPU-bound

The same shape, four jobs of pure Python arithmetic:

```
1 run, serial            : 0.42s
4 runs, asyncio.to_thread: 1.64s
4 runs, ThreadPool       : 1.66s
4 runs, ProcessPool      : 0.52s
```

Four threads took 1.64 seconds to do what one thread does in 0.42 — that is 3.9×, which is the serial total plus overhead. **Zero parallelism.** Four processes took 0.52 seconds on four cores, near-linear, because each process brought its own interpreter and its own GIL.

Those two tables together are the whole decision, and having measured them yourself is worth more than having read them.

### 3.5 What a coroutine costs versus what a thread costs

Two thousand idle waiters, resident memory measured:

```
2000 coroutines : +4.5 MB    (setup 0.53s)
2000 threads    : +32.1 MB   (setup 0.24s)
```

Seven times the memory, because every thread gets a stack from the OS while a coroutine is just an object on the heap. This is why "use threads for I/O" stops being the answer somewhere in the low thousands of concurrent operations and asyncio takes over. At twenty concurrent requests the difference is irrelevant and threads are simpler. At twenty thousand, threads are not an option.

---

## 4. Break it on purpose

### 4.1 The GIL does not make your code thread-safe

This is the single most consequential misunderstanding about the GIL, and it costs money in financial code.

```python
balance += 1
```

One line. Here is what it compiles to:

```
LOAD_GLOBAL  balance
LOAD_CONST   1
INPLACE_ADD
STORE_GLOBAL balance
```

**Four bytecodes.** The GIL guarantees that no two threads execute a bytecode simultaneously. It guarantees nothing whatsoever about a thread keeping the GIL across all four. If a switch happens between `LOAD_GLOBAL` and `STORE_GLOBAL`, two threads read the same value, both add one, both store — and one deposit vanishes.

Made deterministic with an explicit switch point, four threads, two thousand deposits each:

```python
def deposit_unsafe(n):
    global balance
    for _ in range(n):
        tmp = balance        # READ
        time.sleep(0)        # a switch point
        balance = tmp + 1    # WRITE
```

```
no lock    expected 8000, got  2100   lost  5900
with Lock  expected 8000, got  8000   lost     0
```

**Seventy-four percent of the deposits were lost.**

Now the finding that makes this a senior answer rather than a memorised warning. When I ran the *tight* version — plain `balance += 1` in a loop, no sleep, four threads, even with `sys.setswitchinterval(1e-6)` to force aggressive switching — I ran it five times and **lost nothing**. Every attempt returned exactly 800,000.

That is the dangerous part. The GIL makes read-modify-write races **rare, not impossible**. A race that fires once in ten million iterations does not appear in your tests, does not appear in staging, and appears in production as a balance that is wrong by one, twice a year, unreproducibly. The GIL does not protect you; it hides the bug until it is expensive.

The rule to carry: **any read-modify-write across threads needs a lock, regardless of the GIL.** If you want it lock-free, use a structure whose operations are single atomic bytecodes — `list.append`, `deque.append`, `queue.Queue` — or do not share the state at all.

### 4.2 Processes do not share your memory, and it will surprise you

```python
counter = 0
def bump(_):
    global counter
    counter += 1
    return (os.getpid(), counter)

with mp.Pool(3) as p:
    print(p.map(bump, range(6)))
print("parent counter after children ran:", counter)
```

```
start method: fork
parent pid: 7   parent counter: 0
child (pid, counter): [(9, 1), (10, 1), (11, 1), (9, 2), (10, 2), (9, 3)]
parent counter after children ran: 0
```

Read the child results. Three distinct PIDs, and **each child's counter starts from zero and climbs independently** — 9 reaches 3, 10 reaches 2, 11 reaches 1. The parent's counter is still 0 after six increments ran.

Each process got a *copy* of the module state at fork time. Mutating it mutates the copy. Nothing propagates back, nothing raises, nothing warns. Code that is correct with `ThreadPoolExecutor` becomes silently wrong when someone swaps in `ProcessPoolExecutor` for speed — and it will look like it works, because the return values are right and only the shared state is broken.

When processes genuinely must share a counter, you have to say so explicitly:

```python
val = mp.Value('i', 0)
def add(v, n):
    for _ in range(n):
        with v.get_lock():
            v.value += 1
```

```
mp.Value + lock: expected 200000, got 200000
```

Note that even in shared memory you still need the lock — `mp.Value` gives you shared storage, not atomicity.

### 4.3 Everything crossing a process boundary must pickle

```python
with mp.Pool(2) as p:
    p.map(lambda x: x*2, range(4))
```

```
passing a lambda to a process: PicklingError
```

Separate address spaces mean arguments and return values are serialised, shipped, and deserialised. Lambdas, closures, open file handles, database connections and most objects holding OS resources cannot make that trip. This is why multiprocessing code is full of module-level functions that look awkward — it is not style, it is the pickle constraint.

The performance consequence is easy to miss: **the pickle boundary can cost more than the parallelism saves.** Four processes crunching numbers is a clear win. Four processes each receiving a 200MB DataFrame is a loss, because you paid to serialise, copy and deserialise 800MB before any work started.

### 4.4 `fork` inherits things you did not mean to share

The output above shows `start method: fork`, which is the Linux default in 3.10. `fork` clones the parent process — including any locks that happened to be held at that instant, and any already-open database connections, whose sockets are now used by two processes that both think they own them.

The classic production failure is a connection pool created at import time, before workers fork. Every worker inherits the same sockets, responses get interleaved, and the symptom is corrupted or cross-wired query results that no amount of reading the query will explain.

Two defences. Create connection pools **after** the fork, inside the worker, not at module import. And know that `spawn` — the default on macOS and Windows, and available everywhere via `mp.set_start_method("spawn")` — starts a fresh interpreter that inherits nothing. It is slower to start and much harder to get silently wrong.

*Note for currency: the default start method on Linux has been under discussion for several CPython releases because of exactly these hazards. Check the current default for the version you are running before asserting it in an interview.*

---

## 5. The judgment call

### 5.1 The decision table

| | Parallel? | Shares memory? | Cost each | Use for |
|---|---|---|---|---|
| **asyncio** | No — one thread | Yes, trivially | ~2 KB | Thousands of concurrent I/O operations, when the libraries are async |
| **Threads** | Only during I/O | Yes — and this is the danger | ~16 KB | Tens to low thousands of I/O operations, especially with synchronous libraries |
| **Processes** | **Yes, genuinely** | No — must be explicit | ~MB + startup | CPU-bound work |

Measured backing: I/O — serial 10.09s, threads 0.51s, coroutines 0.50s. CPU — serial 0.42s, 4 threads 1.64s, 4 processes 0.52s. Memory — 2000 coroutines 4.5MB, 2000 threads 32.1MB.

### 5.2 How to actually choose

The first question is always **what is the thread waiting for**, because that single answer eliminates two of the three options.

If it is waiting on the network, the disk, or a database, the GIL is released during the wait and both threads and asyncio work. Choose between them on scale and ecosystem: threads if the count is in the tens or hundreds and your libraries are synchronous, asyncio if the count is in the thousands or your stack is already async. Do not migrate a working threaded service to asyncio for concurrency you do not have.

If it is computing — parsing, aggregating, hashing, transforming a DataFrame — no amount of threading helps and you need processes, or you need to leave Python for that section of the work.

That last clause matters more than it sounds. NumPy, Polars and DuckDB release the GIL and run their inner loops in C, so a "CPU-bound" Python program that spends its time inside those libraries may already be parallel without any concurrency primitives at all. Before reaching for `ProcessPoolExecutor`, check whether the hot loop is Python bytecode or a C extension. Vectorising is usually cheaper than parallelising, and it is the answer an interviewer hopes to hear.

### 5.3 Where this shows up in a web application

Tying it back to [module 01](01_async_execution_model.md): a FastAPI `async def` endpoint runs on the event loop and must never block. A plain `def` endpoint is offloaded to a threadpool of 40 by default — which is exactly the "threads for I/O with synchronous libraries" case, and it is why sync endpoints work fine.

CPU-bound work belongs in neither. A heavy computation inside an `async def` blocks the loop for every user; inside a `def` it occupies a threadpool slot and gains nothing from the other 39. It belongs in a process pool, or better, in a task queue outside the request cycle entirely.

---

## 6. Interview angles

### "What is the GIL, and how do you work around it?"

> "It's a mutex inside CPython that protects interpreter state, mainly reference counts, which aren't atomic — without it, two threads touching the same refcount would corrupt memory. The practical effect is that one thread executes Python bytecode at a time.
>
> But it's released in two situations, and that's the part that decides your design. It's released around blocking I/O, so threads waiting on sockets genuinely overlap — I measured twenty I/O operations going from ten seconds serial to half a second on twenty threads. And it's released periodically, about every five milliseconds, so CPU-bound threads take turns rather than running in parallel.
>
> So there's nothing to work around for I/O — threads or asyncio both work, and I'd pick on scale, threads in the hundreds and asyncio in the thousands, since two thousand coroutines cost about four megabytes against thirty-two for the same number of threads. For CPU-bound work you need processes, because each one has its own interpreter and its own GIL. I measured four CPU jobs: 1.64 seconds across four threads versus 0.52 across four processes, on a four-core box. The threads gave literally zero parallelism.
>
> The thing I'd add is that before reaching for processes I'd check whether the hot loop is actually Python bytecode, because NumPy and Polars release the GIL and run in C — vectorising is usually cheaper than parallelising."

### "Does the GIL make your code thread-safe?"

> "No, and this is the misconception I'd most want to correct. The GIL guarantees that no two threads execute a bytecode at the same instant. It guarantees nothing about a thread holding it across a sequence of bytecodes. `balance += 1` looks atomic but compiles to four instructions — load, push, add, store — and if a thread switch lands between the load and the store, two threads read the same value, both add one, and a deposit disappears.
>
> I measured that: four threads, two thousand deposits each, no lock, and 5,900 of 8,000 were lost. With a lock, zero.
>
> The part that worries me more is what happened when I ran the tight version without an artificial switch point — five runs, nothing lost, every time, even with the switch interval turned right down. So the GIL doesn't make the race impossible, it makes it *rare*. And a race that fires once in ten million iterations never shows up in tests; it shows up as a balance that's wrong by one, twice a year, that nobody can reproduce. My rule is that any read-modify-write across threads gets a lock regardless of the GIL, or I don't share the state at all — I use a queue."

### "Threads or processes — how do you choose?"

> "I start with one question: what is it waiting for? If it's waiting on the network or the disk or a database, the GIL is released during the wait, so threads work and asyncio works, and I'd choose on scale and on what my libraries support. If it's computing, threads are useless and I need processes.
>
> But processes aren't free and the costs are the part people skip. Memory isn't shared — I ran a pool where each child incremented a global, and each child got its own copy starting from zero while the parent's stayed at zero. Nothing raised, nothing warned. So code that's correct with a thread pool can go silently wrong when someone swaps in a process pool for speed. And everything crossing the boundary has to pickle, so you can't pass a lambda or a database connection, and if you're shipping a large DataFrame to each worker the serialisation can cost more than the parallelism saves.
>
> The other thing I'd watch for on Linux is that `fork` inherits open connections. If a pool is created at import time before the workers fork, they all share the same sockets and you get interleaved responses that look impossible. Create the pool inside the worker, or use the `spawn` start method."

### "You have a data pipeline that's too slow. Where do you start?"

> "I'd profile before choosing a concurrency model, because the answer is usually not concurrency. First I want to know whether it's I/O-bound or CPU-bound, because that eliminates two of the three options immediately.
>
> If it's I/O — waiting on an API, or on the database — then it's threads or asyncio, and I'd also ask whether the work needs to be sequential at all. In my experience the bigger win there is usually batching rather than parallelism: one query returning ten thousand rows instead of ten thousand queries.
>
> If it's CPU, before I reach for multiprocessing I'd check what's actually consuming the time, because if it's a Python loop over a DataFrame the answer is to vectorise, not to parallelise — that's often an order of magnitude for a fraction of the complexity, and it doesn't introduce a pickle boundary. Multiprocessing is where I'd go if the work is genuinely CPU-heavy Python and already vectorised, and I'd want to check the serialisation cost of what I'm sending to each worker before assuming it'll help."

---

## 7. To add to `RECALL.md`

- Process = own address space and **own GIL**. Thread = shared address space, own stack.
- GIL released around **blocking I/O** and every **~5ms** (`sys.getswitchinterval()`)
- I/O measured: serial 10.09s · 20 threads 0.51s · 20 coroutines 0.50s · 8 processes 1.54s
- CPU measured: serial 0.42s · 4 threads 1.64s (**zero parallelism**) · 4 processes 0.52s
- Memory: 2000 coroutines **4.5MB** · 2000 threads **32.1MB**
- `balance += 1` is **four bytecodes**, not atomic. No lock → **5,900 of 8,000 lost**
- Tight loop lost **nothing** in 5 runs → the GIL makes races **rare, not impossible**
- Processes: children mutate **copies**; parent counter stayed 0, silently
- `mp.Value` gives shared storage, **not** atomicity — still needs `get_lock()`
- Lambdas across a process boundary → `PicklingError`
- `fork` inherits open DB connections → create pools **inside** the worker
- NumPy/Polars/DuckDB **release the GIL** — vectorise before you parallelise

---

← [Python index](README.md) · [01 — async execution model](01_async_execution_model.md) · [repo plan](../README.md)
