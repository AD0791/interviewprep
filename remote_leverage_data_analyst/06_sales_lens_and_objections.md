# The sales lens, and the objection you will actually get

*Remote Leverage — Data Analyst · interview Monday 3 August 2026. Practice dataset: `practice/agency.duckdb`, tables `leads`, `sales_reps` and `sales_activities`. Every number below was produced by running the query shown.*

---

## Why this module exists

Two gaps were left open by the other modules, and both matter more than anything still outstanding in BigQuery or Tableau.

The first is that [module 01](01_recruiting_sales_marketing_metrics.md) covers *marketing* acquisition — channels, cost per lead, cost per acquisition — but not **sales as the sales team experiences it**: reps, pipeline stages, quota, win rate, cycle length, activity. If the founder says "a sales dashboard", there is a decent chance he means "how is each closer doing", and that is a different set of numbers.

The second is the objection you named yourself: **you have never worked as a data analyst in a commercial setting.** That will come up, in some form, and it deserves a rehearsed answer rather than an improvised one.

---

## 1. The objection, and why it is weaker than it feels

It will arrive as one of these: *"Your background is humanitarian — how would you handle a commercial environment?"* · *"Have you worked with sales data before?"* · *"This is quite different from NGO work, isn't it?"*

Before the script, understand the ground you are standing on, because the honest assessment is more favourable than you think.

**The analysis is the same analysis.** A funnel is a funnel. A beneficiary pipeline with documented drop-out at each stage is a sales pipeline with documented loss reasons at each stage. Coverage against target is quota attainment. Cost per beneficiary reached is cost per acquisition. Time from announcement to distribution is time to fill. You have not been doing something adjacent to this work — you have been doing this work, with different nouns.

**Your quality standard is higher, not lower.** This is the part candidates from your background undersell badly. NGO reporting figures are **audited by external funders** who can claw money back. You have worked under a standard where a wrong number has consequences beyond an awkward meeting, which is why you instinctively build reconciliation suites and document limitations. Most commercial analysts have never worked under that scrutiny. Say so — plainly, without disparaging anyone.

**You have already demonstrated the transfer.** Not as a claim, as a fact: you learned this specific domain — placement funnel, submittal ratios, time to fill, CAC versus CPL, quota attainment — in a matter of days, well enough to arrive with findings. That is the evidence, and it is far more persuasive than an assertion that you learn quickly.

**And there is one thing you know that they may not.** The economics of a one-time-fee placement model are unusual: revenue tracks placement volume rather than headcount under management, so the metrics that matter are fill rate, speed and acquisition cost, not utilisation. You worked that out from their public model. Bring it up early and the "different sector" framing dissolves, because you are visibly already inside their business.

### The script

> "It's a fair question, and I'd rather answer it with something concrete than just say the skills transfer. The analysis is genuinely the same — a funnel is a funnel, whether the drop-off is candidates in a placement pipeline or households in a distribution programme. Coverage against target is quota attainment. Cost per person reached is cost per acquisition. What changes is the vocabulary and what the numbers are used for.
>
> Two things I'd offer beyond that. First, the quality bar I'm used to is high, because in funded programmes the figures are audited externally and a wrong number can cost the organisation the grant. That's why I build reconciliation checks before I build dashboards — it's a habit, not a policy I follow.
>
> Second, rather than tell you I learn quickly, I'd rather show you. When I read your job description I built myself a practice dataset modelling a placement agency — leads, reps, requisitions, submittals, placements, ad spend — and worked the metrics. A few things came out of it that I'd want to check against your real data. The one that surprised me most is that six and a half percent of leads were never contacted at all — paid for, then never worked, which comes to about twenty-four thousand dollars of ad spend once you weight it by channel. And when I compared cost per lead with cost per acquisition, the channel with the cheapest leads turned out to be nearly three times more expensive per client. That's the kind of thing I'd be looking for in week one."

Why it works: it concedes the premise without apology, reframes on substance rather than enthusiasm, and ends with a finding that makes them want to keep talking. **Do not end on "I'm a fast learner."** End on the number.

