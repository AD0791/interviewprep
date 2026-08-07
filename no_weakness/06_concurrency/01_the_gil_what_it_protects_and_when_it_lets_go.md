# The GIL — what it protects, and when it lets go

*Zero speedup, eight times speedup, and the race that refuses to happen until you add a function call.*

**Level:** L4–L5 · **Prerequisites:** [`05_python/05` bytecode](../05_python/05_bytecode_and_the_runtime.md)
**Syllabus:** [`CONC-01`–`CONC-05`](00_knowledge_graph.md) · **Roles:** DE ● FS ●
**Measurement:** `Measured` — CPython 3.14.6, arm64, 8 cores, macOS 26.5.2, GIL enabled. Every figure below came out of a terminal on this machine. **One section reports a negative result** — a race that would not reproduce — and then explains why, which turned out to be the most useful thing in the module.

---

## 1. The thing you already do

You have written both of these, and you have a rough sense that one of them is a good idea and the other might not be:

```python
# Gist: fetch_all.py — fan out over an API
from concurrent.futures import ThreadPoolExecutor

def fetch_account(account_id: int) -> dict:
    return httpx.get(f"{BASE}/accounts/{account_id}").json()

with ThreadPoolExecutor(max_workers=8) as pool:
    accounts = list(pool.map(fetch_account, account_ids))
```

```python
# Gist: reconcile_all.py — fan out over a computation
def reconcile(batch: list[Transaction]) -> Decimal:
    total = Decimal(0)
    for tx in batch:
        total += tx.amount * tx.fx_rate       # pure Python arithmetic
    return total

with ThreadPoolExecutor(max_workers=8) as pool:
    totals = list(pool.map(reconcile, batches))
```

Identical structure. Eight workers, a pool, a `map`. The first one will make your program roughly eight times faster. The second will make it exactly as fast as not using threads at all — not slower in any dramatic way, just *completely pointless*, eight threads taking precisely as long as one.

You probably know this as a rule: "threads are for I/O, processes are for CPU." The rule is correct. What it does not tell you is why, or when it stops being true, or what it costs.

---

## 2. The questions you cannot answer about it

**What does the GIL protect?** Not what it prevents — everyone can recite that it prevents using multiple cores. What is it *for*? There is a specific data structure it exists to keep consistent, and naming it turns a complaint into an explanation.

**When exactly is it released?** "On I/O" is the standard answer and it is incomplete in a way that matters, because it fails to explain why a NumPy operation parallelises across threads when a `for` loop does not.

**Are Python's built-in types thread-safe?** You have probably heard "yes, because of the GIL." Decide whether you believe that, then read §3.4 and §3.5, because the honest answer has two halves and most people only know one.

**And the one that should genuinely bother you.** Take the canonical demonstration of a data race — two threads incrementing a shared counter — and run it on CPython 3.14. Sixteen threads. Four hundred thousand increments. Switch interval forced down to one nanosecond, a thousand times more aggressive than the default.

**Zero updates lost. Every single time.**

The textbook race, on the interpreter you are running, refuses to happen. Then add one function call between the read and the write, change nothing else, and 59% of the updates vanish.

If you can explain both halves of that, skip to §6. Otherwise, section 3.

---

## 3. What the machine actually does

### 3.1 The analogy: a talking stick

The GIL is a talking stick. There is exactly one, and no thread may execute Python bytecode without holding it. A thread picks it up, runs, and puts it down either because it has been holding it for a while or because it is about to do something that does not need it — like waiting for a network reply.

Two things follow immediately, and they are the whole module. Only one thread runs Python at a time, so pure-Python computation never parallelises. And a thread that is *waiting* rather than *computing* puts the stick down, so waiting parallelises beautifully.

The interesting part — the part almost nobody knows — is *when* a thread is allowed to put the stick down. It is not "whenever." It is at specific, identifiable points, and knowing where they are explains the negative result in §2.

### 3.2 What it actually protects: reference counts

CPython reclaims memory primarily by reference counting. Every object carries a count of how many things point at it, and when the count hits zero the object is freed immediately.

