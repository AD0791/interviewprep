# MEASUREMENTS

*Every number quoted anywhere in this repo, with its provenance. If a figure appears in a module and not here, it does not get spoken in an interview.*

This file exists because the measured claims are what make these modules worth more than the documentation they compete with. A number with a command and an environment behind it is the strongest thing a candidate can bring into a technical interview. A number without them is a liability, because the follow-up question — *"how did you measure that?"* — is the one that exposes it.

Read the tag before quoting anything. The rules are in [`AGENTS.md` §7](AGENTS.md).

---

## Environments

**`ENV-A` — the current machine.** All new measurements go here.

```
CPython 3.14.6 (main, Jun 11 2026) [Clang 22.1.3], arm64
macOS 26.5.2 (build 25F84), Apple Silicon, 8 cores
GIL enabled (free-threaded 3.14t not yet installed)
Node v20.20.2 · SQLite 3.51.0 · uv 0.11.23
Docker 29.5.3 installed, daemon down — Postgres and mongod not yet available
gcloud / bq not installed
```

**`ENV-B` — the v1 machine, August 2026.** Every archived figure came from here. It is **not** this machine.

```
CPython 3.10.12, 4 cores
Node v22.22.3
FastAPI 0.141.1 under uvicorn
SQLite (version not recorded)
```

`ENV-A` and `ENV-B` differ in three ways that change results rather than merely shifting them. The core count doubled, which changes the shape of every process-pool scaling claim. CPython's specialising adaptive interpreter landed in 3.11, so bytecode-level timings from 3.10 do not transfer. And the Node version went *down*, from 22 to 20, so anything depending on a v22 default needs rechecking.

**Consequence:** every `ENV-B` row is tagged `measured-stale-env`. Those figures may be quoted only with the original environment named — *"on a four-core machine running 3.10 I measured…"*. Rows marked **re-run priority** are the ones worth re-measuring on `ENV-A` before they are spoken.

---

## Tags

| Tag | Meaning | How it may be spoken |
|---|---|---|
| `measured` | Came out of a terminal on `ENV-A`, command recorded below | *"I measured this."* |
| `measured-stale-env` | Real measurement, but on `ENV-B` | *"On a four-core 3.10 machine I measured…"* — never bare |
| `reproduced-small` | Mechanism correct, magnitude does not transfer | *"I reproduced the behaviour locally; the numbers wouldn't transfer."* Never quote the magnitude |
| `documented` | From vendor documentation, no measurement | *"The way it works is…"* — **never** *"I measured"* |
| `pending` | Claimed in a syllabus, not yet measured | Not quotable at all |

---

## SQL — indexes and the query planner

Source: [`09_sql/01_indexes_and_the_query_planner.md`](09_sql/01_indexes_and_the_query_planner.md), measured 2026-08-04 on `ENV-A` (SQLite 3.51.0) against a purpose-built **200,000 account / 1,000,000 transaction** schema (50 MB, `ANALYZE`d). Scripts: `s1_index.py`, `s2_joins.py`; dataset builder inline.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `SQL-IDX-01` | Index presence: **`SCAN` 53.7ms → `SEARCH` 0.02ms, 2,401×**. Scan work is proportional to table size, search to result size | `s1_index.py` | `measured` |
| `SQL-IDX-02` | **Sargability:** a range predicate ran in **0.6ms**; `substr(created_at,1,7) = '2024-01'` on the same indexed column took **52.5ms — 92×**. Plan showed `SCAN … USING COVERING INDEX`, proving the word "INDEX" in a plan means nothing | `s1_index.py` | `measured` |
| `SQL-IDX-03` | **Selectivity:** `kind='fee'` matched 249,506 rows (25%) and took **42.5ms via the index** — no better than scanning. Low-cardinality columns rarely repay a plain index | `s1_index.py` | `measured` |
| `SQL-IDX-04` | **The headline result.** Query *shape* mattered by **1.3×** (subquery 0.6ms vs join 0.4ms). The *index* mattered by **31,786×** (0.6ms → 18,450ms when dropped). Without the index, join 1,554ms vs subquery 18,450ms — shape only matters after the important battle is lost | `s2_joins.py` | `measured` |
| `SQL-IDX-05` | **`LEFT JOIN` + right-table condition in `WHERE` silently becomes an `INNER JOIN`:** **307,160 → 249,506 rows, 57,654 vanished**, no error | `s2_joins.py` | `measured` |
| `SQL-IDX-06` | **`NOT IN` with a single NULL returns ZERO rows** — 0 vs 199,999 with the NULL filtered. `NULL = NULL` evaluates to `None` (unknown). `NOT EXISTS` is NULL-safe | `s2_joins.py` | `measured` |
| `SQL-IDX-07` | `COUNT(*)` **1,000,000** · `COUNT(note)` **899,500** (skips NULLs) · `COUNT(DISTINCT account_id)` **198,622** | `s1_index.py` | `measured` |

`SQL-IDX-04` is the module's counterintuitive claim and the strongest single number in the repo — four orders of magnitude between what code reviews argue about and what actually decides performance. **Supersedes the v1 `SQL-IDX-05`/`SQL-IDX-06` pair** (17,000× on an unrecorded SQLite version); this run is on a documented dataset with the shape comparison controlled.

`SQL-IDX-05` supersedes the v1 `LEFT JOIN` figure (207,001 → 55,538) with a reproducible dataset.

