# SQLAlchemy 2.0, From Zero

You know SQL and Python. This article explains what an ORM actually buys you, builds a working async setup from nothing, and then makes you deliberately hit the two failures every SQLAlchemy interview probes: the N+1 problem and the async lazy-load crash. Watching them happen is how you earn the right to explain them.

---

## 1. The Problem: Rows Are Not Objects

Talk to Postgres directly and you write string SQL, get back tuples, and map them to your domain by hand:

```python
row = cursor.execute("SELECT id, balance FROM accounts WHERE id = %s", (7,)).fetchone()
account = {"id": row[0], "balance": row[1]}   # position-based, untyped, repeated everywhere
```

This works, and for some workloads it's even right (we'll come back to that). But at application scale it has three chronic costs: the mapping code is duplicated and drifts; there is no type checking between your SQL strings and your Python code, so a renamed column becomes a runtime error; and relationships ("this account's transactions") mean hand-writing joins and re-assembling nested structures everywhere you need them.

An ORM — Object Relational Mapper — maintains the mapping in one place: a class per table, an attribute per column, typed. SQLAlchemy is Python's standard one, and version 2.0 made the mapping *statically typed*, so your editor and mypy know that `account.balance` is a float before anything runs.

## 2. Models and the Engine (How)

```bash
pip install "sqlalchemy[asyncio]" asyncpg
```

```python
# Gist: models.py
from datetime import datetime
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(100))
    balance: Mapped[float] = mapped_column(default=0.0)

    # One account has many transactions. lazy="raise" is explained in section 5 —
    # it turns a silent performance bug into a loud error.
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", lazy="raise"
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    amount: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="transactions")
```

`Mapped[int]` does double duty: it tells SQLAlchemy the column type *and* tells your type checker the attribute type. `Mapped[list["Transaction"]]` declares the one-to-many; `back_populates` makes the two sides aware of each other, so setting `tx.account` also appends to `account.transactions` in memory.

Connecting takes two objects with different lifetimes:

```python
# Gist: database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://app:secret@localhost:5432/bank",
    echo=True,  # log every SQL statement — leave this on while learning
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

The **engine** is created once per process. It owns the connection pool — a set of open Postgres connections that get borrowed and returned, because opening a fresh connection per request is far too expensive ([01/03](../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md) covers sizing it). A **session**, which `SessionLocal()` creates, is the short-lived workspace for one unit of work — in a web app, one request. Engine: application lifetime. Session: request lifetime. Mixing those up is a classic review catch.

## 3. The Session Is a Staging Area, Not a Connection (Why)

Here's the mental model that unlocks everything else. A session is like **git's staging area for database rows**. You stage changes; nothing hits the database until a flush; nothing is permanent until a commit.

```python
async with SessionLocal() as session:
    account = Account(owner="Alexandro")   # 1. plain object — DB knows nothing
    session.add(account)                   # 2. staged ("pending") — still no SQL
    await session.flush()                  # 3. INSERT executes; account.id now exists
    print(account.id)                      #    ...but it's inside an open transaction
    await session.commit()                 # 4. COMMIT — now it's real and visible to others
```

Run this with `echo=True` and watch the log: nothing at step 2, the `INSERT` at step 3, `COMMIT` at step 4. The distinction between flush and commit is a favorite interview probe, and now you've *seen* it: **flush sends SQL** (so the database can assign the primary key, which is why repositories flush when they need an id mid-transaction), while **commit ends the transaction** (making the changes durable and visible to other connections). Between the two, your own session can read its own writes; nobody else can.

The session also keeps an **identity map**: within one session, the row with primary key 7 is always the *same Python object*. Query it twice, get the same instance — so two parts of your request handler can't hold diverging copies of one account. That's a big part of what "unit of work" means: the session tracks every object you've touched and, at flush, computes the minimal SQL to persist exactly what changed. You rarely write `UPDATE` by hand — you mutate the object (`account.balance -= 50`) and flush.

Reading uses `select()` — the same construct for simple and complex queries:

```python
from sqlalchemy import select

result = await session.execute(
    select(Account).where(Account.balance > 1000).order_by(Account.balance.desc())
)
rich_accounts = result.scalars().all()   # scalars() unwraps 1-column rows to objects
```

## 4. Break It On Purpose #1: The N+1 Problem

Now the failure everyone asks about. Render a page of 50 accounts, each with its transactions. The natural code:

```python
result = await session.execute(select(Account).limit(50))
for account in result.scalars():
    print(account.owner, len(account.transactions))   # innocent-looking line
