# FastAPI, From Zero

You know Python. This article takes you from an empty file to an API with validation, database sessions, auth, and error handling — and at each step it explains what the framework is doing underneath, because that's where interview questions live.

---

## 1. The Problem: HTTP Is Strings All the Way Down

An HTTP request is text: a method, a path, some headers, maybe a JSON body. Your business logic wants none of that — it wants an `account_id: int` and a validated `Transfer` object. Every web framework exists to bridge that gap. What makes FastAPI distinctive is *how little you write* to get the bridge: you declare ordinary Python type hints, and FastAPI derives everything else from them — parsing, validation, error responses, and interactive documentation.

Under the hood it's two libraries glued together. **Starlette** handles the web part: routing, middleware, WebSockets, and the async server interface (ASGI). **Pydantic** handles the data part: turning untrusted JSON into typed objects ([04_pydantic.md](04_pydantic.md) covers it from zero). FastAPI's own contribution is the type-hint glue plus dependency injection. That one sentence — "a thin declarative layer wiring Starlette's ASGI runtime to Pydantic's validation through type hints" — is a complete interview answer to "what is FastAPI."

## 2. First Endpoint, and What Actually Happens

```bash
pip install "fastapi[standard]"
```

```python
# Gist: main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/accounts/{account_id}")
async def read_account(account_id: int, include_closed: bool = False):
    return {"account_id": account_id, "include_closed": include_closed}
```

Run it with `fastapi dev main.py` (or `uvicorn main:app --reload`) and open `http://localhost:8000/accounts/7?include_closed=true`. You get JSON back. Now look at what you *didn't* write.

You never parsed the URL. FastAPI read the function signature: `account_id` appears in the path, so it's a path parameter; `include_closed` doesn't, so it's a query parameter with a default. You never converted strings either — `"7"` arrived as text and your function received the integer `7`, because the type hint said `int`. And if someone requests `/accounts/banana`, your function never runs at all: FastAPI answers with a **422** response containing a machine-readable list of what failed validation. Try it. Then open `http://localhost:8000/docs` — the interactive Swagger page was generated from the same type hints. One set of annotations produced parsing, validation, coercion, error responses, and documentation. That's the core trick, and everything else in this article is the same trick applied to bigger inputs.

When you need constraints beyond the type, wrap them around the hint:

```python
from fastapi import Path, Query

@app.get("/accounts/{account_id}/transactions")
async def list_transactions(
    account_id: int = Path(gt=0),
    limit: int = Query(default=50, le=200),  # cap page size at the edge
):
    ...
```

## 3. Request Bodies: The Validation Boundary

For a POST body, declare a Pydantic model and take it as a parameter:

```python
# Gist: schemas.py + endpoint
from pydantic import BaseModel, Field

class TransferRequest(BaseModel):
    source_account: int
    destination_account: int
    amount: float = Field(gt=0)  # business rule enforced before your code runs

@app.post("/transfers", status_code=201)
async def create_transfer(transfer: TransferRequest):
    # By this line, transfer is GUARANTEED well-formed: right fields, right
    # types, amount positive. Malformed input already got a 422.
    return {"status": "accepted", "amount": transfer.amount}
```

This is worth internalizing as an architectural stance, not a convenience: **the endpoint signature is a boundary**. Outside it, data is untrusted text. Inside it, data is typed and constrained, and your service and repository layers never re-check. The same applies on the way out — declare `response_model=AccountOut` on the route and FastAPI filters the return value through that schema, which means a stray `hashed_password` attribute on your ORM object *cannot* leak: it isn't in the output schema, so it isn't in the response. `response_model` is an output firewall, not just documentation.

## 4. Dependency Injection, Derived From the Pain (Why & How)

Write a few endpoints against a database and you'll type the same first line every time: open a session, and make sure it closes even when things blow up. Copy-pasting that into thirty endpoints is how connection leaks are born ([01/03](../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md) shows what leaked sessions do to a connection pool). FastAPI's answer is `Depends`:

```python
# Gist: dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with SessionLocal() as session:  # runs BEFORE the endpoint
        yield session                      # endpoint executes here
    # session closes AFTER the response — even if the endpoint raised

@app.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account))
    return result.scalars().all()
```

A dependency is just a function; `Depends` tells FastAPI "call this and hand me the result." The `yield` form makes it a per-request context manager: setup above the `yield`, guaranteed teardown below it. That teardown guarantee is the entire reason DB sessions are dependencies.

Dependencies compose, and this is where the design gets its power. A dependency can itself depend on others, forming a graph that FastAPI resolves per request:

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return decode_and_validate(token)          # raises 401 on failure

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Admins only")  # 403: authenticated, not allowed
    return user

@app.delete("/accounts/{account_id}")
async def close_account(account_id: int, admin: User = Depends(require_admin)):
    ...
