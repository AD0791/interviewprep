# Monday morning — the ninety minutes before

*Monday 3 August 2026. Interview at **`__:__`** — fill this in and count backwards. Everything below is timed against it.*

*This file is for the ninety minutes **before** the call. [File 99](99_during_call_one_pager.md) is for **during** it. Do not confuse them, and do not have both open at once — at T-5 you close this one.*

---

## Read this paragraph first

Today's job is **retrieval, not learning.** Everything you are going to know on this call, you already know. Nothing you read this morning will make it into a usable answer, and anything new you try to absorb now will do two things: it will not stick, and it will crowd out something that was already solid. The single most common way a well-prepared candidate underperforms is by cramming in the last hour and walking in with a head full of half-formed new material and no access to the well-formed old material.

So the plan below is deliberately narrow. It touches four things — the numbers, the three decisive answers, the pitch, and the machine — and nothing else. If you finish early, stop. Finishing early is a good sign, not spare capacity.

---

## T-90 to T-75 · The numbers, out loud, in English

Fifteen minutes. Read this table **aloud**, saying the figures as words. This is not a memory exercise — you know these — it is an articulation exercise, because saying "three thousand nine hundred and eighteen" and "forty-six point eight percent" in English under mild pressure is a physical skill and it is where people stumble.

| | |
|---|---|
| Funnel | 3,918 submittals → 1,835 interviews → 482 offers → 362 hires |
| Ratios | 46.8% submittal→interview · 28.0% interview→offer · 75.1% acceptance |
| Time to fill | 28 days Technical, 17 days Customer Support — an 11-day spread |
| Time to first submittal | 5 days Technical, 2 days Customer Support — the metric the client feels |
| Fill rate | 49.4% filled · 21.6% cancelled · 20.2% open · 8.9% on hold |
| English → hire rate | B1 2.9% → B2 7.9% → C1 13.4% → C2 13.4% |
| …reverses at offer | C2 accept 63.2% · B2 accept 78.9% — competing offers |
| CPL | Outbound $83.78 cheapest · Paid Social $146.27 dearest |
| CAC | Paid Search $1,362 · Paid Social $3,625 — nearly three times |
| ROAS | Paid Search 1.79 · **Paid Social 0.60** |
| Referral | 22.3% lead→client, zero recorded spend, $198,434 in fees |
| Untouched leads | 256 — 6.5% — ≈$24,000 of paid spend, 21 of them referrals |
| Reps | Best 11.1% win rate on closed vs worst 8.2% · nobody hits quota, best 68% |
| Repeat clients | 58.7% open a second requisition |
| Censoring | July 11.9% vs a stable ~55% — the cohort is too young, nothing is wrong |
| **Reconciliation** | **12 vacancies marked filled with no placement record** |
| Pipeline | `ads_spend` fails 10% of runs, schema drift — and it feeds the CAC dashboard |

**Every one of these is prefixed with "in the dataset I've been practising on…".** Say the prefix out loud a few times too, until it is automatic, because the one time you forget it is the time it matters.

If a figure will not come, skip it. One missing number costs nothing; five minutes spent retrieving one costs you the rest of this block.

---

## T-75 to T-60 · The three answers that decide it

Fifteen minutes, spoken at full length, standing up. Not read — spoken. If you read them silently you will believe you have rehearsed them and you will not have.

**Tableau.** Name the gap first, before they have to. Power BI and Looker Studio depth. The specific equivalence: a FIXED LOD is `CALCULATE` with `ALLEXCEPT` in DAX, an extract is import mode, a live connection is DirectQuery. Then the evidence: *"I installed Tableau Public and rebuilt a recruiting-funnel dashboard this weekend — I can send you the link."* Then the honest ramp: productive in two to three weeks. **Never say "fast learner."** Send the link instead. Full script: [question bank Q91](07_question_bank/05_tableau_and_dashboards.md).

**Who you are.** *"I'm a data analyst with about five years, and what's slightly unusual is that I've worked both sides of the stack."* Then the analysis proof, the engineering proof, and why this role. Say **"data analyst" in the first five words.** Do not lead with MEAL. Full pitch: [question bank Q1](07_question_bank/01_profile_and_screening.md).

**What you'd do first.** *"I'd run a reconciliation suite before building anything, because I'd rather find the problems than have someone find them in my chart."* Then the twelve uninvoiced fees. Full answer: [question bank C6](07_question_bank/07_case_and_live_exercise.md).

Say each one twice. The second time will be better than the first, and the second time is the one your mouth remembers.

---

## T-60 to T-45 · Rapid self-quiz

Twelve questions, answered out loud, one line each. Do not look at the answers until you have said all twelve — the point is retrieval under mild pressure, and checking as you go destroys it.

1. Does `LIMIT 10` make a BigQuery query cheaper?
2. What's the difference between cost per lead and cost per acquisition?
3. Why can't you trend fill rate on the current month?
4. What does a FIXED LOD do when the user applies a dimension filter?
5. Extract or live — and what does live cost you against BigQuery?
6. Why do you build the funnel from the interviews table and not the submittal status column?
7. Partitioning versus clustering?
8. What are the three things you monitor on a pipeline?
9. Someone says your dashboard is wrong. First move?
10. Why is Paid Social a problem in the practice data?
11. What's the grain of a table, and why do you ask?
12. What's the one question you must ask them?

