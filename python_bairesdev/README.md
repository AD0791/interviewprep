# BairesDev — Fullstack Python

**Target role: Fullstack Python (dashboards, aggregation, real-time metrics, performance and scaling) · Language: English · First call: recruiter screen, Wed 22 July 2026**

The largest track in this repo — 174 markdown files, roughly 28 500 lines — covering the full technical depth behind a staffing-firm placement process: recruiter screen, automated tests, then technical interviews with the end client.

Stack in scope: **FastAPI, SQLAlchemy 2.0 async, Alembic, Pydantic, Postgres** on the backend; **React, Redux Toolkit, SWR/Axios, Zod, Formik, Tailwind/Chakra, TypeScript, Vite** on the frontend.

---

## Where to start, by situation

**Recruiter screen tomorrow** → `03_mock_interviews_and_scenarios/` files 05–08. The 90-second pitch and CV walkthrough, the salary and BairesDev-model script, the agile primer, and the CCAT primer. Nothing else.

**Technical interview scheduled** → `03_mock_interviews_and_scenarios/03_senior_rapid_fire_qa_bank.md`, then the two deep-dive folders below matching the role's emphasis.

**Studying with time** → `frameworks_specifics/` first. Those nine articles are the reference implementation of the house writing style, and they are the best material in the repo.

---

## The folders

| Folder | Contents |
|---|---|
| `01_fastapi_sqlalchemy_postgres/` | Postgres aggregation with SQLAlchemy, FastAPI runtime internals, connection pools and locking, `EXPLAIN ANALYZE` with partitioning and materialised views |
| `02_react_redux_swr_dashboard/` | Dashboard rendering and state, browser APIs and storage, error boundaries, Suspense, profiling |
| `03_mock_interviews_and_scenarios/` | Mock Q&A and behavioural drills, scenario drills, senior rapid-fire bank, study schedule, pitch and CV walkthrough, recruiter-screen script, agile primer, CCAT primer, plus a `battle_cards/` set |
| `04_architecture_and_system_design/` | Dashboard architecture, modern tooling, twelve-factor config, project structure, design patterns, API contracts and idempotency, OAuth2/JWT, Redis caching, deployment and scaling |
| `05_networking_and_data_transport/` | Networking protocols for a dashboard application |
| `06_testing_and_migrations/` | Testing and migrations, test pyramid, mocking, contract tests |
| `07_advanced_runtimes_and_compilers/` | Advanced Python, Node and TypeScript runtime behaviour |
| `frameworks_specifics/` | The nine "From Zero" teaching articles — the style reference for the whole repo |
| `usable_gists/` · `gist_toolkit/` | Standalone runnable snippets, each headed with use case, purpose and key features |
| `virtual_banking_dashboard/` | Runnable full-stack app: Postgres, Redis, FastAPI, React, via Docker Compose |

Most subfolders carry their own `README.md` with a finer-grained reading order.

---

## The runnable apps

```bash
cd virtual_banking_dashboard && docker compose up
# Postgres :5432 · Redis :6379 · FastAPI :8000 · React :80
```

Backend uses `pyproject.toml` (Python ≥ 3.11, async SQLAlchemy with asyncpg); tests via `pytest` with `pytest-asyncio` and `aiosqlite`. Frontend: `npm run dev` for Vite, `npm run build` for `tsc && vite build`.

`gist_toolkit/` is the second, smaller app — same Compose pattern.

---

## Two anecdotes that carry across every track

The **N+1 story** — a login page at 36 seconds reduced to under half a second by replacing a per-item query loop with a single aggregated join plus eager loading, diagnosed from the query log. It answers "tell me about a time you optimised something" in any interview, technical or not.

The **composite index story** — deadlocks under concurrent access removed by indexing so locks landed on targeted rows rather than ranges, plus a consistent table access order and shorter transactions.

Both are reused in [`../acted_bdd/`](../acted_bdd/README.md) and [`../remote_leverage_data_analyst/`](../remote_leverage_data_analyst/README.md). Keep the wording consistent across tracks — the same story told two different ways is worse than either version.

---

## Conventions

Study material follows the "From Zero" contract set out in `.agents/AGENTS.md`: open with the problem before the tool, build one real thing incrementally with runnable code, break it on purpose before explaining the fix, trace what the machine does, teach through banking-domain analogies, and close with `## Interview Angles` answered in speakable prose. No fragment bullets, no arrow chains.

CV source of truth: `../../curiculum-vitae-and-letter/alexandrodislaResume.tex`. The stray `1784116314338.pdf` at the folder root is a third-party caching guide, not a CV.