**Postgres-specific claims** — `Seq Scan`/`Index Scan` naming, `EXPLAIN (ANALYZE, BUFFERS)`, `pg_stat_statements` — are tagged `documented` inline; the Docker daemon is down on `ENV-A`.

## SQL — window functions

Source: [`09_sql/04_window_functions_and_analytical_sql.md`](09_sql/04_window_functions_and_analytical_sql.md), measured 2026-08-04, SQLite 3.51.0. Script: `w1_windows.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `SQL-WIN-01` | **The default frame is `RANGE`, and it is value-based.** Two rows tied on one date: default gave the first a running total of **150 before its own 50 was added**; explicit `ROWS` gave **100 then 150**. Both reach the same grand total, so a spot check passes | `w1_windows.py` | `measured` |
| `SQL-WIN-02` | Ties at 90: `ROW_NUMBER` **1,2,3,4** · `RANK` **1,1,3,4** (never a 2) · `DENSE_RANK` **1,1,2,3**. `RANK`+`<=3` returns a variable row count; `ROW_NUMBER` returns exactly 3 but arbitrarily | `w1_windows.py` | `measured` |
| `SQL-WIN-03` | **Gaps and islands:** `date − ROW_NUMBER()` is constant within a consecutive run. Correctly split user 1 into a 3-day and a 2-day streak with boundaries | `w1_windows.py` | `measured` |

`SQL-WIN-01` is the module's counterintuitive claim: the published running-total idiom is wrong on any date column with more than one row per day.

## JavaScript — the event loop

Source: [`07_javascript/03_the_event_loop_microtasks_and_async.md`](07_javascript/03_the_event_loop_microtasks_and_async.md), measured 2026-08-04, **Node v20.20.2**. Script: `j1_loop.js`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `JS-LOOP-01` | Total order measured: **synchronous → `process.nextTick` → `promise.then` / `queueMicrotask` → `setTimeout(0)` → `setImmediate`** | `j1_loop.js` | `measured` |
| `JS-LOOP-02` | **Microtasks drain to exhaustion**, including ones queued during the drain: **1000 microtasks ran before a 0 ms timer** registered earlier | `j1_loop.js` | `measured` |
| `JS-LOOP-03` | 20 × `sleep(100)`: **sequential 2022ms vs `Promise.all` 101ms — 20.0×**. Supersedes v1 `JS-LOOP-01` (Node v22, 5052/503ms) | `j1_loop.js` | `measured` |
| `JS-LOOP-04` | **A timer set for 0 ms fired at 1001 ms** behind a blocking loop — and its output printed *after* three synchronous logs that appear later in the source | `j1_loop.js` | `measured` |
| `JS-LOOP-05` | IEEE-754: `0.1 + 0.2 = 0.30000000000000004`, `(1.005).toFixed(2) === "1.00"`, `0.1+0.2 === 0.3` is **false** | `j1_loop.js` | `measured` |

`JS-LOOP-02` is the counterintuitive claim. `JS-LOOP-03` paired with `CONC-ASY-02` (Python's identical 19.9×) is the cross-language result.

## TypeScript — variance and inference

Source: [`08_typescript/02_generics_inference_and_variance.md`](08_typescript/02_generics_inference_and_variance.md), measured 2026-08-04 via `npx -p typescript tsc` on `ENV-A`. Files: `ts/variance.ts`, `ts/cov.ts`, `ts/claim.ts`, `ts/erasure.ts`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `TS-VAR-01` | Parameter contravariance **is** caught under `--strict`: `error TS2322: Type '(d: Dog) => void' is not assignable to type 'Handler'` — and the error **disappears** with only `--strictFunctionTypes false`, the rest of strict unchanged | `tsc --strict variance.ts` | `measured` |
| `TS-VAR-02` | **Methods stay bivariant even under full `--strict`.** `handle(a: Animal): void` in method syntax produced **no error**; the same thing as a property is caught. Exempted so `Array<T>` remains assignable | `tsc --strict variance.ts` | `measured` |
| `TS-VAR-03` | **The counterintuitive one.** Array covariance: `Dog[]` → `Animal[]` → `push(Animal)` → **zero compile errors under `--strict`**, then `TypeError: dogs[1].bark is not a function` at runtime | `tsc --strict cov.ts`; `node cov.js` | `measured` |
| `TS-VAR-04` | `as` is a claim, not a check: asserting a parsed JSON object as a type with a field it lacks **compiled clean** and threw `TypeError: Cannot read properties of undefined (reading 'amount')` | `tsc --strict claim.ts`; `node claim.js` | `measured` |
| `TS-VAR-05` | Excess property checking fires on **object literals only**: `error TS2353` on the literal, **no error** for the identical object assigned via a variable | `tsc --strict variance.ts` | `measured` |
| `TS-VAR-06` | Erasure confirmed from emitted JS: `interface` and `type` emit **nothing**; `enum` emits a real runtime IIFE object; `class` emits a real class | `tsc --target es2022 erasure.ts` | `measured` |

**Four deliberately unsound constructs, `--strict` caught two** — and not the one that throws. `TS-VAR-03` is the module's counterintuitive claim and the four-line proof that the type system is deliberately unsound.

## Python — object model and attribute lookup

Source: [`05_python/01_object_model_and_attribute_lookup.md`](05_python/01_object_model_and_attribute_lookup.md), measured 2026-08-04 on `ENV-A`. Scripts in the session scratchpad: `m1_lookup_order.py`, `m2_slots.py`, `m3_mro.py`, `m4_breaks.py`, `lazy_descriptor.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `PY-OBJ-01` | A data descriptor on the class **beats the instance `__dict__`**: with `'shadow'` visibly present in `a.__dict__`, reading `a.x` still returned the descriptor's value | `m1_lookup_order.py` | `measured` |
| `PY-OBJ-02` | A non-data descriptor **loses** to the instance dict as soon as it holds a value — proving the rule turns on descriptor *kind*, not on descriptors generally | `m1_lookup_order.py` | `measured` |
| `PY-OBJ-03` | `property` defines both `__get__` and `__set__` — `hasattr(property,'__get__') and hasattr(property,'__set__')` is `True`, which is what buys it precedence | `m3_mro.py` | `measured` |
| `PY-OBJ-04` | A plain function has `__get__` but **not** `__set__`; `T.__dict__['method'].__get__(t, T)` returns the identical bound method as `t.method`. **This is the entire mechanism of `self`** | `m3_mro.py` | `measured` |
| `PY-OBJ-05` | `super()` is not "the parent": in a diamond, `Interest`'s `super().describe()` dispatched to **`Fees`**, which is not in `Interest.__bases__` (`('Account',)`) | `m3_mro.py` | `measured` |
| `PY-OBJ-06` | C3 refuses inconsistent hierarchies at class-creation time: `TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y` | `m3_mro.py` | `measured` |
| `PY-OBJ-07` | `__slots__` memory: 1,000,000 instances of a 3-field class, **153.0 MB → 114.9 MB** (160.4 → 120.4 bytes/instance), a 38 MB saving | `m2_slots.py`, `tracemalloc` | `measured` |
| `PY-OBJ-08` | `__slots__` speed: 10,000,000 attribute reads, **0.157s → 0.083s**, roughly **1.9× faster** | `m2_slots.py`, `timeit` | `measured` |
| `PY-OBJ-09` | **The counterintuitive one.** `sys.getsizeof` reports the slotted instance as **larger** (56 vs 48 bytes) while total memory is 38 MB lower — it does not follow references and never sees the plain instance's separate **96-byte** `__dict__` | `m2_slots.py` | `measured` |
| `PY-OBJ-10` | An unslotted subclass of a slotted class **silently regains `__dict__`**, discarding the optimisation with no warning | `m2_slots.py` | `measured` |
| `PY-OBJ-11` | A class-level mutable mutated via `self.x.append()` is shared by all instances (`a.transactions is b.transactions` → `True`, and `'transactions' in a.__dict__` → `False`); **rebinding** then fixes only the instance rebound | `m4_breaks.py` | `measured` |
| `PY-OBJ-12` | `__getattr__` fires **only on lookup failure** — never called for an attribute found normally | `m4_breaks.py` | `measured` |
| `PY-OBJ-13` | `__getattribute__` returning `self.__dict__[name]` re-enters itself: `RecursionError: maximum recursion depth exceeded` | `m4_breaks.py` | `measured` |
| `PY-OBJ-14` | Without `__slots__` a typo'd attribute (`n.balnace = 500`) is accepted silently; with `__slots__` it raises `AttributeError` immediately | `m4_breaks.py` | `measured` |
| `PY-OBJ-15` | A hand-built lazy descriptor issues its `SELECT` on first access only and is free thereafter — the N+1 mechanism reproduced in 30 lines | `lazy_descriptor.py` | `measured` |
| `PY-OBJ-16` | The **write** path is a separate 3-step cascade: a data descriptor's `__set__` intercepts a plain assignment and can reject it (`ValueError: balance cannot be negative, got -5`). A non-data descriptor has **no say in writes at all** | `m5_writepath.py` | `measured` |
| `PY-OBJ-17` | `__init_subclass__` registers every subclass automatically and rejects a non-conforming one **at import time** (`TypeError: Broken must declare event=`) — no metaclass required | `m5_writepath.py` | `measured` |
| `PY-OBJ-18` | `type` is its own type (`type(type(Account)) == <class 'type'>`), and `type('Made', (), {'x': 1})` builds a working class — which is what the `class` statement compiles to | `m5_writepath.py` | `measured` |

