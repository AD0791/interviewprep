# Case scenarios and live exercises

*C1–C10. Ten scenarios of the kind that get posed as "suppose we told you…", each worked through the way you would talk through it. These are the questions where the answer is a method rather than a fact, and where thinking out loud is the deliverable.*

---

## How to handle a case question

Three moves, every time, in this order.

**Clarify before answering.** One question, not five. *"When you say the fill rate dropped — is that against last month, or against target?"* In a data role, asking a clarifying question before answering is a demonstrated strength rather than a hesitation, and it is the single easiest way to look senior. It also buys you ten seconds to think.

**State your method before your conclusion.** "I'd approach this in three steps" gives the interviewer a structure to follow and gives you a structure to hold. It also means that if you run out of time, they have heard the shape of a complete answer.

**Say what would change your mind.** Every case answer should end with the check you would run before acting. "I'd want to see X before recommending Y" is the difference between an analyst and someone with an opinion.

---

## C1 — Our fill rate dropped twenty percent last month. Find out why.

> "First question before I start: is that against last month, or against a target? And when you say fill rate — filled over opened in the same period, or a cohort measure?"

Then the method, and the first step is the one that wins the case.

> "My first hypothesis is that it didn't drop, and I'd rule that out before investigating anything real. Fill rate computed on recent cohorts is right-censored — the newest requisitions haven't had time to close, so the current month always looks broken. In the practice dataset I've been using, the current month shows an 11.9% fill rate against a band that otherwise sits around 50 to 60%, and nothing is wrong at all. So I'd recompute on a fixed window — share filled within thirty days of opening — and if the drop disappears, we're done and the finding is that the metric needs fixing rather than the business.
>
> If it survives that, I decompose rather than theorise. It's a ratio, so it moves for two reasons: fewer filled, or more opened. Those are completely different problems — the first is a delivery problem and the second is a sales success that looks like a delivery failure. Then I'd cut by role family, because a mix shift alone can drag the blended rate down without anything getting worse; Technical takes 28 days at the median against 17 for Customer Support, so a month heavy in Technical roles is arithmetically going to look worse. Then by client and by recruiter, looking for concentration — if one client opened forty requisitions and cancelled thirty, that's not a fill-rate story at all.
>
> Then I'd walk the funnel stage by stage to find where the drop-off actually moved, because that determines who owns it. A fall in submittal-to-interview is a sourcing or screening problem. A fall in interview-to-offer is a candidate-quality or client-expectation problem. A fall in offer acceptance is compensation or competition — and in this data the strongest candidates already decline more often, so a shift in candidate mix towards C2 would do it on its own.
>
> And before I trusted any of it I'd check pipeline health, because a partial load looks exactly like a business decline and it's much more common."

## C2 — Which marketing channel should we cut?

> "On the numbers alone, Paid Social. In the practice data it spent $134,127 and returned $80,027 in placement fees — a return on ad spend of 0.60, so it loses forty cents on the dollar. Paid Search returns 1.79 and Outbound 1.73. Its cost per acquisition is $3,625 against Paid Search's $1,362, nearly three times as much, and that's despite having a cost per lead in the same range — the whole gap is conversion.
>
> But I wouldn't recommend cutting it on that number, and here's why. Single-touch attribution credits each client to one channel, and if Paid Social is doing awareness work that converts later as Organic or Referral, the saving is illusory and you'd see it show up as a decline in the channels that look free. So what I'd actually propose is a staged reduction — cut Paid Social by half for six weeks and watch Organic and Referral volume, not just Paid Social's own numbers. If they hold, cut further. If they fall, we've learned that the attribution model was lying and that's worth more than the budget.
>
> And there's a cheaper move I'd make first, because it costs nothing. 256 leads — 6.5% of everything that came in — were never contacted at all, 199 of them from paid channels, which is roughly $24,000 of spend that produced literally nothing. Fixing lead routing recovers more than cutting a channel does, and it doesn't require anyone to give up a budget line, which means it's much easier to get agreed."

Leading with the free fix before the expensive decision is the move that reads as commercially sensible rather than merely analytical.

## C3 — The CEO wants a single number on a screen. What is it, and what goes wrong?

