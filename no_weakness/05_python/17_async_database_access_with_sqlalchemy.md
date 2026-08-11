# Async database access with SQLAlchemy — one `select()` for Core and ORM, and the bridge async lazy-loading depends on

*The metaclass behind the declarative base, why touching an unloaded relationship inside `async def` can raise an error naming a library you never imported, and the 2.0 rewrite that made one query construct answer to both halves of the library.*

**Level:** L4 · **Prerequisites:** [03 closures, decorators, and metaprogramming](03_closures_decorators_and_metaprogramming.md)
**Covers:** PY-16
**Sources:** Tragura, *Building Python Microservices with FastAPI*, ch.5 (2022) — SQLAlchemy 1.x material, cited only as the migration source · SQLAlchemy's own 2.0 migration documentation

---

## 1. The problem this solves

SQLAlchemy has historically been two libraries wearing one name: **Core**, a general SQL expression language for building queries against tables directly, and the **ORM**, a separate layer mapping Python classes to those tables and historically querying them through its own `Query` object with its own syntax. Learning SQLAlchemy well enough to use both meant learning two overlapping ways to say the same thing, and knowing, for any given task, which one was idiomatic. SQLAlchemy 2.0 answers this by unifying both behind one construct — `select()`, executed through one method, `Session.execute()` — which section 2.2 shows is not merely a style convention but a genuine, verifiable fact about the object each style produces.

This is not merely a matter of taste between two spellings of the same idea. The ORM's `Query` object, in the years before 2.0, carried its own accumulated set of conventions — `.filter()` versus `.filter_by()`, `.get()` as a shortcut method with its own special-cased identity-lookup behavior, join syntax that diverged from Core's own — each one more surface a developer had to learn on top of Core's expression language, for behavior that, underneath, ultimately compiled to the same SQL either way. A project mixing both styles freely, as many pre-2.0 codebases did out of simple convenience, ended up with two dialects of "how to write a query" living side by side in the same file, chosen inconsistently depending on which example a given piece of code happened to be copied from.

The second, unrelated problem is what makes this chapter's title mention async at all. SQLAlchemy's ORM — the part that turns a row into a Python object, tracks what changed, and lazily fetches a related row the moment code asks for it — was built long before Python had `async`/`await`, and its internal machinery is, underneath, ordinary synchronous code. Running it inside an `async def` handler without breaking anything requires a real bridge between two execution models that were never designed with each other in mind, and that bridge is not invisible — it leaks into behavior a reader has to understand directly, most visibly the moment code touches a database-backed value the bridge was not actively watching at the time.

---

## 2. The mechanism, built up

### 2.1 The declarative base is not a convention — it is a real metaclass, doing real work at class-definition time

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(50))

print(type(Account))
```

```text
<class 'sqlalchemy.orm.decl_api.DeclarativeAttributeIntercept'>
```

`Account`'s type is not `type` — it is `DeclarativeAttributeIntercept`, a real metaclass, exactly the construction chapter 3 already covers: a class whose instances are themselves classes, customizing what happens as `Account`'s own class body is processed. This is precisely why annotating a class attribute `owner: Mapped[str] = mapped_column(String(50))` does something far more active than chapter 9's ordinarily-inert annotations — the metaclass inspects `Account`'s namespace as it is built, recognizes `mapped_column(...)` assignments, and wires each one into the ORM's mapping configuration, replacing the plain class attribute with a real descriptor (chapter 1's mechanism) that tracks reads and writes against a specific database column. Chapter 3's own account of this shelf's material already names exactly this — a declarative ORM base as one of the few places application code genuinely encounters a metaclass rather than merely being told metaclasses exist — and this is that place, made concrete.

### 2.2 Core and ORM both build the identical `Select` object, executed through the identical method

```python
from sqlalchemy import select

core_stmt = select(Account.__table__.c.owner)                  # Core: a column
orm_stmt = select(Account).where(Account.owner == "alexandro")  # ORM: a mapped class

