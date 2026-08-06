# no_weakness — the capability repo

*Python · SQL · JavaScript/TypeScript · MongoDB · frameworks for a hybrid data-and-engineering profile.*

**This is a plan, not yet a body of work.** Read it, argue with it, then we build.

---

## 1. What this folder is, and what it is not

The four existing folders in `interviewprep/` — `remote_leverage_data_analyst/`, `acted_bdd/`, `assitant_pmel/`, `python_bairesdev/` — are **campaigns**. Each is tied to one employer, one date, one job description. They are written to be thrown away. That is not a criticism; it is what makes them good. A campaign folder can say "the interview is Monday" and organise itself around the countdown.

`no_weakness/` is the opposite kind of thing. It is a **capability repo**: permanent, employer-independent, undated. No company names, no interview dates, no "by Sunday you should." It is the thing campaigns *draw from*. When the next Remote Leverage appears, the campaign folder should be thin — positioning, company research, a rate script — because the technical depth already lives here and gets linked, not rewritten.

Two rules follow from that, and they are the rules most likely to be broken later:

**Nothing dated goes in here.** The moment a module says "before Thursday," it has become a campaign file and belongs elsewhere.

**Campaigns link in; this folder never links out to a campaign.** A dependency from `no_weakness/` to `remote_leverage_data_analyst/` would rot the day that job closes.

---

## 2. The actual problem, stated honestly

"I have years of experience, I must be bulletproof, I should know these at the highest level."

The instinct is right but the diagnosis needs sharpening, because the study plan that follows from a wrong diagnosis wastes months.

You are not a beginner in any of these five. You have shipped FastAPI services with JWT and the repository pattern, an Apache Beam pipeline moving MongoDB into BigQuery, a React Native codebase upgraded across a major architecture change, MySQL administration with real DQA protocols, and an N+1 fix that took a page from thirty-six seconds to under half a second. That is not a person with knowledge gaps in the ordinary sense. A syllabus that starts at "what is a list comprehension" would insult the work and teach you nothing.

The real failure mode for someone at your stage is different and much more specific: **the gap between working knowledge and explainable knowledge.**

You can write the code. Under interview pressure, in your second language, with someone watching, can you say *why* — in ninety seconds, without hedging? Can you explain what the runtime is actually doing, name the failure mode before it is described to you, and defend the choice you made against the two alternatives you did not make?

That gap is where senior candidates lose interviews they were qualified for. And it is worth naming precisely because it feels like nothing when you are working. Nobody asks you to explain the GIL while you are shipping. The knowledge stays compiled, unexamined, perfectly adequate for building and useless for talking.

So `no_weakness/` is not a syllabus. It is a **decompiler for knowledge you already have**, plus honest filling of the places where the knowledge turns out to be thinner than it felt.

---

## 3. The depth ladder

Every topic in this repo gets rated on the same five-level scale. This is the organising device for the whole folder, so it is worth reading slowly.

| Level | Name | What it means | Can you fake it? |
|---|---|---|---|
| **L1** | Fluency | You write it daily without looking things up | Yes, briefly |
| **L2** | Idiom | You write it the way an experienced practitioner writes it, not the way a translator from another language would | Yes, with practice |
| **L3** | Mechanism | You can explain what the machine actually does underneath | **No** |
| **L4** | Failure | You know how it breaks, you have watched it break, and you can diagnose it from a symptom | **No** |
| **L5** | Judgment | You can choose between options, defend the choice, and teach the reasoning to someone else | **No** |

Senior technical interviews are almost entirely **L3 and L4 probes**. This is not arbitrary — those are the two levels that cannot be acquired by reading a tutorial the night before, so they are the cheapest reliable signal an interviewer has.

L4 in particular is where years of experience become *visible*. Anyone can read about the N+1 problem. Only someone who has sat in front of a query log at thirty-six seconds a page load can describe what it felt like to find it. Your career is full of L4 knowledge that you have never articulated, and articulating it is the single highest-return activity available to you.

