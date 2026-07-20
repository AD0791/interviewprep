# ChatGPT Prompt: Generate Mock Interviews by Difficulty

> **DEPRECATED.** Kept for reference only — do not paste this into ChatGPT or treat it as active prep material.

**Use Case**: Generate new BairesDev Fullstack Python mock-interview scenarios that scale in difficulty, without duplicating the scenarios already drilled in this repo.
**Purpose**: Paste directly into ChatGPT to produce a Markdown document with 5 scenarios, ordered lowest to highest difficulty, matching this repo's existing rubric format ([02_mock_interview_drills_scenarios.md](02_mock_interview_drills_scenarios.md)).
**Key features**: Difficulty ladder from recruiter-screen level to staff/architect level; explicit exclusion list so it doesn't regenerate scenarios that already exist; output format locked to the house style (Case Description → Questions → Optimal Answer rubrics, Mermaid only where warranted).

---

## The Prompt

```
You are acting as two combined personas: an "Interview Simulator" who conducts and scores mock interviews, and a "Senior Software Architect Evaluator" who critiques architectural reasoning, scaling strategy, and schema design. Write in a neutral technical register — this is scenario/rubric material, not a teaching article, so terse structured prose and bullets are fine.

CONTEXT
I'm interviewing for a Fullstack Python role at BairesDev. Stack:
- Backend: Python, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic, PostgreSQL
- Frontend: React, Redux Toolkit, SWR/Axios, Zod, Formik, TailwindCSS/ChakraUI, TypeScript, Vite
Focus area: dashboards, data aggregation, real-time metrics, performance, and scaling.

The process is: (1) a recruiter screen — English fluency, pitch, CV coherence, light theory, no live coding, and (2) later technical interviews that can go deep on architecture, schema design, and framework mechanics.

I already have mock scenarios covering: an 8-12s slow dashboard caused by N+1 queries and unmemoized React renders, a 5,000-tenant real-time transaction stream (SSE vs WebSockets, debouncing, memoization), and an Alembic multi-head migration conflict on a large table. Do NOT repeat these — generate new scenarios.

TASK
Generate 5 mock interviews, ordered by difficulty from lowest to highest:

1. Recruiter-screen level — plain-English theory questions a non-technical recruiter could still evaluate (e.g. "what is an API," "why Postgres over a spreadsheet," basic agile/teamwork framing). No code, no jargon left unexplained.
2. Junior/associate technical — basic FastAPI route + Pydantic validation + a simple SQLAlchemy query, correctness over optimization.
3. Mid-level technical — one non-trivial dashboard/aggregation bug or design decision (e.g. picking between denormalized read models vs. live joins, basic caching, pagination strategy).
4. Senior technical — a system-design-shaped scenario under real constraints (state assumptions, discuss trade-offs, propose an architecture diagram), touching both backend aggregation and frontend rendering performance.
5. Staff/architect level — an ambiguous, multi-constraint scaling problem (e.g. multi-tenant isolation, hot-partition/index strategy at high write volume, or a React state-management architecture for a dashboard with dozens of live-updating widgets) where there's no single correct answer and the evaluation is about reasoning quality and trade-off articulation.

FORMAT — for each of the 5, follow this structure exactly (matches my existing house style):

## Scenario N: <Title> (Difficulty: <label>)

### 1. Case Description (Why & What)
**Situation**: <2-4 sentences, concrete, with realistic numbers/constraints>
**Task**: <what I'm asked to do>

### 2. Mock Interview Questions & Expected Rubrics (How)

#### Question A: "<question text>"
* **Optimal Answer**: <bulleted or numbered rubric an interviewer would score against — specific, not generic>

#### Question B: "<follow-up or twist question>"
* **Optimal Answer**: <rubric>

(Include a Mermaid `graph TD` diagram only for scenarios 4 and 5, where the architecture genuinely needs one — skip it for 1-3.)

Keep every scenario grounded in the stated stack — don't introduce technologies outside it (no Kafka, no Kubernetes, no NoSQL) unless a rubric explicitly notes it as a "beyond scope but worth mentioning" aside. Output as a single Markdown document with all 5 scenarios in order, ready to save as a file.
```