print(type(core_stmt) is type(orm_stmt))
```

```text
True
```

There is no separate "Core query" type and "ORM query" type to learn — `select(...)`, regardless of whether it is given a raw `Table` column or a mapped class, returns the same `sqlalchemy.sql.selectable.Select` object, and both are executed the same way, through `session.execute(stmt)`. This is the concrete, verifiable content behind "2.0 unifies Core and ORM": not a marketing claim about the two feeling more similar, but a fact about the actual class hierarchy — one construct, one execution path, regardless of which layer's syntax built it.

### 2.3 An async engine wraps an async-capable driver; the session API is otherwise the same shape, `await`ed

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("sqlite+aiosqlite:///:memory:")

async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

async with AsyncSession(engine) as session:
    session.add(Account(owner="alexandro"))
    await session.commit()

async with AsyncSession(engine) as session:
    result = await session.execute(select(Account).where(Account.owner == "alexandro"))
    account = result.scalar_one()
```

`aiosqlite` in the connection URL names an async-capable DBAPI driver — the actual library speaking the wire protocol to the database — and `create_async_engine` is what SQLAlchemy provides specifically to drive that driver from `async def` code. `AsyncSession` mirrors the synchronous `Session`'s API closely enough that most method names are identical; the difference is that every operation touching the database — `execute`, `commit`, `refresh`, and others — is now a coroutine, awaited exactly as chapter 15's own asynchronous FastAPI handlers already are. `Base.metadata.create_all`, notably, is *not* async — it is ordinary synchronous SQLAlchemy code, run through `conn.run_sync(...)`, which is section 2.4's mechanism made visible at the one point this example needs it.

### 2.4 `run_sync` and the `greenlet` library are the actual bridge between async Python and SQLAlchemy's synchronous internals

SQLAlchemy's ORM — object tracking, lazy attribute loading, unit-of-work change detection — predates `async`/`await` in Python entirely, and was never rewritten as native async code underneath. The async extension does not reimplement that machinery; it runs the *existing*, synchronous ORM code inside a **greenlet** — a lightweight, cooperatively-scheduled execution context — and bridges that greenlet's blocking calls back into the surrounding `asyncio` event loop. Without the `greenlet` package installed, the async engine fails immediately and explicitly, rather than silently falling back to something slower:

```text
ValueError: the greenlet library is required to use this function. No module named 'greenlet'
```

This is worth knowing as a real, named dependency rather than an implicit assumption: an async SQLAlchemy application has a hard runtime dependency on `greenlet`, pulled in automatically by `pip install sqlalchemy[asyncio]`, and the entire async ORM experience — every `await session.execute(...)` — is, underneath, synchronous ORM code running inside that bridge, not a from-scratch asynchronous reimplementation of the ORM's actual logic.

```mermaid
graph TD
    ASYNC["async def handler:<br/>await session.execute(stmt)"] --> BRIDGE["greenlet_spawn —<br/>hands control to a greenlet"]
    BRIDGE --> SYNC["the ORM's real, synchronous<br/>query-building and mapping logic"]
    SYNC --> DRIVER["the async DBAPI driver<br/>(aiosqlite, asyncpg, ...)"]
    DRIVER -->|"actual I/O awaited<br/>back on the event loop"| BRIDGE
    BRIDGE --> ASYNC
```

### 2.5 Touching an unloaded relationship outside the bridge's active scope raises `MissingGreenlet`, not a slow, silent query

Chapter 1 already flags — as a `documented`, not directly inspected, claim — that an ORM's lazy-loading attribute is a descriptor issuing a query the moment code reads it. Under the async extension, that same mechanism has a sharper failure mode than merely "slow":

```python
async with AsyncSession(engine) as session:
    result = await session.execute(select(Account))
    account = result.scalar_one()

print(account.transactions)     # accessed after the session's own await has already returned
```

```text
MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
Was IO attempted in an unexpected place?
```

