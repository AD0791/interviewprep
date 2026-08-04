# Data quality, pipelines, tooling and AI

*Q109–Q126. This is your home turf. Responsibilities four and five in their job description — pipeline health and data quality — are the two things most analyst candidates cannot do, and you have been doing them for years. The only work here is saying it in their vocabulary rather than yours.*

---

## Q109 — How would you monitor the health of our data pipelines?

> "'I check whether it failed' is where most people stop, and it's the weakest possible answer, because the failure that hurts you is the one that succeeds. I watch three things. **Freshness** — when did this table last update successfully, which is the only question a dashboard consumer actually cares about. **Volume** — row counts compared against the same weekday last week, because a job that succeeds with zero rows is far worse than one that fails loudly: it fails silently, the dashboard renders, and everyone believes it. And **schema drift** — new columns appearing or expected ones vanishing, which is the failure mode of any pipeline pulling from a third-party API you don't control. Then I'd separate monitoring from alerting, which people conflate. Monitoring is everything you record. Alerting is the small subset that's worth waking someone for, and it must be actionable and rare — the moment an alert fires routinely and gets ignored, you've lost the channel entirely and you won't notice when it's the real one."

## Q110 — What would you do about a pipeline that fails ten percent of the time?

> "In the practice dataset that's `ads_spend` — 58 failures out of 572 runs, and the dominant error is schema drift, meaning the ad platform changed its export format and the loader wasn't tolerant of it. Two responses, and they're different. The immediate one is to make the loader tolerant: read the columns you need by name rather than by position, and treat an unexpected new column as something to log rather than something to die on. The structural one is the connection I'd make explicit — **`ads_spend` is the least reliable pipeline and it feeds the cost-per-acquisition analysis.** A marketing dashboard is only as trustworthy as its worst upstream job. Which is why I'd put a freshness indicator *on* the dashboard — a small note saying 'spend data last loaded successfully on X' — rather than in a separate monitoring tool that nobody opens. If the CAC number is stale, the person reading the CAC number needs to know, not the person who owns the pipeline."

## Q111 — What's the difference between validation and reconciliation?

> "Validation asks whether a record is internally plausible: is this date real, is this rate positive, is this field populated. Reconciliation asks whether two independent systems agree about the same fact. Validation catches a fill date before an open date. Reconciliation catches the ATS saying a vacancy is filled while the billing table has no placement for it — which is the finding that actually matters commercially, because it's twelve fees potentially never invoiced. Most people build validation and stop, because validation is easy and lives inside one table. Reconciliation is where the money is, and it's harder because it requires knowing both systems."

## Q112 — Walk me through the quality framework you'd build in week one.

> "Seven or eight checks, each one a single query returning a count that must be zero, stacked into one suite that runs before every reporting cycle. On the practice data those are: filled vacancies with no placement record, placements against non-filled vacancies, impossible dates where a fill precedes an open, non-positive monetary values, duplicate submittals on the same vacancy and date, duplicate candidate emails, and ad spend with no campaign attribution. That returns 12, 9, 6, 7, 15, 40 and 42 respectively — so nothing is clean, which is normal and not an indictment of anyone. The framing I use out loud is: **constraints prevent what can be prevented; checks detect what can't.** Impossible dates shouldn't need a check, they need a constraint at write time. Cross-system disagreement can't be constrained, so it needs a check. And every non-zero line is either a fix or a documented exception — never a thing we've all quietly agreed to stop looking at."

## Q113 — You find forty duplicate candidate emails. What do you do?

> "Not deduplicate them, first. I'd find out what a duplicate means here, because the fix depends entirely on the cause. If the same person registered twice through two different channels, that's one human with two records and merging them is right — but it also means your channel attribution is double-counting, which is a bigger finding than the duplicates. If it's a shared family email address on two genuinely different candidates, merging would be a serious error. If it's a loader that reran without idempotency, the fix isn't in the data at all, it's in the pipeline. So: characterise, then decide, then prevent. And I'd flag the specific operational risk rather than the abstract one — duplicate candidate records mean you can present the same person to the same client twice, which is embarrassing in front of a customer and costs more than the data problem does."

## Q114 — How do you make a data load idempotent, and why does it matter?

> "Idempotent means running it twice produces the same result as running it once. It matters because pipelines get rerun constantly — after a failure, during a backfill, when someone clicks the button twice — and a non-idempotent load silently doubles a day's data, which then looks like a great day for the business. Two patterns. `MERGE` on a stable key, so a rerun updates rather than inserts. Or delete-and-reinsert the affected partition inside one transaction, which is often simpler and cheaper when you're reloading a whole day. I built this into the Beam pipelines at Tekkod moving MongoDB into BigQuery — idempotency was a design requirement rather than something we retrofitted, because reruns were going to happen and we knew it."

