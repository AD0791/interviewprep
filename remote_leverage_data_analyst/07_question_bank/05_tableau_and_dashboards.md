# Tableau and dashboard questions

*Q91–Q108. Tableau is the first responsibility in their job description and the one thing on it you have not used. This file is about holding that honestly and well, which is a different skill from knowing Tableau.*

---

## Q91 — What's your experience with Tableau?

**The single most important answer in this bank.** It is a script, not an improvisation. Say it evenly — delivered hesitantly it sounds like an apology, delivered evenly it sounds like judgement.

> "I'll be straight with you: my dashboarding depth is in Power BI and Looker Studio rather than Tableau — I've built donor-facing and operational dashboards in both for several years. I know the concepts transfer closely, because a FIXED level-of-detail expression is what I'd write as `CALCULATE` with `ALLEXCEPT` in DAX, extracts are import mode, and live connections are DirectQuery. So when I saw Tableau was the first thing in your job description, I installed Tableau Public and spent the weekend rebuilding a recruiting-funnel dashboard in it — funnel conversion, time to fill by role family, open requisition aging, and channel economics. I can send you the link. I'm not going to tell you I'm a Tableau expert after four days, but I know exactly what I don't know yet, and given I've picked up mWater, CommCare, Kobo and Looker Studio on the job, I'd expect to be productive within two or three weeks."

Four things make it work. It names the gap before they have to, which removes their leverage over it. It proves transfer with a *specific* technical equivalence rather than a vague claim about transferable skills. It offers **evidence** — a link — instead of a promise. And it gives a realistic ramp rather than an implausible one; "two or three weeks" is believable in a way that "I'll be up to speed immediately" is not.

**Never say "I'm a fast learner."** With the link you do not need the phrase, and without the link the phrase is worthless. If you have not published the dashboard by Monday morning, change the sentence to "I've been rebuilding a recruiting-funnel dashboard in Tableau Public this weekend and I'll send you the link today" — and then actually send it. A promise with a deadline attached is still evidence; a promise without one is not.

## Q92 — What's the difference between a dimension and a measure? And between discrete and continuous?

> "Dimensions are categorical fields you slice by; measures are numeric fields that get aggregated. That's the same distinction Power BI makes, just more visible in Tableau's interface. Discrete versus continuous is a *separate* axis and that's what confuses people — discrete fields are blue and produce headers and separate panes, continuous fields are green and produce axes. A date can be either: discrete `MONTH(date)` gives you labelled columns, continuous gives you a proper time axis. You can have a continuous dimension and a discrete measure, which is why they're genuinely two different distinctions rather than one."

If someone asks what blue and green mean, they are asking exactly this. Answering it cleanly is a quick credibility win with an interviewer who is checking whether your weekend was real.

## Q93 — What does a FIXED LOD do, and how does it interact with filters?

**The most commonly asked Tableau question above beginner level.** Learn it close to verbatim.

> "A FIXED level-of-detail expression computes an aggregate at the dimensions you name, regardless of what's in the view. So `{FIXED [Client Id] : SUM([Placement Fee])}` gives you total fees per client available on any row of any visualisation, even one that isn't broken down by client. The interaction with filters is the part that gets asked: **a FIXED expression is computed before dimension filters are applied**, so filtering the view doesn't change it. That's usually exactly what you want — a denominator that stays constant while the user filters, so a percent-of-total behaves sensibly instead of silently rebasing to 100%. When you *do* want the filter to affect it, you promote that filter to a context filter, which moves it above FIXED in the order of operations."

## Q94 — What is Tableau's order of operations?

> "Extract filters, then data source filters, then context filters, then FIXED LODs, then dimension filters, then INCLUDE and EXCLUDE LODs, then measure filters, then table calculations and their filters, then reference lines and totals. Almost every 'why is my number wrong' question in Tableau traces back to that sequence, and the two consequences worth knowing are that FIXED sits above dimension filters — hence a context filter being the way to make a filter bite on a FIXED expression — and that table calculations sit right at the bottom, operating only on what has already survived every filter above them."

## Q95 — When would you use INCLUDE rather than FIXED?

> "INCLUDE computes at the view's granularity *plus* the dimensions you name, then aggregates back up — so use it when you need a calculation finer than the view is showing. The classic case is an average of per-client totals displayed at channel level: `AVG({INCLUDE [Client Id] : SUM([Placement Fee])})`. A plain `AVG` would average rows rather than clients, which is a different and usually wrong number. FIXED ignores the view entirely; INCLUDE respects it and goes one level finer. EXCLUDE is the mirror — the view's granularity minus a dimension — which is how you write 'this role family's share of the month'."

## Q96 — What's the difference between an LOD expression and a table calculation?

> "Where they're computed. **An LOD is computed by the database as part of the query; a table calculation is computed by Tableau after the query returns.** That has a hard consequence: an LOD can change granularity, and a table calculation can only operate on what's already in the view. If you need a value at a granularity the view doesn't contain, only an LOD can do it. My rule of thumb is: table calculation if the answer only needs what's in the view, LOD if it needs a granularity the view doesn't have, and a database-side calculation if it needs to be reused everywhere — because a calculation that lives in three workbooks will eventually disagree with itself."