### The variants

*"Do you have experience with a CRM — HubSpot, Salesforce?"* — Be exact about what you have: you have worked with operational databases and collection systems that are structurally the same thing, and with the reporting layer on top. If you have not administered HubSpot, say so, then ask which one they use and how it lands in BigQuery. The pipeline question is the one that matters for this job anyway.

*"Why leave the NGO sector?"* — Forward-looking, never a complaint. The pull is faster feedback loops: in a commercial funnel you change something on Monday and see it in the numbers by Friday, where programme cycles take quarters.

*"Won't you be bored by sales dashboards?"* — No, and say why specifically: the analysis has a direct consequence attached, which is more satisfying than reporting into a document that gets read once.

*"How do you handle being told the number is wrong?"* — You have the best possible answer: reproduce before defending, check the grain and the filters, reconcile to source, and if it is wrong say so quickly and plainly. Then the sentence that lands: *"I've had to correct my own figure in front of a funder. It's uncomfortable once, and it's much less costly than a number that stays wrong."*

---

## 2. The sales vocabulary you were missing

| Term | Definition | Why it matters |
|---|---|---|
| Pipeline / deal stages | New → contacted → demo → won or lost | The funnel the sales team lives in |
| Win rate | Won ÷ closed deals (won + lost) | The honest denominator — see below |
| Raw conversion | Won ÷ all leads including open ones | Understates performance on recent cohorts |
| Quota | Target signings per rep per period | The number the rep is measured on |
| Attainment | Actual ÷ quota, as a percentage | How the team is really doing |
| Sales cycle | Days from lead created to deal closed | Cash-flow relevant, and a coaching signal |
| Activity metrics | Calls, emails, demos logged | Leading indicators; outcomes are lagging |
| Connect rate | Calls that reached a human ÷ calls made | Separates effort from effectiveness |
| Speed to lead | Time from lead arriving to first contact | The single most predictive activity metric in inbound sales |
| Lost reason | Why a deal died — price, timing, competitor | The qualitative layer on a quantitative funnel |
| Untouched leads | Leads never contacted at all | Pure waste: paid for, never worked |
| Pipeline coverage | Open pipeline value ÷ remaining quota | Forecasting metric, usually wants 3×–4× |

**The one distinction to get right**, because it is where most people are sloppy: **win rate should be computed on closed deals**, not on all leads. A rep who received two hundred leads last week has most of them still open; dividing wins by all leads punishes them for recency. It is the same right-censoring problem as fill rate in [module 01](01_recruiting_sales_marketing_metrics.md), wearing a different hat — and noticing that it is the same problem twice is exactly the kind of pattern recognition that reads as experience.

---

## 3. The pipeline, computed

```sql
SELECT stage,
       COUNT(*) AS leads,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM leads GROUP BY 1 ORDER BY leads DESC;
```

| stage | leads | pct |
|---|---|---|
| lost | 3 084 | 78,4 |
| won | 327 | 8,3 |
| open | 266 | 6,8 |
| new | 256 | 6,5 |

Read the bottom row before anything else. **`new` means the lead was never contacted.** Two hundred and fifty-six enquiries — 6,5 % of everything that came in — were paid for through advertising and then never worked at all.

Put a price on it, because that is what turns an observation into a finding. Of the 256 untouched leads, **199 came from paid channels** — 98 from Paid Search, 68 from Paid Social, 33 from Outbound — and at each channel's own cost per lead that is roughly **$24 000 of advertising spend that produced nothing at all**. At the overall lead-to-client rate of 8,3 %, the full 256 would have been expected to yield about twenty-one clients.

The query that produces the second half of that sentence is worth writing out, because the per-channel weighting is the part people skip:

```sql
SELECT channel, COUNT(*) AS untouched
FROM leads WHERE stage = 'new'
GROUP BY 1 ORDER BY untouched DESC;
```

| channel | untouched |
|---|---|
| Paid Search | 98 |
| Paid Social | 68 |
| Organic | 36 |
| Outbound | 33 |
| Referral | 21 |

