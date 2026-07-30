# Tableau in five days

*Remote Leverage — Data Analyst · interview Monday 3 August 2026. Build against `practice/csv/`, which Tableau Public reads directly.*

---

## Read this paragraph first

"Develop and maintain dashboards using Tableau" is the **first responsibility** in the job description, and Tableau does not appear anywhere on your resume. You cannot close that gap in five days and you must not pretend to.

What you can do in five days is arrive with three things: an accurate command of the concepts Tableau interviews actually test, a small dashboard you built yourself over the weekend on their kind of data, and an honest sentence about where you are. That combination beats a vague claim of familiarity every time, because the moment they ask what a FIXED level-of-detail expression does, a bluff collapses and an honest answer with a portfolio link does not.

The transfer is also genuinely large. You are an expert in Power BI. Both tools sit on the same conceptual base — a semantic layer over a warehouse, dimensions and measures, aggregation contexts, extracts versus live connections, dashboard interactivity. What changes is vocabulary and the mechanics of the interface. Section 8 is the translation table; read it and you will find you already know most of what is in this module under different names.

**Install Tableau Public today.** It is free, it opens CSVs, and everything in this module works in it. The only real limitation is that saved workbooks are published publicly — which for a practice portfolio is a feature, because you can send them a link.

---

## 1. The vocabulary, mapped from Power BI

Tableau splits every field into **dimensions** (categorical, used to slice) and **measures** (numeric, aggregated). Power BI makes the same distinction less visibly.

Fields are also **discrete** (blue) or **continuous** (green), and this is the distinction that confuses newcomers because it is *not* the same as dimension versus measure. Discrete fields produce headers and separate panes; continuous fields produce axes. A date can be either: discrete `MONTH(date)` gives you labelled columns, continuous gives you a proper time axis. You can have a continuous dimension and a discrete measure. **If someone asks what blue and green mean in Tableau, they are asking about discrete and continuous**, and answering that cleanly is a quick credibility win.

The canvas is built from **shelves** — Columns and Rows determine the structure — and the **Marks card**, which controls colour, size, label, detail, tooltip and mark type. Dropping a field on Detail changes the granularity of the view without displaying anything, which is the mechanism behind a lot of otherwise mysterious behaviour.

A **worksheet** is one visualisation. A **dashboard** assembles worksheets with layout and interactivity. A **story** sequences dashboards. Workbooks are `.twb`, or `.twbx` when packaged with the data.

---

## 2. Order of operations — the thing that gets asked

Tableau applies filters in a fixed sequence, and almost every "why is my number wrong" question in Tableau traces back to it.

```
Extract filters
  → Data source filters
    → Context filters
      → FIXED level-of-detail expressions
        → Dimension filters
          → INCLUDE / EXCLUDE level-of-detail expressions
            → Measure filters
              → Table calculations and their filters
                → Reference lines, totals, forecasts
```

The consequence worth memorising: **a FIXED expression is computed *before* dimension filters are applied**, so filtering the view does not change it. That is usually exactly what you want — a total that stays constant while the user filters, so percentages of total behave sensibly. When you *do* want the filter to affect it, you promote the filter to a **context filter**, which moves it above FIXED in the order.

That single paragraph — FIXED ignores dimension filters unless you add them to context — is the most commonly asked Tableau question above beginner level. Learn it verbatim.

---

## 3. Level-of-detail expressions

LOD expressions compute an aggregate at a granularity **different from the view**. There are three.

**`{FIXED [dim] : AGG(measure)}`** computes at the stated dimensions regardless of what is in the view.

```
// Total fees per client, available on any row of any view
{ FIXED [Client Id] : SUM([Placement Fee Usd]) }
```

**`{INCLUDE [dim] : AGG(measure)}`** computes at the view's granularity *plus* the stated dimensions, then aggregates back up. Use it when you need a finer calculation than the view shows — the classic being an average of per-client totals displayed at channel level.

```
// Average fee per client, shown by acquisition channel
AVG({ INCLUDE [Client Id] : SUM([Placement Fee Usd]) })
```

**`{EXCLUDE [dim] : AGG(measure)}`** computes at the view's granularity *minus* the stated dimensions. Use it for "percent of a coarser total" — a role family's share of the month, for instance.

```
// This role family's placements as a share of the month
SUM([Placements]) / SUM({ EXCLUDE [Role Family] : SUM([Placements]) })
```

The three canonical use cases to have ready, because they make the abstraction concrete. **Cohort analysis**: `{FIXED [Client Id] : MIN([Signup Date])}` stamps every row with the client's acquisition date so you can group by cohort. **Customer-level aggregation displayed at a coarser level**: average revenue per client, shown by channel, which a plain `AVG` would get wrong because it would average rows rather than clients. **Percent of total that survives filtering**: a FIXED total as the denominator so the percentage does not silently rebase when the user filters.

