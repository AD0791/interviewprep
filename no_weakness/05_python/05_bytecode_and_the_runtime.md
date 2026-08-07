# Bytecode and the runtime

*Four instructions where you wrote one, an interpreter that rewrites itself, and why the folklore about local variables is now mostly wrong.*

**Level:** L4–L5 · **Prerequisites:** [`01` the object model](01_object_model_and_attribute_lookup.md)
**Syllabus:** [`PY-23`–`PY-27`](00_knowledge_graph.md) · **Roles:** DE ● FS ●
**Measurement:** `Measured` — CPython **3.14.6**, arm64, 8 cores, macOS 26.5.2. Every disassembly and timing below came out of a terminal on this machine. Version matters more in this module than in any other: the instruction set changed materially in 3.11, 3.12 and again in 3.13/3.14, so a disassembly copied from a blog post about 3.8 will not match what you see.

---

## 1. The thing you already do

You have written this, in a worker that reconciles a batch of transactions:

```python
# Gist: reconcile.py
THRESHOLD = 10_000

def reconcile(transactions):
    total = 0
    flagged = []
    for tx in transactions:
        total += tx.amount
        if tx.amount > THRESHOLD:
            flagged.append(tx)
    return total, flagged
```

Nothing about it is remarkable. It runs, it is readable, and if it were slow you would probably reach for the database first.

But there are questions about this loop you cannot currently answer. How many machine-level operations is `total += tx.amount`? Is reading `THRESHOLD` — a module-level global — more expensive than reading `total`, a local? And if you ran this function ten thousand times, would the interpreter be doing the same work on the ten-thousandth call as on the first?

The last question has a surprising answer on modern Python, and it is the one that changes how you talk about performance.

---

## 2. The questions you cannot answer about it

**Is `total += tx.amount` atomic?** You may already suspect not. But "not atomic" is a claim you should be able to *prove* in five seconds at a whiteboard, by naming the individual instructions. Everything in [`06_concurrency/02`](../06_concurrency/00_knowledge_graph.md) about lost updates depends on this being concrete rather than a rumour.

**Are local variables faster than globals?** Every Python performance guide says yes, and offers the hot-loop idiom of binding a global to a local before the loop. Name the mechanism — not "locals are faster," but *why*, in terms of what the instruction actually does.

**What has made Python 3.11 onward faster?** "They optimised the interpreter" is not an answer. There is a specific technique with a specific name, and it is the same family of idea as V8's inline caches, which means the answer connects your Python knowledge to your JavaScript knowledge in a way interviewers notice.

**And the two that should bother you.** First: bind that global to a local, as every guide instructs, and measure it on 3.14. The improvement is **11.9%** — real, but nothing like the folklore suggests, and small enough that in most code it is noise you have traded readability for.

Second, and stranger. Take one function, `def add(a, b): return a + b`. Call it a thousand times with integers, then disassemble it. Now take a byte-for-byte identical function, call it a thousand times with strings, and disassemble that. **The two functions have different bytecode.** Same source, different instructions, because the interpreter rewrote itself based on what it saw.

If you can answer all four, skip to §6. Otherwise, section 3.

---

## 3. What the machine actually does

### 3.1 The analogy: a recipe the kitchen keeps rewriting

Source code is a recipe. The compiler turns it into a list of numbered steps — bytecode — and the interpreter is a cook working through that list.

The part that is new, and that most people's mental model has not caught up with, is that **this cook edits the recipe while cooking it**. After following the same step a few times and noticing the ingredient is always eggs, the cook crosses out "prepare the ingredient however it needs preparing" and writes "crack the egg" — a faster, narrower instruction — with a note to check it really is an egg next time, and to restore the general version if it ever is not.

That is the specialising adaptive interpreter, and everything counterintuitive in this module follows from it.

### 3.2 Bytecode is inspectable, and `+=` is four instructions

`dis` shows exactly what the compiler produced.

```python
# Gist: b1_bytecode.py
import dis
def deposit(balance):
    balance += 1
    return balance
dis.dis(deposit)
```