`account.transactions` is a plain, synchronous attribute read — chapter 1's descriptor protocol, not a coroutine, and never `await`ed — and when SQLAlchemy's lazy-loading descriptor decides it needs to issue a query to satisfy it, it needs the same greenlet bridge section 2.4 describes to actually run that query against an async driver. If that specific attribute access happens outside a greenlet SQLAlchemy has already spawned for the current operation, there is no bridge available to hand the I/O off to, and the library raises immediately rather than attempting something unsafe. This is a direct, structural consequence of async lazy loading rather than a bug: a lazy attribute is, in effect, a piece of hidden I/O with no `await` anywhere near it in the calling code, which the synchronous ORM has always allowed and which the async bridge can only support from within its own, carefully-scoped greenlet context.

### 2.6 Eager loading resolves relationships inside the same query, before the greenlet bridge's scope ends

```python
from sqlalchemy.orm import selectinload

async with AsyncSession(engine) as session:
    result = await session.execute(
        select(Account).options(selectinload(Account.transactions))
    )
    account = result.scalar_one()

print([t.amount for t in account.transactions])   # already loaded — no further query, no MissingGreenlet
```

```text
[10, -5]
```

```mermaid
graph TD
    subgraph lazy["lazy (default) — under async"]
        L1["select(Account)"] --> L2["greenlet scope ends —<br/>session.execute() has returned"]
        L2 --> L3["account.transactions read later"]
        L3 --> L4["MissingGreenlet — no bridge<br/>available for this I/O"]
    end
    subgraph eager["eager (selectinload)"]
        E1["select(Account).options(selectinload(...))"] --> E2["both queries run inside<br/>ONE greenlet scope"]
        E2 --> E3["account.transactions already populated —<br/>reading it later touches no I/O at all"]
    end
```

`selectinload(Account.transactions)` tells SQLAlchemy to issue a second, explicit `SELECT` for the related rows as part of the same `session.execute(...)` call — fully inside the bridge's active scope — rather than deferring that query to whenever something later happens to read `.transactions`. This is the direct fix for section 2.5's failure, and it is also, independently, the correct fix for chapter 1's N+1 problem: a loop reading `.transactions` off fifty accounts, each triggering its own lazy query, becomes one additional query total, run eagerly, regardless of how many accounts the loop later iterates over.

### 2.7 The connection pool's shape depends entirely on which database is actually behind the URL

```python
from sqlalchemy import create_engine

sqlite_engine = create_engine("sqlite:///:memory:")
print(type(sqlite_engine.pool).__name__)          # SingletonThreadPool

pg_engine = create_engine("postgresql+psycopg2://user:pass@localhost/db")
print(type(pg_engine.pool).__name__)               # QueuePool
print(pg_engine.pool.size())                        # 5
```

An in-memory SQLite database — a single file-like connection with no real concurrent-connection concept — gets `SingletonThreadPool`, a pool shaped around SQLite's own constraints. A real client-server database reached over a network gets `QueuePool`, SQLAlchemy's general-purpose pool, defaulting to five persistent connections kept open and reused across requests rather than opened and closed on every single query. This default is a real, load-bearing capacity number for a deployed service — five concurrent database operations before a sixth request has to wait for one to free up — and it is set per-engine, not globally, which means a service holding more than one `create_engine(...)` call (a primary database and a separate analytics database, for instance) is choosing that capacity independently for each.

Two further parameters shape what happens once that base capacity is exhausted, and both are worth configuring deliberately rather than leaving at their defaults for a production service: `max_overflow` (default `10`) allows the pool to open additional connections beyond `pool_size` under burst load, and `pool_timeout` (default `30` seconds) bounds how long a request will wait for a connection to become available before giving up rather than queuing indefinitely. A service that never configures either is implicitly accepting SQLAlchemy's own defaults — up to fifteen total connections under sustained load, and a thirty-second wait before a caller sees a timeout error — which may or may not match what the actual database server's own connection limit, and the application's own latency budget, can tolerate.