The distinction interviewers probe: **an LOD expression is computed by the database, a table calculation is computed by Tableau after the query returns.** LOD can change granularity; table calculations can only operate on what is already in the view. If you need a value at a granularity absent from the view, only an LOD can do it.

---

## 4. Table calculations

Table calculations run on the aggregated result — running totals, percent of total, rank, difference from previous, moving average. They are configured by **partitioning** and **addressing**: which fields define each group, and which direction the calculation moves along.

"Compute using → Table (across)" versus "Pane (down)" versus a specific dimension is the whole game, and the classic failure is a running total that resets in the wrong place because the addressing is wrong. When a table calc gives a strange answer, the diagnosis is almost always the compute-using setting rather than the formula.

Know the built-in shortcuts — Quick Table Calculations for running total, percent of total, rank, year-over-year — and know that `WINDOW_SUM`, `WINDOW_AVG`, `LOOKUP`, `INDEX`, `FIRST`, `LAST` and `RANK` are the underlying functions. `LOOKUP(SUM([Fees]), -1)` is the previous period, which is how you build month-over-month growth.

The rule of thumb to state: **table calculation if the answer only needs what is in the view; LOD if it needs a granularity the view does not have; database-side calculation if it needs to be reused everywhere.**

---

## 5. Data connections

**Live versus extract** is a near-certain question.

A **live connection** queries the source on every interaction. Data is always current, the source bears the load, and dashboard responsiveness depends entirely on the warehouse. Against BigQuery, that also means **every filter click costs money** — a live Tableau dashboard on an unaggregated BigQuery table is a genuinely expensive object, and connecting this back to module 02 is a strong move in the interview.

An **extract** (`.hyper`) is a compressed columnar snapshot held by Tableau. It is fast, it works offline, it insulates the warehouse — and it is stale between refreshes, which can be scheduled and can be incremental. For a small agency with data landing overnight, an extract refreshed each morning is almost always the right answer, and saying so shows you are thinking about cost and load rather than defaulting to "live is better because it is fresher".

**Relationships, joins and blending** — three ways to combine data, introduced at different points in Tableau's history, and knowing which is which reads as current knowledge.

*Relationships* (the logical layer, since 2020.2) are the modern default: you declare how tables relate and Tableau decides the appropriate join at query time, per worksheet, based on the fields you use. Crucially they **avoid the duplication that a physical join causes** when one side has multiple matching rows — the fan-out problem that inflates revenue when you join placements to submittals.

*Joins* (the physical layer) produce one flattened table, with the usual inner, left, right and full options. Use them when you genuinely want a single flat table.

*Blending* combines data from two separate data sources on a shared dimension, aggregating each independently before combining. It is the fallback when the sources cannot be joined at all, and it is more limited — the secondary source can only contribute aggregates.

If you say one sentence about this, say: *"I'd use relationships by default because they avoid the fan-out duplication you get from physical joins, and fall back to blending only when the data lives in genuinely separate sources."*

---

## 6. Performance

Extract rather than live where freshness allows. Aggregate the extract to the grain the dashboard needs instead of shipping raw rows. Reduce the number of marks — a scatter plot with two hundred thousand points is slow and unreadable, and fixing the second problem fixes the first. Prefer a small number of well-chosen filters to a screenful of quick filters, and avoid "Only relevant values" on high-cardinality filters because it forces an extra query per filter. Hide unused fields in the data source. Use the **Performance Recorder** to see which queries are slow rather than guessing.

That last sentence is the same instinct as reading a query plan before touching an index — which is language you already use naturally. Reuse it: *"I don't guess at dashboard performance, I record it and look at what's actually slow."*

---

## 7. What to build this weekend

Two evenings. The point is not a beautiful dashboard, it is being able to say "here is one I built, here is the link, here is what I'd change".

**Load the data.** In Tableau Public, connect to `practice/csv/vacancies.csv`, then add `clients.csv`, `submittals.csv` and `placements.csv` and set up **relationships** — `vacancies` to `clients` on `client_id`, `submittals` to `vacancies` on `vacancy_id`, `placements` to `vacancies` on `vacancy_id`. Deliberately use relationships rather than joins so you can talk about why.

**Sheet 1 — Funnel.** Submittals, interviews, offers, hires as a horizontal bar chart, with conversion percentages as labels.

**Sheet 2 — Time to fill by role family.** Bars sorted descending, showing the median, with the count of filled roles in the tooltip. The calculated field is `DATEDIFF('day', [Opened Date], [Filled Date])`, filtered to filled vacancies where the fill date is on or after the open date.

