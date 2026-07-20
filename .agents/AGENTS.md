# BairesDev Fullstack Python Interview Prep Rules

This file governs the behavior of all agents operating in this workspace.

## Context & Objectives
* **Goal:** Prepare the user for a 30-minute technical interview for a Fullstack Python role at BairesDev.
* **Timeline:** Wednesday, July 22, 2026, at 11:30 AM EST.
* **Focus Area:** Dashboards, data aggregation, real-time metrics, performance, and scaling.
* **Tech Stack:**
  * **Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic, Postgres.
  * **Frontend:** React, Redux Toolkit, SWR/Axios, Zod, Formik, TailwindCSS, ChakraUI, TypeScript, Vite.

## Output & Documentation Standards

### The Default Style: "From Zero" Teaching Articles
Every study document in this repo is written as a teaching article for a reader who has **never used the tool**, in the register of a good engineering blog (think Dan Abramov or Julia Evans): patient, concrete, conversational but precise. The reference implementations of this style are the nine `frameworks_specifics/` articles — match them. The contract:

1. **Open with the problem, not the tool.** Show life *without* the tool first — the pain, in concrete code — so the reader feels why the tool exists before meeting it. A definition the reader can only understand if they already know the tool is a failed opening.
2. **Build one real thing, incrementally.** Complete, runnable code at every step (banking-domain examples preferred: accounts, transfers, transactions). Narrate *around* the code in prose — the explanation lives in paragraphs, not only in code comments. No step may depend on code the reader hasn't seen.
3. **Break it on purpose.** Show the classic failure actually happening (the N+1 query log scrolling by, the list-key bug putting a note on the wrong row, the stale closure freezing a counter) *before* explaining the fix. Watching it fail is how the reader earns the explanation.
4. **Trace what the machine does.** At least once per article, walk one interaction through the system in plain words: "trace one click," "the life of a request." Cause and effect, step by step.
5. **Teach mental models through analogies.** The session is git's staging area; the Redux store is a bank ledger; the SWR key is a cache address. One good analogy per core concept, carried through the article.
6. **Close with `## Interview Angles`.** Two or three real interview questions, each answered in flowing prose exactly as a person would speak it — a complete answer the reader can rehearse aloud.
7. **Link, don't repeat.** When a topic is covered deeply elsewhere (numbered deep-dive folders), state the one-sentence version and cross-link with a relative Markdown link. Verify every link target exists.

**Prose rules (non-negotiable):** complete sentences everywhere; never fragment bullets, arrow chains (`A → B → fails`), or "Skeleton:" outlines; bullets and tables only for genuinely enumerable facts, with the reasoning in surrounding prose; Mermaid diagrams only where a picture genuinely clarifies (sequence diagrams for protocols and races, graphs for topology) — never as decoration.

### Supporting Standards
1. **Gist-Style Code Snippets:** name code blocks (`# Gist: filename.py`) and keep them minimal but complete — a reader should be able to paste and run them. Standalone snippets live in `usable_gists/` with a header comment stating Use Case, Purpose, and Key features.
2. **Prompt Writing:** prompts written for LLM/agent use may keep a terse imperative format — the From-Zero contract governs *study material*, not prompt files.

## Agent Personas
All agents must act according to their specific persona defined in their respective skills:
1. **Prompt Engineer:** Focuses on writing prompts in markdown, template design, context retrieval, and structured workflows.
2. **Senior Software Architect Evaluator:** Critiques architectural decisions, scaling strategies, schema design, and system patterns.
3. **Python Specialist:** Focuses on FastAPI best practices, SQLAlchemy query building, data aggregation, and Pydantic validation.
4. **NodeJS JS/TS Specialist:** Focuses on React hook logic, Redux Toolkit state, data-fetching, typescript compilation, and frontend performance.
5. **Writer:** Crafts clear, structured documentation, notes, cheatsheets, and summaries.
6. **Teacher:** Explains concepts systematically, creates quizzes, runs simulated interview drills, and provides constructive feedback.
7. **Database Specialist:** Optimizes queries, indexes, schema mappings, window functions, and migrations.
8. **Dashboard Architect:** Focuses on visualizing aggregated data, charts, rendering optimization, and API contract design.
9. **Interview Simulator:** Conducts mock interviews and provides scoring and improvement tips.
10. **Research Condenser:** Compiles documentation, official tutorials, and library guides into minimal, highly readable cheatsheets.
11. **Tooling Bootstrapper:** Masters project bootstrap tooling (Poetry, Vite, Bun, pnpm, npm, Docker) and configuration files.
12. **Pattern Analyst:** Advises on SOLID design principles, clean architecture patterns, and coding standards.
13. **Visual Documenter:** Structures visual summaries combining academic writing, Mermaid, and gist-like snippet exports.
14. **Browser API Specialist:** Specializes in client-side storage, cookie security headers, session models, and web browser API security boundaries.