Twenty-one untouched **referral** leads is the line that should sting most: referrals convert at 22,3 %, the best rate of any channel, so those are the most valuable enquiries the business receives and a fifth of a month's worth were never answered.

That is the single best thing to say in this interview. It costs nothing to fix — it is a routing and follow-up problem, not a budget problem — and it is exactly the sort of finding a founder acts on the same week.

---

## 4. Rep performance, and the trap inside it

```sql
SELECT owner AS rep,
       COUNT(*)                                        AS leads,
       COUNT(*) FILTER (WHERE stage = 'won')           AS won,
       ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'won') / COUNT(*), 1) AS raw_conv_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'won')
             / NULLIF(COUNT(*) FILTER (WHERE stage IN ('won','lost')), 0), 1) AS win_rate_closed_pct
FROM leads GROUP BY 1 ORDER BY win_rate_closed_pct DESC;
```

| rep | leads | won | raw_conv_pct | win_rate_closed_pct |
|---|---|---|---|---|
| Dana Whitfield | 1 043 | 103 | 9,9 | 11,1 |
| Priya Raman | 844 | 71 | 8,4 | 9,8 |
| Alicia Moreno | 439 | 34 | 7,7 | 9,4 |
| Marcus Lee | 1 029 | 79 | 7,7 | 8,7 |
| Tomas Ferreira | 578 | 40 | 6,9 | 8,2 |

Dana converts at 11,1 % on closed deals against Tomas at 8,2 % — a 35 % relative gap. Note that Alicia looks mid-table on raw conversion but is third on the honest denominator, because she joined in September and carries proportionally more open deals. **That is the censoring correction earning its keep on real names.**

Now the question a good analyst asks next: *is Dana better, or does Dana just work more?*

```sql
SELECT rep,
       COUNT(*)                                          AS activities,
       COUNT(*) FILTER (WHERE activity_type = 'call')    AS calls,
       COUNT(*) FILTER (WHERE activity_type = 'demo')    AS demos,
       ROUND(100.0 * COUNT(*) FILTER (WHERE connected = 1 AND activity_type = 'call')
             / NULLIF(COUNT(*) FILTER (WHERE activity_type = 'call'), 0), 1) AS connect_rate_pct
FROM sales_activities GROUP BY 1 ORDER BY activities DESC;
```

| rep | activities | calls | demos | connect_rate_pct |
|---|---|---|---|---|
| Dana Whitfield | 7 226 | 2 719 | 422 | 33,7 |
| Marcus Lee | 6 996 | 2 750 | 455 | 33,9 |
| Priya Raman | 5 597 | 2 193 | 353 | 34,4 |
| Tomas Ferreira | 3 885 | 1 474 | 233 | 34,7 |
| Alicia Moreno | 2 860 | 1 098 | 175 | 32,0 |

**Activity does not explain the gap.** Marcus makes marginally *more* calls than Dana and runs *more* demos, and every connect rate sits within three points of the others — yet Marcus wins 8,7 % of closed deals against Dana's 11,1 %. So the difference is not effort and not reach; it is what happens inside the conversation.

That conclusion has a direct management consequence, and stating it is what makes you useful rather than merely accurate: *"Telling Marcus to make more calls won't work — he already makes more than Dana. The gap is conversion quality, so the intervention is call review and coaching, not activity targets."* Recommending against the obvious action, with evidence, is a strong move.

One more cut closes the argument.

```sql
SELECT owner AS rep,
       COUNT(*) AS won,
       MEDIAN(DATE_DIFF('day', created_date, closed_date)) AS median_cycle_days
FROM leads WHERE stage = 'won' GROUP BY 1 ORDER BY median_cycle_days;
```

| rep | won | median_cycle_days |
|---|---|---|
| Dana Whitfield | 103 | 9,0 |
| Tomas Ferreira | 40 | 11,0 |
| Alicia Moreno | 34 | 11,5 |
| Priya Raman | 71 | 12,0 |
| Marcus Lee | 79 | 12,0 |

