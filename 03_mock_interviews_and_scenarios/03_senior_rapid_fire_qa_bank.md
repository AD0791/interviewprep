# Senior Rapid-Fire Q&A Bank

Verbal drill material: general mid/senior questions, deliberately **not** tied to the dashboard scenario. Answer each aloud in under 45 seconds — the printed answer is the *shape* of a strong response (why-first, names the tradeoff), not a script. Each ends with the follow-up an interviewer typically fires next.

---

## Python & Async Internals

**Q: What does the GIL actually prevent, and when does it matter?**
Only one thread executes Python bytecode at a time per process. It caps CPU-bound threading (use processes), but barely matters for I/O-bound work — threads release the GIL while waiting, and asyncio sidesteps threads entirely.
*Follow-up:* "So how do you parallelize CPU work?" → `ProcessPoolExecutor` or a task queue. → deep dive: [07/01](../07_advanced_runtimes_and_compilers/01_advanced_python_node_typescript.md)

**Q: asyncio vs threading vs multiprocessing — pick per workload.**
I/O-bound with high concurrency → asyncio (thousands of cheap coroutines). I/O-bound with sync-only libraries → threads. CPU-bound → processes. The mistake is defaulting to one hammer for all three.
*Follow-up:* "What breaks if you mix them wrong?" → sync-in-async blocks the loop; CPU work in threads gains nothing under the GIL.

**Q: What is an event loop, in one breath?**
A single-threaded scheduler that runs coroutines until they `await`, then switches to the next ready one — cooperative multitasking, so concurrency comes from yielding, not preemption.
*Follow-up:* "What's the contract that imposes on your code?" → never block. → [01/02](../01_fastapi_sqlalchemy_postgres/02_fastapi_runtime_internals.md)

**Q: `await` vs `asyncio.gather` — when does gather actually help?**
`await a(); await b()` is sequential; `gather(a(), b())` runs both concurrently. It helps when calls are independent I/O — two DB queries, three HTTP calls — and total latency drops to the slowest one.
*Follow-up:* "Error semantics?" → one exception cancels the rest unless `return_exceptions=True`.

**Q: What's a context manager really doing, and why do DB sessions use them?**
Deterministic acquire/release around a block (`__enter__`/`__exit__`), release guaranteed even on exception — exactly the shape of session/transaction lifetimes.
*Follow-up:* "Async version?" → `async with`, e.g. `session.begin()`. → gist: [python_async_context_manager.py](../usable_gists/python_async_context_manager.py)

## FastAPI

**Q: `async def` vs `def` route — what does FastAPI do differently?**
`async def` runs on the event loop (must never block); plain `def` is dispatched to a threadpool (~40 threads). Both are valid — the crime is a *blocking* `async def`.
*Follow-up:* "Symptom in production?" → cross-endpoint p99 spikes, since one blocked loop stalls all in-flight requests.

**Q: Sell me dependency injection in FastAPI in three sentences.**
Dependencies are declared as function parameters and resolved per request, composing into a graph (auth → session → repository). It centralizes cross-cutting concerns and — the senior half — makes them *swappable*: tests override `get_db` with a fixture in one line.
*Follow-up:* "Yield-dependencies?" → setup before `yield`, guaranteed teardown after the response — mini context managers per request.

**Q: What is lifespan for?**
Once-per-worker resource lifecycle: build the engine/HTTP clients before traffic, dispose them on SIGTERM after in-flight requests drain — the hook that makes graceful deploys work.
*Follow-up:* "Why not module-level?" → no clean teardown, wrong timing relative to fork/loop. → [01/02](../01_fastapi_sqlalchemy_postgres/02_fastapi_runtime_internals.md)

**Q: Middleware vs dependency — where does each belong?**
Middleware wraps *every* request (logging, timing, CORS, compression); dependencies attach per-route/router and can inject values into handlers (auth context, sessions). Rule: global and value-less → middleware; scoped or value-producing → dependency.
*Follow-up:* "Where does rate limiting go?" → coarse at the edge, per-tenant as a dependency/middleware with Redis state.

**Q: How does Pydantic earn its runtime cost?**
It's the validation boundary: untrusted JSON becomes typed, constrained objects at the edge, so the rest of the code trusts its inputs. v2's Rust core made the tax small; `response_model` also *filters* output, preventing accidental field leaks.
*Follow-up:* "Validation fails — what leaves the API?" → 422 with field-level errors. → [frameworks_specifics/04_pydantic.md](../frameworks_specifics/04_pydantic.md)

## SQLAlchemy & Postgres

**Q: Explain N+1 and both fixes.**
Loading N parents then querying children per parent = N+1 roundtrips. Fix with `selectinload` (second query, `IN` clause — collections) or `joinedload` (one JOIN — many-to-one). Set `lazy="raise"` so regressions fail loudly in dev.
*Follow-up:* "How do you *detect* it?" → query logs/echo in dev, per-request query counts in APM. → [01/01](../01_fastapi_sqlalchemy_postgres/01_postgres_aggregation_sqlalchemy.md)