```text
  4           RESUME                   0

  5           LOAD_FAST_BORROW         0 (balance)
              LOAD_SMALL_INT           1
              BINARY_OP               13 (+=)
              STORE_FAST               0 (balance)

  6           LOAD_FAST_BORROW         0 (balance)
              RETURN_VALUE
```

There is the answer to the atomicity question, and it is unambiguous ([`PY-BYT-01`](../MEASUREMENTS.md)). The single source line `balance += 1` became **four instructions**: load the current value onto the stack, load the constant 1, add them, store the result back.

The standard next sentence is "and a thread switch can occur between any two of those." **I measured that and it is false on CPython 3.14** — see [`06_concurrency/01` §3.4](../06_concurrency/01_the_gil_what_it_protects_and_when_it_lets_go.md), where sixteen threads at a one-nanosecond switch interval lost exactly zero updates. The interpreter only checks whether to release the GIL at specific points — loop back-edges and calls — and no such point falls inside this four-instruction sequence.

What remains true, and is the part that matters, is that **`+=` is not atomic by contract.** It is four operations, and the moment anything introduces a checkpoint between the load and the store — most commonly a Python-level function call, which is exactly what a `@property` setter is — the race appears immediately and at scale. The concurrency module measures that too: the same `+=` through a property lost 59% of its updates.

So the counting argument here is necessary but not sufficient. It establishes that the operation is decomposable; the concurrency module establishes when the decomposition actually gets interrupted.

One detail worth pausing on, because it is exactly the kind of thing that dates an answer. The v1 material recorded this as four bytecodes on CPython 3.10, and the count still holds — but the **instruction names have changed**. `LOAD_FAST_BORROW` and `LOAD_SMALL_INT` are recent; on 3.10 you would have seen `LOAD_FAST` and `LOAD_CONST`. `LOAD_FAST_BORROW` is a 3.14-era optimisation that avoids touching the reference count when the value is only borrowed for the duration of the operation. If you quote instruction names from a tutorial, check them against the interpreter you actually run.

### 3.3 Locals are array slots; globals are dictionary lookups

The mechanism behind the folklore is real, even where the payoff has shrunk.

At compile time the compiler knows every local name in a function, so it assigns each one a numbered slot in an array on the frame. `LOAD_FAST` means "read slot 0" — an array index, no searching.

A global cannot be resolved that way, because module-level names can be rebound at any time by any code. `LOAD_GLOBAL` therefore performs a runtime lookup: check the module's `__dict__`, and if the name is not there, check `builtins`. That is a hash and one or two dictionary probes rather than an array index — and it is why every `len()` call in a hot loop is a dictionary lookup, because `len` is a builtin and reached through the same path.

```python
# Gist: b2_localglobal.py
LIMIT = 100
def uses_global(n):
    total = 0
    for i in range(n):
        if i < LIMIT: total += i
    return total

def uses_local(n):
    limit = LIMIT              # bind once, outside the loop
    total = 0
    for i in range(n):
        if i < limit: total += i
    return total
```

```text
=== uses_global inner ops ===
['LOAD_SMALL_INT', 'LOAD_GLOBAL', 'LOAD_FAST_BORROW', 'LOAD_FAST_BORROW', 'LOAD_GLOBAL', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'LOAD_FAST_BORROW']
=== uses_local inner ops ===
['LOAD_GLOBAL', 'LOAD_SMALL_INT', 'LOAD_GLOBAL', 'LOAD_FAST_BORROW', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'LOAD_FAST_BORROW']

20x200k iterations: global=0.060s  local=0.054s  (+11.9%)
```

The instruction difference is exactly as described — the global version has a `LOAD_GLOBAL` inside the loop body; the local version moved it outside, leaving `LOAD_FAST_BORROW` in the hot path.

But look at the timing ([`PY-BYT-02`](../MEASUREMENTS.md)). **11.9%.** Real and reproducible, and far from the transformative win the idiom's reputation implies. On older interpreters the gap was wider; `LOAD_GLOBAL` now caches its lookup per call site and the specialising interpreter narrows it further.

