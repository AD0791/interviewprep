# Connection Pools, Locking & Database Concurrency Masterclass

How an async FastAPI service shares a finite Postgres with hundreds of concurrent requests without exhausting connections or corrupting money. This is the single highest-signal senior backend conversation.

---

## 1. Why Connection Pools Exist (Why)

Opening a Postgres connection is expensive: a TCP handshake, optionally a TLS handshake, authentication, and — critically — **Postgres forks a dedicated OS process per connection**. Each backend process costs real memory (commonly several MB) and scheduler overhead. Two consequences drive all pool design:

1. **Per-request connections don't scale.** Paying the handshake tax on every HTTP request adds tens of milliseconds and floods the server with process churn.
2. **`max_connections` is a hard, shared ceiling.** The default is 100. Every API replica, worker, Alembic run, cron job, and dashboard client draws from the *same* budget. A pool is how each process pre-negotiates its slice and reuses it.

A pool keeps N connections open and checks them out to requests like library books: borrow, use, **return** — never own.

## 2. Tuning the SQLAlchemy Async Pool (How)

```python
# Gist: tuned_async_engine.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://app:secret@db:5432/core_db",
    pool_size=10,        # Steady-state connections held open per process
    max_overflow=5,      # Burst headroom: extra connections opened under load, closed after use
    pool_timeout=30,     # Seconds a request waits for a free connection before TimeoutError
    pool_recycle=1800,   # Replace connections older than 30 min (beats silent firewall drops)
    pool_pre_ping=True,  # Cheap liveness check on checkout; evicts dead connections
)
```

### The Sizing Math (memorize this)

> **replicas × workers × (pool_size + max_overflow) ≤ max_connections − headroom**

Example: 2 replicas × 4 workers × (10 + 5) = **120 demand** against `max_connections = 100` → you will see `TimeoutError: QueuePool limit` under load *even though each process looks conservatively configured*. Fixes, in order of preference: lower per-worker pool size, raise `max_connections` (costs Postgres memory), or put **PgBouncer** (a transaction-mode connection multiplexer) between the app and the database so thousands of client connections share a few dozen server connections.

| Knob | Too low | Too high |
|---|---|---|
| `pool_size` | Requests queue on `pool_timeout` | Wasted Postgres memory; ceiling breached when scaling out |
| `max_overflow` | No burst absorption | Load spikes translate directly into DB pressure |
| `pool_timeout` | Spurious 500s under brief spikes | Requests hang, users retry, load compounds |

## 3. Diagnosing Pool Exhaustion (How)

Symptom: intermittent `TimeoutError: QueuePool limit of size 10 overflow 5 reached` under load. Three usual causes:

1. **Leaked sessions** — a code path that never returns the connection. The `get_db` dependency's `finally: await session.close()` is the guard; ad-hoc sessions created outside it are the usual culprit.
2. **Slow queries holding checkouts** — the pool is sized fine, but each borrow lasts 2 s. Fix the query, not the pool.
3. **Genuine under-provisioning** — traffic grew; apply the sizing math.

Interrogate the live server before touching config:

```sql
-- Gist: pool_diagnosis.sql
SELECT state, wait_event_type, COUNT(*), MAX(now() - query_start) AS oldest
FROM pg_stat_activity
WHERE datname = 'core_db'
GROUP BY state, wait_event_type;
-- Many 'idle in transaction' rows = app code holding transactions open (the leak signature).
```

## 4. Pessimistic Locking: SELECT FOR UPDATE (Why & How)

The classic failure is the **double spend**. Two requests read `balance = 100`, both subtract 80, both write — the account ends at 20 having paid out 160. Read-modify-write over separate statements is a race; default `READ COMMITTED` isolation does not save you.

```mermaid
sequenceDiagram
    autonumber
    participant A as Request A
    participant B as Request B
    participant DB as Postgres
    A->>DB: SELECT balance FOR UPDATE (acct 1)
    Note over DB: Row locked by A
    B->>DB: SELECT balance FOR UPDATE (acct 1)
    Note over B,DB: B BLOCKS, waiting on A's lock
    A->>DB: UPDATE balance = 20; COMMIT
    DB-->>B: Returns fresh balance = 20
    B->>DB: Insufficient funds → ROLLBACK
```

`SELECT ... FOR UPDATE` locks the selected rows until the transaction commits, serializing writers on that row while readers proceed untouched.

```python
# Gist: pessimistic_transfer.py
from sqlalchemy import select

async def debit(session, account_id: int, amount: float) -> None:
    async with session.begin():  # Lock lifetime == transaction lifetime
        acct = await session.scalar(
            select(Account).where(Account.id == account_id).with_for_update()
        )
        if acct.balance < amount:
            raise InsufficientFunds(account_id)
        acct.balance -= amount
    # Commit releases the row lock
```

Two refinements worth naming unprompted:

* **Lock ordering**: when locking multiple accounts (a transfer), always lock in a stable order (e.g. ascending id) or two transfers A→B and B→A deadlock.
* **`with_for_update(skip_locked=True)`**: the standard Postgres job-queue pattern — each worker grabs only unclaimed rows, no coordinator needed.

## 5. Optimistic Locking: Version Columns (How)

Pessimistic locks hold database resources while they wait. When conflicts are *rare* (e.g. two admins editing the same profile), it is cheaper to detect the collision than to prevent it: add a `version` column, include it in the `WHERE` clause of the update, and retry if zero rows matched.

```python
# Gist: optimistic_version.py
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[float] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    __mapper_args__ = {"version_id_col": version}
    # SQLAlchemy now emits: UPDATE ... WHERE id = ? AND version = ?
    # and raises StaleDataError when another writer got there first → catch and retry.
```

| Strategy | Mechanism | Best when | Cost |
|---|---|---|---|
| Pessimistic (`FOR UPDATE`) | Block competing writers up front | High contention; money; must-not-fail writes | Held locks, deadlock risk, waiting |
| Optimistic (version column) | Detect conflict at write, retry | Low contention; user-editable records | Retry logic; wasted work on conflict |

Rule of thumb to say in the room: **contention level chooses the strategy** — locks for hot rows, versions for cold ones.

## 6. Interview Angles

**"Two requests debit the same account at the same time — walk me through every layer of defense."**
Skeleton: name the race (read-modify-write) → `SELECT FOR UPDATE` inside one transaction as the primary fix → lock ordering for multi-row transfers → optimistic versioning as the low-contention alternative → a DB `CHECK (balance >= 0)` constraint as the last line. Bonus: idempotency keys stop the *retry* variant of the same bug (see [04/06](../04_architecture_and_system_design/06_api_contracts_idempotency_pagination.md)).

**"Production throws 'QueuePool limit reached' — diagnose it."**
Skeleton: it means all checkouts were busy for `pool_timeout` seconds → check `pg_stat_activity` for `idle in transaction` (leak) vs. long `active` queries (slow SQL) vs. neither (under-provisioned) → only then touch `pool_size`, and re-run the sizing math against `max_connections` first → mention PgBouncer when replicas multiply.

**"Why not just size the pool at 100?"**
Skeleton: connections are Postgres processes, not free sockets — memory per backend, and the ceiling is shared across every replica and job; big pools also hide slow queries instead of surfacing them.

Related deep dives: session lifecycle in [01_postgres_aggregation_sqlalchemy.md](01_postgres_aggregation_sqlalchemy.md), worker-count interaction in [04/09 deployment](../04_architecture_and_system_design/09_deployment_scaling_statelessness.md), runnable gist [sqlalchemy_select_for_update_optimistic.py](../usable_gists/sqlalchemy_select_for_update_optimistic.py).