That count is an ordinary integer being incremented and decremented constantly — every assignment, every function call, every list append touches dozens of them. And `count += 1` on a C integer is itself not atomic at the machine level: load, add, store.

If two threads decrement the same object's refcount simultaneously and one update is lost, the count never reaches zero and you leak. Worse, if the count is decremented twice when it should have been once, the object is freed while something still points at it — and now you have a use-after-free, which in a memory-unsafe C program is a segfault or an exploitable bug rather than a wrong number.

**So the GIL exists to keep the interpreter's own bookkeeping consistent**, chiefly reference counts but also the internal structures of built-in types. The single-core limitation is a *consequence* of that choice, not its purpose. This distinction is the difference between "the GIL is a design flaw" and "the GIL is how CPython buys fast single-threaded refcounting and a simple C API" — and the second answer is the one that leads somewhere in an interview.

The alternative designs all pay somewhere else. Atomic reference counts are slower on every single operation, including the overwhelmingly common single-threaded case. Tracing garbage collection avoids refcounts entirely but introduces pauses and a much more complex C API. Enforced isolation — JavaScript's workers, Erlang's processes — means no shared objects at all, so nothing needs protecting. Every runtime pays; CPython chose to pay in parallelism.

### 3.3 Measured: zero speedup, and eightfold speedup

The rule from §1, with numbers.

```python
# Gist: g2_procs.py
def cpu(n=6_000_000):
    t = 0
    for i in range(n): t += i*i
    return t

def _io(_): time.sleep(0.5)

N = 8
# serial, then ThreadPoolExecutor(N), then ProcessPoolExecutor(N)
```

```text
=== CPU-BOUND, 8 jobs, 8 cores ===
  serial       1.88s   (1.00x)
  8 threads    1.87s   (1.00x)
  8 processes  0.54s   (3.47x)

=== I/O-BOUND (sleep 0.5), 8 jobs ===
  serial       4.03s
  8 threads    0.51s   (7.97x)
```

Three results, each worth stating precisely ([`CONC-GIL-01`](../MEASUREMENTS.md)).

**Threads on CPU-bound work: 1.00×.** Not slower, not faster — identical. Eight threads took 1.87 seconds to do what one thread does in 1.88. They took turns holding the stick, and the total work was unchanged. This is the clearest possible demonstration that the GIL serialises Python execution.

**Threads on I/O-bound work: 7.97×.** Nearly perfect scaling on eight jobs, because `time.sleep` releases the GIL — as does every blocking syscall. Seven threads wait while one holds the stick, and waiting costs nothing.

**Processes on CPU-bound work: 3.47×.** Real parallelism, because each process has its own interpreter and therefore its own GIL. But note it is 3.47× rather than 8× on an eight-core machine: process startup, pickling the results back, and the fact that Apple Silicon's eight cores are a mix of performance and efficiency cores all eat into it. **Quoting "processes give you N× on N cores" is the kind of claim an interviewer will probe, and the honest number is better than the theoretical one.**

### 3.4 The negative result: the race that would not happen

Now the finding that made this module worth writing.

The canonical race is two threads incrementing a shared counter. [Module 05](../05_python/05_bytecode_and_the_runtime.md) established that `balance += 1` is four separate instructions. The textbook conclusion is that a thread switch can land between any two of them, so updates get lost.

I tried to reproduce it, and escalated hard:

```python
# Gist: g4_race2.py
balance = 0
def deposit(per):
    global balance
    for _ in range(per):
        balance += 1

# 2, 4, 8, 16 threads; switch interval down to 1 nanosecond
```

```text
   2 threads x 100,000 @ interval 0.005    -> lost        0  (0.00%)
   4 threads x 100,000 @ interval 1e-06    -> lost        0  (0.00%)
   8 threads x 200,000 @ interval 1e-09    -> lost        0  (0.00%)
  16 threads x 100,000 @ interval 1e-09    -> lost        0  (0.00%)
```

**Nothing.** Sixteen threads, a switch interval five million times more aggressive than the default, four hundred thousand increments — and not one lost ([`CONC-GIL-02`](../MEASUREMENTS.md)).