### 2.8 `Session.get()` is the 2.0 form of what `Query.get()` used to be, and the legacy form still runs, loudly deprecated

```python
with Session(engine) as session:
    a1 = session.get(Account, 1)              # 2.0 style
    a2 = session.query(Account).get(1)         # legacy style
```

```text
LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of
SQLAlchemy and becomes a legacy construct in 2.0. The method is now available as
Session.get() (deprecated since: 2.0)
```

Both calls return the identical result — `session.query(Account)` still works, internally building a 2.0-style `select()` underneath its older interface — and the legacy path emits an explicit `LegacyAPIWarning` naming exactly which 2.0-native method replaces it. This mirrors chapter 16's own account of Pydantic's v1 shims more than it resembles chapter 15's `on_event` trap: the old spelling keeps working, correctly, with a loud and specific warning, rather than silently doing nothing — a codebase inherited from a 1.x-era book like this node's own migration source can be modernized incrementally, one `Query.get()` at a time, guided directly by the warnings it produces on its own.

### 2.9 A session autoflushes pending changes before a query, and discards everything unwritten on rollback

```python
with Session(engine) as session:
    session.add(Account(owner="alexandro"))
    result = session.execute(select(Account).where(Account.owner == "alexandro"))
    print(result.scalar_one_or_none() is not None)   # True — before any explicit commit

    session.rollback()
    print(session.execute(select(Account)).scalars().all())   # []
```

```text
True
[]
```

`session.add(...)` does not immediately write to the database — it registers the new object with the session's pending changes. The `SELECT` that follows finds it anyway, because a `Session`, by default, **autoflushes**: it sends every pending change to the database, inside the current transaction, before running any query, specifically so a query never has to account for changes the same session already knows about but has not yet physically written. None of this is committed yet, which `session.rollback()` demonstrates directly — every pending and even already-flushed-but-uncommitted change within the transaction is discarded in full, and the table is empty again, exactly as if `add(...)` had never been called. This is the mechanism that makes a session a genuine transaction boundary: nothing is durable until `commit()` succeeds, and anything short of that — an exception, an explicit `rollback()`, or the session simply being discarded without a commit — leaves the database exactly as it was before the session began.

### 2.10 A session's scope should match a request's scope, not the application's

The examples throughout this chapter open a fresh `AsyncSession` per unit of work — a pattern worth stating as a rule rather than a coincidence of how the examples happen to be written. A session tracks every object it has loaded or modified, as part of the ORM's change-tracking machinery, and holding one open across multiple, unrelated requests means one request's uncommitted changes, or one request's stale cached view of a row another request has since modified, can leak into a completely different request's logic. Chapter 15's own `Depends()` mechanism is the natural place this scoping lives in a FastAPI application: a dependency function that opens a session, yields it for the handler to use, and closes it afterward — via a generator dependency, `yield`ing the session between setup and teardown — ties the session's entire lifetime to exactly one request's dependency graph, reusing chapter 15's own per-request caching so every dependency within that one request shares the identical session rather than each opening its own.

---

## 3. Failure modes

### 3.1 Reading a lazy relationship outside the greenlet bridge's scope raises `MissingGreenlet`, and the fix is not "add an `await`"

```python
# Gist: missing_greenlet.py
async with AsyncSession(engine) as session:
    result = await session.execute(select(Account))
    account = result.scalar_one()

print(account.transactions)
```

