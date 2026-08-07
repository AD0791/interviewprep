# Self-assessment

*Seventy questions, keyed to competency IDs. Answering this honestly decides what gets built next.*

The previous version of this file contained sixty-two good questions and **not one of them was ever answered.** Six modules were then written on assumption. They were defensible choices, but they were chosen by exactly the method the plan said not to use.

So the rule this time is blunt: **Phase 2 does not start until this file is filled in.** The result reorders everything downstream.

---

## How to run it

**Say every answer out loud, in English, with nothing open.** Not in your head. The gap between what you can recognise and what you can say is the entire subject of this folder, and it only shows up in speech. If you find yourself thinking "I know this" without producing sentences, that is a 2.

**Ninety seconds per question.** If you are still circling at ninety seconds, the answer is a 1 or a 2 regardless of how it feels. Interviews have the same timer and it is not generous.

**Rate immediately, before moving on.** Rating in hindsight inflates.

**Do not look anything up until a whole section is rated.** Looking things up mid-diagnostic converts a measurement into a study session, and then you have neither.

**Sittings of about twenty questions.** Four sittings. Fatigue on question sixty is not a knowledge signal.

### The scale

| | |
|---|---|
| **5** | Fluent. Could teach it, including at least one failure mode and one trade-off |
| **4** | Solid. Correct answer with the mechanism, maybe missing an edge case |
| **3** | Correct but thin. The what, not the why. No failure mode |
| **2** | **The dangerous one.** Feels solid from the inside, comes out vague. Recognition without retrieval |
| **1** | Cannot answer |

**A 3 that you can only reach after forty seconds of visible thinking is a 2.** Be strict — the point of this file is to be wrong here rather than in an interview.

---

## Section A — Python *(12 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| A1 | What actually happens when you write `obj.x`? Give the full resolution order. | `PY-01` | |
| A2 | How does `@property` work under the hood — and what else in code you write daily uses the same mechanism? | `PY-02` | |
| A3 | What does `__slots__` buy you, and name three things it costs. | `PY-04` | |
| A4 | What does `super()` actually do? It is not "call the parent class." | `PY-05` | |
| A5 | You define `__eq__` and the object becomes unhashable. Why did Python do that to you? | `PY-07` | |
| A6 | What happens if `__exit__` returns `True`? | `PY-09` | |
| A7 | Why doesn't assigning `obj.__len__ = lambda: 5` make `len(obj)` work? | `PY-11` | |
| A8 | Explain a closure in terms of what the function object actually holds. | `PY-12` | |
| A9 | What exactly does `functools.wraps` restore, and what breaks without it? | `PY-15` | |
| A10 | Have you ever written a metaclass? Name one running in code you already use. | `PY-16` | |
| A11 | You freed a large list and RSS didn't drop. Is that a leak? | `PY-21` | |
| A12 | Do type hints do anything at runtime? | `PY-28` | |

**Section A total: ___ / 60**

---

## Section B — Concurrency *(12 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| B1 | What does the GIL protect? Not what it prevents — what it *protects*. | `CONC-01` | |
| B2 | Name every circumstance under which CPython releases the GIL. | `CONC-02` | |
| B3 | You added threads to speed up a CPU-bound job and it got slower. Explain precisely why. | `CONC-03` | |
| B4 | Are Python's built-in types thread-safe? | `CONC-04` | |
| B5 | Is `x += 1` atomic? Justify your answer at the bytecode level. | `CONC-06` | |
| B6 | Two transactions deadlock in your code. What is the fix that actually ships? | `CONC-08` | |
| B7 | Your multiprocessing code works on a colleague's Linux box and hangs on your Mac. Why? | `CONC-12` | |
| B8 | A worker process updated a counter and the parent still reads zero. What happened, and why was there no error? | `CONC-14` | |
| B9 | What does calling an `async def` function actually do? | `CONC-16` | |
| B10 | One endpoint got slow and now every endpoint is slow. Where do you look first, and why? | `CONC-18` | |
| B11 | You need to call an API for ten thousand records. Write the shape of the solution. | `CONC-19` | |
| B12 | Is the GIL going away? What would that cost? | `CONC-22` | |

**Section B total: ___ / 60**

---

## Section C — SQL *(12 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| C1 | Explain an index in one sentence, then derive three consequences from that sentence. | `SQL-01` | |
| C2 | You are handed an `EXPLAIN ANALYZE` output. What do you look at first? | `SQL-02` | |
| C3 | When does adding an index make a query *slower*? | `SQL-03` | |
| C4 | Why is `WHERE DATE(created_at) = '2026-01-01'` slow, and what are the two fixes? | `SQL-06` | |
| C5 | The query was fast yesterday, slow today, and nobody changed the code. | `SQL-07` | |
| C6 | Why can't you use a `SELECT` alias in `WHERE` but you can in `ORDER BY`? | `SQL-08` | |
| C7 | Your `LEFT JOIN` is dropping rows. What did you do? | `SQL-10` | |
| C8 | What isolation level does your database run by default, and what anomaly does it still permit? | `SQL-13` | |
| C9 | Two transactions each read, check a condition, and write. Both commit and the invariant is broken. Name it. | `SQL-16` | |
| C10 | Write a running total. Now explain the default frame and why it is probably not what you meant. | `SQL-18` | |
| C11 | Find each user's longest streak of consecutive active days. | `SQL-21` | |
| C12 | What is the difference between `COUNT(*)`, `COUNT(col)` and `COUNT(DISTINCT col)`? | `SQL-25` | |

**Section C total: ___ / 60**