This is a negative result and it is reported rather than buried, because chasing it produced the actual mechanism.

The folklore is wrong in a specific way. **The interpreter does not consider switching threads between arbitrary bytecodes.** It checks a flag — the "eval breaker" — at particular points in the evaluation loop: backward jumps, which is to say loop back-edges, and function calls. Between `LOAD_GLOBAL`, `LOAD_SMALL_INT`, `BINARY_OP` and `STORE_GLOBAL` there is no such point. The sequence runs to completion before any switch can be considered, which makes it *effectively* atomic on this interpreter.

`sys.getswitchinterval()` returns 0.005 — five milliseconds — and that value is not a promise that a switch happens every five milliseconds. It is the minimum interval after which a switch will be *requested*; the switch itself happens at the next checkpoint.

### 3.5 The race, forced

If the hypothesis is right, inserting a checkpoint between the read and the write should produce the race immediately. A function call is a checkpoint.

```python
# Gist: g5_why.py
def identity(x): return x

def deposit_with_call(per):
    global balance
    for _ in range(per):
        v = balance
        v = identity(v) + 1      # a CALL sits between read and write
        balance = v
```

```text
  plain  balance += 1                    lost        0 of 400,000  (0.00%)
  with a CALL between read and write     lost  220,762 of 400,000  (55.19%)
```

There it is ([`CONC-GIL-03`](../MEASUREMENTS.md)). Same threads, same interval, same counter. One function call between the load and the store, and **55% of the updates disappear.**

So which real-world code has a call in that position? This is where it stops being a curiosity:

```python
# Gist: g6_real.py
acct.balance += 1          # plain attribute
acct.prop_balance += 1     # a @property — getter and setter are Python functions
d['k'] += 1                # dict item
lst.append(1)              # single C call
```

```text
  obj.balance += 1        lost        0 of 400,000  (0.00%)
  obj.prop_balance += 1   lost  236,574 of 400,000  (59.14%)
  d['k'] += 1             lost        0 of 400,000  (0.00%)
  list.append (C call)    lost        0 of 400,000  -> append IS safe
```

**A `@property` loses 59% of its updates while a plain attribute loses none** ([`CONC-GIL-04`](../MEASUREMENTS.md)).

This is the cross-module payoff. [Module 01](../05_python/01_object_model_and_attribute_lookup.md) established that a `@property` is a data descriptor whose `__get__` and `__set__` are ordinary Python functions. Ordinary Python functions mean `CALL` instructions. `CALL` instructions are eval-breaker checkpoints. So the descriptor protocol — the thing that makes `account.balance` look exactly like `account.owner` at the call site — is precisely what turns a safe increment into a catastrophic one.

Two attribute accesses, syntactically identical, with completely different concurrency behaviour, and nothing in the code tells you which is which.

And `list.append` losing nothing confirms the other half: it is a single C call that completes without any interpreter-level checkpoint inside it, which is why the built-in types have their reputation for thread safety.

### 3.6 When the GIL is released

Collecting the mechanism into a list, now that each entry has been demonstrated:

**Around blocking syscalls.** `time.sleep`, socket reads and writes, file I/O, `subprocess` waits. The thread is not executing Python, so it drops the stick. This is why the I/O measurement hit 7.97×.

**At eval-breaker checkpoints, after the switch interval has elapsed.** Loop back-edges and function calls, per §3.4. Not between arbitrary bytecodes.

**Explicitly, by C extensions.** This is the one most people miss and it has the largest practical consequence. A C extension can wrap a long computation in `Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS`, releasing the GIL while it works in C and reacquiring it before touching any Python object. **NumPy, Polars, DuckDB and PyArrow all do this** around their compute kernels.

The consequence is the single most useful practical rule in this module: a NumPy operation over a large array *does* parallelise across threads, because the GIL is released for its duration, while the equivalent Python `for` loop does not. Which is why **vectorising often beats parallelising** — you get the C speed and the parallelism together, with none of the process-boundary costs. Reaching for `multiprocessing` on a Pandas workload that should have been one vectorised expression means paying pickling costs to parallelise work that should not have been a Python loop.