**Q: Why aggregate in the database instead of Python?**
Payload (send the summary, not a million rows), memory (native C aggregation vs Python object churn), and the planner (indexes, parallelism). Python aggregation is the classic junior tell.
*Follow-up:* "GROUP BY vs window function?" → collapse vs in-place: summaries vs running totals/LAG/ranks.

**Q: Two writers, one row — your options?**
Pessimistic: `SELECT ... FOR UPDATE` serializes writers up front (hot rows, money). Optimistic: version column + retry on `StaleDataError` (rare conflicts). Contention level chooses.
*Follow-up:* "Deadlocks?" → lock in stable key order. → [01/03](../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md)

**Q: Size a connection pool.**
replicas × workers × (pool_size + max_overflow) must stay under Postgres `max_connections` minus headroom — connections are OS processes, not free sockets. Past that, PgBouncer multiplexes.
*Follow-up:* "QueuePool timeout errors mean?" → leaked sessions, slow queries hogging checkouts, or genuine undersizing — check `pg_stat_activity` before touching config.

**Q: A query is slow. Go.**
`EXPLAIN ANALYZE`, compare estimated vs actual rows (stats drift → `ANALYZE`), find the dominant node — Seq Scan discarding millions → composite index, equality columns before range — re-measure. Only after that: caching or matviews.
*Follow-up:* "Index Only Scan requirement?" → covering index (`INCLUDE`) + heap visibility. → [01/04](../01_fastapi_sqlalchemy_postgres/04_explain_analyze_partitioning_matviews.md)

**Q: Why Alembic at all, and what's the scary failure mode?**
Migrations as versioned, reviewable code with up/down paths. Scary mode: a DDL change that takes an exclusive lock (or rewrites the table) during peak traffic — hence expand/contract: add nullable, backfill in batches, then constrain.
*Follow-up:* "Two devs, two heads?" → `alembic merge`. → [frameworks_specifics/03_alembic.md](../frameworks_specifics/03_alembic.md)

## API Design & Auth

**Q: What makes an endpoint idempotent, and why care?**
Repeat calls converge to the same state. Networks retry — a non-idempotent POST retried is a double charge. Fix: client-supplied `Idempotency-Key`, server stores and replays the first response.
*Follow-up:* "Same key, different body?" → 409, client bug. → [04/06](../04_architecture_and_system_design/06_api_contracts_idempotency_pagination.md)

**Q: Offset vs cursor pagination — the two structural flaws of OFFSET?**
Cost grows with depth (produce-and-discard), and concurrent writes shift pages (dupes/gaps). Keyset filters past the last-seen `(created_at, id)` — O(1) with the right index, stable, but no random page jumps.
*Follow-up:* "What does the API return?" → an opaque cursor, so encoding stays server-side.

**Q: 401 vs 403 vs 409 vs 422 vs 429.**
401 unauthenticated, 403 authenticated-but-forbidden, 409 valid-but-business-refused, 422 schema-invalid, 429 rate-limited (+`Retry-After`). Uniform error *bodies* via RFC 7807 so clients parse one shape.
*Follow-up:* "Why does 429 + Retry-After help *you*?" → clients back off during incidents.

**Q: Walk the JWT refresh flow.**
Short access token verified locally per request; on 401, the interceptor single-flights a refresh; rotation burns the old refresh token; reuse of a burned token = theft signal → revoke the family. Statelessness for access, revocability at the refresh layer.
*Follow-up:* "Where do tokens live in the browser?" → HttpOnly cookie vs memory; never localStorage for refresh tokens. → [04/07](../04_architecture_and_system_design/07_oauth2_jwt_lifecycle.md), [02/02](../02_react_redux_swr_dashboard/02_browser_apis_and_storage.md)

## Caching & Scaling

**Q: Cache-aside in four steps, plus the write path.**
Read: check Redis → miss → query DB → populate with TTL. Write: mutate DB, then *delete* the key (never recompute inline). TTL is the agreed staleness budget, and the backstop for missed invalidations.
*Follow-up:* "Stampede at 9 AM?" → jittered TTLs, per-key rebuild lock, serve-stale-while-revalidate. → [04/08](../04_architecture_and_system_design/08_redis_caching_strategies.md)

**Q: You scale from 1 replica to 5 — what breaks?**
Everything hiding in process memory: in-memory caches drift, rate-limit counters split 5 ways, in-process websocket registries fragment, local file uploads vanish per pod. State moves to Redis/S3/pub-sub; the app must be stateless.
*Follow-up:* "Sticky sessions instead?" → an anti-pattern: defeats load balancing and breaks on pod death. → [04/09](../04_architecture_and_system_design/09_deployment_scaling_statelessness.md)

**Q: How many workers for async FastAPI on 4 cores?**
Start ~one worker per core (async workers each handle thousands of concurrent requests; `2×cores+1` is the *sync*-worker heuristic), then re-run pool math — workers multiply DB connections.
*Follow-up:* "gunicorn's role vs uvicorn's?" → process manager (fork, restart, signals) vs the ASGI server inside each worker.