`PY-OBJ-09` is this module's counterintuitive claim and satisfies anti-filler check 6. `PY-OBJ-05` is the strongest single fact for the `super()` question, because it is a result rather than an assertion.

**Not measured in this module:** SQLAlchemy's instrumented attributes. SQLAlchemy is not installed on `ENV-A`, so the claim that its `Mapped` columns are descriptors is tagged `documented` inline in §3.6, and the mechanism is demonstrated with a hand-built equivalent instead.

## Python — closures, decorators, metaprogramming

Source: [`05_python/03_closures_decorators_and_metaprogramming.md`](05_python/03_closures_decorators_and_metaprogramming.md), measured 2026-08-04 on `ENV-A`. Scripts: `c1_closures.py`, `c2_wraps.py`, `c3_meta.py`, `c4_verify.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `PY-CLO-01` | A closure holds **cells, not values**: `__closure__` is an inspectable tuple, `cell_contents` went 0 → 2 as the function was called, and `co_freevars` shows the compiler marked the name free at compile time | `c1_closures.py` | `measured` |
| `PY-CLO-02` | Late binding: `[lambda: i for i in range(3)]` yields **`[2, 2, 2]`**, and all three functions hold the **identical cell object** (`is` chain returns `True`) | `c1_closures.py` | `measured` |
| `PY-CLO-03` | **The counterintuitive one.** Without `functools.wraps`, `inspect.signature` reports `(*a, **kw)` and **`inspect.get_annotations` returns `{}`** — every type hint erased. With it, the full annotated signature survives and `__wrapped__` is set | `c2_wraps.py` | `measured` |
| `PY-CLO-04` | Two fixes, different mechanisms: the default-arg fix produces **`__closure__ is None`** (no closure at all, value in `__defaults__`); the factory fix produces **distinct cells** per iteration | `c1_closures.py` | `measured` |
| `PY-CLO-05` | Class-creation hook order: **metaclass `__new__` → `__set_name__` → `__init_subclass__` → metaclass `__init__`**, then `__call__` at instantiation. Only `__new__` sees the namespace before the class exists | `c3_meta.py` | `measured` |
| `PY-CLO-06` | **Metaclass conflict:** two classes with unrelated metaclasses cannot be combined — `TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`. No fix available to the caller | `c3_meta.py` | `measured` |
| `PY-CLO-07` | A module-level cache decorator keyed on `self` **prevents collection**: after `del a` and a forced `gc.collect()`, the entry remains and the instance is immortal | `c4_verify.py` | `measured` |
| `PY-CLO-08` | Mutable default argument: three independent calls accumulate (`[100]`, `[100,200]`, `[100,200,300]`) because `__defaults__` holds **one list created once at `def` time** — the same rule that makes the `lambda i=i` fix work | `c4_verify.py` | `measured` |

`PY-CLO-03` is this module's counterintuitive claim: the missing decorator line does not produce a cosmetic defect, it strips the API contract off a FastAPI endpoint. `PY-CLO-08` and `PY-CLO-04` are a matched pair worth quoting together — identical mechanism, opposite outcome, depending only on whether the captured value is mutable.

**Not measured:** SQLAlchemy's declarative base and Pydantic's model machinery. Neither is installed on `ENV-A`; both are tagged `documented` inline and the mechanism is reconstructed from scratch in §3.6 instead.

## Python — bytecode and the runtime

Source: [`05_python/05_bytecode_and_the_runtime.md`](05_python/05_bytecode_and_the_runtime.md), measured 2026-08-04 on `ENV-A` (**CPython 3.14.6**). Scripts: `b1_bytecode.py`–`b6_identity.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `PY-BYT-01` | `balance += 1` compiles to **four instructions** on 3.14 — `LOAD_FAST_BORROW`, `LOAD_SMALL_INT`, `BINARY_OP`, `STORE_FAST`. **Supersedes `PY-CONC-03`**, whose count still holds but whose opcode names (`LOAD_FAST`, `LOAD_CONST`) are 3.10-era | `b1_bytecode.py`, `dis` | `measured` |
| `PY-BYT-02` | Hoisting a global into a local gained **only 11.9%** (0.060s → 0.054s, 20×200k iterations) — far less than folklore implies, because `LOAD_GLOBAL` now caches per call site | `b2_localglobal.py`, `timeit` | `measured` |
| `PY-BYT-03` | **The counterintuitive one.** Identical source, different bytecode: warmed on ints a function's `BINARY_OP` became **`BINARY_OP_ADD_INT`**; a byte-for-byte identical function warmed on strings became **`BINARY_OP_ADD_UNICODE`**. Requires `dis.get_instructions(fn, adaptive=True)` to observe | `b3_specializing.py` | `measured` |
| `PY-BYT-04` | Two *separate* interning mechanisms: `257 is 257` is **True** (compile-time constant folding within one code object) while `(250+7) is 257` is **False** (outside the −5…256 small-int cache). Conflating them yields an explanation that mispredicts this output | `b4_interning.py` | `measured` |
| `PY-BYT-05` | Runtime string concatenation is equal but **not identical** (`s4 == s1` True, `s4 is s1` False) until `sys.intern`. Compile-time `"acc" + "ount"` *is* identical | `b4_interning.py` | `measured` |
| `PY-BYT-06` | Exception cost is in **raising, not guarding**. On a hit `try/except` **beats** `.get` (**0.040s vs 0.047s**) because `.get` costs a method lookup; on a miss it loses **2.8×** (**0.129s vs 0.046s**) | `b5_exc.py`, `timeit` | `measured` |
| `PY-BYT-07` | `status is "reconciled"` returns True for a literal argument and **False** for the same string built at runtime — and Python warns: `SyntaxWarning: "is" with 'str' literal` | `b6_identity.py` | `measured` |
| `PY-BYT-08` | `LOAD_FAST_BORROW_LOAD_FAST_BORROW` is a **superinstruction** — the compiler fuses common local-load pairs to cut dispatch overhead | `b2_localglobal.py` | `measured` |