---

## 4. Break it on purpose

### 4.1 The pool that made nothing faster

The failure in §1, now with the diagnosis.

```python
# Gist: pointless_pool.py
with ThreadPoolExecutor(max_workers=8) as pool:
    totals = list(pool.map(reconcile, batches))
```

```text
  serial       1.88s   (1.00x)
  8 threads    1.87s   (1.00x)
```

Nothing raised. No error, no warning, no degradation. The code is more complex than the serial version, harder to debug, and has introduced the possibility of races — and it is exactly as fast.

This is the most common concurrency mistake in Python and it is invisible precisely because it *works*. The tests pass. The output is correct. Only a measurement reveals that the entire abstraction bought nothing.

The fix is `ProcessPoolExecutor`, which measured 3.47×, and the cost is real: arguments and return values must be picklable, process startup is not free, and on macOS the `spawn` start method re-imports your module. Those costs are the subject of [module 03](00_knowledge_graph.md).

**Run this one yourself.** Swapping `Thread` for `Process` in a one-line change and watching the wall-clock drop from 1.87 to 0.54 is the moment the GIL stops being an abstraction.

### 4.2 The property that ate the deposits

§3.5's result, framed as the bug it would actually be.

```python
# Gist: g6_real.py
class Account:
    @property
    def prop_balance(self): return self._p
    @prop_balance.setter
    def prop_balance(self, v): self._p = v

# 4 threads, 100,000 increments each, via acct.prop_balance += 1
```

```text
  obj.prop_balance += 1   lost  236,574 of 400,000  (59.14%)
```

Four hundred thousand deposits went in. **A hundred and sixty-three thousand came out.** In a financial system this is not a bug, it is an incident.

And the developer who wrote it did nothing unusual. They used a property — the most ordinary encapsulation in Python — on a counter shared between threads. The identical code with a plain attribute loses nothing, which means the bug can appear when someone *refactors an attribute into a property* for validation, months after the threading was written, in a change that looks entirely unrelated.

The fix is a lock around the read-modify-write, and its cost is contention: every thread now serialises on that lock, so if the increment is hot you have removed the parallelism you were trying to get. The better fix is usually to not share the counter — give each thread its own and combine at the end, or use a `queue.Queue`.

### 4.3 The thread safety you cannot rely on

The dangerous half of "built-ins are thread-safe."

```text
  list.append (C call)    lost 0 of 400,000  -> append IS safe
  d['k'] += 1             lost 0 of 400,000
```

Both safe. Both safe **by accident of implementation**, not by contract.

`list.append` is safe because it is one C call with no checkpoint inside it. `d['k'] += 1` is safe because no eval-breaker point falls between its load and store on this interpreter. Neither is documented as atomic. Neither is guaranteed by the language.

Three things break these guarantees, and all three are foreseeable:

**A different implementation.** PyPy, Jython and GraalPy have no GIL and different atomicity properties entirely.

**A free-threaded build.** PEP 703 removes the GIL, and code that was accidentally safe stops being safe. This is not hypothetical — free-threaded builds ship alongside the default now.

**A refactor.** §4.2 is the demonstration: turning an attribute into a property introduced a checkpoint and destroyed the guarantee, in a change that had nothing to do with threading.

The rule I would defend: **if correctness depends on an operation being atomic, make it atomic explicitly** — with a lock, or by not sharing the state. Relying on the GIL is depending on an implementation detail that the language is actively working to remove.

---

## 5. The judgment call

### The options, honestly costed

