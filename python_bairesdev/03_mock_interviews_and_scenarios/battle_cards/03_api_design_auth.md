# Battle Card 03 — API Design & Auth

## 30-Second Answers

**Retry-safe POST.** "A client-generated `Idempotency-Key` header with store-and-replay: claim the key atomically, execute once, persist the full response, replay it on retry. Same key with a different payload is a 409 — that's a client bug, never a silent replay."

**Pagination.** "OFFSET has two structural flaws: cost grows with depth because Postgres produces and discards skipped rows, and concurrent writes shift pages. Keyset filters past the last-seen `(created_at, id)` — O(1) with a matching index, stable, at the cost of random page jumps. The API returns an opaque cursor."

**Error contract.** "One error shape everywhere: RFC 7807 `application/problem+json` via a FastAPI exception handler mapping domain errors to problem documents — the frontend writes one parser, support greps one stable `type`."

**Rate limiting.** "Two layers: coarse at the edge, per-tenant in app middleware with Redis state — never process memory, or N workers give N× the limit. Always 429 plus `Retry-After`, which makes well-behaved clients reduce your load during incidents."

**Refresh flow.** "Short access token verified locally; on 401 the axios interceptor single-flights one refresh; rotation burns the old refresh token; a burned token reappearing means theft — revoke the family. Statelessness for access, revocability at the refresh layer."

## Numbers & Facts

| Fact | Value |
|---|---|
| Access / refresh token lifetimes | 5–15 min / days–weeks |
| Idempotency key TTL | ~24 h, full response stored |
| Status codes | 401 unauthenticated · 403 forbidden · 409 business refusal · 422 schema · 429 limited |
| Flow for SPAs | Authorization Code + PKCE (password grant = legacy, OAuth 2.1 drops it) |
| JWT validation set | signature + pinned alg + `exp` + `iss` + `aud` |

## Rapid Fire

- **Why PKCE?** → An intercepted auth code is useless without the code_verifier only the initiating client holds.
- **HS256 vs RS256?** → Shared secret, same-service; private-sign/public-verify once multiple services validate.
- **What never goes in a JWT?** → Secrets — signed is readable, not encrypted.
- **Revoke a stateless JWT?** → You mostly don't: short expiry caps damage; real revocation is killing the (stateful) refresh token.
- **Where do keyset cursors get their speed?** → A composite index on exactly the ORDER BY columns.

## Trap Questions

- *"401 or 403 for a user lacking permission?"* — 403. 401 means *unauthenticated*; sending 401 triggers clients' re-login/refresh machinery for no reason.
- *"Idempotency keys make locking unnecessary?"* — No: idempotency dedupes *the same* request retried; `FOR UPDATE` serializes *different concurrent* requests on one row. A safe transfers endpoint needs both.

## Deep Dives

[04/06 API contracts](../../04_architecture_and_system_design/06_api_contracts_idempotency_pagination.md) · [04/07 OAuth2/JWT](../../04_architecture_and_system_design/07_oauth2_jwt_lifecycle.md) · [02/02 token storage](../../02_react_redux_swr_dashboard/02_browser_apis_and_storage.md)