**Bulletproof, defined operationally:** reliably L4 across all five areas, and L5 on the two you claim as specialties. Not L5 everywhere — that is a career, not a study plan, and claiming it is how people get caught.

### What L3 and L4 look like concretely

This table exists so the ladder is not an abstraction. These are the actual things the modules will cover.

| | **L3 — mechanism** | **L4 — failure** |
|---|---|---|
| **Python** | What `import` really does; the descriptor protocol behind `@property`; how `async def` produces a coroutine object and who drives it; when the GIL is and is not held | Mutable default arguments; late-binding closures in a loop; a synchronous call blocking the event loop; ORM N+1; unbounded caches growing memory |
| **SQL** | How the planner chooses an index; why a composite index only helps on its leftmost prefix; what a transaction actually holds and for how long; the evaluation order of window functions | A function on the column killing index use; deadlock from inconsistent lock ordering; correlated subquery as N+1 in disguise; stale statistics producing a catastrophic plan |
| **JavaScript** | Event loop phases; microtask versus macrotask ordering; closure capture; the prototype chain; how `this` is bound | Stale closure in a hook; `await` inside a loop serialising what should be parallel; unhandled rejection; floating-point money; coercion under `==` |
| **TypeScript** | Structural typing versus nominal; generic inference; conditional and mapped types; exactly what is erased at runtime and what survives | `any` leaking silently through a module boundary; an unsound `as` cast; excess-property checks that do not fire; function-parameter variance surprises |
| **MongoDB** | How the query planner picks and caches a plan; the ESR rule for compound indexes; which aggregation stages can still use an index and which cannot; what write and read concern actually guarantee | Unbounded array growth in a document; a silent COLLSCAN in production; `$lookup` at scale; schema drift across five years of writes; assuming no transactions exist |

---

## 4. Module anatomy

Every module in this folder has the same six parts, in the same order. Consistency matters more than it sounds: once the shape is familiar you stop reading structure and start reading content, and you can find the part you need without a search.

**One — the thing you already do.** Open with real code you have written or could have written, presented without explanation. No preamble, no "let's start with the basics." This establishes immediately that the module is not going to condescend, and it gives the rest of the module something concrete to interrogate.

**Two — the question you cannot answer about it.** The hook. *"This works. Why does it work? What happens if two requests hit it at once?"* This is where the module earns its existence, and it should be a question you actually cannot answer cleanly right now.

**Three — what the machine does.** The mechanism, traced in plain words. Not a specification restatement — a walk through one concrete execution, cause and effect, step by step. This is L3.

**Four — break it on purpose.** The classic failure, reproduced in runnable code, *shown failing* before the fix is explained. This is the part that produces L4, and it is non-negotiable. Reading about the failure produces recognition; watching it happen produces memory.

**Five — the judgment call.** When you would use this and when you would not, what the two credible alternatives are, and what you give up by choosing. This is L5, and it is what separates an answer from a good answer.

**Six — spoken answers.** Two or three interview questions on the topic, each answered in flowing prose exactly as a person would speak it, sixty to ninety seconds. Written to be said aloud, not read. This is the part that closes the working-to-explainable gap, and it is the reason to read a module rather than a reference manual.

### A note on writing style — this needs a decision

`interviewprep/.agents/AGENTS.md` defines the house style as the **"From Zero" teaching article**: assume the reader has never used the tool, open by showing life *without* it, build one thing incrementally.

That contract is excellent and it is **wrong for this folder**, because its central assumption is false here. The reader has used the tool for five years. Opening a module on Python decorators by showing life without decorators would waste the reader's time and, worse, would train the reflex of skimming.

What I propose is a documented sibling contract, `no_weakness/AGENTS.md`, called **"From Depth"**. It keeps everything in the From Zero contract that is about *quality* and changes only what is about *audience*:

**Kept, unchanged:** break it on purpose before explaining the fix; trace what the machine does in plain words; complete runnable code; mental models through analogy; close with spoken interview answers; and the non-negotiable prose rules — complete sentences everywhere, never fragment bullets, never arrow chains, tables only for genuinely enumerable facts.

**Changed:** the opening move goes from "life without the tool" to "the thing you already do, and the question you cannot answer about it." And the target moves from L1–L2 to L3–L5.

This should be written down rather than left implicit, because otherwise the next agent that touches this folder will apply the From Zero contract and produce beginner material.

---

## 5. Structure

```
no_weakness/
├── README.md                  ← this plan, and the index
├── 00_self_assessment.md      ← the diagnostic. Build order depends on it.
├── RECALL.md                  ← the master cold-answer list, all languages
├── assets/                    ← the video syllabus screenshots, mapped in each folder's README
│
├── 01_python/
│   ├── 01_async_execution_model.md           ✅
│   └── 02_concurrency_threads_processes.md   ✅
├── 02_sql/
│   └── 01_indexes_and_the_query_planner.md   ✅
├── 03_js_ts/                  ← one track, two halves: JS mechanism, then TS type system
│   ├── 01_event_loop_and_microtasks.md       ✅
│   └── 02_the_type_system.md                 ✅
├── 04_mongodb/
│   └── 01_document_modelling_and_indexes.md  ✅  (partly unmeasured — see its README)
├── 05_cross_cutting/          ← the capstone: the same problem across languages
├── 06_frameworks/             ← recommendations for the hybrid profile
└── drills/                    ← no-answer quizzes, per language and mixed
```

Each language folder has its own README with the full module list, the build order, and a **mapping to the video syllabus** in `assets/` — so you can watch a video for a topic and then work the module that makes it explainable.

Two structural choices worth defending.

**JavaScript and TypeScript are one folder, not two.** You called TypeScript "a complement to JavaScript," which is exactly right, and it should be reflected in the layout. You cannot reason well about TypeScript's type system without the JavaScript object model and async model underneath it, and splitting them into two tracks invites studying TS syntax without JS mechanism — which is the most common way people end up writing TypeScript that compiles and fails.

**`05_cross_cutting/` is the capstone, not an appendix.** Per-language depth is table stakes at senior level. What actually distinguishes a candidate is answering *across* languages: how Python's `asyncio` and JavaScript's event loop solve the same problem with different trade-offs, how SQL's relational model and MongoDB's document model push the same modelling decision to different places, what "type system" means in a gradually-typed language versus a structurally-typed one. Nobody expects those answers. Everybody is impressed by them.

The SQL-and-MongoDB pairing is worth calling out specifically. Most candidates know one well and the other by rumour. You have shipped both — MySQL administration and DQA at Caris, MongoDB into BigQuery through Beam at Tekkod. The comparative answer to "when would you not use a relational database" is available to you and to almost nobody else in the pool, and it reads as senior immediately.

---

## 6. Build order, and the honest scope estimate

Five languages at L4–L5 with runnable labs is roughly forty to fifty modules. At two to four thousand words plus working code each, this is a **six-to-twelve month project** at a sustainable pace, not a sprint. Anyone who tells you otherwise is selling something.

That is fine — it is a capability repo, it is supposed to outlive several job hunts. But it means sequencing by return, and it means **not building blind**.

### Phase 0 — the diagnostic *(first, and cheap)*

`00_self_assessment.md` before anything else. Forty to sixty questions across the five areas, each written to probe L3 or L4 rather than L1, with no answers included. You work through it out loud and rate yourself honestly on the ladder.

This is the most important step in the plan and the easiest to skip. "No weakness" is a goal that starts by **finding the weaknesses**, and building modules on assumption rather than evidence is how study repos end up thorough in the areas you were already strong in. The diagnostic decides the build order for phases 2 and 3. Everything downstream depends on it.

