# Behavioural and situational questions

*Q23–Q42. Every answer below is built from a project that is actually on your CV. Nothing here is invented, and nothing here needs to be, because you have more usable material than most candidates twice your age.*

---

## The five stories you own

Behavioural interviews are not twenty questions, they are five stories asked twenty ways. Learn the stories and the mapping, and you stop needing a script per question.

**The N+1 fix.** A production page took 36 seconds to load. You read the query logs, found the application was fetching a list and then firing one query per row, replaced it with a single aggregated join plus eager loading, and brought it under half a second. Covers: technical problem-solving, diagnosis, measurable impact, performance.

**The reconciliation habit.** At Caris you established a data-quality framework — automated checks that had to pass before any figure was published, with anomalies triaged and documented rather than silently corrected. Covers: quality, process, prevention, standards, catching your own errors.

**The 40% automation.** Recurring reporting at Caris, previously assembled by hand, rebuilt in Python and SQL — cutting manual production time by 40% and removing a recurring source of transcription error. Covers: initiative, automation, efficiency, impact on colleagues.

**The Beam pipeline.** MongoDB collections into BigQuery via Apache Beam, mapping nested documents onto BigQuery's nested and repeated fields rather than flattening, with idempotent loads so reruns did not duplicate data. Covers: engineering depth, design decisions, working with imperfect source data.

**The enablement work.** Across HANWASH, Anseye Pou Ayiti and Caris, you trained non-technical field teams on collection tools and wrote the guides that outlasted you. Covers: communication, teaching, stakeholder management, working with people who are not like you.

Every question below routes to one of those five. When you are asked something this file does not cover, ask yourself which of the five fits and tell that one.

---

## Q23 — Tell me about a time you solved a difficult technical problem.

> "The clearest one is a performance problem at Tekkod. A page in a production application was taking about thirty-six seconds to load, and the complaints were coming in as 'the app is slow', which isn't a diagnosis. I turned on query logging and watched what the request actually did, and the pattern was immediately visible in the log: one query fetching a list of records, and then one further query per row to count its related items. About a hundred rows meant about a hundred and one round trips to the database, each one fast on its own and catastrophic in aggregate. That's the classic N+1 pattern. The fix was to replace the loop with a single aggregated join and eager-load the relationship, so the same page went from a hundred and one queries to two. Load time came down from thirty-six seconds to under half a second. What I'd add is the part that mattered more than the fix: I put the query log in front of the team afterwards, because the reason it survived to production is that nobody had ever looked at what the page was doing at the database level — every individual query looked fine."

The last sentence is what turns a war story into evidence of judgement. Interviewers hear the fix from everyone; almost nobody says what they changed so it would not recur.

## Q24 — Tell me about a time you improved a process.

> "At Caris Foundation I inherited a weekly reporting cycle that was assembled by hand — someone pulled extracts, pasted them into a workbook, recalculated the indicators, and rebuilt the same tables every week. It took most of two days and it had a failure mode nobody talked about, which is that copying numbers between systems introduces transcription errors that are almost impossible to find afterwards, because the wrong number looks exactly like the right one. I rebuilt it in Python and SQL: the extracts became queries, the indicator calculations became code with the definitions written down, and the output became generated rather than assembled. It cut the manual production time by about forty percent, but the part I'd argue was more valuable is that it removed a whole class of error and made the indicator definitions explicit — before that they lived in the head of whoever built the workbook."

## Q25 — Tell me about a time you had to learn something quickly.

> "Most recently, Tableau — for this role. I read your job description, saw Tableau as the first responsibility, and rather than tell you I'd pick it up I installed Tableau Public and rebuilt a recruiting-funnel dashboard in it over a weekend. But the pattern is older than that. mWater, CommCare and Kobo were all tools I learned on the job because a programme needed them, and the approach is the same each time: find the concept in the new tool that maps onto something I already understand, build one real thing end to end rather than working through tutorials, and deliberately break it to find out where the edges are. With Tableau the mapping was to Power BI — a FIXED level-of-detail expression is what I'd write as CALCULATE with ALLEXCEPT in DAX, an extract is import mode, a live connection is DirectQuery. Once you have that spine, what's left is the interface."