## Q97 — Explain live versus extract, and when you'd choose each.

> "A live connection queries the source on every interaction: always current, but the source bears the load and dashboard responsiveness depends entirely on the warehouse. An extract is a compressed columnar snapshot — a `.hyper` file — held by Tableau: fast, works offline, insulates the warehouse, and stale between refreshes, which can be scheduled and can be incremental. The trade-off is identical to DirectQuery versus import mode in Power BI. The thing I'd add that's specific to your stack: against BigQuery, a live connection means **every filter click costs money**, because you're billed per byte scanned and each interaction fires a new query. A live Tableau dashboard on an unaggregated BigQuery table is a genuinely expensive object. For a business where data lands overnight, an extract refreshed each morning is almost always right — and I'd aggregate the extract to the grain the dashboard needs rather than shipping raw rows into it."

Connecting the Tableau answer back to BigQuery cost is a strong move, because it shows the two halves of their stack sitting in one head.

## Q98 — What's the difference between a join, a relationship and a blend?

> "Three ways to combine data, introduced at different points in Tableau's history. Relationships are the modern default since 2020.2 — you declare how tables relate and Tableau decides the appropriate join at query time, per worksheet, based on which fields you actually use. The reason they matter is that they avoid the duplication a physical join causes when one side has multiple matching rows, which is the fan-out problem that inflates revenue when you join placements to submittals. Joins are the physical layer and produce one flattened table, with the usual inner, left, right and full — use them when you genuinely want a flat table. Blending combines two separate data *sources* on a shared dimension, aggregating each independently before combining, and it's the fallback when the sources can't be joined at all; it's more limited because the secondary source can only contribute aggregates. If I say one sentence: I'd use relationships by default because they avoid fan-out duplication, and fall back to blending only when the data lives in genuinely separate sources."

## Q99 — What's a context filter and why would you promote a filter to context?

> "Two reasons. The correctness reason is the order of operations — context filters sit above FIXED LODs, so promoting a filter to context is how you make it actually affect a FIXED calculation, and that's usually why you reach for it. The performance reason is that a context filter creates a temporary subset that subsequent filters operate against, so on a large dataset with a very selective first filter it can speed things up. But it materialises that subset, so applying it to a filter that barely reduces anything makes things slower rather than faster. Use it deliberately, not as a habit."

## Q100 — How do you troubleshoot a slow dashboard?

> "Measure before guessing — Tableau has a Performance Recorder that shows you which queries are actually slow, and I'd use it rather than theorising. That's the same instinct as reading a query plan before touching an index, which is how I work in SQL anyway. Once I can see where the time goes, the usual causes are a handful: too many marks, because a scatter plot with two hundred thousand points is slow *and* unreadable and fixing the second problem fixes the first; a live connection where an extract would do; an extract at raw grain when the dashboard only needs a monthly summary; too many quick filters, each of which fires its own query; and 'Only relevant values' on a high-cardinality filter, which forces an extra query every time anything changes. Hiding unused fields in the data source helps too. The sentence I'd use is that I don't guess at dashboard performance, I record it and look at what's actually slow."

## Q101 — How would you map Power BI concepts onto Tableau?

| Power BI | Tableau |
|---|---|
| Power Query (M) | Data Source tab, or Tableau Prep for real ETL |
| DAX measure | Calculated field |
| `CALCULATE(SUM(x), ALLEXCEPT(...))` | `{FIXED [dim] : SUM([x])}` |
| `ALL()` to strip filters | Removing a dimension from an LOD |
| Filter context / row context | Order of operations and view granularity |
| Slicer | Filter, or a parameter |
| Relationships and star schema | Relationships (the logical layer) |
| DirectQuery | Live connection |
| Import mode | Extract (`.hyper`) |
| Bookmarks | Dashboard actions, parameter actions |
| Row-level security | User filters, or RLS on the server |
| Power BI Service | Tableau Server / Tableau Cloud |
| `.pbix` | `.twb` / `.twbx` |

> "The concepts carry over almost completely. What I'm learning is the interface and Tableau's order of operations, not the underlying model."

The `CALCULATE` + `ALLEXCEPT` ↔ `FIXED` pair is the one to have ready. It is the single most convincing sentence available to you on this subject, because it is the kind of thing you cannot say without actually understanding both tools.

## Q102 — What's the difference between Tableau Desktop, Public, Server and Cloud?

> "Desktop is the authoring tool. Public is the free version that authors the same way but can only publish to Tableau's public gallery, which is what I've been building in this week — worth flagging, because it means anything I publish is visible, so I've used synthetic data rather than anything real. Server is self-hosted for sharing and scheduling inside an organisation; Cloud is the same thing hosted by Tableau. Server and Cloud are where extract refresh schedules, permissions and row-level security live."