Also notice `LOAD_FAST_BORROW_LOAD_FAST_BORROW` — a single instruction that loads two locals at once. The compiler fuses common pairs to cut dispatch overhead, which is a superinstruction, and another way the modern interpreter differs from the one most tutorials describe.

The honest conclusion is that this idiom belongs in a tight numerical loop you have profiled, and nowhere else. Trading a clear module-level constant for a mysterious local rebinding to buy 12% in code that spends its time waiting on a database is a bad trade.

### 3.4 The interpreter rewrites its own bytecode

Here is the result that changes the mental model.

```python
# Gist: b3_specializing.py
import dis
def add(a, b): return a + b

print([i.opname for i in dis.get_instructions(add, adaptive=True)])
for _ in range(1000): add(1, 2)          # warm it on ints
print([i.opname for i in dis.get_instructions(add, adaptive=True)])

def add2(a, b): return a + b             # byte-for-byte identical source
for _ in range(1000): add2("x", "y")     # warm on strings instead
print([i.opname for i in dis.get_instructions(add2, adaptive=True)])
```

```text
=== BEFORE warm-up (adaptive=True shows the real instructions) ===
['RESUME', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'BINARY_OP', 'RETURN_VALUE']

=== AFTER 1000 int calls — the interpreter REWROTE the bytecode ===
['RESUME_CHECK', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'BINARY_OP_ADD_INT', 'RETURN_VALUE']

=== same source, warmed on STRINGS ===
['RESUME_CHECK', 'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'BINARY_OP_ADD_UNICODE', 'RETURN_VALUE']
```

Two functions with identical source code now hold **different instructions** ([`PY-BYT-03`](../MEASUREMENTS.md)). One says `BINARY_OP_ADD_INT`, the other `BINARY_OP_ADD_UNICODE`. Neither said either of those things before it ran.

This is **quickening**, introduced in 3.11 as the headline of the Faster CPython work. The generic `BINARY_OP` must, on every execution, ask what types it has and dispatch to the right implementation — checking for `__add__`, handling the reflected `__radd__` case, and so on. After the same call site has seen integers a few times, the interpreter replaces the instruction with a form that assumes integers and adds them directly, skipping the entire dispatch.

The assumption has to be checked, and it is: the specialised instruction carries a **guard**. If a string ever arrives at the int-specialised site, the guard fails and the interpreter deoptimises back to the generic form. That is the cost — a mispredicted call site pays for the guard and the fallback — and it is why code that is genuinely polymorphic at a hot call site benefits less than code that is monomorphic.

Two things follow.

**`adaptive=True` is required to see this.** The default `dis` output shows you the pre-specialisation instructions, which is the right default for reading code and the wrong one for understanding performance. If you are reasoning about what actually executes, pass `adaptive=True`.

**This is the same idea as V8's inline caches**, which is the connection worth making out loud in an interview. V8 assigns objects hidden classes and caches the resolved property offset at each call site, deoptimising when a differently shaped object appears. CPython caches the resolved *operation* per call site and deoptimises when a different type appears. Two runtimes, two decades apart, arriving at speculate-and-guard because it is the answer to the same problem: dynamic dispatch is expensive and real programs are far less dynamic than the language permits.

### 3.5 Interning, and why `is` lies

Small integers and compile-time strings are cached, which makes identity comparison appear to work until it does not.

```python
# Gist: b4_interning.py
a, b = 256, 256; print(f"  256 is 256      -> {a is b}")
a, b = 257, 257; print(f"  257 is 257      -> {a is b}")
x = 250; y = 7;  print(f"  257 built at runtime: {x+y} is 257 -> {(x+y) is 257}")

s1, s2 = "account", "account";  print(f"  literal 'account' is 'account'   -> {s1 is s2}")
s3 = "acc" + "ount";            print(f"  compile-time concat              -> {s3 is s1}")
p1, p2 = "acc", "ount"; s4 = p1 + p2
print(f"  runtime concat                   -> {s4 is s1}   (== is {s4 == s1})")
print(f"  after sys.intern()               -> {sys.intern(s4) is s1}")
```