| Approach | Use when | Because | Real cost |
|---|---|---|---|
| **Serial** | The work is small, or already fast | No coordination, no races, trivially debuggable | Leaves I/O concurrency on the table |
| **Threads** | Waiting on I/O — network, disk, database | GIL released during the wait; **measured 7.97×** on 8 jobs | Shared memory means races; each thread costs a real OS stack |
| **`asyncio`** | Many concurrent I/O operations, thousands not dozens | One thread, far cheaper per task than a thread | Whole call stack must be async; one blocking call stalls everything ([module 04](00_knowledge_graph.md)) |
| **Processes** | CPU-bound pure-Python work | Own interpreter, own GIL, true parallelism; **measured 3.47×** | Pickling, startup, no shared objects, `spawn` re-imports on macOS |
| **Vectorise (NumPy/Polars/DuckDB)** | CPU-bound numeric work over arrays | The C kernel **releases the GIL**, so you get C speed *and* parallelism | A dependency and a data-conversion boundary; no help for non-numeric work |
| **Free-threaded build** | Experimenting with genuine thread parallelism | No GIL at all | Single-threaded penalty, C extensions need rebuilding, ecosystem still catching up |

### When you would not do this

**Do not reach for `multiprocessing` before checking whether you can vectorise.** This is the recommendation I would defend hardest for the data work on this CV. The measured process speedup was 3.47×, and it cost pickling, startup and a `__main__` guard. A vectorised NumPy or Polars expression releases the GIL *and* runs in C, frequently beating the process pool with none of the ceremony. Paying serialisation costs to parallelise a loop that should not have been a Python loop is a real and common mistake.

**Do not add threads to CPU-bound code, ever.** §4.1 measured 1.00×. There is no scenario in which pure-Python CPU work benefits from threading under the GIL, and the added complexity is pure cost — including the race in §4.2 that you did not previously have.

**Do not rely on the GIL for correctness.** §4.3. It is an implementation detail of one interpreter, it is being removed, and a routine refactor can silently withdraw the protection.

**Do not assume processes scale linearly.** The honest number was 3.47× on eight cores, not 8×. Startup, serialisation and heterogeneous cores all take a cut. If someone asks how much faster a process pool will make something, "I'd measure it, and I'd expect meaningfully less than the core count" is a better answer than a theoretical multiple.

---

## 6. Interview angles

**"What is the GIL?"**

> A single lock that has to be held to execute Python bytecode, so only one thread runs Python at a time. But I'd push back gently on how the question is usually framed, because the interesting part isn't what it prevents, it's what it protects. CPython reclaims memory with reference counting, and every assignment and function call touches refcounts constantly. Those counts are plain integers, and incrementing one isn't atomic at the machine level — so without a lock, two threads racing on the same refcount either leak the object or free it while something still points at it, which in C is a use-after-free rather than a wrong number. So the GIL keeps the interpreter's own bookkeeping consistent, and the single-core limitation is a consequence of that, not the goal. Framed that way it's a trade rather than a flaw: CPython bought fast single-threaded refcounting and a simple C API, and paid in parallelism. Every runtime pays somewhere — atomic refcounts cost you on every operation including the common single-threaded case, tracing GC gives you pauses and a harder C API, and JavaScript and Erlang avoid the problem by not sharing objects at all.

**"So Python's built-in types are thread-safe?"**

> Yes, and I'd be careful about that yes, because it's true by accident rather than by contract. I measured it: four threads doing four hundred thousand `list.append` calls lose nothing, and `d['k'] += 1` loses nothing either. The reason is that the interpreter only checks whether to switch threads at specific points — loop back-edges and function calls — not between arbitrary bytecodes. `list.append` is one C call with no checkpoint inside it, so it completes atomically. But none of that is documented or guaranteed. It breaks on PyPy, it breaks on a free-threaded build, and — this is the one that actually bit me in the experiment — it breaks on an ordinary refactor. I ran `obj.balance += 1` across four threads and lost zero updates. Then I changed `balance` from a plain attribute to a `@property` and lost fifty-nine percent of four hundred thousand increments. A property's getter and setter are Python functions, function calls are checkpoints, so introducing a property introduces the race. Same syntax at the call site, completely different concurrency behaviour. So my rule is: if correctness depends on atomicity, make it atomic explicitly with a lock or don't share the state — don't lean on the GIL, because the language is actively working to remove it.

**"Is `x += 1` atomic?"**