## Q115 — What's the difference between ETL and ELT, and which would you use here?

> "In ETL you transform before loading, which made sense when storage was expensive and compute was scarce, so you only kept the shaped result. In ELT you land the raw data first and transform inside the warehouse, which is the modern default because warehouse compute is cheap and elastic. The practical argument for ELT is that you keep the raw layer, so when someone changes a business definition — and they will — you can rebuild history rather than telling them it's not recoverable. With BigQuery I'd land raw, build a cleaned layer, then build the metric layer on top, and have the dashboards read only from the metric layer so nobody is quietly redefining a KPI in a workbook. My Beam work at Tekkod was closer to ETL because it was mapping documents onto a warehouse schema in flight, and I'd say the honest lesson from it is that transform-in-flight is harder to debug — when something's wrong you can't go back and look at what arrived."

## Q116 — What's a backfill and what goes wrong with them?

> "Reprocessing historical data — because you fixed a bug, added a column, or changed a definition. Three things go wrong. Without idempotency you duplicate everything you touch, which is the big one. Cost, because a backfill over two years of a partitioned table can scan the entire history and produce a bill nobody budgeted for; the mitigation is to run it partition by partition rather than as one query. And silent inconsistency, where the backfill applies new logic to old periods and now your trend has a discontinuity nobody documented — the metric changes at the boundary and everyone attributes it to the business. So I'd version the logic, note the boundary date, and put it on the chart."

## Q117 — How do you decide what to alert on?

> "The test is whether a human would do something differently in the next hour because of it. If the answer is no, it's a log entry, not an alert. Concretely I'd alert on a pipeline that feeds a customer-facing or decision-facing dashboard failing, on freshness breaching the promise the dashboard makes, and on volume anomalies beyond a threshold — a load with zero rows, or one at triple the normal size. I would not alert on individual record-level validation failures, because they're routine and constant and you'd train everyone to ignore the channel. Those go into a report someone reviews on a cadence. The failure mode I've seen most is alert fatigue: once people mute the channel, you have no monitoring at all, and you have it in the worst possible way, because everyone believes you do."

## Q118 — What's your experience with n8n?

> "I haven't used n8n itself. I've built the same class of thing in code — Apache Beam pipelines, and scheduled Python jobs on AWS with retry and failure alerting — so the concepts are familiar, and honestly the node-based approach is a shorter learning curve than what I'm used to rather than a longer one. I spent an evening in it this week to get the shape of it: a schedule trigger, an HTTP node, a filter. What are you currently automating with it?"

Two things. Actually spend the evening — forty minutes on their quickstart makes the sentence true and converts a gap into evidence of initiative. And end on the question, because it turns a weak moment into a conversation and their answer tells you whether n8n is central to the role or a preference on a list. It is listed as preferred, not required, so this is a minor gap; do not treat it like the Tableau one.

## Q119 — How do you use Git in an analytics workflow?

> "Everything that produces a number lives in version control — SQL, transformation code, the definitions. The argument I'd make is that analysis without version control has no history, and a metric with no history is a metric nobody can audit. When someone asks in six months why the March figure changed, 'I don't know' is an unacceptable answer, and it's the only available one if the query lives in a workbook. Practically: feature branches, pull requests for anything that changes a published metric definition, and a review from someone else before a definition changes, because a definition change is a bigger deal than a code change and gets treated as a smaller one. I've used Git rigorously across both Tekkod engagements and the consultancy work."

## Q120 — How do you document your work?

> "Three levels, because they have three audiences. In the code, comments that explain *why* rather than what — the what is visible. Alongside the dataset, a definition of every metric: the exact rule, the denominator, the exclusions, and the date the definition took effect. And on the dashboard itself, the limitations, in the place where someone might otherwise misread the number. That last one is the one people skip, and it's the one that prevents the most damage. I write documentation designed to outlast me at the organisation, which is a habit from consulting — if the system stops working when I'm not reachable, I didn't build a system, I built a dependency."

## Q121 — Who owns a metric definition when two teams disagree?

> "Someone has to, and the failure mode is that nobody does, which is how you get two reports with the same title and different numbers and a permanent low-grade argument. My view is that the metric layer should be owned by whoever is accountable for the number being right — usually the analytics function — with the business owner signing off on the definition. Written down, dated, versioned, and singular. The analyst's job in that argument isn't to pick a winner, it's to make the disagreement explicit: 'you're both right, you're counting different things, here are the two definitions, which one are we publishing?' Nine times out of ten the argument evaporates the moment both definitions are written next to each other. That's actually one of the questions I'd want to ask you — who owns a metric definition here today?"