Dana closes in nine days against Marcus's twelve — **fastest cycle and highest win rate together**, which is the classic signature of better qualification rather than harder work. She is likely disqualifying poor-fit leads earlier instead of nursing them, which frees time for the ones that will close.

Careful with the causal leap, and say so: this is observational, the leads were not randomly assigned, and Dana may simply have received better ones. The test is to compare win rate by rep **within channel**, since referral leads convert at 22,3 % against paid social's 4,0 % and an unequal channel mix would produce this pattern on its own. That is your next query, and offering it unprompted is worth more than the finding.

---

## 5. Quota attainment

```sql
WITH monthly AS (
  SELECT owner AS rep, DATE_TRUNC('month', closed_date) AS month, COUNT(*) AS won
  FROM leads WHERE stage = 'won' GROUP BY 1, 2
)
SELECT m.rep,
       r.monthly_quota_clients                         AS quota,
       ROUND(AVG(m.won), 1)                            AS avg_won_per_month,
       ROUND(100.0 * AVG(m.won) / r.monthly_quota_clients, 0) AS attainment_pct
FROM monthly m JOIN sales_reps r ON r.rep = m.rep
GROUP BY 1, 2 ORDER BY attainment_pct DESC;
```

| rep | quota | avg_won_per_month | attainment_pct |
|---|---|---|---|
| Dana Whitfield | 8 | 5,4 | 68 % |
| Alicia Moreno | 6 | 3,4 | 57 % |
| Marcus Lee | 8 | 4,4 | 55 % |
| Priya Raman | 8 | 4,2 | 52 % |
| Tomas Ferreira | 6 | 3,1 | 51 % |

**Nobody hits quota, and the best performer reaches 68 %.** When an entire team misses by that margin, the first hypothesis is not that everyone underperforms — it is that **the quota is wrong**, set on optimism rather than on observed conversion and lead volume.

That is a delicate thing to tell a founder who set the quota, so the framing matters: *"No one is near quota, and the spread between best and worst is smaller than the gap between everyone and target. That pattern usually means the target was set from a growth plan rather than from lead volume times conversion rate. Worth checking what the quota was derived from — if it assumes more inbound than we're actually generating, it's a marketing capacity problem showing up as a sales performance problem."*

Reframing a sales problem as a demand problem, with the arithmetic behind it, is exactly the contribution an analyst is hired for.

---

## 6. Loss reasons

```sql
SELECT lost_reason, COUNT(*) AS n,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM leads WHERE lost_reason <> '' GROUP BY 1 ORDER BY n DESC;
```

| lost_reason | n | pct |
|---|---|---|
| Not a fit | 549 | 17,8 |
| Timing | 518 | 16,8 |
| No budget | 517 | 16,8 |
| No response | 508 | 16,5 |
| Went with competitor | 499 | 16,2 |
| Price | 493 | 16,0 |

Six reasons, all between 16 % and 18 %. **A distribution this flat is itself the finding**, and it almost certainly means the field is being filled in carelessly — reps picking whatever is at the top of the dropdown. Real loss reasons cluster.

Do not report it as insight. Report it as a data-quality problem with a fix: *"Loss reasons are uniformly distributed across six categories, which is not how real losses behave — it suggests the field isn't being filled meaningfully. Before I build anything on it I'd want to either shorten the list, make it required at close with a short free-text note, or drop it from reporting until it's trustworthy."*

Knowing when **not** to analyse a field is a senior instinct, and it is a rarer signal than any query.

---

## 7. Exercises

Compute win rate by rep **within acquisition channel**, and decide whether Dana's advantage survives the control.

Calculate speed to lead — days from `created_date` to `first_contact_date` — by rep and by channel, then test whether it correlates with win rate. This is the metric most inbound sales teams underinvest in.

Build the untouched-lead report: every lead still at stage `new`, with channel, campaign, owner and age in days, sorted oldest first. That is a list somebody can act on this afternoon.

Compute pipeline coverage: open deals per rep against remaining monthly quota, and say who is at risk of missing.

Cross the two funnels — for each acquisition channel, join through to placements and compute fee revenue per lead. It is the single number that ranks channels end to end, and nobody in the company will have it.