```

With default settings, that innocent attribute access triggers **lazy loading**: the ORM notices transactions weren't loaded and quietly runs `SELECT * FROM transactions WHERE account_id = ?` — *per account*. One query became 51. With `echo=True` you'll see them scroll by, which is exactly how you'd catch it in development. The nasty part is the shape of the failure: 51 fast queries feel fine on your laptop and melt under production concurrency, because the cost is round-trips, not row count.

Our model declared `lazy="raise"`, so instead of 51 silent queries you get an immediate exception — the bug announces itself in dev. The fix is telling SQLAlchemy your access pattern up front:

```python
from sqlalchemy.orm import selectinload

result = await session.execute(
    select(Account).options(selectinload(Account.transactions)).limit(50)
)
# Exactly 2 queries, always:
#   SELECT ... FROM accounts LIMIT 50
#   SELECT ... FROM transactions WHERE account_id IN (1, 2, ..., 50)
```

Two strategies cover nearly everything, and the choice follows the relationship's direction. **`selectinload`** issues that second `IN` query — right for one-to-many collections, because a join would duplicate each parent row once per child. **`joinedload`** folds the related row into the original query with a LEFT OUTER JOIN — right for many-to-one (each transaction's single account), where the join duplicates nothing. Collection: `selectinload`. Single parent: `joinedload`. The deeper treatment, including when to skip the ORM and aggregate in SQL, is [01/01](../01_fastapi_sqlalchemy_postgres/01_postgres_aggregation_sqlalchemy.md).

## 5. Break It On Purpose #2: The Async Lazy-Load Crash

The async story is mostly "same API with `await`" — but one crash is so common it deserves its own section, because explaining it well is a senior signal.

By default, `session.commit()` **expires** every loaded object: the next attribute access re-fetches from the database, to guarantee freshness. In sync code that's a hidden query. In async code, a plain attribute access like `account.owner` *cannot* await anything — so when it tries to do I/O, SQLAlchemy raises the infamous `MissingGreenlet` error. The sequence: commit, then touch an attribute, then crash with an error message that names none of those things.

That's why our sessionmaker set `expire_on_commit=False` — objects stay readable after commit — and why relationships get `lazy="raise"` plus explicit `selectinload`. Both settings enforce the same philosophy: **in async code, all I/O must be explicit and awaited; anything that does hidden I/O on attribute access is a landmine.** Say that sentence in the interview and the follow-ups take care of themselves.

For transaction control, the cleanest shape makes scope visible in the code:

```python
async with session.begin():        # opens a transaction
    src = await session.get(Account, 1)
    dst = await session.get(Account, 2)
    src.balance -= 100
    dst.balance += 100
# clean exit: COMMIT (both changes or neither) — exception: ROLLBACK
```

That's atomicity from the code's shape. What it does *not* give you is protection from a concurrent request modifying the same rows — that needs row locking (`with_for_update`) or optimistic versioning, built up properly in [01/03](../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md).

## 6. When to Skip the ORM

The unit of work earns its overhead when you *mutate* what you read. When you don't, it's pure cost. Fetching 100,000 rows to aggregate them builds 100,000 tracked Python objects that you'll throw away; the answer is to aggregate in SQL and read plain tuples — `select(func.sum(...))`, window functions, labeled columns — or bulk-insert with `insert().values([...])` instead of `session.add()` in a loop. The rule of thumb: **objects for behavior, tuples for analytics.** A candidate who volunteers when *not* to use the ORM is instantly more credible than one who ORMs everything.

## 7. Interview Angles

**"Walk me through what happens between `session.add(obj)` and the row being visible to another request."** Nothing at `add` — the object is only staged in the identity map. At flush (explicit, or automatic before a query, or as part of commit) the INSERT executes and the primary key comes back, but the open transaction means only your session sees the row. At commit it becomes durable and visible to everyone. Being precise about which step emits SQL and which step publishes it is the whole answer.

**"Your API is slow and the DB log shows hundreds of tiny queries per request. Diagnose."** That's the N+1 signature: a parent query followed by one child query per row, caused by lazy-loading a relationship in a loop. Confirm with the query log, fix with `selectinload` for collections or `joinedload` for many-to-one, and prevent recurrence with `lazy="raise"` so the next accidental lazy load fails loudly in development instead of silently in production.

**"Why does `expire_on_commit=False` matter in async apps?"** Because the default expires objects at commit, and the refresh that fires on next attribute access is hidden I/O — which async attribute access can't perform, so it crashes with `MissingGreenlet`. Disabling expiry keeps committed objects readable, and pairing it with eager loading keeps all I/O explicit and awaited, which is the discipline async database code lives by.
