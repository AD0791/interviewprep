# Mock Interviews & Interview Scenarios

A 30-minute interview is fast-paced. You need to deliver high-signal answers quickly without getting bogged down in minor details.

## Quick-Fire Interview Strategy

### 1a. If It's a Recruiter Screen (the likely shape of the first BairesDev call)

The first 30-minute call at BairesDev is usually a recruiter screening, conducted entirely in English, and it grades communication and fit before technical depth:

* **0 - 5 mins**: Your 90-second pitch ([05](05_ninety_second_pitch_and_cv_walkthrough.md)), then CV-coherence probes on two or three resume entries.
* **5 - 15 mins**: Brief theory questions on the core stack, basic architecture, and agile methodology ([07](07_agile_scrum_speakable_primer.md)) — spoken concepts, no live coding.
* **15 - 25 mins**: Salary expectations, the BairesDev staffing model, and process next steps ([06](06_recruiter_screen_salary_and_bairesdev_model.md)).
* **25 - 30 mins**: Your questions for the recruiter (prepared list in [06](06_recruiter_screen_salary_and_bairesdev_model.md)).

Keep every answer under two minutes so the recruiter can finish their checklist — running long is itself a negative signal at this stage.

### 1b. If It's a Technical Interview

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
5. [05_ninety_second_pitch_and_cv_walkthrough.md](05_ninety_second_pitch_and_cv_walkthrough.md) — The word-for-word 90-second pitch, the CV-coherence map, the two profile probes, and plain-English explanations for a non-technical recruiter.
6. [06_recruiter_screen_salary_and_bairesdev_model.md](06_recruiter_screen_salary_and_bairesdev_model.md) — How BairesDev's staffing model works, the salary-expectations script, the process map, and questions to ask the recruiter.
7. [07_agile_scrum_speakable_primer.md](07_agile_scrum_speakable_primer.md) — Agile/Scrum in rehearsable prose, with your own engagements retold in agile terms.
8. [08_ccat_and_online_tests_primer.md](08_ccat_and_online_tests_primer.md) — Strategy for the post-screen automated tests (CCAT-style cognitive + technical MCQs). Next-stage material, not interview-day material.
9. [battle_cards/](battle_cards/) — Six one-page cram sheets (FastAPI runtime, Postgres/SQLAlchemy, API design & auth, caching/scaling/deploy, React, testing/migrations). **These, plus the pitch, are the only material for Wednesday morning.**
10. [09_chatgpt_mock_interview_generator_prompt.md](09_chatgpt_mock_interview_generator_prompt.md) — **Deprecated.** Formerly a copy-paste ChatGPT prompt for generating 5 new mock-interview scenarios by difficulty; kept for reference only.