`PY-BYT-03` is the module's counterintuitive claim and the strongest single answer to "what made recent Python faster." `PY-BYT-06` is a second one: the popular advice to prefer `.get` because "exceptions are expensive" is measurably backwards on the hit path.

`PY-BYT-01` **retires the re-run priority on `PY-CONC-03`** — the four-bytecode claim is confirmed on the current interpreter with current opcode names.

## Concurrency — the GIL

Source: [`06_concurrency/01_the_gil_what_it_protects_and_when_it_lets_go.md`](06_concurrency/01_the_gil_what_it_protects_and_when_it_lets_go.md), measured 2026-08-04 on `ENV-A` (CPython 3.14.6, 8 cores, GIL enabled). Scripts: `g1_gil.py`–`g6_real.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `CONC-GIL-01` | CPU-bound, 8 jobs on 8 cores: **serial 1.88s · 8 threads 1.87s (1.00×) · 8 processes 0.54s (3.47×)**. I/O-bound: **serial 4.03s · 8 threads 0.51s (7.97×)**. **Supersedes `PY-ASYNC-01`/`PY-CONC-01`** (4-core, 3.10) | `g2_procs.py` | `measured` |
| `CONC-GIL-02` | **The negative result.** 16 threads × 100,000 `balance += 1`, switch interval forced to **1e-9**, lost **zero** updates across every configuration tried (2/4/8/16 threads). The folklore "a switch can occur between any two bytecodes" is **false on CPython 3.14** — the eval breaker is only checked at loop back-edges and calls, and no checkpoint falls inside the four-instruction `+=` sequence | `g4_race2.py` | `measured` |
| `CONC-GIL-03` | Inserting a single **function call** between the read and the write produces the race immediately: **220,762 of 400,000 lost (55.19%)**, same threads and same interval | `g5_why.py` | `measured` |
| `CONC-GIL-04` | **The cross-module payoff.** `obj.balance += 1` (plain attribute) loses **0**; `obj.prop_balance += 1` (a `@property`) loses **236,574 of 400,000 (59.14%)**. A property's accessors are Python functions → `CALL` → eval-breaker checkpoint. **Refactoring an attribute into a property silently introduces a data race** | `g6_real.py` | `measured` |
| `CONC-GIL-05` | `list.append` (single C call) and `d['k'] += 1` both lose **0 of 400,000** — thread-safe **by accident of implementation, not by contract** | `g6_real.py` | `measured` |
| `CONC-GIL-06` | `sys.getswitchinterval()` default is **0.005s**, and it is a minimum before a switch is *requested*, not a guarantee of when one occurs | `g3_race.py` | `measured` |

`CONC-GIL-02` through `CONC-GIL-04` are the strongest sequence in the repo: a textbook claim that failed to reproduce, a hypothesis about why, and a controlled experiment confirming it. **This retires `PY-CONC-04`/`PY-CONC-05`** — the v1 "5,900 of 8,000 lost" figure was produced on 3.10 with a manipulated switch interval and does not reproduce on 3.14; the mechanism found here is the more accurate account.

`CONC-GIL-04` also links directly to `PY-OBJ-02` — the descriptor protocol that makes a property indistinguishable from an attribute at the call site is exactly what changes its concurrency behaviour.

## Concurrency — threads, races, synchronisation

Source: [`06_concurrency/02_threads_races_and_synchronisation.md`](06_concurrency/02_threads_races_and_synchronisation.md), measured 2026-08-04 on `ENV-A`. Scripts: `t1_deadlock.py`, `t2_lockcost.py`, `t3_release.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `CONC-THR-01` | Lock cost on the **uncontended** path: 2,000,000 increments, unlocked **0.077s** vs locked **0.201s** — **2.6×**. Under contention the cost is unbounded because threads serialise | `t2_lockcost.py` | `measured` |
| `CONC-THR-02` | **A real deadlock reproduced in twelve lines**: two locks acquired in opposite orders, both threads timed out (`acquired B? False` / `acquired A? False`). Imposing a consistent order made both succeed | `t1_deadlock.py` | `measured` |
| `CONC-THR-03` | A plain `Lock` re-acquired by **its own thread** blocks on itself — `acquire(timeout=0.5)` returned **`False`** (self-deadlock). `RLock` returned `True` | `t1_deadlock.py` | `measured` |
| `CONC-THR-04` | `queue.Queue(maxsize=10)` reports `full=True` after 10 puts, so `put` blocks — **back-pressure**, the property hand-rolled pipelines lack | `t2_lockcost.py` | `measured` |
| `CONC-THR-05` | `Lock` tracks **no owner**: a thread that never acquired it released it **silently** and the lock became free. `RLock` raises `RuntimeError: cannot release un-acquired lock` | `t3_release.py` | `measured` |