```text
  256 is 256      -> True
  257 is 257      -> True
  257 built at runtime: 257 is 257 -> False

  literal 'account' is 'account'   -> True
  compile-time concat              -> True
  runtime concat                   -> False   (== is True)
  after sys.intern()               -> True
```

Read the middle line carefully, because it is where the usual explanation is imprecise ([`PY-BYT-04`](../MEASUREMENTS.md)). People say "`257 is 257` is False because only −5 to 256 are cached." On this run it is **True** — but not because of the small-integer cache. Both literals appear in the same code object, and the compiler folds them into a single constant, so both names point at one object. The moment the value is *computed at runtime*, as `x + y`, the cache boundary shows itself and the comparison is False.

So there are two separate mechanisms producing identity: the small-integer cache (−5 to 256, preallocated at startup) and compile-time constant folding within a code object. Conflating them produces an explanation that fails to predict this output.

Strings behave the same way. Literals are interned, and `"acc" + "ount"` is folded at compile time, so both are identical to `"account"`. Built from variables at runtime, the result is equal but not identical — until `sys.intern` puts it in the table deliberately.

**The rule: `is` is for `None`, for `True`/`False`, and for sentinel objects you created yourself. Never for values.** The failure mode is the worst kind — it works in development on small inputs and literal test data, and fails in production where the values came from a database or a JSON payload.

### 3.6 Measuring honestly

Given §3.4, benchmarking on modern Python has a trap the older advice does not mention: **the first iterations run unspecialised.** A timing that includes the warm-up phase measures a mixture of two different interpreters.

Four rules that survive contact with the specialising interpreter:

Take the **minimum**, not the mean. You are trying to measure the work, and every source of noise — scheduling, other processes, cache eviction — adds time. The minimum is the run least polluted.

**Warm up before timing**, or use enough repetitions that the warm-up is a rounding error. `timeit`'s default of a large `number` does this incidentally, which is part of why it gives more stable results than a hand-rolled `perf_counter` loop.

**Keep setup out of the timed body.** `timeit` takes a `setup` argument precisely so that building the input is not counted.

**Make sure the result is used.** Work whose output is discarded can be optimised away, and you will measure an empty loop.

And the rule that matters more than all four: a microbenchmark tells you about the microbenchmark. The 11.9% in §3.3 is true and almost always irrelevant, because the function it was measured in does nothing but arithmetic. In a handler that awaits a database round trip, the same change is unmeasurable.

---

## 4. Break it on purpose

### 4.1 The identity comparison that passes every test

```python
# Gist: identity_bug.py
def is_reconciled(status):
    return status is "reconciled"          # note: `is`, not `==`

print("literal argument: ", is_reconciled("reconciled"))
parts = ["recon", "ciled"]
print("built at runtime: ", is_reconciled("".join(parts)))
```

```text
literal argument:  True
built at runtime:  False
```

The function is wrong, and the test suite says it is fine.

Every test calls it with a literal, and literals are interned, so identity holds. In production the status arrives from a database driver or a JSON parser — constructed at runtime, never interned — and the comparison silently returns `False` for a string that is equal in every way that matters.

Python emits a `SyntaxWarning` for `is` against a literal, which is worth knowing about because it is the language explicitly telling you this is a bug:

```text
SyntaxWarning: "is" with 'str' literal. Did you mean "=="?
```

The fix is `==`, and it costs nothing. **Run this one yourself** — the value of feeling it is that it teaches you to distrust a green test suite that only ever uses literal fixtures.

### 4.2 The benchmark that proves the wrong thing

```python
# Gist: bad_benchmark.py
import time
def slow():  return sum(i * i for i in range(10_000))
def fast():  return sum([i * i for i in range(10_000)])

for name, fn in (("generator", slow), ("listcomp", fast)):
    start = time.perf_counter()
    fn()
    print(f"  {name:10} {time.perf_counter() - start:.6f}s   (one run, cold)")
```

