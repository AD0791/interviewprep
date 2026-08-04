# The diagnostic

*Sixty-two questions. No answers — deliberately. This file decides what gets built and in what order, so answering it honestly is worth more than any single module in the repo.*

---

## How to work this

**Out loud, in English, with nothing open.** Not in your head, not typing. Speaking is the skill being tested and it is measurably harder than thinking — you will discover that several answers you were sure of dissolve somewhere around the second sentence. That dissolution is the finding. It is the entire point of the exercise.

**Timebox each answer to ninety seconds.** If you are still constructing the answer at ninety seconds, it does not count as known, regardless of whether you would eventually get there. Interviews do not wait.

**Rate immediately, before moving on.** Not at the end, when fatigue and self-consciousness have set in.

**Do it in sittings of about twenty questions.** Three sessions of roughly forty minutes. Doing all sixty-two at once produces exhaustion rather than data — the last twenty ratings will be worse than the first twenty for reasons that have nothing to do with your knowledge.

**Do not look anything up until the whole section is rated.** Looking things up mid-diagnostic converts a measurement into a study session, and then you have neither.

### The scale

Use the ladder from the [README](README.md). Rate what you can say *right now, aloud*, not what you could reconstruct given an afternoon.

| | |
|---|---|
| **1** | I could not answer this. |
| **2** | I know the words but could not explain the mechanism. |
| **3** | I can explain what actually happens underneath. |
| **4** | I can explain it *and* describe how it breaks, from experience. |
| **5** | I can explain it, break it, defend the trade-off against alternatives, and teach it. |

A 3 that you can only reach after forty seconds of visible thinking is a 2. Be strict — this file has no audience but you, and inflating it only buys you modules aimed at the wrong places.

---

## Section A — Python *(14 questions)*

| # | Question | Rating |
|---|---|---|
| A1 | Walk through what Python actually does, step by step, when it executes `import pandas`. What gets cached, and where? | |
| A2 | `def f(x, acc=[])` — what goes wrong, and at exactly which moment does the thing that causes it happen? | |
| A3 | You write `@property`. What protocol makes that work, and where in the lookup does it get invoked? | |
| A4 | Calling `foo()` where `foo` is an `async def` returns what, precisely? Who runs the body, and when? | |
| A5 | Inside an async FastAPI endpoint you call `requests.get(...)`. What happens to the other requests currently in flight, and why? | |
| A6 | When is the GIL released? Name at least two distinct cases. | |
| A7 | Threads, multiprocessing, asyncio — pick one for a CPU-bound job, one for I/O-bound, one for mixed, and defend each choice. | |
| A8 | `b = a[:]` versus `copy.deepcopy(a)`. Construct a case where the difference causes a real bug. | |
| A9 | You build a list of lambdas inside a `for` loop. What is the classic bug, why does it happen, and what are two fixes? | |
| A10 | What does `__slots__` buy you, and what does it cost you? | |
| A11 | A generator versus a list comprehension over ten million rows — trace what is actually held in memory in each case. | |
| A12 | A SQLAlchemy query returns 100 rows and the page takes thirty seconds. Diagnose it out loud without seeing the code. | |
| A13 | `is` versus `==`. Give a case from real code where confusing them caused a bug. | |
| A14 | What does Python do with type hints at runtime? What does that imply for validation? | |

**Section A total: ___ / 70**

---

## Section B — SQL *(13 questions)*

| # | Question | Rating |
|---|---|---|
| B1 | A composite index on `(school, week)`. Your query filters only on `week`. Is the index used? Explain why. | |
| B2 | `WHERE DATE(created_at) = '2026-01-01'` — why might this be slow, and what would you write instead? | |
| B3 | The planner chooses a sequential scan over an available index. Give two situations where that is the *correct* decision. | |
| B4 | What does a transaction actually hold, and for how long, under READ COMMITTED? | |
| B5 | Two transactions deadlock. What was the underlying cause, and how do you prevent that class of deadlock structurally? | |
| B6 | A window function versus `GROUP BY` — what can each do that the other cannot, and where do they sit in the evaluation order? | |
| B7 | Why is a correlated subquery the N+1 problem wearing different clothes? | |
| B8 | You `LEFT JOIN` and then put a condition on the right table in `WHERE`. What have you just done to your join? | |
| B9 | When would you reach for a materialised view, and what are you giving up? | |
| B10 | Stale statistics — what is the symptom, and how do you establish that is what you are looking at? | |
| B11 | Production is slow. How do you *find* the offending query without guessing? | |
| B12 | `COUNT(*)`, `COUNT(col)`, `COUNT(DISTINCT col)` — semantics and relative cost of each. | |
| B13 | Describe a query plan you have actually read in your work. What did it tell you, and what did you change? | |

**Section B total: ___ / 65**

---

## Section C — JavaScript *(10 questions)*

| # | Question | Rating |
|---|---|---|
| C1 | `setTimeout(fn, 0)` and `Promise.resolve().then(fn)` are both pending. Which runs first, and why? | |
| C2 | Trace one button click through the event loop: call stack, microtask queue, macrotask queue, render. | |
| C3 | `for (var i = 0; i < 3; i++) setTimeout(() => console.log(i))` — what prints, and why? Now change `var` to `let` and explain the difference. | |
| C4 | A method is extracted from an object and passed as a callback. What is `this` now? Give three ways to fix it. | |
| C5 | You `await` inside a `for` loop over a hundred URLs. What have you done to the total time, and what is the fix? | |
| C6 | A property lookup misses on the object. What happens next, mechanically? | |
| C7 | An unhandled promise rejection — what happens in Node, and what happens in a browser? | |
| C8 | `0.1 + 0.2` — explain the cause, and say what you do about money in a financial application. | |
| C9 | `==` versus `===` — name a coercion that genuinely surprises experienced developers. | |
| C10 | A stale closure in a React hook. Explain it at the level of renders and closures, without using framework vocabulary. | |