## Q26 — Tell me about a time you disagreed with a stakeholder about a number.

> "It has happened more than once, and the shape is always the same: someone's spreadsheet says one thing and my report says another, and the temptation on both sides is to defend. What I've learned to do is not defend at all in the first conversation. I ask for their number and the query or workbook behind it, and I reproduce it. Usually the disagreement isn't about arithmetic, it's about definition — a different date field, a different inclusion rule, someone counting people and someone counting records. In one case at Caris the whole gap was that one report counted every registration and the other counted unique individuals, so duplicates were being treated as coverage. The resolution isn't 'I was right', it's writing the definition down and agreeing which one we're publishing. I showed the query rather than arguing about the answer, and the fix was a documented definition rather than a correction."

*"I showed the query rather than arguing about the answer"* is the sentence to make sure you say. It answers the question behind the question, which is whether you are difficult to work with.

## Q27 — Tell me about a time you had to explain something technical to a non-technical audience.

> "This has been most of my working life, because programme staff and funders are not technical and the numbers still have to mean something to them. The lesson I'd offer is that the failure mode isn't vocabulary, it's the shape of the explanation. People try to explain the mechanism, and the audience doesn't want the mechanism, they want to know what they can conclude and what they can't. So I lead with the conclusion, then the confidence, then the caveat — 'coverage is at seventy-two percent, that figure is solid, and the one thing it doesn't tell us is whether the people we missed are systematically different from the ones we reached.' The other thing that works is showing them the shape of the data rather than the summary. I've resolved more confusion by putting twenty raw rows on a screen than by any amount of explanation."

## Q28 — Tell me about a time you trained or onboarded someone.

> "At HANWASH and at Anseye Pou Ayiti I ran enablement for field teams on the digital collection tools — mWater, ODK, Google Forms with validation logic. The thing I changed after the first round is that I stopped training on the tool and started training on the failure. Walking someone through the correct workflow produces someone who can do it while you're watching. What actually sticks is showing them what goes wrong: what a bad GPS reading looks like, what happens when you submit a form offline and never sync it, why a date typed as text breaks the report at the other end. And I wrote the guides, deliberately, so the knowledge wasn't dependent on me being reachable — that's the part that decides whether the system still works six months later."

## Q29 — Tell me about a time you worked with people you never met in person.

> "Almost my entire career. Both Tekkod engagements are fully remote, HANWASH was through Upwork with an international client, and my current team is distributed. What I've learned is that remote work fails on ambiguity rather than on distance. In an office, an unclear request gets resolved by someone leaning over a desk; remotely it becomes three days of the wrong work. So I over-confirm scope in writing before starting — 'here's what I understood, here's what I'm going to produce, tell me if that's not it' — and I make my work visible in progress rather than only at the end. And I write things down as a default, because in a distributed team the documentation is the shared memory. Nobody has ever complained that I wrote too much down."

## Q30 — How do you prioritise when three people each want a dashboard?

> "I ask each of them the same two questions: what decision does this change, and what happens if it arrives two weeks later. That usually collapses the list on its own, because a surprising number of requests turn out to be curiosity rather than decisions, and the ones attached to a real decision announce themselves. Then I look for overlap, because three dashboard requests are often two views of one dataset, and building the shared layer once serves all three. And I'd rather deliver one thing properly and tell the other two people a date than deliver three half-built things — but I say the date out loud rather than letting them discover the delay. If it's genuinely unresolvable I take it to whoever owns the roadmap rather than silently picking, because choosing between stakeholders isn't my decision to make quietly."

## Q31 — Tell me about a time you missed a deadline or made a mistake.

