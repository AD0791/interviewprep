# Battle Card 01 — FastAPI Runtime

## 30-Second Answers

**async vs sync routes.** "An `async def` route runs on the worker's single event loop and must never block — one sync call stalls every in-flight request. A plain `def` route is dispatched to a threadpool, which makes it the *correct* choice for sync-bound handlers, not a mistake."

**Blocking the loop.** "The production signature is p99 spiking across unrelated endpoints at once, because they share the loop. Escapes: async-native clients (httpx/asyncpg), `run_in_threadpool` for legacy sync libs, processes for CPU work — threads don't help CPU under the GIL."

**Lifespan.** "Expensive resources — engine, HTTP clients — are built once per worker in the lifespan context manager, before traffic; teardown after `yield` disposes them on SIGTERM. That teardown is what makes graceful, zero-drop deploys possible."

**Streaming.** "For a 2 GB export I return a `StreamingResponse` over an async generator paired with `db.stream()` — a server-side cursor — so memory stays flat at both ends and the loop keeps serving between chunks. Interactive clients get pagination instead."

**Dependency injection.** "Dependencies compose into a per-request graph (auth → session → repository) and — the senior half — they're swappable: tests override `get_db` in one line."

## Numbers & Facts

| Fact | Value |
|---|---|
| Threadpool for `def` routes / `run_in_threadpool` | ~40 threads per worker (AnyIO default) |
| One worker | 1 process, 1 event loop, ~1 core |
| Async concurrency per worker | Thousands of coroutines |
| Validation failure response | 422 with field-level errors |

## Rapid Fire

- **Why is `time.sleep` in an async route catastrophic?** → It holds the loop; every request in the worker freezes for its duration.
- **`requests` vs `httpx` in FastAPI?** → `requests` is sync (blocks the loop); `httpx.AsyncClient` awaits.
- **Where does a per-request DB session come from?** → A yield-dependency: setup before `yield`, guaranteed teardown after.
- **Middleware or dependency for auth context?** → Dependency — it's scoped and produces a value handlers consume.
- **Why not create the engine at import time?** → No clean teardown, wrong timing vs fork/loop; lifespan ties it to the worker's life.

## Trap Questions

- *"So `def` routes are bad, right?"* — No: plain `def` is correct for sync-bound work; FastAPI threadpools it. The bug is *blocking inside `async def`*, not sync code per se.
- *"Threads will speed up my CPU-heavy endpoint?"* — Under the GIL, no — one thread runs Python bytecode at a time. CPU work needs processes or a task queue; threads only help I/O.

## Deep Dives

[01/02 runtime internals](../../01_fastapi_sqlalchemy_postgres/02_fastapi_runtime_internals.md) · [frameworks/01_fastapi](../../frameworks_specifics/01_fastapi.md) · [07/01 event loops & GIL](../../07_advanced_runtimes_and_compilers/01_advanced_python_node_typescript.md)