The parenthetical about Public being public is worth saying out loud. It demonstrates the data-handling instinct they are hiring for, in a place they were not testing for it.

## Q103 — How do you make a dashboard interactive across sheets?

> "Dashboard actions. A filter action lets a selection in one sheet filter the others — click a role family in the funnel and the aging chart follows. A highlight action emphasises rather than filters, which is better when you want to keep the context visible. A parameter action lets a click set a parameter, which can then drive calculated fields, and that's the most flexible of the three. Parameters differ from filters in that a parameter is a single value that exists independently of the data and can be used inside calculations, while a filter operates on the data directly. The design point I'd make is restraint: one well-chosen filter action usually beats five, because each one adds a way for the user to end up in a state they can't explain."

## Q104 — Walk me through the dashboard you built.

Have this ready, in this order, whether or not the link is live.

> "Four sheets on one canvas. Top left is the recruiting funnel — submittals, interviews, offers, hires — with the conversion percentage between each stage, built from the interviews table rather than the submittal status column, because status overwrites history. Top right is median time to fill by role family, which is where the eleven-day spread between Technical and Customer Support shows up. Bottom left is open requisition aging, bucketed by weeks and coloured by priority, so it reads as a work queue rather than a report. Bottom right is channel economics — spend, clients acquired, and cost per acquisition side by side, which is where cost per lead and cost per acquisition visibly disagree. There's one filter action from role family, and a freshness note on the canvas saying when the underlying data last loaded. The design principle was one question per sheet, and the four questions are: where are we losing candidates, how long does this take, what needs attention today, and what are we paying for a client."

"One question per sheet" is a good line, and the freshness note is the detail that makes an interviewer think you have shipped dashboards people actually depend on.

## Q105 — How do you design a dashboard for an executive versus an operator?

> "They're different products and the commonest dashboard failure is building one and calling it both. An executive dashboard answers 'is the business healthy?' — a small number of headline metrics, each with a comparison to something, because a number without a reference point isn't information. It should be readable in about thirty seconds and it should not be interactive in any way that requires learning. An operator dashboard answers 'what should I do this morning?' — it's a work queue, sorted by urgency, at row level, and it needs filtering and drill-down because the operator's job is to find their specific cases. Same data, opposite designs. If someone asks me for a dashboard, my first question is which of those two it is, and my second is what decision it changes."

## Q106 — What makes a bad dashboard?

> "Three things, in order of how often I see them. No stated question — a collection of charts because the data was available, which nobody can act on because it doesn't ask anything. No reference point — a number with no target, no prior period and no benchmark, so the reader can't tell whether 47% is good. And no visible freshness, so the reader can't tell whether they're looking at this morning or last Tuesday, which is how a stale dashboard silently drives a decision. I'd add a fourth that's specific to how I think: no stated limitations. If a chart excludes a population, or a cut is only supported for part of the period, that belongs on the face of the dashboard rather than in a conversation the reader wasn't in."

## Q107 — How do you decide which chart to use?

> "By the comparison the reader needs to make, not by what looks good. Change over time is a line. Comparison between categories is a bar, sorted by value rather than alphabetically, which is a free improvement people skip constantly. Part-to-whole is a stacked bar or a treemap — rarely a pie, and never a pie with more than about four slices. Relationship between two measures is a scatter. Distribution is a histogram or a box plot, and a distribution shown as an average is information destroyed. The one I'd defend specifically for your funnel is a plain horizontal bar chart with the conversion percentages between stages, rather than the tapered funnel graphic, because the tapered shape encodes the numbers in an area that people misread. The unglamorous chart is usually the right chart."

## Q108 — They ask a Tableau question you can't answer. What do you do?

> "Say so, and say what you'd do instead — in one breath, without apologising twice. 'I don't know that one yet. Here's the equivalent I'd reach for in Power BI, and here's how I'd go and find the Tableau answer.' For a role where the whole job is being trustworthy about numbers, admitting the edge of what you know is close to the right answer rather than a failure. What loses the room is inventing a plausible-sounding mechanism — because if the interviewer knows Tableau, they'll know instantly, and then everything else you said becomes suspect."

**"I don't know that one — here's how I'd find out"** is a complete, respectable answer. Rehearse saying it without flinching, because the version delivered with an apology attached sounds much worse than the version delivered flatly.

---

## If the Tableau link isn't ready by Monday

Do not pretend. The answer becomes: *"I've been rebuilding a recruiting-funnel dashboard in Tableau Public over the weekend — it's not published yet, I'll send you the link today."* Then send it that day, in the follow-up email, which turns your thank-you note into evidence rather than politeness. That is a strictly better outcome than a link you rushed, and it gives the follow-up email a reason to exist.

---

*Next: [06 Data quality, pipelines and AI](06_data_quality_pipelines_ai.md) · Back to [question bank index](README.md) · Source: [03 Tableau in five days](../03_tableau_in_five_days.md)*