> "The honest general version is my weakness answer in practice: I've delivered late by building the durable version of something when the person needed the rough version on a date. The specific pattern was a reporting request where I designed the pipeline that would produce it repeatably, and what was actually wanted was the number that week. I delivered good work later than it was useful, which is a way of not delivering. What I changed is that I now split the ask explicitly at the start — 'here's what I can have to you Thursday, and here's what it would take to make it repeatable, tell me which one you want' — and I let them make that trade rather than making it for them."

## Q32 — Tell me about a time you had to push back on a request.

> "The one I'd give is being asked for a breakdown the data couldn't support. Someone wanted results split by a category that was only recorded for part of the period and inconsistently entered when it was. I could have produced the chart — it would have rendered fine, and nobody looking at it would have known. What I did instead was produce it with the coverage stated on the face of it: this cut is based on the forty percent of records where the field is populated, and here's why the missing sixty percent probably aren't random. Then I offered the alternative that was actually supportable. The framing I use is that I'm not refusing the question, I'm refusing to answer it with more confidence than the data has. That's an easier conversation than 'no', and it usually leads to a better question."

## Q33 — How do you handle competing instructions from two managers?

> "Surface it rather than absorb it. Trying to satisfy both quietly means doing both badly and taking the blame twice. I'd go back with the specific conflict, written down neutrally — 'A needs X by Tuesday, B needs Y by Tuesday, here's what each costs, which comes first?' — and let the people who own the priorities own them. What I'd avoid is presenting it as a complaint about either person. It's a scheduling fact, not a grievance."

## Q34 — Tell me about a time your analysis changed a decision.

> "The pattern I'd point to is quality analysis rather than a headline finding. At Caris the data-quality framework I built surfaced that a chunk of records were duplicated across sites — the same individuals registered more than once — which meant coverage was being reported higher than it was. That changed how the numbers were reported to the funder and it changed the registration process, because the fix wasn't deduplicating the existing data, it was preventing it at collection. And on the practice dataset I built for this role, the equivalent finding is that twelve vacancies are marked filled with no matching placement record. That isn't a data curiosity, it's twelve fees potentially never invoiced — and that's the kind of finding that changes a decision the same week."

## Q35 — Tell me about a time you found an error in your own analysis.

**One of the five most important questions in the bank.** What is being tested is not whether you make mistakes — everyone does — but whether you catch them yourself, own them fast, and change the process afterwards.

> "Yes, and the general shape has caught me more than once: a join that fanned out. You join two tables where the relationship isn't one-to-one, the rows multiply, and every sum in the report is inflated — but nothing errors, nothing looks broken, and the chart renders beautifully. I caught one of these because the total didn't reconcile against a source I'd checked it against out of habit, not because anything looked wrong. That's the uncomfortable part: I didn't spot it by being clever, I spotted it because I had a reconciliation step. When I found it I said so immediately and plainly rather than quietly correcting it, because a number that has already been quoted needs to be un-quoted. And then I added the check that would have caught it earlier — a row-count assertion before and after the join, so if the grain changes, it fails loudly rather than producing a plausible wrong answer. That's the general lesson I'd give: the dangerous errors aren't the ones that crash, they're the ones that produce a believable number."

## Q36 — A stakeholder says your dashboard is wrong. What do you do?

> "Reproduce before defending, always. I ask them for the specific number they're looking at, which filters were applied, and what they expected instead — because about half the time the answer is a filter or a date range and there's nothing wrong with anything. If it survives that, I go to the grain: what does one row mean, and has a join changed it. Then I reconcile against the source system rather than against my own intermediate steps, since if I made a mistake I'll make it again the same way. If the dashboard is wrong I say so fast and plainly, and I'd rather say it in the meeting than after checking for an hour, because the cost of a wrong number rises with every hour it stays quoted. And then the check gets added. What I try never to do is argue first — I've seen people defend a number for twenty minutes and then discover it was wrong, and they don't get that credibility back."

