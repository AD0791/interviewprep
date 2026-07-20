# Battle Card 06 — Testing & Migrations

## 30-Second Answers

**Pyramid.** "It's a cost argument, not dogma: hundreds of millisecond unit tests on fakes, a few dozen integration tests proving real SQL against Postgres, a few API tests asserting the HTTP contract through dependency overrides, single-digit E2E. Each layer asserts only its own concern — the expensive layers exist to catch exactly what fakes can't."

**Fakes over mocks.** "The repository Protocol lets me swap the data layer for an in-memory fake with real behavior — tests read as scenarios and survive refactors. `MagicMock` couples tests to call signatures and happily returns nonsense. Mocks are for third-party edges where the call itself is the assertion."

**What fakes can't prove.** "Constraints, locking, collation, the real ORDER BY — which is precisely the integration layer's job. Naming that loss is the senior half of the answer."

**Contract drift.** "The OpenAPI schema FastAPI already generates is the contract: CI regenerates TS types and Zod schemas from it, so a breaking rename fails the frontend *build*, not production. Pact-style consumer-driven contracts when consumers multiply — consumers drive, providers verify."

**Safe migrations.** "Rolling deploys mean old and new code share one schema, so every migration is expand/contract: add nullable, deploy code writing both, backfill in batches, constrain and drop only when nothing references the old shape. The killer is DDL taking an exclusive lock at peak."

## Numbers & Facts

| Fact | Value |
|---|---|
| Layer costs | unit µs–ms · integration ms–s · E2E s–min |
| Honest suite shape | hundreds / dozens / dozens / single digits |
| API-test DB substitution | `app.dependency_overrides[get_db]` |
| Async pytest kit | pytest-asyncio + aiosqlite/Postgres conftest |
| Two Alembic heads | `alembic merge` → linear history |

## Rapid Fire

- **Test business logic without Postgres?** → Fake repository implementing the Protocol; service tests become pure scenarios.
- **Why does the fake mirror the real ORDER BY?** → Behavioral fidelity is the whole point — a fake that lies is a mock with extra steps.
- **Where do auth tests live?** → API layer: assert 401/403 through the real dependency chain, overriding only the DB.
- **Downgrade scripts — worth writing?** → Yes for dev; production rollback of a *contract*-phase change is usually roll-forward.
- **Who verifies a Pact contract?** → The provider, replaying consumer expectations in its own CI.

## Trap Questions

- *"100% coverage through the HTTP layer — good goal?"* — An inverted pyramid: 20-minute flaky suites nobody runs pre-push. Coverage per layer for that layer's concern beats one number.
- *"Alembic autogenerate caught everything?"* — It diffs models vs schema; it misses data backfills, lock behavior, and out-of-band DDL — review every generated script like code.

## Deep Dives

[06/01 mechanics: fixtures, overrides, locks](../../06_testing_and_migrations/01_testing_and_migrations.md) · [06/02 strategy: pyramid, fakes, contracts](../../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md) · [frameworks/03_alembic](../../frameworks_specifics/03_alembic.md)
