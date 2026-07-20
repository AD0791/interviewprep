# Mock Interviews & Interview Scenarios

A 30-minute technical interview is fast-paced. You need to deliver high-signal answers quickly without getting bogged down in minor details.

## Quick-Fire Interview Strategy

### 1. The Structure of a 30-Minute Interview
* **0 - 5 mins**: Intro, icebreaker, candidate background overview.
* **5 - 25 mins**: Technical questions (architecture, schema design, framework mechanics, optimization scenarios).
* **25 - 30 mins**: Candidate questions for the company.

### 2. Formulating Answers
* **System Design / Architecture**: 
  * Always start high-level (client -> gateway/API -> services -> database).
  * State your assumptions immediately (e.g., read-to-write ratio, data size, freshness requirements).
  * Discuss trade-offs (e.g., normalization vs. denormalization, polling vs. WebSockets for dashboards).
* **Coding / Framework Mechanics**:
  * Be concise. Reference design patterns (e.g., "I use FastAPI Dependency Injection for session management...").
  * Talk about performance constraints (e.g., "For data aggregation, I avoid looping in Python; I push the aggregation to PostgreSQL using window functions or GROUP BY...").

## Contents of This Folder

1. [01_mock_qa_and_behavioral_drills.md](01_mock_qa_and_behavioral_drills.md) — Technical Q&A reference + STAR behavioral templates and a worked story.
2. [02_mock_interview_drills_scenarios.md](02_mock_interview_drills_scenarios.md) — Three full mock scenarios (Slow Dashboard, Real-Time Stream, Migration Lock) with rubrics.
3. [03_senior_rapid_fire_qa_bank.md](03_senior_rapid_fire_qa_bank.md) — General mid/senior verbal drills across nine domains, each with the likely follow-up.
4. [04_study_schedule_sun_to_wed.md](04_study_schedule_sun_to_wed.md) — The Sunday→Wednesday battle plan, including the interview-morning protocol.
5. [battle_cards/](battle_cards/) — Six one-page cram sheets (FastAPI runtime, Postgres/SQLAlchemy, API design & auth, caching/scaling/deploy, React, testing/migrations). **These are the only material for Wednesday morning.**