> "Placements per month, because in a one-time-fee model that *is* revenue. But I'd push back gently on the single number, and the pushback is the useful part of my answer. A single number is a scoreboard, and a scoreboard tells you the result after the game. What a founder actually needs is something that tells them what next month looks like while there's still time to change it.
>
> So I'd propose three tiles rather than one, and argue that three is still glanceable. Placements this month against the same month last year, which is the headline. Cost per acquisition, because volume bought at any price isn't a business. And median time to fill on the last thirty days, which is the leading indicator — it moves before placement volume does.
>
> Two things go wrong with single-number dashboards and I'd name them. Without a comparison the number is meaningless, so every tile needs a reference point. And a single number invites gaming — if placements per month is the only thing measured, the rational behaviour is to push marginal placements through, and you'll see it come back as replacements under the guarantee, which costs you the work twice for one fee."

## C4 — Design the dashboard the recruiting team would use every morning.

> "First thing: that's an operator dashboard, not an executive one, and they're different products. The question it answers is 'what do I work on today', not 'is the business healthy'. So it's a work queue, at row level, sorted by urgency, and it needs filtering — where an executive view needs no interaction at all.
>
> Four things on it. Open requisitions aged and prioritised, sorted by risk rather than by age, because a three-week-old high-priority role matters more than an eight-week-old low-priority one. Requisitions with zero submittals after some threshold, called out separately, because that's a sourcing failure and it's a different intervention from a role that has six submittals and no interviews. Interviews scheduled in the next few days, so nothing falls through. And candidates awaiting client feedback beyond an SLA, because that's the delay recruiters can't see but clients feel — and it's the one that turns into a lost placement.
>
> The design principles I'd hold to: one question per view, sorted by what needs action rather than alphabetically, a freshness stamp so nobody works from stale data, and no metric on it that doesn't have someone who can act on it this morning. If a number is interesting but not actionable, it belongs on the monthly review, not here."

## C5 — Your dashboard says 47 placements, the CRM says 51. What do you do?

> "Reproduce before defending, and I'd say that out loud because it's the whole method. Four is small enough that it's almost certainly definitional rather than a bug, and the temptation on both sides is to argue about which system is right when neither is.
>
> I'd work through it in a fixed order. Date boundaries first, since they're the most common cause — is one counting by placement creation date and the other by start date, and is one of them using a different timezone? Four placements is exactly the size of a boundary difference. Then status filters: does the CRM include cancelled or withdrawn placements that my dashboard excludes? Then grain: is one counting placement records and the other counting distinct candidates, which would differ if a candidate was placed twice. Then freshness: when did each source last load, because a four-row gap is what a pipeline that ran an hour apart looks like — and in this data the ATS loaders do fail occasionally.
>
> Then I'd find the four specific rows and look at them, rather than reasoning about it in aggregate. Four rows is a small enough set to just read, and the answer is usually obvious the moment you see them.
>
> What I'd report back isn't 'my number is right'. It's the definition difference, written down, and an agreement on which one we publish — because if we don't fix the definition, this conversation happens again next month with different numbers."

## C6 — What would you do in your first thirty days?

**Near-certain to be asked. One of the five decisive answers.**

> "I'd resist building a dashboard in week one, which I know is the opposite of what's expected, and I'd explain why rather than just doing it.
>
> The first week is understanding the grain and lineage of every table — what one row means, which source system it comes from, how it gets here, and how fresh it is. That takes about a morning per dataset and it prevents most of the mistakes people make in their first month. Alongside it, I'd trace one real client end to end: lead, opportunity, client, vacancy, submittals, placement, invoice. Following a single record all the way through teaches you more in an hour than an ER diagram does in a day.
>
> The second week I'd run a reconciliation suite before building anything, because I'd rather find the problems than have someone find them in my chart. On the practice dataset I built, that suite surfaces twelve vacancies marked filled with no placement record, which isn't a data curiosity — it's potentially twelve fees that were never invoiced. That's the kind of finding that pays for the hire in week one, and it's the conversation I'd want to have with you first rather than showing you a prettier version of a chart you already have.
>
> The third week I'd try to reproduce the numbers you already trust. If I can't reproduce your existing headline metrics, I don't understand the system yet, and that's much better to discover in week three than in month three. Anywhere I get a different answer is either a bug I've found or a definition I've misunderstood, and both are worth knowing.
>
> Only then would I build — starting with whatever you told me is the first thing you'd want this person to fix, which is the question I'd have asked in this interview."

Ending by referring back to the question you asked *them* closes a loop and makes the whole conversation feel like a working session rather than an interrogation.

## C7 — We're spending more on ads and getting fewer placements. What's happening?