### Phase 1 — done

Five flagship modules are written, one per area plus concurrency:

| Area | Module | Evidence |
|---|---|---|
| **Python** | [The async execution model](01_python/01_async_execution_model.md) | Measured — CPython 3.10.12, FastAPI 0.141.1 |
| **Python** | [Concurrency — threads, processes, the GIL](01_python/02_concurrency_threads_processes.md) | Measured — 4 cores, `fork` |
| **SQL** | [Indexes and the query planner](02_sql/01_indexes_and_the_query_planner.md) | Measured — 200k accounts, 1M transactions |
| **JS** | [The event loop and microtasks](03_js_ts/01_event_loop_and_microtasks.md) | Measured — Node v22.22.3 |
| **TS** | [The type system](03_js_ts/02_the_type_system.md) | Measured — TypeScript 7.0.2 `--strict` |
| **MongoDB** | [Document modelling and the ESR rule](04_mongodb/01_document_modelling_and_indexes.md) | **Partly unmeasured** — no `mongod` available |

Everything in the first five came out of a terminal. The MongoDB module is the exception and says so at the top: its BSON sizes are real, its query plans are not. That gap is the highest-priority outstanding task in the repo, and it is recorded in [that folder's README](04_mongodb/README.md) rather than quietly ignored — the measured claims are what make these modules worth more than documentation, and borrowing that authority for unmeasured ones would undermine all of it.

### Phase 2 — what comes next

The cross-cutting capstone comparing Python, JavaScript and the database directly; then depth per language in whatever order [the diagnostic](00_self_assessment.md) says. Each language folder's README carries its own module list and its mapping to the video syllabus.

### Phase 2 — depth, ordered by return

The default order, subject to what the diagnostic finds:

**Python first.** Your primary language, and the one place where the data half and the engineering half of your profile overlap completely. Every hybrid role you would want asks Python questions.

**SQL second.** Asked in *both* analyst and developer interviews, which no other item on this list can claim. You also already have substantial material in `acted_bdd/` and `assitant_pmel/` — that work should be consolidated and levelled up rather than rewritten, and this is the one area where we harvest rather than build.

**JavaScript and TypeScript third.** JavaScript mechanism first — event loop, closures, prototypes, `this` — then the TypeScript type system on top of it. Type-system depth is where I would expect the largest genuine gap, because it is the part you can ship professionally without ever needing.

**MongoDB fourth.** Narrower in scope, but it is a differentiator rather than a commodity, and it is cheap to reach L4 in because the surface area is smaller.

### Phase 3 — cross-cutting and frameworks

The comparative modules, and the framework recommendations. Framework material comes last on purpose: it is the fastest-decaying content in the repo, so writing it early wastes it.

---

## 7. On the framework module — one caveat up front

`06_frameworks/` is where I would give opinionated recommendations for the hybrid data-and-engineering profile: what to keep, what to add, and what to stop investing in.

My instinct on the shape of it, to be argued with rather than accepted: your backend stack is already right and needs consolidation rather than replacement. The genuine gaps are on the analytics-engineering side, where the tooling has moved substantially and where a hybrid profile is judged by tools that did not exist when your career started. There is at least one credential-grade tool in that space that I would expect to be the highest-return single addition to your profile — but I want to verify the current landscape before naming it in writing.

That caveat is deliberate. My reliable knowledge runs to around May 2026, and the data-tooling landscape moves faster than anything else on this list. **Before writing `06_frameworks/`, we should do a web-verification pass** — current versions, what has been deprecated, what job specs are actually asking for now. Writing that module from memory is the one way this repo could actively mislead you, and a framework recommendation that was true eighteen months ago is worse than no recommendation.

The language modules do not have this problem. The Python object model, the event loop, B-tree indexes and the ESR rule are stable knowledge, and that is another argument for building them first.

---

## 8. How knowledge gets verified, so this is not reading theatre

The failure mode of every self-study repo is that reading feels like learning. Recognition is not retrieval, and a module you have read twice will feel mastered right up until someone asks you about it out loud. Four mechanisms, all of them borrowed from things that already worked in the campaign folders:

**Runnable labs.** Every module ships code in `labs/` that you execute rather than read, including the broken version. You have to *see* the event loop stall and the query log scroll. This is the difference between knowing about a failure and recognising it.

**No-answer drills.** `drills/` holds the questions without the answers — the format from `remote_leverage_data_analyst/first_step/07_question_bank/08_quiz_no_answers.md`, which worked. You answer aloud first, then check. Reading the answer first teaches you almost nothing and feels like progress, which is the worst combination available.

**Spoken rehearsal.** Every module closes with answers written to be said, not read. Interviews are spoken, in English, under pressure. Studying silently trains the wrong skill, and this is doubly true when the interview is in your second language.

**The recall list.** `RECALL.md` is the running master list of everything you must be able to answer cold — thirty or so per language, one line each, no answers. It is what you re-read before any technical interview regardless of employer, and it is the thing a campaign folder links to instead of duplicating.

Self-rating on the L1–L5 ladder goes in the self-assessment and gets revisited quarterly. Topics that come back red get a module. Topics that stay green get left alone, which is just as important — the point is to eliminate weakness, not to write exhaustively about strength.

---

## 9. Decisions taken

| Decision | Setting | Consequence |
|---|---|---|
| Time budget | **3–5 hours a week** | Long-haul pace. Forces hard prioritisation — see below. |
| Code | **Prose only, complete code inline** | Roughly 40% less effort per module. Code is shown complete and runnable but not shipped as a lab. |
| Frameworks | **Verify the landscape by search first** | `06_frameworks/` is written only after a current-sources pass. |
| Starting point | **The self-assessment** | Build order is decided by evidence rather than assumption. |

### What 3–5 hours a week actually means, said plainly

At four hours a week, prose-only, a module of the depth described in section 4 takes roughly three to four hours to write and an hour to work through properly. The forty-to-fifty module repo sketched in section 6 is therefore something like a **twelve-to-fifteen month project**, and a twelve-month plan is a plan that gets abandoned in month three.

So the scope changes, and it should change now rather than by silent attrition later. **The target is roughly twenty to twenty-five modules, not fifty** — chosen by the diagnostic rather than by covering a syllabus. That is achievable in six to eight months at this pace, and it is a better repo, because a folder of twenty-five modules aimed at your actual gaps beats fifty modules half of which restate things you already do daily.

The consequence for Phase 1: **two flagship modules, not five.** Python's async execution model and SQL's query planner — the two highest-return topics across every role you would want. If the format works, we scale. If it does not, we have spent eight hours finding out.

The `RECALL.md` list and the drills matter *more* under this constraint, not less. When writing time is scarce, the cheap high-frequency activity — answering questions out loud without notes — has to carry proportionally more of the load. Twenty minutes of spoken drilling is worth more per hour than any reading you can do.

### One consequence of dropping labs

Prose-only was the right call for the time budget, but it removes the mechanism that produced L4 most reliably: watching the failure happen. Two substitutes go into the module contract to compensate.

Every "break it on purpose" section shows the **actual output** — the real traceback, the real query log, the real timing — rather than describing what would happen. Reading `36.4s` next to `0.31s` is not the same as running it, but it is much closer than a sentence saying it gets faster.

And where a failure is genuinely worth feeling rather than reading, the module says so explicitly and gives you the ten-line reproduction to paste into a terminal yourself. Not a lab to maintain, just a snippet with an instruction: *run this one, do not just read it.* Reserved for the handful of cases where it truly matters — the blocked event loop is one of them.

---

*Nothing in this folder should reference a specific employer or a specific date. If a module starts to, it belongs in a campaign folder instead.*