`CONC-THR-02` is the module's strongest artefact — a deadlock is usually described rather than demonstrated, and having reproduced *and fixed* one is a materially different interview signal.

## Concurrency — multiprocessing and the process boundary

Source: [`06_concurrency/03_multiprocessing_and_the_process_boundary.md`](06_concurrency/03_multiprocessing_and_the_process_boundary.md), measured 2026-08-04 on `ENV-A`. Script: `p1_procs.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `CONC-MP-01` | **macOS defaults to `spawn`**; all three of `['spawn', 'fork', 'forkserver']` are available | `p1_procs.py` | `measured` |
| `CONC-MP-02` | **Discovered accidentally.** Module-level `print` calls re-executed **once per child** under `spawn` — the script header appeared **13 times** for one invocation, because each child re-imports the module | `p1_procs.py` | `measured` |
| `CONC-MP-03` | Children mutate **copies, silently**: two workers reported their own counters reaching 2 under distinct PIDs while the **parent's counter stayed 0**. No exception, no warning | `p1_procs.py` | `measured` |
| `CONC-MP-04` | Pickle stores functions **by qualified name**: `lambda` and local closures raise `PicklingError`; an open file raises `TypeError: cannot pickle 'TextIOWrapper' instances` because it is a kernel handle | `p1_procs.py` | `measured` |
| `CONC-MP-05` | **The counterintuitive one.** 200,000 squares: serial **0.01s**; 4-process pool `chunksize=1` **3.01s** — **300× slower on 8 idle cores**. `chunksize=100` → **0.09s** (33× better); `chunksize=10000` → **0.05s**, still **5× slower than serial** | `p1_procs.py` | `measured` |

`CONC-MP-05` is the module's counterintuitive claim and the strongest correction to "processes fix CPU-bound work." `CONC-MP-02` is a genuine accidental discovery — the measurement script demonstrated the `spawn` re-import problem on itself, which is exactly how it reaches production.

## Concurrency — asyncio internals

Source: [`06_concurrency/04_asyncio_internals.md`](06_concurrency/04_asyncio_internals.md), measured 2026-08-04 on `ENV-A`. Scripts: `a1_async.py`, `a2_tasks.py`.

| ID | Claim | Command | Tag |
|---|---|---|---|
| `CONC-ASY-01` | Calling an `async def` returns a coroutine object and **executes nothing** — a side effect on the first line left the list empty. `coro.send(None)` then ran the body, returning the value inside `StopIteration`. **JS runs the body to the first `await`; Python runs nothing** | `a1_async.py` | `measured` |
| `CONC-ASY-02` | 20 × 100ms operations: **sequential 2022ms vs `gather` 102ms — 19.9×**. `await` in a loop is a sequential loop in async clothing | `a1_async.py` | `measured` |
| `CONC-ASY-03` | **The counterintuitive one.** 10 concurrent: `await asyncio.sleep(0.2)` **202ms** vs blocking `time.sleep(0.2)` **2039ms — 10.1×**. The blocking call did not get slower; the other nine queued behind it | `a1_async.py` | `measured` |
| `CONC-ASY-04` | `asyncio.to_thread` restored the blocking case to **212ms** | `a1_async.py` | `measured` |
| `CONC-ASY-05` | On failure, `asyncio.gather` let **siblings run to completion** (both printed COMPLETED after the exception was handled); `asyncio.TaskGroup` **cancelled them** and raised `ExceptionGroup` | `a2_tasks.py` | `measured` |
| `CONC-ASY-06` | 50 tasks through `asyncio.Semaphore(5)`: **peak in-flight exactly 5**, elapsed 514ms — ten batches | `a2_tasks.py` | `measured` |
| `CONC-ASY-07` | `asyncio.timeout` cancels the inner task, which observes `CancelledError` **at its current await point** | `a2_tasks.py` | `measured` |
| `CONC-ASY-08` | **Negative result.** 5 unreferenced `create_task`s plus a forced `gc.collect()` → **5/5 completed**. Could not force the documented orphan failure. **Not evidence it is safe — evidence it is nondeterministic**, which is what makes it dangerous | `a2_tasks.py` | `measured` |

`CONC-ASY-03` is the module's counterintuitive claim and the single most useful production diagnostic in the repo: *unrelated endpoints slowing together means a blocked loop, not a slow dependency.* `CONC-ASY-08` is the second honestly-reported negative result in this topic, following `CONC-GIL-02`.

**Supersedes `PY-ASYNC-02`** in mechanism (the v1 `def`-beats-`async def` FastAPI result, 4-core/3.10) — the underlying cause is measured here on `ENV-A`, though the FastAPI endpoint comparison itself has not been re-run.

## Python — async execution model

Source: `_archive/2026-08_v1/05_python/01_async_execution_model.md`, measured 2026-08-03.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `PY-ASYNC-01` | CPU-bound job: 1 process **0.42s** · 4 threads **1.64s** · 4 processes **0.52s**. Threads made a CPU-bound job nearly four times *slower* | ENV-B | `measured-stale-env` · **re-run priority** |
| `PY-ASYNC-02` | 10 concurrent requests: `/async-await` **0.53s** · `/async-blocking` **5.06s** · `/sync-def` **0.53s**. The plain `def` endpoint was ten times faster than the `async def` one running identical code | ENV-B, FastAPI 0.141.1 | `measured-stale-env` · **re-run priority** |
| `PY-ASYNC-03` | Starlette offloads plain `def` endpoints to `anyio.to_thread.run_sync`, default pool **40** threads; the concurrency cliff was observed at exactly 40 | ENV-B | `measured-stale-env` |
| `PY-ASYNC-04` | `asyncio.run(..., debug=True)` warns above `slow_callback_duration`, default **100ms** | — | `documented` |
| `PY-ASYNC-05` | A `create_task` reference held only by the event loop could not be made to fail on demand: five unreferenced tasks plus a forced `gc.collect()` all completed normally | ENV-B | `measured-stale-env` — a **negative result**, and the honest framing is that the failure is nondeterministic, not absent |

`PY-ASYNC-02` is the single most valuable figure in the archive. It is counterintuitive, it is memorable, and it directly answers "tell me about a time you found something surprising." It should be re-measured on `ENV-A` in Phase 2 before it is used.

## Python — threads and processes

Source: `_archive/2026-08_v1/05_python/02_concurrency_threads_processes.md`, measured 2026-08-03.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `PY-CONC-01` | I/O-bound job: serial **10.09s** · 20 threads **0.51s** · 20 coroutines **0.50s** · 8 processes **1.54s**. Threads and coroutines tie; processes lose to startup cost | ENV-B | `measured-stale-env` |
| `PY-CONC-02` | Memory for 2000 concurrent units: coroutines **4.5 MB** · threads **32.1 MB** — roughly a sevenfold difference | ENV-B | `measured-stale-env` |
| `PY-CONC-03` | `balance += 1` compiles to **four bytecodes**, not one, and is therefore not atomic | ENV-B (`dis`) | `measured-stale-env` · **re-run priority** — bytecode changed after 3.11 |
| `PY-CONC-04` | With `sys.setswitchinterval` forced low, two threads doing 4,000 increments each lost **5,900 of 8,000** deposits | ENV-B | `measured-stale-env` · **re-run priority** |
| `PY-CONC-05` | The same race in a *tight* loop with no artificial switch point lost **nothing across five runs**. The GIL makes read-modify-write races **rare, not impossible** — which is what makes them dangerous | ENV-B | `measured-stale-env` |
| `PY-CONC-06` | Child processes mutate copies: the parent's counter stayed at **0**, silently, with no error | ENV-B | `measured-stale-env` |
| `PY-CONC-07` | `multiprocessing.Value` provides shared storage but **not** atomicity; it still requires `get_lock()` | ENV-B | `measured-stale-env` |
| `PY-CONC-08` | A lambda passed across a process boundary raises `PicklingError` | ENV-B | `measured-stale-env` |
| `PY-CONC-09` | NumPy, Polars and DuckDB release the GIL around their C loops — vectorise before you parallelise | — | `documented` |

`PY-CONC-04` and `PY-CONC-05` together are the best answer available to "is Python thread-safe?" — the pair shows the race is real *and* rare. On a free-threaded build (`3.14t`, not yet installed) the tight loop should lose updates with no switch-interval manipulation at all. **That contrast, measured personally, would be a top-percentile answer and no candidate has it.** It is the single highest-value new measurement available.

## SQL — indexes and the query planner

Source: `_archive/2026-08_v1/02_sql/01_indexes_and_the_query_planner.md`, measured 2026-08-03 against SQLite on a synthetic 200,000-account / 1,000,000-transaction schema.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `SQL-IDX-01` | A function applied to the indexed column defeats the index: **62.4 ms** versus **1.8 ms** — a **35×** penalty. Moving the function to the constant side restores it | ENV-B, SQLite | `measured-stale-env` |
| `SQL-IDX-02` | Selectivity governs whether the planner uses an index at all: at 2% selectivity **1.4 ms** via index; at 98% the index took **13.2 ms** against **7.8 ms** for a plain scan — **the index made it slower** | ENV-B, SQLite | `measured-stale-env` |
| `SQL-IDX-03` | Methodology correction worth preserving: measuring selectivity using only columns present in the index made the planner use it even at 98%, because index-only access removes the pointer-following cost. A column *outside* the index was required to see a real trade-off | ENV-B | `measured-stale-env` |
| `SQL-IDX-04` | A `LEFT JOIN` with the right table's condition in `WHERE` instead of `ON` silently cut **207,001 rows to 55,538** | ENV-B, SQLite | `measured-stale-env` |
| `SQL-IDX-05` | Index presence dominates query shape: with the index dropped, **19,183 ms**; restored, **1.1 ms**. Query shape moved it by under 2×, the index by roughly **17,000×** | ENV-B, SQLite | `measured-stale-env` · **re-run priority** — belongs on Postgres with `EXPLAIN (ANALYZE, BUFFERS)` |
| `SQL-IDX-06` | Correlated subquery **10.4 ms** versus single join with `GROUP BY` **17.2 ms** — the subquery won, which contradicts the folk wisdom | ENV-B, SQLite | `measured-stale-env` |
| `SQL-IDX-07` | `COUNT(*)` **1,000,000** · `COUNT(col)` **900,000** (skips NULLs) · `COUNT(DISTINCT col)` **198,662** | ENV-B, SQLite | `measured-stale-env` |

`SQL-IDX-05` and `SQL-IDX-06` are a matched pair and should always be quoted together: the subquery beat the join, *and* both were irrelevant next to the index. The lesson is that developers argue about query shape while the planner is starved of the one thing that matters. Re-running on Postgres upgrades this from a SQLite curiosity to something an interviewer will recognise.

## JavaScript — the event loop

Source: `_archive/2026-08_v1/03_js_ts/01_event_loop_and_microtasks.md`, measured 2026-08-03 on Node v22.22.3, 4 cores.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `JS-LOOP-01` | Ten sequential `await`s in a loop took **5052 ms**; the same work through `Promise.all` took **503 ms** | ENV-B, Node v22.22.3 | `measured-stale-env` |
| `JS-LOOP-02` | A timer scheduled for 0 ms behind a blocking loop fired at **1002 ms**. The signature of a blocked loop is that unrelated endpoints slow down together | ENV-B, Node v22.22.3 | `measured-stale-env` |
| `JS-LOOP-03` | `worker_threads` on a CPU-bound job: **12,012 ms** on the main thread versus **3,280 ms** across 4 workers. A single run took **2,996 ms** | ENV-B, Node v22.22.3, 4 cores | `measured-stale-env` · **re-run priority** — core count is now 8 |
| `JS-LOOP-04` | A microtask chain starved a 0 ms timer for **1000 microtasks**; microtasks drain to exhaustion before any macrotask runs | ENV-B, Node v22.22.3 | `measured-stale-env` |
| `JS-LOOP-05` | `0.1 + 0.2 === 0.30000000000000004`, and `(1.005).toFixed(2) === "1.00"` | Language-invariant, IEEE-754 | `measured` — reproducible anywhere, no environment dependency |
| `JS-LOOP-06` | Closures capture bindings, not values: a `var` loop logs **3 3 3**, a `let` loop logs **0 1 2** | Language-invariant | `measured` |
| `JS-LOOP-07` | An unhandled promise rejection exits the process with code 1 on Node ≥ 15; in a browser it fires an event and the page survives | — | `documented` |

`JS-LOOP-03` paired with `PY-ASYNC-01` is the cross-language result worth the most in an interview: **JavaScript threads parallelise CPU work and Python threads do not**, because `worker_threads` are isolated V8 heaps with no shared interpreter state and therefore no GIL. Both pay the same isolation tax — structured clone on one side, pickle on the other. Both halves must be re-run on `ENV-A` so the core count matches; quoting a 4-core Node figure against a 4-core Python figure measured on a machine that no longer exists is the kind of detail an interviewer catches.

## TypeScript — the type system

Source: `_archive/2026-08_v1/03_js_ts/02_the_type_system.md`. These are compiler behaviours rather than timings, verified by running `tsc`.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `TS-SYS-01` | Structural typing: `AccountId` and `UserId`, both `{ id: string }`, are mutually assignable. Branding is the fix | `tsc` | `measured-stale-env` — trivially re-verifiable |
| `TS-SYS-02` | `interface` and `type` emit nothing; `enum` emits real JavaScript | `tsc` | `measured-stale-env` |
| `TS-SYS-03` | The excess-property check fires on object literals only; the same object via a variable passes | `tsc` | `measured-stale-env` |
| `TS-SYS-04` | `as` is a claim, not a check — the failure surfaces at runtime as `TypeError: Cannot read properties of undefined` | `tsc` + Node | `measured-stale-env` |
| `TS-SYS-05` | Arrays are unsoundly covariant by design: `dogs[1].bark is not a function` with zero compile errors | `tsc` | `measured-stale-env` |
| `TS-SYS-06` | Function parameters are contravariant, and the violation is caught only under `strictFunctionTypes` | `tsc` | `measured-stale-env` |

## MongoDB — modelling and indexes

Source: `_archive/2026-08_v1/04_mongodb/01_document_modelling_and_indexes.md`. **This was v1's one weak module and it said so in its own header:** no local `mongod` was available, so plans and timings were stated from documentation rather than measured. Only the BSON sizes were real.

Docker is installed on `ENV-A`, so `mongo:8` is reachable and this gap closes in Phase 3.

| ID | Claim | Environment | Tag |
|---|---|---|---|
| `MONGO-01` | Roughly **90 bytes** of BSON per embedded transaction, giving roughly **186,000** embedded documents before the 16 MB ceiling | ENV-B, computed from real BSON encoding | `measured-stale-env` |
| `MONGO-02` | BSON document limit **16 MB** | — | `documented` |
| `MONGO-03` | In-memory sort limit **32 MB**; aggregation stage limit **100 MB** without `allowDiskUse` | — | `documented` |
| `MONGO-04` | The ESR rule — Equality, Sort, Range — falls out of index sortedness, because a range predicate scatters everything ordered after it | — | `documented` · **must be re-derived from real `explain("executionStats")` output in Phase 3, not asserted** |
| `MONGO-05` | `$lookup` executes per input document, making it the N+1 shape unless the foreign field is indexed | — | `documented` |
| `MONGO-06` | Only leading pipeline stages can use an index; after `$group` or `$unwind` the stream is synthetic | — | `documented` |
| `MONGO-07` | Mongo indexes are type-sensitive: `"123"` and `123` are different keys | — | `documented` · trivially measurable once `mongod` runs |

## BigQuery

Nothing measured. `gcloud` and `bq` are not installed on `ENV-A`.

| ID | Claim | Tag |
|---|---|---|
| `BQ-01` | Bytes scanned determines the bill; `SELECT *` is the most expensive habit in the product | `pending` |
| `BQ-02` | Partition pruning and clustering reduce bytes scanned, measurable as a before/after via `bq query --dry_run` | `pending` |

`bq query --dry_run` returns real bytes-processed and **costs nothing**, and the BigQuery sandbox is free without a credit card, with `bigquery-public-data` providing genuinely large tables. That makes the entire cost-control module measurable at zero spend — before/after bytes for `SELECT *` versus named columns, and with versus without a partition filter. This is a case where "we can't measure it" would have been the lazy answer.

What stays genuinely unmeasurable, and must carry the `documented` tag: Dataflow autoscaling and fusion under real load, streaming watermark behaviour at volume, and slot contention under a reservation.

---

## The re-run queue

Ordered by value. These execute in Phase 2 and Phase 3 as their modules are written.

| Priority | IDs | Why |
|---|---|---|
| 1 | `PY-CONC-03`, `PY-CONC-04`, `PY-CONC-05` + the new `3.14t` free-threaded comparison | The GIL-versus-no-GIL contrast measured personally is the highest-value new number available, and `3.14t` is one `uv python install` away |
| 2 | `PY-ASYNC-01`, `PY-ASYNC-02` | The best story in the archive; currently unquotable without a four-core caveat |
| 3 | `JS-LOOP-03` + `PY-ASYNC-01` together | The cross-language table needs one consistent machine and one consistent core count |
| 4 | `SQL-IDX-05`, `SQL-IDX-06` | Upgrading from SQLite to Postgres with `EXPLAIN (ANALYZE, BUFFERS)` makes these interview-grade |
| 5 | `MONGO-04`, `MONGO-07` | Closes v1's only honesty gap once `mongod` is running |

Setup still required, each gated on explicit approval: starting the Docker daemon for `postgres:17` and `mongo:8`, running `uv python install 3.14t`, and installing `gcloud`/`bq`.