---

## Section D — JavaScript *(10 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| D1 | What is hoisting? Be careful — nothing moves. | `JS-01` | |
| D2 | Why does reading a `let` before its declaration throw, when `var` gives `undefined`? | `JS-02` | |
| D3 | Why do all three callbacks in a `var` loop log the same number? | `JS-04` | |
| D4 | The counter inside your `setInterval` is frozen at zero. Diagnose it and give all three fixes. | `JS-05` | |
| D5 | What is the difference between `__proto__` and `.prototype`? | `JS-07` | |
| D6 | What determines the value of `this`? | `JS-09` | |
| D7 | Order these: synchronous code, `setTimeout`, `process.nextTick`, a resolved promise's `.then`. | `JS-12` | |
| D8 | What does `await` compile to? | `JS-14` | |
| D9 | All your endpoints slowed down at once. What does that signature tell you? | `JS-15` | |
| D10 | What happens to an unhandled promise rejection in Node? In a browser? | `JS-17` | |

**Section D total: ___ / 50**

---

## Section E — TypeScript *(8 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| E1 | Are two types with identical shapes but different names interchangeable? | `TS-01` | |
| E2 | How do you stop a `UserId` being passed where an `AccountId` is expected? | `TS-02` | |
| E3 | What does TypeScript emit for an `interface`, a `type` and an `enum`? | `TS-03` | |
| E4 | What does the compiler actually guarantee you? | `TS-06` | |
| E5 | Is a function taking `Animal` assignable to a parameter typed as a function taking `Dog`? | `TS-10` | |
| E6 | Is TypeScript's type system sound? Give the counterexample. | `TS-11` | |
| E7 | How do you guarantee at compile time that you handled every case of a union? | `TS-15` | |
| E8 | What type is the response from `fetch`, and what should it be? | `TS-18` | |

**Section E total: ___ / 40**

---

## Section F — MongoDB *(8 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| F1 | What is the document size limit, and what breaks long before you reach it? | `MDB-01` | |
| F2 | Embed or reference? Give a decision procedure, not a preference. | `MDB-02` | |
| F3 | Store five years of sensor readings per device. Name the pattern. | `MDB-03` | |
| F4 | Order the fields in a compound index — and **derive** the rule rather than reciting it. | `MDB-08` | |
| F5 | How do you know an index is doing its job? Name the specific ratio. | `MDB-09` | |
| F6 | Does stage order matter in an aggregation pipeline? | `MDB-13` | |
| F7 | Is `$lookup` a join? | `MDB-14` | |
| F8 | What does `w: majority` actually guarantee? | `MDB-18` | |

**Section F total: ___ / 40**

---

## Section G — BigQuery and the pipeline *(8 questions)*

| ID | Question | Competency | Rating |
|---|---|---|---|
| G1 | Why is BigQuery fast on huge tables, and what does that imply about `SELECT *`? | `BQ-01` | |
| G2 | Does adding `LIMIT 10` make a BigQuery query cheaper? | `BQ-06` | |
| G3 | What is the difference between partitioning and clustering? | `BQ-09` | |
| G4 | How do you know what a query costs *before* running it? | `BQ-10` | |
| G5 | Batch load, Storage Write API, or streaming inserts — and why is the first one special? | `BQ-13` | |
| G6 | Your pipeline redelivered a batch. What happens to the warehouse table? | `BQ-15` / `CONC-30` | |
| G7 | **You moved MongoDB data into BigQuery with Beam. What did you have to decide about schema at that boundary, and why was it hard?** | `MDB-22` | |
| G8 | Would you use Beam again for that job? Argue the other side. | `BQ-24` | |

**Section G total: ___ / 40**

**G7 is the single most likely question in any data-engineering interview you sit**, because it is the one line on your CV where three claimed technologies meet. If it is not a 5, it is the highest-priority item in the repo regardless of what the rest of this diagnostic says.

---

## Scoring

| Section | Topic | Score | Max |
|---|---|---|---|
| A | Python | | 60 |
| B | Concurrency | | 60 |
| C | SQL | | 60 |
| D | JavaScript | | 50 |
| E | TypeScript | | 40 |
| F | MongoDB | | 40 |
| G | BigQuery & pipeline | | 40 |
| | **Total** | | **350** |

**Below 50%** — work the module sequence as written. The gap is real and broad.

**50% to 70%** — the knowledge is mostly there and the language is not. Read for the spoken answers in each module's §6 rather than for the mechanism in §3.

**Above 70% in a section** — leave that section alone entirely. Being thorough about things that were never weaknesses is the failure this repo was built to avoid.

### Now count your 2s

Not your 1s. **Your 2s.**

A 1 is honest. You know you cannot answer it, you will not try to bluff it, and an interviewer asking it gets a clean "I don't know, here's how I'd find out" — which costs you far less than people think.

A 2 is knowledge that feels solid from the inside and comes out vague under pressure. It is the rating that produces the answer you thought was fine and the rejection email you did not expect. It is what happened in the evaluation that started this folder.

**The 2s are the build order.** Write them out below in the order they appear, and that list — not the phase table in the README — decides what gets written after the Phase 2 core.

---

## Result

| | |
|---|---|
| Date taken | |
| Weakest section | |
| Number of 1s | |
| **Number of 2s** | |
| The three worst questions | |
| Biggest surprise | |
| G7 rating | |

**Re-run this quarterly, cold, with no notes. Same questions.** The delta is the only honest measure of whether any of this is working.

---

← [repo index](../../README.md) · [role paths](SYLLABUS.md)