```

Two properties to name in an interview. First, **caching**: if three dependencies in one request all need `get_db`, FastAPI runs it once and shares the result — one session per request, automatically. Second, **overridability**: `app.dependency_overrides[get_db] = get_test_db` swaps any node of the graph in tests, which is how the whole API-testing strategy in [06/02](../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md) works without a running Postgres.

## 5. async def vs def: The One Rule That Bites (Why)

Every FastAPI worker is one process running one asyncio event loop, and `async def` endpoints run *on that loop*. The loop serves thousands of concurrent requests by switching between them at every `await`. Which means the rule is absolute: **an `async def` endpoint must never call anything blocking.** One `requests.get()` or `time.sleep(3)` inside an async route doesn't slow that request down — it freezes *every request in the worker* for three seconds, because they all share the loop. The production symptom is spooky: p99 latency spikes on endpoints that have nothing to do with the guilty one.

Your escape hatches, in order of preference: use the async-native library (`httpx.AsyncClient` instead of `requests`, `asyncpg` via SQLAlchemy's async engine); wrap an unavoidable sync call in `await run_in_threadpool(legacy_call)`; or declare the whole endpoint with plain `def` — FastAPI automatically runs `def` endpoints in a thread pool, so blocking there is safe. A sync endpoint is not a mistake; a *blocking async* endpoint is. The full mechanics, including CPU-bound work and the GIL, are in [01/02](../01_fastapi_sqlalchemy_postgres/02_fastapi_runtime_internals.md).

```mermaid
sequenceDiagram
    autonumber
    participant R1 as Request 1 (calls time.sleep)
    participant Loop as Event loop
    participant R2 as Requests 2..N
    R1->>Loop: async route blocks for 3s
    Note over Loop: Loop cannot switch tasks
    R2--xLoop: ready, but frozen for 3s
    Loop-->>R1: sleep ends, everyone resumes
```

## 6. The Production Trio: Errors, Middleware, Lifespan (How)

Three pieces turn the toy into a service. **Exception handlers** map your domain errors to consistent HTTP responses in one place, so no endpoint hand-builds error JSON:

```python
# Gist: production_pieces.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

class InsufficientFunds(Exception):
    """Raised by the domain layer; it knows nothing about HTTP."""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP, once per worker: build expensive shared resources here,
    # not at import time and never per request.
    app.state.engine = create_async_engine(settings.db_url, pool_pre_ping=True)
    yield
    # SHUTDOWN, on SIGTERM: drain cleanly so deploys drop zero requests.
    await app.state.engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(InsufficientFunds)
async def insufficient_funds_handler(request: Request, exc: InsufficientFunds):
    return JSONResponse(status_code=409, content={"type": "insufficient-funds", "detail": str(exc)})

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)  # everything inside runs here
    response.headers["X-Response-Time"] = f"{time.perf_counter() - start:.4f}s"
    return response
```

**Middleware** wraps every request like layers of an onion — the right home for timing, logging, CORS, compression: concerns that are global and don't produce a value your endpoint needs. When something *is* scoped or produces a value (the current user, a session), it belongs in a dependency instead. And **lifespan** ties resource lifetime to worker lifetime: the engine is built once before traffic and disposed on shutdown, which is what makes graceful, zero-downtime deploys possible ([04/09](../04_architecture_and_system_design/09_deployment_scaling_statelessness.md)).

One last built-in: `BackgroundTasks` runs a function *after* the response is sent — handy for an audit log the user shouldn't wait for. But it runs inside the same worker process, so if the worker dies or deploys, the task is silently gone. The honest rule: fire-and-forget and loss-tolerable, use `BackgroundTasks`; must-not-lose or heavy, use a real queue (Celery or arq backed by Redis) with retries.

## 7. The Life of a Request (say this out loud once)

Tie it together by narrating one request, because "walk me through what happens when a request hits your API" is a real interview question. Uvicorn accepts the socket and hands Starlette the raw request. The middleware stack wraps it, outermost first. The router matches path and method to your endpoint. Pydantic validates path, query, and body against your annotations — bad input dies here with a 422, before your code exists to it. The dependency graph resolves in order, cached per request: token becomes user, sessionmaker becomes session. Your handler runs, on the loop or in the thread pool depending on `async def` vs `def`. The return value passes through `response_model` filtering and serialization. The middleware unwinds inside-out, and after the response is sent, yield-dependency teardown closes the session. Eight steps, and you can name where any given bug lives in them.

## 8. Interview Angles

**"Why is FastAPI fast?"** Two unrelated reasons that candidates usually blur together. Request throughput comes from the ASGI event loop: one worker multiplexes thousands of concurrent I/O-bound requests instead of one-thread-per-request. Validation speed comes from Pydantic v2's Rust core. But the answer that lands is the third thing: development speed — type hints are a single source of truth from which validation, serialization, docs, and DI all derive, so there's no drift between what the docs say and what the code enforces.

**"Where do you put auth: middleware or a dependency?"** A dependency. Auth is scoped (some routes are public), it produces a value the handler needs (the current user), it composes into stricter variants (`require_admin` builds on `get_current_user`), and tests can override it. Middleware is for global, value-less concerns. The follow-up is usually the 401-versus-403 distinction: 401 means "I don't know who you are," 403 means "I know exactly who you are, and no."

**"What happens if you call a slow synchronous function inside an async endpoint?"** The event loop blocks, so every in-flight request in that worker stalls, not just yours — visible as correlated p99 spikes across unrelated endpoints. Fix by going async-native, wrapping in the thread pool, or declaring the endpoint `def`. The sentence that shows depth: a sync endpoint is fine; a blocking *async* endpoint is the bug.