```text
MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

The instinctive fix — `await account.transactions` — does not exist, because `.transactions` is a plain attribute, not a coroutine; there is nothing to `await` at the call site at all. Section 2.5 already establishes the actual mechanism: this line needed I/O, and the bridge that makes I/O possible from inside SQLAlchemy's synchronous ORM code was only active during the `session.execute(...)` call already completed above, not at the point this later, ordinary-looking attribute access occurs. The message itself — naming `greenlet_spawn` and `await_only`, neither of which appears anywhere in the calling code — is unusually opaque for exactly this reason: it is describing an internal bridging mechanism the caller never invoked directly, from a line of code that looks like the most ordinary possible Python. The real fix is one of two structural changes, not a syntax tweak: eager-load the relationship with `selectinload`/`joinedload` at query time (section 2.6), or explicitly `await session.refresh(account, ["transactions"])` before the attribute is ever read outside the original session's active operation — both of which move the I/O back inside a scope the bridge can actually see.

### 3.2 A `Query.get()` call inherited from a 1.x-era codebase still runs correctly, which hides how much of the migration to 2.0 idioms actually remains

```python
# Gist: silently_still_legacy.py
account = session.query(Account).get(1)   # works, emits a warning, easy to miss in test output
```

Exactly like chapter 16's Pydantic v1 shims, this line succeeds, returns the correct object, and passes any test asserting on its result — the only signal anything is outdated is a `LegacyAPIWarning`, filtered out of CI output in any project that has not explicitly configured warnings to fail a build. A codebase that upgraded its `sqlalchemy` pin to 2.0 without also auditing its own query code for `session.query(...)` calls can run correctly, and slowly accumulate more of them over time as new code is written by habit against the familiar `Query` interface, all while never actually adopting the `select()`-based style this node's own currency correction identifies as the only form a current article should teach. The risk is not correctness — the legacy path is a genuine, supported compatibility layer, not a landmine — it is that "the tests pass" is, once again, evidence only that the compatibility shim works, not evidence that a team has captured whatever benefit motivated the 2.0 rewrite in the first place. The fix is the same discipline chapter 16 already recommends: treat "still emits a legacy warning" as a tracked, swept-through category of technical debt, not a passive footnote in build logs nobody reads.

### 3.3 Sharing one long-lived session across unrelated requests lets one request's uncommitted state leak into another's

```python
# Gist: shared_session_leak.py
session = AsyncSession(engine)   # opened once, at application startup — the bug

async def handle_request_a():
    account = (await session.execute(select(Account).where(Account.id == 1))).scalar_one()
    account.owner = "renamed-but-not-committed-yet"
    # request A crashes here, before session.commit()

async def handle_request_b():
    account = (await session.execute(select(Account).where(Account.id == 1))).scalar_one()
    print(account.owner)   # sees "renamed-but-not-committed-yet" — a change from a DIFFERENT request