> Not by contract, and this is one where I'd give you a more precise answer than the usual one. It compiles to four instructions — load, load constant, add, store — so it's decomposable, and everyone stops there and says a thread switch can land between any two of them. I tried to reproduce that on 3.14 and I couldn't. Sixteen threads, four hundred thousand increments, switch interval forced down to one nanosecond, and I lost exactly zero updates, every run. What's actually going on is that the interpreter checks the eval breaker at loop back-edges and calls, and there's no such checkpoint inside that four-instruction sequence — so it's effectively atomic on this interpreter even though it isn't atomic in principle. Then I put a function call between the read and the write and immediately lost fifty-five percent. So the honest answer is: it's not atomic, it's four operations, and on current CPython it happens to be uninterrupted — but anything that introduces a call between the load and the store, which includes a property, a `__getitem__` on a custom class, or a free-threaded build, turns it into a real race instantly. I'd never rely on the accident.

**"How would you speed up a batch job that's taking forty minutes?"**

> First I'd find out whether it's actually CPU-bound, because that decides everything else and it's cheap to check. If it's waiting on a database or an API, threads or asyncio will help a lot — I measured eight I/O-bound jobs going from four seconds to half a second with a thread pool, near-perfect scaling, because the GIL is released during any blocking syscall. If it's genuinely CPU-bound in Python, then threads do literally nothing: I measured eight threads on eight CPU-bound jobs at 1.00×, identical to serial, and that's the failure mode I'd watch for because it doesn't error, it just silently buys you nothing while making the code harder to reason about. For real CPU-bound work my first move isn't a process pool though — it's asking whether the loop should be a loop. NumPy, Polars and DuckDB release the GIL around their C kernels, so a vectorised expression gets you both the C speed and the parallelism with none of the pickling. Process pools work — I measured 3.47× — but note that's on eight cores, not 8×, because you pay startup and serialisation and the cores aren't uniform. I'd want to be straight that this is knowledge I went and built rather than production experience: the concurrency in my own work was I/O concurrency inside FastAPI, and on the pipeline side Beam owned the parallelism, so that was the runner's job rather than mine. I can reason about the CPU-bound decision and I'd validate it with measurements, but I'd be doing it in production for the first time.

---

## 7. To add to `RECALL.md`

- The GIL protects **interpreter bookkeeping — chiefly reference counts**. Single-core execution is the *consequence*, not the purpose
- Without it, a lost refcount decrement is a **use-after-free**, not a wrong number
- Every runtime pays: atomic refcounts cost the single-threaded case, tracing GC gives pauses, JS/Erlang avoid it by **sharing nothing**
- Measured on 8 cores: CPU-bound **serial 1.88s · 8 threads 1.87s (1.00×) · 8 processes 0.54s (3.47×)**
- Measured: I/O-bound **serial 4.03s · 8 threads 0.51s (7.97×)** — the GIL is released around blocking syscalls
- Processes gave **3.47× on 8 cores, not 8×** — startup, pickling, and heterogeneous cores. Quote the real number
- **The eval breaker:** the interpreter only considers switching at **loop back-edges and calls**, not between arbitrary bytecodes
- `sys.getswitchinterval()` = 0.005s is a **minimum before a switch is requested**, not a guarantee of when one happens
- **Negative result:** 16 threads, 400k increments, switch interval 1e-9 → **zero lost**. Plain `+=` has no checkpoint inside it
- Add one **function call** between read and write → **55% lost**. Add a **`@property`** → **59% lost of 400,000**
- A property's getter/setter are Python functions → `CALL` → checkpoint. **Refactoring an attribute into a property introduces the race**
- `list.append` is safe because it is **one C call**; `d['k'] += 1` is safe because no checkpoint falls inside. **Both by accident, neither by contract**
- Accidental safety breaks on **PyPy, free-threaded builds, and ordinary refactors**
- C extensions release the GIL explicitly — **NumPy, Polars, DuckDB, PyArrow**. So **vectorise before you parallelise**: C speed *and* parallelism, no pickling

---

← [Concurrency knowledge graph](00_knowledge_graph.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
