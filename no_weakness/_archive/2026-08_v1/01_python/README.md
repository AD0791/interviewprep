# Python

*Depth modules. Each is L3–L4: mechanism, then failure, then the spoken answer.*

| # | Module | Level | Status |
|---|---|---|---|
| 01 | [The async execution model](01_async_execution_model.md) — coroutines, the event loop, the GIL | L3–L4 | **Written** |
| 02 | [Concurrency — threads, processes, and the GIL](02_concurrency_threads_processes.md) | L3–L4 | **Written** |
| 03 | The object model — attribute lookup, descriptors, MRO, `__slots__` | L3 | Planned |
| 04 | Closures, scope, and the late-binding trap | L3–L4 | Planned |
| 05 | Memory — references, cyclic GC, `weakref`, generators | L3–L4 | Planned |
| 06 | The data model — dunder protocols, iterators, context managers | L3 | Planned |
| 07 | Typing at runtime — annotations, Pydantic, and what is actually enforced | L3–L4 | Planned |
| 08 | Decorators, `functools`, and metaprogramming | L3–L4 | Planned |
| 09 | CPython internals — bytecode, `dis`, and where the time goes | L4 | Planned |
| 10 | SQLAlchemy 2.0 — sessions, identity map, and N+1 | L4 | Planned |

Order past 02 is decided by [the diagnostic](../00_self_assessment.md), section A — not by this table.

---

## Coverage against the syllabus

The video syllabus in `../assets/` runs to fifty topics. They are not fifty modules — most cluster, and several are L1–L2 material this repo deliberately skips. The mapping:

| Syllabus topics | Module |
|---|---|
| CPython · GIL · Concurrency · Multithreading · Multiprocessing · race conditions · shared memory | **02 — written** |
| asyncio | **01 — written** |
| MRO · encapsulation · abstraction & abc · inheritance · polymorphism · `__slots__` · staticmethod & classmethod | 03 |
| Not returning dicts & lists (mutable defaults) · closures | 04 |
| Garbage collection with circular references · `weakref` · `WeakKeyDictionary` · `del` · `memory_profiler` · `sys.getsizeof` · generators · `memoryview` | 05 |
| Data model · iterators · generators · context managers · custom context managers | 06 |
| Dataclasses · advanced dataclass features · serialization · `__getstate__`/`__setstate__` | 07 |
| Advanced decorators · `functools` · metaclasses · metaprogramming · dependency injection | 08 |
| Bytecode and `dis` · bytes · arrays · `heapq` · `collections` | 09 |
| Parameterized testing · fixtures | *(campaign folders, not here)* |
| Walrus operator · `operator.attrgetter` · `filter` · higher-order functions · advanced list comprehension | *(L1–L2, skipped — see below)* |

**On the skipped row.** The walrus operator and `operator.attrgetter` are syntax you either know or can look up in ten seconds, and no interviewer probes them at L3. Spending module time there would be exactly the failure mode [the plan](../README.md) warns about — writing thoroughly about things that are not weaknesses. If the diagnostic shows otherwise, they get added.

The pairing that works: **watch the video for the topic, then work the module.** The video teaches the material; the module makes it explainable under pressure, which is the gap this repo exists to close.

---

## Why 01 and 02 are first

Together they are the most-probed and most-misexplained area of Python at senior level, they sit directly on the FastAPI and pipeline work you have shipped, and their failure modes appear in production rather than in tutorials.

They are also the pair that proves the format. Real code, real measured output, the failure shown before the fix, spoken answers at the end. If that shape works, the rest of the repo gets built the same way.