**Sheet 3 — Open requisition aging.** A table of currently open vacancies with client, role family and days open, sorted descending, with conditional colour above thirty days. This is your operational view.

**Sheet 4 — Acquisition by channel.** A dual-axis or side-by-side comparison of spend against fee revenue by channel, which is where Paid Social's loss becomes visible.

**Sheet 5 — Monthly trend.** Vacancies opened and filled by month, with the incomplete current month visibly marked — because after [module 01](01_recruiting_sales_marketing_metrics.md) you know that July's fill rate is censored, and showing that you handled it is the detail that will get remembered.

**Assemble a dashboard.** Put the funnel and the trend on top, aging and channel economics below. Add one filter action so that clicking a role family filters the other sheets. Add a text tile at the bottom stating the data's freshness date. Publish it and keep the link in your phone.

Then write three sentences about what you would do differently with more time. Being able to critique your own work is worth as much as the work.

**Use at least one LOD expression somewhere**, even if a simpler approach would do, so that you have used the feature you will be asked about. `{FIXED [Client Id] : MIN([Opened Date])}` to identify each client's first requisition is a natural fit.

---

## 8. Power BI to Tableau translation

| Power BI | Tableau | Note |
|---|---|---|
| Power Query (M) | Data Source tab, Tableau Prep | Prep is the separate ETL tool |
| DAX measure | Calculated field | Tableau calcs are simpler and view-context aware |
| `CALCULATE(SUM(x), ALLEXCEPT(...))` | `{FIXED [dim] : SUM([x])}` | The closest single mapping — learn this pair |
| `ALL()` to remove filters | Removing a dimension from an LOD | Different mechanism, same intent |
| Filter context / row context | Order of operations, view granularity | Tableau's model is more visual, less explicit |
| Slicer | Filter, or a parameter | Parameters are single-value and can drive calcs |
| Relationships and star schema | Relationships (logical layer) | Conceptually very close |
| DirectQuery | Live connection | Same trade-off |
| Import mode | Extract (`.hyper`) | Same trade-off |
| Bookmarks | Dashboard actions, parameter actions | |
| Row-level security | User filters, row-level security on the server | |
| Power BI Service | Tableau Server / Tableau Cloud | |
| `.pbix` | `.twb` / `.twbx` | |

The sentence this table earns you: *"The concepts carry over almost completely — a FIXED LOD is what I'd write as `CALCULATE` with `ALLEXCEPT` in DAX, an extract is import mode, a live connection is DirectQuery. What I'm learning is the interface and Tableau's order of operations, not the underlying model."* That is true, it is specific, and it is much stronger than claiming experience you do not have.

---

## 9. Ten questions to be ready for

What is the difference between a dimension and a measure, and between discrete and continuous? What does a FIXED LOD do, and how does it interact with filters? When would you use INCLUDE rather than FIXED? What is the difference between an LOD expression and a table calculation? Explain live versus extract and when you would choose each. What is a context filter and why would you promote a filter to context? What is the difference between a join, a relationship and a blend? How do you troubleshoot a slow dashboard? What is the difference between Tableau Desktop, Public, Server and Cloud? How do you make a dashboard interactive across sheets?

If you can answer those ten in two sentences each, you are in credible territory for someone who is honest about being new to the tool.

---

## 10. The honest answer, written out

> "I'll be straight with you: my dashboarding depth is in Power BI and Looker Studio rather than Tableau — I've built donor-facing and operational dashboards in both for several years. I know the concepts transfer closely, because a FIXED level-of-detail expression is what I'd write as `CALCULATE` with `ALLEXCEPT` in DAX, extracts are import mode, live connections are DirectQuery. So when I saw Tableau was the first thing in your job description, I installed Tableau Public and spent the weekend rebuilding a recruiting-funnel dashboard in it — funnel conversion, time to fill by role family, open requisition aging, and channel economics. I can send you the link. I'm not going to tell you I'm a Tableau expert after four days, but I know exactly what I don't know yet, and given I've picked up mWater, CommCare, Kobo and Looker Studio on the job, I'd expect to be productive within two or three weeks."

Three things make that answer work. It names the gap before they have to. It proves transfer with a specific technical equivalence rather than a vague claim. And it offers **evidence** — a link — instead of a promise. Practise saying it out loud until it is comfortable, because delivered hesitantly it sounds like an apology, and delivered evenly it sounds like judgement.

---

*Next: [Positioning and mock interview](04_positioning_and_mock_interview.md) · Back to [Recruiting metrics](01_recruiting_sales_marketing_metrics.md) · [BigQuery](02_bigquery_for_analysts.md) · [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md)*