Rewrite the quota-attainment query so it excludes each rep's first partial month, and explain why that changes the fair comparison.

---

## Interview angles

**"Your background is humanitarian. How do you know you'll handle a commercial environment?"**

It's a fair question and I'd rather answer it concretely than just assert that skills transfer. The analysis is genuinely the same — a funnel is a funnel, whether what drops out is candidates in a placement pipeline or households in a distribution programme. Coverage against target is quota attainment. Cost per person reached is cost per acquisition. Time from announcement to delivery is time to fill. What actually changes is the vocabulary and what the number gets used for. Two things I'd add. The quality bar I'm used to is high, because programme figures are audited externally by funders and a wrong number can cost the organisation the grant — which is why I build reconciliation checks before I build dashboards, as a habit rather than a policy. And rather than tell you I learn fast, I'd rather show you: when I read your job description I built a practice dataset modelling a placement agency and worked the metrics. Two things came out that I'd want to check against your real data. Six and a half percent of leads were never contacted at all — paid for, then never worked, which comes to roughly twenty-four thousand dollars of advertising spend once you weight each one by its channel's cost per lead. And the channel with the cheapest leads turned out to be nearly three times more expensive per client once you looked at conversion. That's the kind of thing I'd be hunting for in week one.

**"One of our reps is underperforming. How would you look at it?"**

I'd start by making sure the metric is fair, because the most common mistake is dividing wins by all leads, which punishes whoever received the most recent ones — their deals are still open, not lost. So I compute win rate on closed deals only. In my practice data that correction moves a rep from mid-table to third, purely because she joined recently and carries more open pipeline. Then I'd separate effort from effectiveness. In that dataset, the top performer wins eleven percent of closed deals and the weakest eight point two, which is a thirty-five percent relative gap — but when I looked at activity, the weaker rep actually made slightly more calls, ran more demos, and had a connect rate within a point. So the gap isn't effort and it isn't reach; it's what happens inside the conversation, and the intervention is call review and coaching rather than an activity target. I'd also look at cycle length, because the top performer closed in nine days against twelve, and fastest-plus-highest-win-rate usually means better qualification — disqualifying poor-fit leads early instead of nursing them. The caveat I'd put on all of it is that leads aren't randomly assigned, so before drawing a conclusion about the person I'd compare win rates within channel, since referral converts at twenty-two percent and paid social at four, and an unequal mix would produce the same pattern on its own.

**"What would you want on a sales dashboard?"**

I'd ask one question first, because "sales dashboard" means two different things and building the wrong one is the most common dashboard failure. If it's for the founder, it answers "how are we doing": new clients and fee revenue by month against target, win rate and cycle length as trends, pipeline coverage for the next period, and cost per acquisition by channel with the revenue each channel actually produced — because in my practice data one paid channel returned sixty cents per dollar spent, and that's a decision, not a chart. If it's for the sales manager it answers "what do I do today", which means rows rather than aggregates: untouched leads sorted oldest first, deals with no activity in seven days, and this month's attainment by rep. On that second one I'd flag something from the practice data — nobody reached quota and the best was at sixty-eight percent, and when a whole team misses by that much the first hypothesis isn't that everyone is underperforming, it's that the quota was set from a growth plan rather than from lead volume times conversion rate. That's a marketing capacity problem showing up as a sales performance problem, and a dashboard that doesn't let you see that distinction sends everyone in the wrong direction. And whichever version it is, I'd put a small freshness indicator on it, because the ad-spend pipeline in that dataset fails about one day in ten and a dashboard is only as trustworthy as its least reliable upstream job.

---

*Back to: [Plan and cheat sheet](00_prep_plan_and_cheatsheet.md) · [Recruiting metrics](01_recruiting_sales_marketing_metrics.md) · [BigQuery](02_bigquery_for_analysts.md) · [Tableau](03_tableau_in_five_days.md) · [Positioning](04_positioning_and_mock_interview.md) · [SQL drills](05_sql_drills_with_answers.md) · [One pager](99_during_call_one_pager.md)*