**Section C total: ___ / 50**

---

## Section D — TypeScript *(8 questions)*

| # | Question | Rating |
|---|---|---|
| D1 | Structural versus nominal typing. Give a case where structural typing accepts something you wish it had rejected. | |
| D2 | What survives to runtime and what is erased? What does that imply about validating data from an API? | |
| D3 | When you write `as`, what are you telling the compiler, and what risk have you taken on? | |
| D4 | Generic inference fails. Describe a case where it does, and what you do about it. | |
| D5 | `unknown`, `any`, `never` — when is each correct? | |
| D6 | Give a problem solved by a mapped type and one solved by a conditional type that a plain interface cannot solve. | |
| D7 | Excess property checking — when does it fire, and when does it silently fail to? | |
| D8 | You receive JSON from an API. Get from `unknown` to a trusted typed object. What is the runtime cost, and who pays it? | |

**Section D total: ___ / 40**

---

## Section E — MongoDB *(11 questions)*

| # | Question | Rating |
|---|---|---|
| E1 | State the ESR rule, and explain why the order is what it is. | |
| E2 | A query does a COLLSCAN in production but was fast in development. What changed? | |
| E3 | Which aggregation stages can still use an index? What happens to index eligibility after the first `$group`? | |
| E4 | Embed or reference — give the actual decision rule, not the platitude about "data that's accessed together." | |
| E5 | The 16MB document limit. What design does it genuinely forbid, and how do you notice you are approaching it before you hit it? | |
| E6 | Unbounded array growth inside a document — why is this a problem beyond simply getting large? | |
| E7 | Write concern `w:1` versus `majority`. What exactly are you trading? | |
| E8 | `$lookup` — when is it fine, and when is it a symptom that you modelled the data wrong? | |
| E9 | Five years of schema drift across a live collection. How do you find it, and how do you fix it without downtime? | |
| E10 | When would you *not* use MongoDB? Answer as someone who has shipped both it and a relational database. | |
| E11 | You moved MongoDB data into BigQuery with Beam. What did you have to decide about schema at that boundary, and why was it hard? | |

**Section E total: ___ / 55**

---

## Section F — Cross-cutting *(6 questions)*

These are the senior-signal questions. Nobody expects good answers, which is exactly why they are worth having.

| # | Question | Rating |
|---|---|---|
| F1 | Python's `asyncio` and JavaScript's event loop solve the same problem. Where do they genuinely differ, and when does that difference matter to a decision? | |
| F2 | The same modelling decision in Postgres and in MongoDB — where does each push the complexity, and who pays for it later? | |
| F3 | Python's gradual typing and TypeScript's structural typing — what does each actually *guarantee*, and what does neither? | |
| F4 | Explain N+1 in three settings: an ORM, hand-written SQL, and a REST or GraphQL API. What is the common shape? | |
| F5 | A report takes four hours. Explain to a non-technical stakeholder why, and what you propose, without saying anything untrue. | |
| F6 | Take a technical decision you actually made and defend it against the option you rejected. Then argue the other side. | |

**Section F total: ___ / 30**

---

## Scoring, and what it means

| Section | Score | Max | % |
|---|---|---|---|
| A — Python | | 70 | |
| B — SQL | | 65 | |
| C — JavaScript | | 50 | |
| D — TypeScript | | 40 | |
| E — MongoDB | | 55 | |
| F — Cross-cutting | | 30 | |
| **Total** | | **310** | |

Percentages matter more than raw totals here, because the sections are different sizes.

**Below 50%** — this area needs a module sequence, not a single module. It goes near the front of the build order regardless of what the ROI ranking in the README says, because a genuine gap outranks a theoretical priority.

**50–70%** — you know the material and cannot yet perform it. This is the most common result for an experienced practitioner and it is the cheapest to fix, because the knowledge is already there and only needs articulating. Modules here get written in the "decompiler" register: less teaching, more putting words to what you already do.

**Above 70%** — leave it alone. Add the questions to `RECALL.md` for periodic drilling and spend the writing time elsewhere. Resist the urge to build here; it is comfortable and it is exactly how study repos end up strongest where you were already strong.

### The finding that matters most

Count your **2s specifically** — "I know the words but cannot explain the mechanism." Not the 1s.

A 1 is a genuine gap and it is honest; you know you do not know, and you will not claim it in an interview. A 2 is the dangerous rating. It is knowledge that *feels* solid from the inside, that you will confidently reach for under pressure, and that will come apart in the second follow-up question. Every 2 is a place where you will walk into an interview believing you are covered.

**The 2s are the build order.** More precisely than any of the reasoning in the README, which was written before either of us had this data.

---

## Output — fill this in when you are done

| | |
|---|---|
| Date completed | |
| Weakest section by percentage | |
| Number of 1s | |
| Number of 2s | |
| The three questions that felt worst to answer aloud | |
| Anything I was surprised to be weak on | |
| Anything I was surprised to be strong on | |

The last two rows are not filler. Surprise is information about where your self-model is wrong, and a wrong self-model is more dangerous in an interview than a known gap.

**Re-run this file every quarter.** Same questions, no notes. The delta is the only honest measure of whether the repo is working, and it costs two hours to find out.

---

← [README and the plan](README.md)