**Q: Polling vs SSE vs WebSockets for live updates?**
Polling: simplest, latency = interval. SSE: one-way server push over HTTP, auto-reconnect — right default for dashboards. WebSockets: bidirectional, needed for chat/collab, costs connection-state management.
*Follow-up:* "WebSockets across 5 replicas?" → pub/sub (Redis) to fan out. → [05/01](../05_networking_and_data_transport/01_networking_protocols_dashboard.md)

## React & TypeScript

**Q: What triggers a re-render, and what's the actual cost model?**
State change re-renders the component and its subtree; reconciliation diffs the virtual DOM and patches minimally. Re-renders are cheap until proven otherwise — profile before memoizing.
*Follow-up:* "When does `React.memo` backfire?" → unstable object/function props re-break equality every render. → [frameworks_specifics/05_react.md](../frameworks_specifics/05_react.md)

**Q: Server state vs client state — why two tools?**
Server state (API data) is a *cache* with staleness, revalidation, and dedupe — SWR/React Query territory. Client state (filters, modals) is owned truth — local state or Redux Toolkit. Jamming server data into Redux hand-rolls a worse SWR.
*Follow-up:* "So what's left in Redux?" → genuinely global, client-owned state: session UI, cross-widget filters. → [02/01](../02_react_redux_swr_dashboard/01_react_dashboard_rendering_state.md)

**Q: A widget crashes on bad data — what does the user see?**
Without an error boundary: a blank page — the whole tree unmounts. With per-widget boundaries: one broken card with a retry that resets the boundary *and* revalidates SWR. Blast-radius design.
*Follow-up:* "Why can't a hook replace the class boundary?" → React exposes render-phase error catching only via class lifecycles; libraries wrap it. → [02/03](../02_react_redux_swr_dashboard/03_error_boundaries_suspense_profiling.md)

**Q: The dashboard is janky — your diagnosis workflow?**
React DevTools Profiler: record the interaction → ranked commits → flamegraph → "why did this render". Typical verdicts: unstable props re-rendering a memoized subtree, or a 5,000-row list needing virtualization. Measure, then fix.
*Follow-up:* "And if it's not React?" → Performance tab: long tasks, layout thrash.

**Q: What do TypeScript generics buy in API code?**
One typed pipe instead of `any` at every boundary: `useApi<Account[]>` flows the type from fetcher to component; Zod validates at *runtime* and infers the same static type — one source of truth for both worlds.
*Follow-up:* "`unknown` vs `any`?" → `unknown` forces narrowing; `any` opts out of the compiler. → gist: [typescript_advanced_generics.ts](../usable_gists/typescript_advanced_generics.ts)

## Testing

**Q: Test pyramid for a FastAPI service, argued not recited.**
Many fast unit tests on domain logic (fake repositories, no DB), fewer integration tests proving SQL against real Postgres, few API tests asserting the HTTP contract via dependency overrides. Shape follows cost: the slow layers exist to catch what fakes can't.
*Follow-up:* "What do fakes miss?" → real SQL behavior — exactly why the integration layer exists. → [06/02](../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md)

**Q: Why prefer a fake repository over MagicMock?**
A fake implements the Protocol with an in-memory dict — it has *behavior*, survives refactors, and can't drift into asserting implementation details. MagicMock happily returns nonsense and couples tests to call signatures.
*Follow-up:* "Where does the Protocol come from?" → [repository_pattern_sqlalchemy.py](../usable_gists/repository_pattern_sqlalchemy.py)

**Q: Frontend and backend deploy independently — how do you stop contract drift?**
The OpenAPI schema is the contract: generate TS types/Zod schemas from it in CI, so a breaking backend change fails the frontend build instead of production. Full consumer-driven contracts (Pact) when teams/services multiply.
*Follow-up:* "Who owns the contract?" → consumers drive, providers verify.

## Behavioral-Technical Hybrids

**Q: Tell me about a performance problem you solved.**
Shape (STAR, 90 seconds): metric that defined "slow" → diagnosis with a tool (EXPLAIN/Profiler), not guesswork → the fix *and the tradeoff it cost* → measured after-number + the regression guard you left behind. Have two ready: one backend, one frontend.

**Q: How do you review a teammate's PR?**
Correctness and blast radius first (migrations, contracts, security), then design fit, then style — and say you distinguish blocking comments from preferences. Mention praising good patterns; reviews teach.

**Q: You disagree with a design decision — walk me through it.**
Steel-man their version first, quantify your concern (latency, ops burden, coupling), propose the experiment that would settle it, and commit fully once decided — disagree-and-commit beats relitigating.

**Q: What would you do in your first two weeks on our codebase?**
Ship something small end-to-end early (forces touching CI, review, deploy), read the data model before the code, pair on a bug, and keep a friction log — fresh eyes are a one-time asset the team loses fast.