> "Before diagnosing I'd want to know whether those two facts are even about the same population, because ad spend affects *client* acquisition and placements depend on *candidate* supply, and it's entirely possible to have a marketing problem and a recruiting problem that are unrelated and look like one thing.
>
> Assuming they are related, I'd separate the funnel into its stages and find where the relationship broke, because 'spend up, placements down' has at least four distinct causes with different fixes. Spend up but leads flat means rising media costs or ad fatigue — check cost per lead over time and impressions against clicks. Leads up but clients flat means a lead-quality problem or a sales capacity problem, and those are distinguishable: if untouched leads are rising, it's capacity, and in this data 6.5% were never contacted at all. Clients up but vacancies flat means you're winning clients who aren't hiring, which is a targeting problem. And vacancies up but placements flat is a candidate-supply problem, which in your model is the one I'd worry about most — if you pay the VA directly, your growth constraint is candidate quality and volume, not sales.
>
> The other thing I'd check before any of that is mix. If spend shifted towards a channel with worse conversion — and in this data Paid Social converts at 4.0% against Paid Search's 8.6% — then total spend rising while placements fall is exactly what you'd expect, with no underlying deterioration at all. That's an allocation problem, and it's a much easier one to fix."

## C8 — Here's a table you've never seen. What do you ask?

> "Four questions, in this order.
>
> What's the grain — what does one row represent? Everything else depends on that, and I'd rather ask than infer, because inferring it from column names is how people end up double-counting.
>
> Which system is it from, and what happens to it on the way here? That tells me what to trust and what to reconcile against, and it tells me who to ask when something looks wrong.
>
> How is it updated — appended, or updated in place? Because if rows get updated in place, then the historical record is being overwritten and I can't compute anything time-based from it reliably. That's the status-column problem: status columns overwrite history, event tables preserve it.
>
> And which columns can be null, and does null mean 'unknown', 'not applicable' or 'not yet'? Those three are completely different and they're all stored identically, and treating them as the same is a quiet way to get a wrong answer.
>
> Then I'd stop asking and go count things — row counts per day, distinct values per key column, null rates per column. Ten minutes of counting tells you more about a table than half an hour of questions, and it usually generates better questions."

## C9 — Live SQL: they screen-share an editor and give you a question.

The exercise is as much about behaviour as syntax. The sequence to run:

Restate the question in your own words before touching the keyboard, because about a third of the time the restatement surfaces an ambiguity and resolving it is worth more than the query. Ask about the grain of the tables involved. Say which table you are starting from and why — *"I'm going to start from the interviews table rather than the submittal status column, because status overwrites history."* Write it in stages rather than all at once, and run the intermediate steps, because a CTE you have verified is a foundation and a fifty-line query you have not run is a guess.

When it returns, sanity-check out loud: is the row count what you expected, are the percentages in a plausible range, did the join change the grain. **If something looks off, say so** — *"that's more rows than I expected, let me check whether that join fanned out"* — because catching your own error in front of them is worth more than not making it, and trying to quietly fix it while talking about something else is very visible.

If you blank on syntax, describe what you are trying to do and keep moving. *"I want the previous month's value on the same row — that's a `LAG` window function, ordered by month."* Interviewers hand you the function name and remember that you knew the shape.

## C10 — What questions do you have for us?

Always have questions; "no, I think you covered everything" is a bad answer to the last question of an interview. Pick four or five, and lead with the strongest.

**"What's the first thing you'd want this person to fix?"** — always ask this one. It gets you the real job description rather than the posted one, and it lets you respond to the actual need in your closing minute.

Then, depending on how the conversation went: What does the data stack look like end to end — what lands in BigQuery, from which systems, and what orchestrates it? Are you on on-demand or capacity pricing? Which dashboards exist today and who opens them daily? Who owns a metric definition when two teams disagree on a number? What is n8n currently automating? How is the team structured and who would I report to? What does success look like at ninety days?

Ask the practical ones too, because they determine what the offer actually means: is this contractor or employment, and how does payment work for someone based in Haiti — currency, method, frequency? Are hours fixed to a US time zone? Is equipment provided?

**Take notes on the answers.** Not for show — the follow-up email within twenty-four hours should reference something specific they said, and that only works if you wrote it down.

---

*Next: [08 Quiz, no answers](08_quiz_no_answers.md) · Back to [question bank index](README.md) · [99 during-call one pager](../99_during_call_one_pager.md)*
