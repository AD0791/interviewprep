# FastAPI Runtime Internals Masterclass

What actually happens between `uvicorn` accepting a socket and your route returning JSON: the event-loop contract, the sync-in-async trap, lifespan management, and streaming. Extends the routing/DI basics in [frameworks_specifics/01_fastapi.md](../frameworks_specifics/01_fastapi.md) — read that first if DI is fuzzy.

---

## 1. The Event Loop Contract (Why)

An async FastAPI worker is **one process running one asyncio event loop**. Concurrency comes from cooperative multitasking: coroutines run until they `await`, then yield the loop to the next ready task. Ten thousand concurrent requests can share one thread — *as long as nobody hogs it*.

That is the contract: **an `async def` route must never block.** One synchronous call — `requests.get()`, `time.sleep()`, a tight CPU loop, a sync DB driver — freezes not just that request but **every in-flight request in the worker**, because they all share the loop.

```mermaid
sequenceDiagram
    autonumber
    participant R1 as Request 1 (blocking)
    participant Loop as Event Loop
    participant R2 as Requests 2..N
    R1->>Loop: async route calls requests.get() — sync, 3s
    Note over Loop: Loop OCCUPIED for 3 full seconds
    R2--xLoop: Ready to run, cannot be scheduled
    Note over R2: Every request in the worker stalls 3s,<br/>health checks included → LB may kill the pod
    Loop-->>R1: requests.get() returns, loop breathes again
```

The insidious part: it's invisible at dev traffic (one request at a time feels fine) and catastrophic under load. Production signature: p99 latency spikes across *unrelated* endpoints simultaneously.

## 2. Sync-in-Async Pitfalls and Escape Hatches (What & How)

Three classes of loop-blockers and the correct escape for each:

| Blocking call | Fix | Why |
|---|---|---|
| Sync I/O (`requests`, `psycopg2`, `open()` on slow disk) | Use the async native (`httpx.AsyncClient`, `asyncpg`) — or wrap in a thread | The loop needs an awaitable to yield on |
| CPU-bound work (report crunching, hashing, pandas) | `ProcessPoolExecutor` / task queue | Threads don't help CPU work under the GIL (see [07/01](../07_advanced_runtimes_and_compilers/01_advanced_python_node_typescript.md)); processes do |
| Legacy sync library you can't replace | `run_in_threadpool`, or declare the route plain `def` | Both push the work onto worker threads, keeping the loop free |

```python
# Gist: escape_hatches.py
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
import legacy_sdk  # sync-only third-party client

app = FastAPI()

@app.get("/reports/{rid}")
async def get_report(rid: int):
    # WRONG here would be: data = legacy_sdk.fetch(rid)   <- freezes the loop
    data = await run_in_threadpool(legacy_sdk.fetch, rid)  # loop stays free
    return data

@app.get("/legacy-status")
def legacy_status():  # plain `def`: FastAPI runs the WHOLE route in the threadpool
    return legacy_sdk.status()
```

Two senior footnotes: the shared AnyIO threadpool defaults to **40 threads per worker** — heavy `def`-route traffic queues behind it, so it's a relief valve, not a scaling strategy. And a plain `def` route is not a failure — it's the *correct* choice when the handler is sync-bound end to end.

## 3. Lifespan: Startup and Shutdown Done Right (How)

Expensive resources — the async engine, an `httpx` client, an ML model — must be created **once per worker**, not per request. The modern mechanism (replacing the deprecated `@app.on_event`) is the **lifespan context manager**: code before `yield` runs at startup, after `yield` at shutdown.

```python
# Gist: lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: once per worker process, before traffic is accepted
    app.state.engine = create_async_engine(SETTINGS.db_url, pool_size=10, pool_pre_ping=True)
    app.state.http = httpx.AsyncClient(timeout=5.0)
    yield
    # SHUTDOWN: on SIGTERM, after in-flight requests drain
    await app.state.http.aclose()
    await app.state.engine.dispose()  # returns pooled connections cleanly

app = FastAPI(lifespan=lifespan)
```

The shutdown half is what makes **graceful deploys** work: Kubernetes/compose sends SIGTERM, uvicorn stops accepting, in-flight requests finish, lifespan teardown closes pools — no dropped requests, no orphaned connections (the deploy sequence lives in [04/09](../04_architecture_and_system_design/09_deployment_scaling_statelessness.md)).

## 4. StreamingResponse and Large Payloads (How)

Returning a 2 GB CSV export the naive way — build the whole string, return it — OOMs the worker and stalls the client until byte one. `StreamingResponse` wraps an **async generator**: each yielded chunk is sent immediately, memory stays flat at one-chunk size, and every `yield` is an await point, so the loop keeps serving other requests mid-export.

```python
# Gist: csv_stream.py
from fastapi.responses import StreamingResponse
from sqlalchemy import text

@app.get("/exports/transactions")
async def export_transactions(db: AsyncSession = Depends(get_db)):
    async def rows():
        yield "id,amount,created_at\n"
        result = await db.stream(  # server-side cursor: DB rows arrive in batches too
            text("SELECT id, amount, created_at FROM transactions ORDER BY id")
        )
        async for row in result:
            yield f"{row.id},{row.amount},{row.created_at}\n"
    return StreamingResponse(
        rows(), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
```

Note `db.stream()` — streaming the HTTP response while `db.execute()` buffers a million rows in memory defeats the point; the server-side cursor keeps *both* ends flat. Decision rule: **paginate** when the client is interactive ([04/06](../04_architecture_and_system_design/06_api_contracts_idempotency_pagination.md)), **stream** when the client genuinely wants the whole dataset (exports, backups). SSE is this same mechanism with an event framing — see [05/01](../05_networking_and_data_transport/01_networking_protocols_dashboard.md).

## 5. Interview Angles

**"A developer calls `requests.get()` inside an `async def` route. What happens, and how do you catch it in production?"**
Skeleton: the loop blocks → every in-flight request in the worker stalls, cross-endpoint p99 spikes, health checks may fail → detect via latency correlation across unrelated routes, `asyncio` debug mode's slow-callback warnings, or py-spy dumps showing the loop thread inside a sync call → fix with the escape-hatch table (async client / threadpool / plain `def`); prevent with a lint rule and review culture.

**"How do you export a 2 GB report without OOMing the worker?"**
Skeleton: `StreamingResponse` over an async generator + `db.stream()` server-side cursor → flat memory both ends, loop yields per chunk → mention `Content-Disposition` and that for *repeated* heavy exports you'd move to a background job + object storage + signed URL instead of holding an HTTP connection for minutes.

**"Why create the engine in lifespan instead of at module import?"**
Skeleton: import-time creation runs before fork/event-loop setup and can't be torn down cleanly → lifespan ties the pool to the worker's actual lifecycle, enabling graceful shutdown and testable startup (dependency overrides can swap `app.state`).