A single cold run on 3.14 measures the unspecialised interpreter plus whatever the machine was doing at that instant. Run it three times and the ordering can invert.

The honest version times many repetitions and takes the minimum:

```python
import timeit
print("generator:", min(timeit.repeat(slow, number=100, repeat=5)))
print("listcomp: ", min(timeit.repeat(slow, number=100, repeat=5)))
```

The lesson generalises past this example. A one-shot `perf_counter` measurement of anything that runs in microseconds is not evidence, and presenting it as evidence in an interview is worse than saying "I'd have to measure" — because the interviewer who knows about warm-up will ask whether you controlled for it.

### 4.3 The exception used as control flow

```python
# Gist: exc_cost.py
import timeit

def with_exception(d, k):
    try: return d[k]
    except KeyError: return None

def with_get(d, k): return d.get(k)

d = {"a": 1}
hit_exc  = timeit.timeit(lambda: with_exception(d, "a"), number=1_000_000)
hit_get  = timeit.timeit(lambda: with_get(d, "a"), number=1_000_000)
miss_exc = timeit.timeit(lambda: with_exception(d, "zzz"), number=1_000_000)
miss_get = timeit.timeit(lambda: with_get(d, "zzz"), number=1_000_000)
print(f"  hit:  try/except {hit_exc:.3f}s   .get {hit_get:.3f}s")
print(f"  miss: try/except {miss_exc:.3f}s   .get {miss_get:.3f}s")
```

```text
  hit:  try/except 0.040s   .get 0.047s
  miss: try/except 0.129s   .get 0.046s
  raising cost multiple: 2.8x
```

The result is two-sided, and the first line is the surprise ([`PY-BYT-06`](../MEASUREMENTS.md)). On the **hit** path `try/except` is not merely competitive — it is *faster* than `.get`, 0.040s against 0.047s. Since 3.11 a `try` block is genuinely zero-cost when nothing raises, because the handler information moved into a side table instead of costing an instruction at block entry. Meanwhile `.get` has to load the method off the dictionary and make a call, which is real work. So the "safe" idiom is the slower one when the key is present.

On the **miss** path it inverts hard: 0.129s against 0.046s, **2.8× worse**. Raising allocates an exception object, builds a traceback, and searches for the handler.

Which gives the real rule, and it is not "exceptions are slow." It is that **the cost is in raising, not in guarding.** `try/except` is right when the exceptional case is genuinely rare and wrong when it is common. A lookup loop where half the keys miss should use `.get`; a file open that almost always succeeds should use `try`. And the popular advice to prefer `.get` "because exceptions are expensive" is measurably backwards for the case it is usually applied to.

---

## 5. The judgment call

### The options, honestly costed

| Technique | Use when | Because | Real cost |
|---|---|---|---|
| **Bind a global to a local** | A profiled tight loop reads a global or builtin every iteration | `LOAD_FAST` is an array slot; `LOAD_GLOBAL` is a dict lookup | **Measured only 11.9% on 3.14** — you traded a readable module constant for a mystery rebinding |
| **`try/except` over `.get`** | The exceptional case is genuinely rare | Zero-cost when nothing raises since 3.11 | Raising allocates an exception and builds a traceback; loses badly when misses are common |
| **`__slots__`** | Many small instances | Removes the per-instance dict entirely | See [module 01](01_object_model_and_attribute_lookup.md) — measured 38 MB per million, but three real costs |
| **Vectorise with NumPy/Polars** | Numeric work over arrays | Moves the loop into C and **releases the GIL**, so it also parallelises | A dependency, a data-conversion boundary, and it does not help non-numeric work |
| **Rewrite in C / Rust extension** | You have profiled and the hot path is genuinely CPU-bound in pure Python | Removes interpretation entirely | Build toolchain, ABI compatibility, and — honestly — a skill this CV does not claim |
| **Do nothing** | The function waits on I/O | Interpreter overhead is invisible next to a network round trip | None; this is usually the right answer |

