# Use Case: Retry-Safe, Abuse-Safe Endpoints (Idempotency-Key + Token Bucket)
# Purpose: Two API-contract guards as composable FastAPI dependencies:
#          store-and-replay idempotency for POSTs, token-bucket rate limiting per client.
# Key features: in-flight marker (concurrent-duplicate race), payload-mismatch 409,
#               429 + Retry-After. In-memory stores here; comments show the Redis swap —
#               in production BOTH stores MUST live in Redis or each worker gets its own.
# Deps: pip install fastapi

import hashlib
import time

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response

app = FastAPI()

# ---------------------------------------------------------------------------
# 1. IDEMPOTENCY — client sends a UUID per logical operation; server stores the
#    first response and replays it on retry, so a flaky network can't double-charge.
# ---------------------------------------------------------------------------

# Redis swap: SET idem:{key} "in-flight" NX EX 86400  /  GET / SET the JSON blob.
_idempotency_store: dict[str, dict] = {}
IDEMPOTENCY_TTL = 86_400  # 24h: long enough for client retries, short enough to bound storage


async def idempotency_guard(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> str:
    body = await request.body()
    payload_hash = hashlib.sha256(body).hexdigest()
    entry = _idempotency_store.get(idempotency_key)

    if entry is not None:
        if entry["payload_hash"] != payload_hash:
            # Same key, different body = client bug. Never replay silently.
            raise HTTPException(409, "Idempotency-Key reused with a different payload")
        if entry["response"] is None:
            # First request still executing — the concurrent-duplicate race.
            raise HTTPException(409, "Request with this key is still in flight")
        raise ReplayResponse(entry["response"])  # replay stored result, skip handler

    # Claim the key BEFORE executing (Redis: SET NX makes this atomic).
    _idempotency_store[idempotency_key] = {
        "payload_hash": payload_hash,
        "response": None,
        "created": time.time(),
    }
    return idempotency_key


class ReplayResponse(Exception):
    def __init__(self, stored: dict):
        self.stored = stored


@app.exception_handler(ReplayResponse)
async def replay_handler(request: Request, exc: ReplayResponse):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=exc.stored["status"], content=exc.stored["body"])


@app.post("/api/v1/transfers", status_code=201)
async def create_transfer(body: dict, idem_key: str = Depends(idempotency_guard)) -> dict:
    result = {"transfer_id": 42, "status": "completed", **body}  # real work here
    # Persist the FULL response so replays are byte-identical.
    _idempotency_store[idem_key]["response"] = {"status": 201, "body": result}
    return result


# ---------------------------------------------------------------------------
# 2. RATE LIMITING — token bucket: refills at `rate` tokens/sec up to `capacity`,
#    each request spends one. Allows controlled bursts, smooth sustained rate.
# ---------------------------------------------------------------------------

# Redis swap: a small Lua script doing the refill+spend atomically per key,
# or a sorted-set sliding window. Atomicity is why Redis, not app locks.
_buckets: dict[str, dict] = {}


def rate_limit(capacity: int = 10, rate: float = 5.0):
    """Dependency factory: e.g. Depends(rate_limit(capacity=10, rate=5))."""

    async def _guard(request: Request, response: Response) -> None:
        client_id = request.client.host if request.client else "anonymous"
        # In a real API, key on the authenticated tenant/user, not the IP.
        now = time.monotonic()
        bucket = _buckets.setdefault(client_id, {"tokens": float(capacity), "ts": now})

        bucket["tokens"] = min(capacity, bucket["tokens"] + (now - bucket["ts"]) * rate)
        bucket["ts"] = now

        if bucket["tokens"] < 1.0:
            retry_after = max(1, int((1.0 - bucket["tokens"]) / rate))
            # 429 + Retry-After: well-behaved clients back off, REDUCING incident load.
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry_after)})

        bucket["tokens"] -= 1.0
        response.headers["X-RateLimit-Remaining"] = str(int(bucket["tokens"]))

    return _guard


@app.get("/api/v1/accounts", dependencies=[Depends(rate_limit(capacity=10, rate=5.0))])
async def list_accounts() -> list[dict]:
    return [{"id": 1, "balance": 100.0}]
