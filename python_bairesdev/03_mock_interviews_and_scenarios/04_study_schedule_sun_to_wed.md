# Study Schedule: Sunday July 19 → Wednesday July 22 (Interview Day)

A four-day battle plan. Deep understanding is built Sunday–Tuesday; Wednesday is retrieval-only. The interview is Wednesday at 11:00 AM EST (confirm the calendar invite — some notes say 11:30; be ready at 10:45 either way).

**The one rule:** every study block ends with you *saying the answers out loud*. Interviews are verbal; reading is not rehearsal.

**The recruiter-screen addendum (added Monday):** the first call is likely a recruiter screen, not a technical interview — see the [README](README.md) for its shape. That adds four short items to the remaining days: the [90-second pitch](05_ninety_second_pitch_and_cv_walkthrough.md) rehearsed out loud every day from today until the call, the [agile primer](07_agile_scrum_speakable_primer.md) Monday evening, the [salary and BairesDev-model script](06_recruiter_screen_salary_and_bairesdev_model.md) Tuesday (fill in your real salary range before Tuesday night), and the [CCAT primer](08_ccat_and_online_tests_primer.md) only after the screen unless you finish everything else early. The technical schedule below stays as the backbone — the screen can still turn technical at any moment.

---

## Sunday, July 19 — Backend Depth Day

| Block | Material | Goal |
|---|---|---|
| Morning (2h) | Core first: [frameworks/01_fastapi](../frameworks_specifics/01_fastapi.md) + [02_sqlalchemy](../frameworks_specifics/02_sqlalchemy.md) (full read — they're rebuilt as ground-up articles), then [02_fastapi_runtime_internals](../01_fastapi_sqlalchemy_postgres/02_fastapi_runtime_internals.md) + [03_connection_pools_locking_and_concurrency](../01_fastapi_sqlalchemy_postgres/03_connection_pools_locking_and_concurrency.md) | Own the request lifecycle, Unit of Work, event loop, and concurrency story — the #1 senior Python filter. |
| Afternoon (2h) | [04_explain_analyze_partitioning_matviews](../01_fastapi_sqlalchemy_postgres/04_explain_analyze_partitioning_matviews.md) + skim [01_postgres_aggregation_sqlalchemy](../01_fastapi_sqlalchemy_postgres/01_postgres_aggregation_sqlalchemy.md) | Be able to narrate an EXPLAIN output and the "table got huge" playbook. |
| Evening (45m) | Backend sections of the [rapid-fire Q&A bank](03_senior_rapid_fire_qa_bank.md), answers spoken aloud | First retrieval pass. Flag every question you stumbled on. |

## Monday, July 20 — Architecture & API Day

| Block | Material | Goal |
|---|---|---|
| Morning (2h) | [06_api_contracts_idempotency_pagination](../04_architecture_and_system_design/06_api_contracts_idempotency_pagination.md) + [07_oauth2_jwt_lifecycle](../04_architecture_and_system_design/07_oauth2_jwt_lifecycle.md) | Design a retry-safe, secured endpoint from a blank page. |
| Afternoon (2h) | [08_redis_caching_strategies](../04_architecture_and_system_design/08_redis_caching_strategies.md) + [09_deployment_scaling_statelessness](../04_architecture_and_system_design/09_deployment_scaling_statelessness.md) | Tell the full story: request → LB → workers → pool → Postgres/Redis. |
| Evening (1h) | Run mock **Scenario 1 (Slow Dashboard)** from [02_mock_interview_drills_scenarios](02_mock_interview_drills_scenarios.md) out loud, then first pass of battle cards [01](battle_cards/01_fastapi_runtime.md)–[04](battle_cards/04_caching_scaling_deploy.md) | Convert Sunday+Monday depth into 30-second verbal answers. |

## Tuesday, July 21 — Frontend, Testing & Full Rehearsal

| Block | Material | Goal |
|---|---|---|
| Morning (1.5h) | [03_error_boundaries_suspense_profiling](../02_react_redux_swr_dashboard/03_error_boundaries_suspense_profiling.md) + [02_test_pyramid_mocking_contracts](../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md) | Close the two remaining gaps: React failure/perf story, testing philosophy. |
| Midday (1.5h) | Full read of [frameworks_specifics/05_react.md](../frameworks_specifics/05_react.md), [06_redux_toolkit.md](../frameworks_specifics/06_redux_toolkit.md), [07_swr_axios.md](../frameworks_specifics/07_swr_axios.md), [08_zod_formik.md](../frameworks_specifics/08_zod_formik.md) — these are ground-up articles now; read them like articles, and say each Interview Angles answer aloud. ([03_alembic](../frameworks_specifics/03_alembic.md) + [04_pydantic](../frameworks_specifics/04_pydantic.md) fit Monday evening.) | The frontend core knowledge, built from zero — the "break it on purpose" examples are your war stories. |
| Afternoon (1h) | **Full 30-minute self-mock**, recorded on your phone, using the structure in [README](README.md). Pull questions randomly from the Q&A bank. Listen back once. | Hear your own filler words, missing tradeoffs, and rambling — fix them. |
| Evening (1h) | Complete Q&A bank pass (all sections, aloud) + battle cards [05](battle_cards/05_react_frontend.md)–[06](battle_cards/06_testing_migrations.md) | Everything flagged Sunday should now be fluent. |

## Wednesday, July 22 — Interview Day (11:00 AM EST)

| Time | Activity |
|---|---|
| 8:30–9:45 | **Battle cards only** — all six, ~10 minutes each, answers spoken aloud. No deep-dive docs today: new information on game day creates doubt, not depth. |
| 9:45–10:15 | [README](README.md) 30-min strategy + your two STAR stories from [01_mock_qa_and_behavioral_drills](01_mock_qa_and_behavioral_drills.md), told once out loud each. |
| 10:15 | **Hard stop.** Logistics: camera, mic, water, close every tab except the call. Warm your voice up — answer one easy question aloud ("walk me through the virtual banking dashboard"). |
| 10:45 | Sit down, breathe. You are prepared from the ground up, not for one scenario. |

---

## If Reading Time Runs Short

Priority order (drop from the bottom, never the top):
1. Battle cards + Q&A bank (retrieval beats coverage)
2. `01/03` pools & locking → `04/06` API contracts → `04/07` auth → `01/02` runtime
3. `04/08` Redis → `01/04` EXPLAIN → `04/09` deployment → `06/02` testing → `02/03` React

## Interview Posture Reminders

* **Why first, code second.** Every answer opens with the tradeoff, not the API name.
* When asked something you don't know: name the adjacent thing you *do* know, state how you'd find out, stop talking.
* You have a runnable reference app ([virtual_banking_dashboard](../virtual_banking_dashboard/README.md)) — steer project questions toward it, but generalize the pattern, not the dashboard.