## Q122 — How do you use AI tools, and how do you keep that secure?

Their job description asks for this explicitly, and almost every candidate will give a vague answer. Yours is concrete, which is the whole advantage.

> "I use Claude and ChatGPT daily — drafting and reviewing SQL, sanity-checking analysis logic, writing documentation, and as a rubber duck for debugging. The security rule I hold to is simple: **never paste real client or candidate data into a prompt.** I work with schemas, column names and synthetic examples, which is almost always enough to get the help I need, and if I need to reason about actual values I generate or anonymise them. And I treat anything it produces as a draft to verify. I've seen models produce SQL that runs perfectly and answers the wrong question — the syntax is fine, the joins are fine, and it's counting the wrong thing — so I check row counts and grain before I trust output. That's not scepticism about the tools, it's the same check I'd run on my own query."

The "never paste real data" line matters most to a company holding candidate PII, and "SQL that runs perfectly and answers the wrong question" is a sentence you cannot say without having actually used these tools on real work. Both land.

## Q123 — What are the risks of AI in analytics work specifically?

> "Three. Confident wrongness, which is the one I described — output that's syntactically perfect and semantically wrong, and it's more dangerous than a syntax error because a syntax error announces itself. Data exposure, which is a policy problem and a discipline problem rather than a technical one. And skill atrophy on the team, which is the slow one — if people accept generated SQL without being able to read it, you eventually have a codebase nobody understands and nobody can debug at three in the morning. My rule is that I don't ship anything I couldn't have written and can't explain. It makes me faster, not less accountable."

## Q124 — How would you handle candidate personal data?

> "Carefully, and with the assumption that I'm handling it wrongly until I've checked. Practically: minimise what I pull — an analysis of hire rates by English level doesn't need names or email addresses, so I don't select them, and I can't leak what I never queried. Aggregate before sharing, and be alert to small cells, because a breakdown with two people in a cell identifies them regardless of whether the name column is present. Never move personal data outside the systems it's meant to live in, which includes AI prompts, spreadsheets on a laptop, and screenshots in a chat thread. And check whether there's a retention policy, because there usually should be one and there often isn't. This is familiar ground — I've worked under beneficiary-data protection requirements in humanitarian programmes, where the consequences of a leak are more serious than commercial embarrassment, so the instincts are already there."

## Q125 — What's the first thing you'd check before trusting a new dataset?

> "The grain, then the completeness, then the lineage — in that order. Grain first: what does one row mean, because everything downstream depends on it and getting it wrong invalidates everything. Then completeness: how far back does it go, are there gaps, and does the row count per day look stable, since a step change in daily volume usually means a source system changed rather than the business changing. Then lineage: which system does this come from, what transforms it on the way, how often does it land, and when did it last land successfully. That takes about a morning per dataset and it prevents most of the mistakes people make in their first month — which is the argument for doing it instead of shipping a chart in week one."

## Q126 — How would you approach a system you've never seen before?

> "Read the schema and count things. I'd start by listing tables with row counts and date ranges, which tells you the shape of the business faster than any documentation — you can see immediately which tables are transactional, which are reference, and where the volume actually is. Then I'd pick one real entity, a single client, and trace it all the way through: lead, opportunity, client, vacancy, submittals, placement, invoice. Following one record end to end teaches you more about a data model in an hour than reading an ER diagram for a day, because it shows you where the joins actually fail and which fields are populated in practice rather than in principle. Then I'd try to reproduce a number someone already trusts. If I can't reproduce their existing headline metric, I don't understand the system yet — and that's a much better thing to discover in week one than in month three."

---

## The framing sentences

Six lines that carry this whole file. If you have these, you can rebuild any of the eighteen answers on the spot.

*"Constraints prevent what can be prevented; checks detect what can't."*

*"A job that succeeds with zero rows is worse than one that fails loudly."*

*"A dashboard is only as trustworthy as its least reliable upstream job, so freshness belongs on the dashboard."*

*"Alerts must be actionable and rare, or people stop reading them — and then you have no monitoring at all while believing you do."*

*"Twelve filled vacancies with no placement record isn't a data problem, it's potentially twelve uninvoiced fees."*

*"I never paste real client or candidate data into an AI prompt — schemas and synthetic examples get me the same help."*

---

*Next: [07 Case and live exercise](07_case_and_live_exercise.md) · Back to [question bank index](README.md) · Source: [01 §9–10 data quality and pipeline health](../01_recruiting_sales_marketing_metrics.md) · [02 §6 monitoring in BigQuery](../02_bigquery_for_analysts.md)*