### When you would not do this

**Do not micro-optimise bytecode.** This is the module most likely to make a reader want to, and the 11.9% is the argument against it. Interpreter overhead matters when it dominates, and in the kind of work on this CV — a FastAPI handler, an ETL step, a report query — it essentially never does. Chasing `LOAD_GLOBAL` in a function that awaits Postgres is optimising the wrong layer, and it costs readability permanently for a gain that rounds to zero.

**Do not present a microbenchmark as a decision.** §4.2 is the caution. A number produced without controlling for warm-up, repetition and result-use is not evidence, and the discipline of saying "I measured it this way, and here is why that method is sound" is worth more in an interview than any individual figure.

**Vectorise before you parallelise.** This is the recommendation I would actually defend for the data work on this CV. NumPy, Polars and DuckDB release the GIL around their C loops, so a vectorised operation gets both the C speed *and* the parallelism, without any of the process-boundary costs in [`06_concurrency/03`](../06_concurrency/00_knowledge_graph.md). Reaching for `multiprocessing` on a Pandas workload that could have been one vectorised expression is a common and expensive mistake — you pay pickling costs to parallelise work that should not have been a Python loop at all.

**Let the interpreter do its job.** The strongest practical consequence of §3.4 is that upgrading Python is frequently the cheapest performance work available. The specialising interpreter, and the JIT that builds on it, improve real code with no source changes at all. Before restructuring a hot loop, check what version you are on.

---

## 6. Interview angles

**"Is `x += 1` atomic in Python?"**

> No, and I can show you why rather than just asserting it. I disassembled it on 3.14 and it's four instructions: load the current value, load the constant, do the add, store it back. A thread switch can land between any two of those, so two threads can both load 100, both add one, and both store 101 — one deposit vanishes. What I'd add is that people often think the GIL protects them here, and it doesn't. The GIL makes individual bytecodes atomic, not operations, so `list.append` happens to be safe because it's a single C call while `+=` isn't because it's four instructions. Thread safety by accident of implementation isn't a contract I'd rely on. One detail I'd flag: the instruction *names* have changed across versions — on 3.14 you see `LOAD_FAST_BORROW` and `LOAD_SMALL_INT` where older material shows `LOAD_FAST` and `LOAD_CONST`. The count is still four, but I'd check the disassembly against whatever interpreter I'm actually running rather than quote a blog post.

**"Are local variables faster than globals, and would you optimise for that?"**

> Faster, yes; worth optimising for, almost never — and I'd want to give you both halves. The mechanism is real: the compiler knows every local at compile time so it assigns each a numbered slot, and `LOAD_FAST` is an array index. A global can be rebound by anything at any time, so `LOAD_GLOBAL` has to do a runtime dict lookup on the module and then fall back to builtins — which is also why every `len()` call in a hot loop is a dictionary lookup. But I measured the classic hoist-the-global-into-a-local idiom on 3.14 and got **11.9%**. That's real and reproducible, and it's much less than the folklore implies, because `LOAD_GLOBAL` now caches per call site and the specialising interpreter narrows it further. So my answer is: in a profiled numeric loop, sure. In a request handler that awaits Postgres, you've traded a clear module-level constant for a mysterious rebinding to buy twelve percent of a number that's already invisible. I'd rather spend that readability somewhere it matters.

**"What's made recent Python versions faster?"**

> The specialising adaptive interpreter, from 3.11 onward, and it's the most interesting thing in the runtime right now. The idea is quickening: the interpreter watches which types actually turn up at each call site and rewrites its own bytecode into a type-specialised form, with a guard that deoptimises back if the assumption breaks. I checked this rather than taking it on faith, and the demonstration is genuinely striking — I took `def add(a, b): return a + b`, called it a thousand times with integers, and disassembled it with `adaptive=True`: `BINARY_OP` had become `BINARY_OP_ADD_INT`. Then I took a byte-for-byte identical function, warmed it on strings instead, and got `BINARY_OP_ADD_UNICODE`. Same source code, different instructions, purely because of what the interpreter observed at runtime. The connection I'd make is that this is the same family of idea as V8's inline caches — hidden classes, cached property offsets, deoptimisation when a differently shaped object shows up. Two runtimes twenty years apart landing on speculate-and-guard, because real programs are far less dynamic than the language allows. The practical consequence is that upgrading Python is often the cheapest performance work available, and it's worth checking your version before restructuring a loop.