```

A session opened once and reused across every request keeps every object it has ever loaded in its own identity map, uncommitted changes included, for as long as the session itself stays open — which means an object one request modified and never committed (because it crashed, or because a bug simply forgot to call `commit()`) is still sitting in that shared session's memory the next time a completely unrelated request asks for the same row, and gets handed the same, still-modified, still-uncommitted Python object instead of a fresh read from the database. Section 2.10 already names the fix as a design principle; here is the concrete shape of what skipping it costs: two logically unrelated requests, served by the same process, observing and potentially corrupting each other's in-progress state through nothing more than sharing one `AsyncSession` that outlived the request it was actually opened for. The fix is structural, not a patch — a session's lifetime must be tied to exactly one unit of work (one request, one background job execution), opened fresh and closed unconditionally at the end of each, which is precisely what chapter 15's `Depends()`-based, `yield`-scoped dependency pattern provides automatically when a session is wired as a per-request dependency rather than a module-level singleton.

### 3.4 `session.execute(select(Account))` returns `Row` tuples, not `Account` instances — the unification section 2.2 describes has a real, easy-to-miss consequence

```python
# Gist: forgot_scalars.py
result = session.execute(select(Account))
first = result.first()
print(type(first))
print(first.owner)
```

```text
<class 'sqlalchemy.engine.row.Row'>
AttributeError: owner
```

`first` is not an `Account` — it is a `Row`, a tuple-like wrapper around every column or entity the `select(...)` named, because `execute()` is the single, unified execution method section 2.2 already establishes serves *both* Core queries (which naturally return tuples of column values) and ORM queries (which a developer typically wants back as plain mapped objects). `select(Account)` asked for one entity, so the resulting `Row` happens to hold exactly one element, but it is still a `Row` of length one, not the `Account` itself — `first[0]` is the actual account, and `first.owner` fails because a `Row` has no attribute by that name at all. This is precisely the kind of trap a developer migrating from the pre-2.0 `Query` API hits immediately: `session.query(Account).first()` always returned a model instance directly, with no unwrapping step, and the muscle memory of writing `result.owner` right after a query transfers cleanly in every case except this one, where it produces an `AttributeError` that gives no hint the actual problem is a missing `.scalars()` call. The fix is `session.execute(select(Account)).scalars().first()` (or `.scalar_one()`, when exactly one result is expected and its absence should itself be an error) — `.scalars()` unwraps every `Row` in the result down to its single entity, which is unnecessary, and unavailable to call meaningfully, on a genuinely multi-column Core query where a `Row` is the actually correct shape of answer.

---

## 4. Trade-offs

| Approach | Use when | Because | Real cost |
| --- | --- | --- | --- |
| **Core-style `select()` on raw tables** | The task is a genuinely relational query — joins, aggregates — with no need for Python object mapping | No ORM overhead; the result is exactly the rows requested | No automatic object identity, change tracking, or relationship navigation |
| **ORM-style `select()` on mapped classes** | The result should be usable as ordinary Python objects with attributes and relationships | Identity map, change tracking, and lazy/eager relationship loading all included | Real per-row overhead for the mapping machinery; a source of the N+1 hazard section 2.6 addresses |
| **Lazy loading (the default)** | A relationship is only sometimes needed, and loading it unconditionally would waste a query most of the time | No extra query paid when the relationship is never actually read | The `MissingGreenlet` failure mode under async, and the classic N+1 cost under any execution model |
| **Eager loading (`selectinload`/`joinedload`)** | The relationship is needed on every result, known at query time | One predictable, bounded number of additional queries regardless of result-set size | Loads data that might go unused on some fraction of results, and adds real complexity to the query definition itself |
| **A session opened per request/unit of work** | The default, correct choice for essentially any web service | Isolates each request's state, matching chapter 15's own per-request dependency scoping | One session's setup/teardown cost paid per request — negligible next to the correctness this buys |
| **`.scalars()` on an ORM-entity query** | The query selected whole mapped entities and the caller wants them back directly | Unwraps every `Row` down to its single entity, matching the pre-2.0 `Query` API's behavior | Meaningless — and unavailable to call sensibly — on a genuinely multi-column result, where `Row` tuples are the correct shape |

### The case against reaching for Core when the ORM's mapping is what a project actually needs

Dropping to Core-style raw `select()` calls to "avoid ORM overhead" is a real option and, absent a measured bottleneck, usually a premature one: the ORM's identity map and change tracking are exactly what makes a service's business logic legible as operations on ordinary Python objects rather than as hand-assembled SQL threaded through every function that touches the database. The rejected alternative to the ORM here is accepting that every piece of code touching a mapped entity now has to manage rows and foreign keys by hand — the cost Core-style code pays uniformly, everywhere, in exchange for a performance benefit that, in the overwhelming majority of ordinary CRUD-shaped services, was never actually the bottleneck to begin with.

### The case against treating the async extension as a drop-in replacement for the sync API

Section 2.4's greenlet bridge is real, working machinery, and it is not free of behavioral edges the synchronous `Session` never had — section 2.5's `MissingGreenlet` failure has no equivalent under synchronous SQLAlchemy, where a lazy attribute simply runs its query inline, on the same thread, with no bridge to fall outside of. A team porting an existing synchronous codebase to `async def` handlers by mechanically prefixing calls with `await` and swapping `Session` for `AsyncSession` is treating the two as interchangeable, when the async extension's behavior around lazy loading specifically is not: every relationship access that used to be an invisible, automatic convenience under the sync API needs to be audited for whether it happens inside or outside an active greenlet scope. The rejected alternative to that audit is discovering each instance the hard way, in production, the first time a request path happens to exercise a lazy attribute the migration missed.

### When Core genuinely is the right choice over the ORM

A reporting query joining six tables and aggregating into values with no natural mapped-class shape at all is precisely where the ORM's object-mapping ceremony buys nothing — there is no meaningful "row as a Python object with relationships" story for a query whose actual output is a handful of aggregate numbers. Core's `select()`, used directly against tables or views with no `DeclarativeBase` involved, expresses exactly that kind of query without inventing a mapped class purely to give the ORM something to attach identity tracking to that the query will never use.

The same reasoning extends to bulk operations — updating or deleting thousands of rows matching a condition, where the ORM's usual per-object change-tracking would mean loading every one of those rows into memory as a mapped instance, mutating each, and flushing the results individually, purely to accomplish something a single `UPDATE ... WHERE ...` statement expresses directly. SQLAlchemy's own Core-level `update()`/`delete()` constructs, executed the same way as a `select()`, exist specifically for this case: bulk, condition-driven mutation with no need for object identity anywhere in the operation, at a fraction of the memory and round-trip cost the ORM's row-by-row model would otherwise impose.

---

## 5. Reference summary

**`DeclarativeBase` is a real metaclass (`DeclarativeAttributeIntercept`)**, inspecting a mapped class's body at definition time exactly as chapter 3's metaclass material describes, converting `mapped_column(...)` assignments into real descriptors tracking a specific database column. **Core and ORM both build the identical `Select` object**, executed identically through `Session.execute()` — SQLAlchemy 2.0's unification is a fact about the actual class produced, not merely a stylistic convergence. **`session.execute(stmt)` always returns `Row` objects, even for a query selecting a single ORM entity** — `.scalars()` unwraps each `Row` down to its entity, matching what the pre-2.0 `Query` API returned directly; omitting it is a common, silent-until-accessed migration trap, surfacing as an `AttributeError` naming the field that was actually requested rather than any hint about the missing call.

**The async extension does not reimplement the ORM's logic natively — it runs the existing synchronous ORM code inside a `greenlet`**, bridging its blocking calls back onto the surrounding event loop; `greenlet` is consequently a real, required runtime dependency for async SQLAlchemy, not an implementation detail. **Touching a lazily-loaded relationship outside that bridge's active scope raises `MissingGreenlet`**, an error naming internal machinery the calling code never invoked directly — the fix is eager loading (`selectinload`/`joinedload`) at query time, or an explicit `await session.refresh(...)`, never adding an `await` to a plain attribute access that has nothing to await.

**Connection pool defaults depend on the actual backend**: SQLite gets `SingletonThreadPool`; a networked database gets `QueuePool`, defaulting to five persistent connections, with `max_overflow` (default `10`) permitting temporary additional connections under burst load and `pool_timeout` (default `30` seconds) bounding how long a caller waits for one before failing — real, per-engine capacity figures worth setting deliberately for a production service rather than assuming. **`Session.get()` is the 2.0-native replacement for the legacy `Query.get()`**, which still runs correctly under a `LegacyAPIWarning` naming its replacement explicitly — a codebase whose tests pass after a 2.0 upgrade has not necessarily migrated its query style, only exercised a working, loudly-deprecated compatibility path.

**A session autoflushes pending changes before running a query**, so a query within the same session sees its own uncommitted work, and **nothing is durable until `commit()` succeeds** — `rollback()`, an unhandled exception, or simply discarding the session without committing all discard every pending and flushed-but-uncommitted change in full.

**A session's lifetime should match exactly one request or unit of work**, never the application's own lifetime — a shared, long-lived session lets one request's uncommitted or stale state leak into an unrelated request through the ORM's own identity map, and the structural fix is scoping session creation through a per-request dependency (chapter 15's `Depends()`/`yield` pattern), not a module-level singleton opened once at startup.

---

← [Python knowledge graph](00_knowledge_graph.md) · [repo index](../README.md)