**Answers.** 1 — No, you pay for bytes scanned; it scans everything then discards. 2 — CPL is spend over leads, CAC is spend over clients; the conversion rate in between can reverse the channel ranking, and cheap leads that don't convert are expensive. 3 — Right-censoring: the newest cohort hasn't had time to close. 4 — Nothing, it's computed before dimension filters — unless you promote the filter to context. 5 — Extract for a business with overnight loads; live means every filter click fires a billed query. 6 — Status columns overwrite history, event tables preserve it. 7 — Partitioning splits the table into segments, usually by date, and prunes whole segments; clustering sorts within a partition on up to four columns and skips blocks — order matters, leftmost first. 8 — Freshness, volume, schema drift. 9 — Reproduce before defending. 10 — ROAS 0.60, and its CAC is nearly three times Paid Search's. 11 — What one row represents; because almost every serious analytical error is a grain error. 12 — *"What's the first thing you'd want this person to fix?"*

Anything you missed, say the answer aloud twice and move on. Do not go and read the module it came from.

---

## T-45 to T-30 · The machine

Fifteen minutes, and do this properly — a technical failure at the start of a call costs you more than any answer in this file gains you.

Camera on and framed, with the light in front of you rather than behind. Microphone tested on an actual recording, not just a level meter — record ten seconds and listen back. Connection tested, and the phone hotspot ready and *already paired*, not something you'd have to set up while they wait. Headset charged.

Close everything you are not using. Every chat application, every notification, every other browser window. A notification banner mid-answer is a small thing that breaks a good sentence.

Three tabs, and only three. The Tableau Public link. The practice dataset or the query editor. [File 99](99_during_call_one_pager.md), the during-call one-pager.

Physical: notepad and a pen that works, water within reach, door shut, and anyone else in the house told.

If something is broken, fix it now — you have the time budgeted, which is the reason this block sits here rather than at T-10.

---

## T-30 to T-15 · The pitch, twice, timed

Stand up. Give the ninety-second pitch out loud, timed. Then do it again.

The first delivery will be stiff. That is what the second one is for, and it is why this block is not at T-75 — you want the last full rehearsal close enough to the call that it is still in your mouth.

Do not tighten the words. You are not memorising a script, you are warming up four beats: what I am, the analytics proof, the engineering proof, why this role. If the second run comes out with different wording and the same beats, that is exactly right and it is the version that will sound natural.

Then say the three recovery phrases once each, so they are available if you stumble:

*"Let me put that a different way."* · *"Sorry, could you rephrase that?"* · *"I want to make sure I understood — are you asking about X, or about Y?"*

The third is not a weakness. Asking a clarifying question before answering is what good analysts do, and in this role it reads as a strength.

---

## T-15 to T-5 · Stop working

Ten minutes of nothing. This block is not padding and it is the one you will be most tempted to spend on one more re-read.

Stand up and walk around. Drink some water. Breathe slowly for a minute or two — the physiological point is real, and going into a call with a raised heart rate makes you talk faster, which makes you sound less certain than you are.

Look at something that is not a screen.

Then sit down and remind yourself of one true thing: you have prepared harder for this than most candidates prepare for anything. You built a dataset. You learned a new BI tool in a weekend. You know their business model well enough to derive their metric priorities from their pricing. That is not confidence talk, it is an accurate description of the last five days.

---

## T-5 · Close this file

Close everything from this folder. Open [file 99](99_during_call_one_pager.md) and nothing else. Join two or three minutes early.

---

## Do not, this morning

**Do not open modules 01 through 06.** They are teaching documents and there is no time to be taught. If you find yourself reading a module this morning, you have stopped preparing and started worrying.

**Do not touch Tableau.** Not to polish the dashboard, not to check the link renders, not to learn one more feature. If the link works, it works. If it does not, the answer changes to "I'll send it today" and that answer is fine.

**Do not rebuild anything.** Not a query, not a chart, not the CV.

**Do not read the job description again.** You have derived more from it than they put in it.

**Do not take a new call or answer a work message.** Whatever it is, it can wait ninety minutes, and it will occupy exactly the working memory you need.

**Do not add new material.** Not one more metric, not one more BigQuery function, not one more Tableau concept. Anything learned this morning will surface as a half-remembered fragment and displace something solid.

---

## The four things you actually need

If everything above goes wrong — you sleep through the alarm, the power cuts, the ninety minutes evaporate — these four are enough to walk in with.

**Say "data analyst" in the first five words.**

**Give a number whenever you have one, prefixed with "in the dataset I've been practising on".**

**Name the Tableau gap before they do, and offer the link.**

**Ask "what's the first thing you'd want this person to fix?"**

Everything else is decoration on those four.

---

## Immediately after the call

Three minutes, before you do anything else, while it is still fresh. Write down: what they said the first thing to fix is, anything they mentioned about the stack, any name you were given, and any question you answered badly.

The follow-up email goes out within twenty-four hours. Three sentences, one specific thing from the conversation, and the Tableau link if you have not already sent it. If you promised the link this morning, send it today — a promise kept the same day is worth more than the dashboard is.

---

*Then: [99 during-call one pager](99_during_call_one_pager.md) · [Question bank](07_question_bank/README.md) · [00 plan and cheat sheet](00_prep_plan_and_cheatsheet.md)*