## Q37 — How do you work without close supervision?

> "It's the only way I've worked, so the honest answer is by making myself legible. Confirm the scope in writing before starting, show progress rather than only outcomes, and flag problems early enough that they're still cheap. The failure mode of unsupervised work isn't laziness, it's drift — going quiet for two weeks and surfacing with something adjacent to what was wanted. So I treat a short weekly written update as part of the job rather than overhead, and I ask a clarifying question the moment something's ambiguous instead of picking an interpretation and hoping."

## Q38 — Tell me about a time you dealt with messy or incomplete data.

> "This is most of the work, honestly. The multi-site collection systems I've administered — CommCare, mWater, MySQL behind them — produced exactly the mess you'd expect from dozens of people entering data on phones in the field: duplicates, inconsistent spellings, dates typed as text, records that referenced sites that didn't exist. The approach I settled on has three layers. Prevent what can be prevented at collection, with validation logic in the form itself, because a constraint at entry is worth ten corrections downstream. Detect the rest with an automated check suite that runs before any reporting cycle and has to come back clean. And document, rather than silently fix, anything that's a judgement call — because a silent correction is indistinguishable from an error to the next person. The sentence I use is that constraints prevent what can be prevented and checks detect what can't."

## Q39 — Tell me about a time you automated something nobody asked you to automate.

> "The reporting rebuild at Caris started that way. Nobody asked for it — the weekly cycle worked, it was just expensive. I built the first version alongside the manual process rather than instead of it, ran both for a couple of cycles, and showed that they agreed. That mattered more than the automation itself, because asking people to trust generated numbers over hand-built ones is a real ask, and running them in parallel is how you earn it rather than argue for it. Once they matched twice, nobody wanted to go back."

## Q40 — What would you do if you were given a task you didn't know how to do?

> "Say so, and then say what I'd do about it, in the same breath. 'I haven't done that — here's how I'd approach it and here's roughly how long it would take me to get to a reliable answer.' The thing I try never to do is take the task away and produce something confident and wrong, because in analysis a wrong answer delivered confidently is worse than no answer, and it can survive for months. For an unfamiliar tool I'd find the smallest real version of the problem and build that end to end before scaling it up, which is exactly what I did with Tableau this week."

## Q41 — How do you know when an analysis is finished?

> "When it answers the question that was asked, it reconciles against a second source, and I can state what it doesn't tell you. That last one is the part people skip. An analysis without stated limitations invites the reader to use it for things it can't support, and then the failure is attributed to the data rather than to the framing. Beyond that I'd rather ship at eighty percent with the caveats visible than at ninety-five percent two weeks later, because analysis decays — a perfect answer to last month's question isn't worth much."

## Q42 — What's the piece of work you're proudest of?

Pick one, tell it with specifics, and end on why it mattered rather than why it was hard.

> "The data-quality framework at Caris, which sounds like the least glamorous option. The dashboards were more visible, but the framework is the thing that made the dashboards worth looking at. Before it, the honest state was that numbers were published and hoped for; afterwards there was a set of checks that ran before every cycle and had to come back clean, with anomalies triaged and written down instead of quietly edited. The reason I'm proud of it is that it changed the default. It stopped being a question of whether someone remembered to check, and it outlasted me at the organisation — which for a consultant is the only real measure of whether you built something."

---

## The STAR discipline, briefly

Situation and Task should take fifteen seconds. Action takes the bulk. Result must contain a number or a stated outcome. The commonest failure is spending ninety seconds on context and thirty on what you actually did — and it is the *did* they are assessing.

If you are asked something these twenty do not cover, do not invent. Say *"let me think for a second"* — silence is allowed, and a considered answer after three seconds beats a fluent answer to a different question. Then route to whichever of the five stories fits.

---

*Next: [03 Business domain and metrics](03_business_domain_metrics.md) · Back to [question bank index](README.md) · [01 Profile and screening](01_profile_and_screening.md)*
