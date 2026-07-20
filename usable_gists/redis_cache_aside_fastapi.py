# Use Case: Cache-Aside Layer for an Expensive Aggregation Endpoint
# Purpose: Serve an 800ms Postgres aggregation in ~1ms for repeat reads, with
#          explicit invalidation on write and TTL as the staleness backstop.
# Key features: redis.asyncio client, FastAPI DI, orjson serialization,
#               jittered TTL (anti-stampede), delete-on-write invalidation.
# Deps: pip install redis orjson fastapi sqlalchemy[asyncio] asyncpg

import random
from typing import AsyncIterator

import orjson
from fastapi import Depends, FastAPI
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session  # Assume async session generator

app = FastAPI()

CACHE_VERSION = "v1"   # Bump when the payload shape changes: old keys orphan harmlessly
BASE_TTL_SECONDS = 300  # The staleness budget agreed with product


# 1. Redis as a lifespan-scoped singleton, injected per request
#    Why: one connection pool per worker, shared across requests (never per-request clients).
async def get_redis() -> AsyncIterator[Redis]:
    yield app.state.redis


@app.on_event("startup")
async def _open_redis() -> None:
    app.state.redis = Redis.from_url("redis://cache:6379/0")


@app.on_event("shutdown")
async def _close_redis() -> None:
    await app.state.redis.aclose()


def summary_key(tenant_id: int) -> str:
    # Namespaced + versioned key. Every cached entity gets its own namespace.
    return f"analytics:summary:{CACHE_VERSION}:{tenant_id}"


# 2. READ PATH — cache-aside: check cache, on miss compute + populate
@app.get("/api/v1/analytics/summary/{tenant_id}")
async def read_summary(
    tenant_id: int,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> dict:
    key = summary_key(tenant_id)

    if (cached := await redis.get(key)) is not None:
        return orjson.loads(cached)  # HIT: ~1ms, Postgres untouched

    # MISS: run the expensive aggregation against the source of truth
    result = await db.execute(
        text(
            """
            SELECT COUNT(*) AS tx_count,
                   COALESCE(SUM(amount), 0) AS total_volume,
                   COALESCE(AVG(amount), 0) AS avg_amount
            FROM transactions
            WHERE tenant_id = :tenant_id AND status = 'completed'
            """
        ),
        {"tenant_id": tenant_id},
    )
    row = result.one()
    payload = {
        "tenant_id": tenant_id,
        "tx_count": row.tx_count,
        "total_volume": float(row.total_volume),
        "avg_amount": float(row.avg_amount),
    }

    # Jittered TTL: co-created keys must not expire in unison (stampede defense #1)
    ttl = BASE_TTL_SECONDS + random.randint(0, 60)
    await redis.set(key, orjson.dumps(payload), ex=ttl)
    return payload


# 3. WRITE PATH — invalidate, never update, the cached projection
#    Why delete instead of recompute here: recomputing inside the write path
#    reintroduces the read-modify-write race the cache was meant to hide.
@app.post("/api/v1/transactions", status_code=201)
async def create_transaction(
    body: dict,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> dict:
    await db.execute(
        text(
            "INSERT INTO transactions (tenant_id, amount, status) "
            "VALUES (:tenant_id, :amount, 'completed')"
        ),
        body,
    )
    await db.commit()

    # Invalidate AFTER commit: deleting first would let a concurrent reader
    # repopulate the cache with pre-commit data.
    await redis.delete(summary_key(body["tenant_id"]))
    return {"status": "created"}
