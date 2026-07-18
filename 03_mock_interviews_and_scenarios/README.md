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

## Sample Questions & Flashcards
This directory will contain practice files detailing:
- FastAPI / SQLAlchemy mock Q&As.
- React state/caching mock Q&As.
- PostgreSQL optimization techniques.