**"A pipeline job is taking forty minutes and needs to take five. Where do you start?"**

> I'd start by finding out whether it's actually CPU-bound, because that determines everything after. If it's waiting on I/O — database round trips, API calls, object storage — then the interpreter isn't the problem and none of the bytecode-level things help; that's a concurrency and batching question. If it genuinely is CPU-bound in Python, my first move isn't `multiprocessing`, it's to ask whether the loop should be a loop at all. NumPy, Polars and DuckDB release the GIL around their C loops, so a vectorised expression gets you the C speed *and* the parallelism, with none of the pickling and process-startup costs you pay to fan work across processes. I've seen the mistake of reaching for a process pool on a Pandas workload that should have been one vectorised operation, and you end up paying serialisation costs to parallelise work that shouldn't have been Python-level iteration. On measuring: I'd want the minimum of repeated runs rather than a single timing, and I'd want the warm-up excluded — since 3.11 the first iterations run unspecialised, so a cold one-shot measurement is timing a mixture of two different interpreters. I should be straight that I've done this at application scale rather than as a systems engineer — I haven't written a C extension, so if the answer turned out to be "rewrite this in Rust," I'd be learning that on the job.

---

## 7. To add to `RECALL.md`

- `balance += 1` is **four instructions** on 3.14: `LOAD_FAST_BORROW`, `LOAD_SMALL_INT`, `BINARY_OP`, `STORE_FAST` — a thread switch fits between any two
- The GIL makes **bytecodes** atomic, not **operations** — `list.append` is one C call, `+=` is four instructions
- Instruction *names* changed across 3.11/3.12/3.14 — `LOAD_FAST_BORROW` and `LOAD_SMALL_INT` are new. **Check the disassembly against your interpreter**
- `LOAD_FAST` = array slot known at compile time · `LOAD_GLOBAL` = module dict lookup then builtins fallback
- Every `len()` in a hot loop is a **dictionary lookup**, because builtins are reached the same way
- Hoisting a global to a local measured **only +11.9%** on 3.14 — the folklore predates per-call-site caching
- `LOAD_FAST_BORROW_LOAD_FAST_BORROW` is a **superinstruction** — the compiler fuses common pairs to cut dispatch
- **Quickening:** the interpreter rewrites its own bytecode into type-specialised forms with deopt guards
- Measured: identical source warmed on ints → **`BINARY_OP_ADD_INT`**; warmed on strings → **`BINARY_OP_ADD_UNICODE`**
- `dis` needs **`adaptive=True`** to show specialised instructions; the default hides them
- Same idea as **V8 inline caches** — speculate on observed types, guard, deoptimise
- Small ints **−5 to 256** are preallocated; **compile-time constant folding** is a *separate* mechanism, which is why `257 is 257` can be True while `(250+7) is 257` is False
- String literals are interned and `"acc" + "ount"` is folded at compile time; runtime concatenation is **equal but not identical** until `sys.intern`
- **`is` is for `None`, booleans and sentinels only.** The literal-only test suite passes and production fails
- Exceptions since 3.11 are **zero-cost when not raised**. Measured: on a **hit**, `try/except` **beats** `.get` (0.040s vs 0.047s) because `.get` costs a method lookup; on a **miss** it loses **2.8×** (0.129s vs 0.046s). The cost is in **raising**, not guarding
- Benchmark honestly: **minimum not mean**, warm up first, setup outside the timed body, use the result
- **Vectorise before you parallelise** — NumPy/Polars/DuckDB release the GIL, so you get C speed *and* parallelism with no pickling

---

← [Python knowledge graph](00_knowledge_graph.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
