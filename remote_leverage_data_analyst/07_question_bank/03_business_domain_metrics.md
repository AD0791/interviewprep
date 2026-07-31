# Business domain and metrics questions

*Q43–Q62. Their vocabulary, spoken back at them. Every figure quoted here was re-executed against `../practice/agency.duckdb` — prefix it with "in the dataset I've been practising on" every single time.*

---

## Q43 — What metrics would you track for a business like ours?

> "I'd derive them from your pricing model rather than listing generic KPIs, because a one-time flat fee changes what matters. Since you're paid per placement and not on ongoing headcount, revenue tracks placement volume, so the metrics that matter are the ones that govern how many requisitions you fill and what each one costs to fill. I'd group them in three. On acquisition: leads by channel, lead-to-client conversion, cost per acquisition rather than cost per lead, and channel return on ad spend. On the recruiting funnel: submittal-to-interview, interview-to-offer, offer acceptance, fill rate, and time to fill split by role family — plus time to first submittal, because that's the one the client actually feels. And on delivery, since you carry a placement guarantee: replacement rate, because a failed placement is the work done twice for one fee, which makes it a direct margin hit rather than a service issue. The one I'd add that people forget is candidate supply, since if you pay the VA directly then your growth constraint is candidate quality and volume, not sales capacity."

That last observation is the differentiator. Anyone can list funnel metrics; deriving the constraint from the business model is what makes the answer sound like it came from someone who thought about *their* company.

## Q44 — What's the difference between a lead, an opportunity and a client?

> "A lead is an enquiry — someone who's raised their hand, from an ad, a referral or outbound. An opportunity is a lead that's been qualified: there's a real need, a budget and someone who can decide, so it's worth a rep's time. A client is a closed-won opportunity that's actually signed. The distinction that matters analytically is that they're different grains, and the classic mistake is computing a conversion rate across two of them without saying which denominator you used. In the dataset I've been practising on the overall lead-to-client rate is 8.3%, but if you compute win rate on *closed* deals only — excluding the ones still open — the reps sit between 8.2% and 11.1%. Same reps, different number, because the denominator changed. Whenever anyone quotes a conversion rate at me, my first question is what's in the bottom half."

## Q45 — How would you calculate our conversion funnel?

> "From events, not from status columns — and that's the single most important thing I'd say about it. A status column records where something *is now*, so it overwrites its own history. In the practice dataset, a submittal that got to interview and was then rejected shows 'rejected', and the interview has vanished from the record. Build the funnel off that column and you'd report an 11% submittal-to-interview rate and a 100% interview-to-offer rate, both nonsense. Computing it from the interviews table instead — one row per interview scheduled, which is an event and can't be overwritten — gives 3,918 submittals, 1,835 interviews scheduled, 1,719 completed, 482 offers and 362 hires. So 46.8% submittal-to-interview, 28.0% interview-to-offer, and 75.1% offer acceptance. Status columns overwrite history; event tables preserve it."

## Q46 — What is fill rate, and what's wrong with measuring it monthly?

> "Fill rate is the share of requisitions that get filled. In the practice data it's 49.4% filled, 20.2% still open, 21.6% cancelled and 8.9% on hold. What's wrong with trending it by month is right-censoring. The most recent cohort of vacancies is younger than the median time to fill, so most of them simply haven't had time to close yet — in the practice data July shows an 11.9% fill rate against a band that otherwise sits around 50 to 60%, and nothing is wrong at all. A dashboard that plots that without handling it will trigger a panic meeting every single month. Three ways to fix it: exclude cohorts younger than your ninetieth-percentile time to fill; report a fixed-window rate like 'share filled within thirty days of opening', which is comparable across cohorts by construction and holds between 42% and 51% for every cohort old enough to have completed the window; or plot the incomplete cohort greyed out and labelled. I'd usually do the fixed window on the trend and the greying on the operational view."

**Bring this one unprompted if it fits.** The sentence is: *"I'd never trend fill rate on the current month without handling right-censoring, because the newest cohort always looks broken."*

## Q47 — What's the difference between cost per lead and customer acquisition cost, and which would you optimise for?

**One of the five decisive questions.** Nail it.

> "Cost per lead is spend divided by leads generated. Customer acquisition cost is spend divided by *clients acquired*. The difference is the conversion rate in between, and it can reverse the ranking of your channels entirely. In the dataset I've been practising on, Outbound has the cheapest leads at $83.78 and Paid Social the most expensive at $146.27 — a 75% gap that would make Outbound look like the obvious place to spend. But Paid Social converts at 4.0% against Paid Search's 8.6%, so Paid Social's acquisition cost is $3,625 a client against Paid Search's $1,362, nearly three times as much. Optimising for cost per lead buys you cheap leads that never become clients. I optimise for CAC, and the line I'd use is that cheap leads that don't convert are expensive. Ideally you go one step further and compare CAC to what a client is actually worth, which in your model is the flat fee times how many requisitions they open over their life."

## Q48 — What is ROAS and what does it tell you that CAC doesn't?

> "Return on ad spend is revenue divided by spend, so it puts the two halves in the same unit and tells you whether a channel pays for itself, where CAC only tells you what it costs. In the practice data, Paid Search spent $181,124 and returned $325,109 in placement fees, a ROAS of 1.79. Paid Social spent $134,127 and returned $80,027 — a ROAS of 0.60, which means the channel is losing sixty cents on the dollar. That's the finding, but I'd be careful with the recommendation, and I'd say so. A single-touch attribution model credits the client to one channel, so if Paid Social is doing awareness work that converts later through Organic or Referral, cutting it wouldn't produce the saving the arithmetic promises. What I'd actually propose is a staged reduction with the other channels watched, rather than switching it off on the strength of one number."

## Q49 — What's the most valuable channel in that data, and why is it easy to miss?

> "Referral, and it's easy to miss because it has no spend attached so it doesn't appear in any efficiency ranking that divides by cost. In the practice data referrals convert at 22.3% lead-to-client — about two and a half times Paid Search — at zero recorded spend, and they produced $198,434 in fees. The thing that makes it a finding rather than an observation is that twenty-one referral leads were never contacted at all. Those are the most valuable enquiries the business receives, and a fifth of a month's worth went unanswered. That costs nothing to fix — it's routing and follow-up, not budget — which is why it's the kind of thing a founder acts on the same week."

## Q50 — Suppose fill rate dropped twenty percent last month. How would you investigate?

> "My first hypothesis is that it didn't, and I'd rule that out before anything else. Right-censoring produces exactly this signature every month, so I'd recompute on a fixed window — share filled within thirty days of opening — and if the drop disappears, the drop wasn't real. If it survives that, I'd decompose rather than theorise. Fill rate is a ratio, so it moves for two reasons: the numerator fell or the denominator rose. Did we fill fewer, or did we open more? Then I'd cut by role family, because a shift in mix towards Technical roles alone would drag the blended rate down without anything getting worse — Technical takes 28 days at the median against 17 for Customer Support. Then by client and by recruiter, looking for concentration. Then I'd walk the funnel stage by stage to find where the drop-off moved, because a fall in submittal-to-interview means a sourcing or screening problem, while a fall in offer acceptance means a compensation or competition problem, and those have completely different owners. And before I trusted any of it, I'd check the pipeline health — in this data the ATS loaders fail occasionally, and a partial load looks exactly like a business decline."

The structure to remember, because it works on any metric-drop question: **is it real, is it mix, is it concentrated, where in the funnel, and is the data even complete.**

## Q51 — What is time to fill, and is it the right metric?

> "Time to fill is the days between a requisition opening and it being filled, and you should report the median alongside the mean, because the distribution has a long right tail and a handful of four-month roles drag the average up to describe nobody's actual experience. In the practice data the median runs from 17 days for Customer Support to 28 for Technical — an eleven-day spread that's an operational fact with a commercial consequence, since you either start sourcing technical candidates before the requisition opens or you set the client's expectation at four weeks instead of two. But it's not the metric the client feels. What a client experiences is the wait until the first candidate lands in their inbox, which is time to first submittal, and that's 5 days for Technical and 2 for Customer Support. Time to fill is your operational metric; time to first submittal is the client-experience metric, and I'd have both on the dashboard."

## Q52 — What is vacancy aging and what would you do with it?

> "Aging buckets open requisitions by how long they've been open — under a week, one to two weeks, two to four, over four. It's the operational view rather than the analytical one: fill rate tells you how you did last quarter, aging tells a recruiter what to work on this morning. The design point is that an aging report should be sorted by risk rather than by age, because an eight-week-old low-priority role matters less than a three-week-old high-priority one that's about to breach a client expectation. I'd combine age with priority and with whether any submittal has been made yet, since a requisition with zero submittals after two weeks is a sourcing failure and one with six submittals and no interviews is a screening or client-responsiveness failure. Same age, completely different intervention."

## Q53 — Which stage of the funnel would you fix first?

> "I'd fix whichever stage has the largest absolute loss with a plausible intervention, not the lowest percentage. In the practice data, submittal-to-interview is 46.8% — so roughly two thousand candidate submissions never produce an interview, which is by far the biggest absolute leak and it's also the stage you control most, since it's about who you're putting forward. Interview-to-offer at 28% is lower as a percentage but the absolute numbers are smaller. And offer acceptance at 75.1% is healthy, so a percentage point there is worth less than a percentage point earlier. The general principle is that I'd rather improve a big stage slightly than a small stage dramatically, and I'd want to know which stages we can actually influence before recommending anything."

## Q54 — What is your English-level finding, and how confident are you in it?

> "In the dataset I've been practising on, English level is the strongest single driver of placement success. Hire rate goes from 2.9% at B1 to 7.9% at B2 to 13.4% at C1, where it flattens — so a C1 candidate is more than four times likelier to be hired than a B1. That's not a curiosity, it's your value proposition expressed as a number, and it converts into a recommendation with a dollar sign: every B1 submittal consumes recruiter time and client goodwill for almost no return, so either raise the screening floor to B2 or move English assessment earlier in sourcing. Now the confidence part, and I'd say this out loud rather than wait to be challenged: this is association, not causation. English level is probably correlated with years of experience, with role family, and with which recruiter handled the file, so before acting on it I'd check whether the effect holds within role family and seniority — because it could partly be a proxy. And there's a twist that makes it more interesting: the variable reverses at the offer stage. C2 candidates accept only 63.2% of offers against B2's 78.9%, almost certainly because the strongest candidates hold competing offers. So the strongest candidates are likeliest to be hired and likeliest to walk, which means speed matters most exactly where you're most tempted to deliberate."

The self-imposed caveat is worth more than the finding. Volunteering the limitation before being asked is the clearest available signal of an analyst rather than a chart-builder.

## Q55 — What is churn, and does it even apply to this business?

> "Less than you'd expect, and noticing that is the point. On a subscription model churn is the central metric because revenue is recurring. On a one-time flat fee it isn't, because there's no recurring revenue to lose — a client who never comes back hasn't churned, they've simply finished. What replaces it is repeat rate: what share of clients open a second requisition. In the practice data 58.7% do, which makes repeat business a majority of volume and means client satisfaction shows up as a second requisition rather than as a retained subscription. The related metric that does bite is replacement rate under the placement guarantee, because a failed placement means doing the work twice for one fee. If I were building your metric set, repeat rate and replacement rate would sit where churn sits in a SaaS dashboard."

## Q56 — What's the difference between a win rate and a conversion rate?

> "Mostly the denominator, and the difference is where people mislead themselves. Conversion rate typically means won divided by *all* leads, including ones still open. Win rate usually means won divided by *closed* deals — won plus lost — which excludes anything still in play. The closed denominator is the fairer comparison between reps, and in the practice data it changes the ranking: Alicia Moreno looks mid-table on raw conversion at 7.7%, but she's third on win rate at 9.4%, because she joined later and carries proportionally more open deals. That's censoring again, showing up on real names. Whenever I'm handed a conversion number I ask what's in the denominator, because it's the fastest way to find out whether a comparison is fair."

## Q57 — Rep A converts at 11.1% and Rep B at 8.7%. What do you conclude?

> "Not much yet, and that's the answer. The first question is whether A is better or just works more, so I'd look at activity. In the practice data the answer is that activity does *not* explain it — Marcus makes marginally more calls than Dana and runs more demos, and every rep's connect rate sits within three points of the others, yet Dana wins 11.1% of closed deals against Marcus's 8.7%. So it isn't effort and it isn't reach, it's what happens inside the conversation. That has a direct management consequence worth stating: telling Marcus to make more calls won't work, because he already makes more than Dana. The intervention is call review and coaching, not activity targets. One more cut closes the argument — Dana also has the shortest sales cycle, nine days against Marcus's twelve, and fastest cycle plus highest win rate together is the signature of better qualification rather than harder work. But I'd flag the confound before recommending anything: leads weren't randomly assigned, and referral leads convert at 22.3% against paid social's 4.0%, so an unequal channel mix would produce this exact pattern on its own. The test is win rate by rep *within* channel, and offering that unprompted is worth more than the finding."

Recommending *against* the obvious action, with evidence, is a strong move. Interviewers notice it.

## Q58 — Nobody on the sales team hits quota. What does that tell you?

> "That the quota is probably wrong, and that's the more useful hypothesis than everyone underperforming. In the practice data the best rep reaches 68% of quota and the worst 51% — so the spread between best and worst is smaller than the gap between everyone and target. When an entire team misses by that margin in the same direction, the target usually came from a growth plan rather than from observed lead volume times conversion rate. That's a delicate thing to say to whoever set the quota, so the framing matters: 'no one is near quota, and the spread between reps is smaller than the gap between everyone and target — that pattern usually means the number was derived from a plan rather than from capacity. Worth checking what it was based on, because if it assumes more inbound than marketing is generating, it's a demand problem showing up as a sales performance problem.' Reframing a sales problem as a demand problem with the arithmetic behind it is exactly what an analyst is for."

## Q59 — What would you do about leads that were never contacted?

> "In the practice data 256 leads — 6.5% of everything that came in — sit at stage 'new', which means nobody ever worked them. The first move is to price it rather than report it, because 'six and a half percent' is a statistic and a dollar figure is a finding. Of those 256, 199 came from paid channels — 98 Paid Search, 68 Paid Social, 33 Outbound — and at each channel's own cost per lead that's roughly $24,000 of advertising spend that produced nothing at all. At the overall 8.3% lead-to-client rate, the full 256 would have been expected to yield about twenty-one clients. And 21 of the untouched ones are referrals, which convert at 22.3% — the most valuable enquiries the business gets, unanswered. The reason I'd lead with this in week one is that it costs nothing to fix. It's a routing and follow-up problem, not a budget problem, and the intervention is an SLA on first contact plus an alert when a lead ages past it."

## Q60 — If you could only track one number for this business, what would it be?

> "Placements per month, because in a one-time-fee model that *is* revenue. But I'd say straight away that a single number is a scoreboard and not a management tool, so I'd want two supporting ones sitting next to it. Cost per acquisition, because placements bought at any price aren't a business. And time to fill, because it's the leading indicator — it moves before placement volume does, so it tells you what next month looks like while there's still time to act. One headline number, one efficiency number, one leading indicator."

## Q61 — How would you segment the client base?

> "By value and by behaviour rather than by firmographics alone, because industry and company size are easy to segment on and rarely actionable. The cut I'd start with is requisition volume — how many roles a client opens over their life — because in a flat-fee model that's the whole of client value, and 58.7% opening a second requisition means the repeat segment is where the money is. Then by role family, because a client hiring Technical roles has a 28-day median time to fill and one hiring Customer Support has 17, so they're different operational propositions and possibly should be different commercial ones. And by acquisition channel, to check whether referred clients behave differently once they're in — if referrals both convert better *and* open more requisitions, the referral programme is worth more than the acquisition numbers alone suggest."

## Q62 — What's a cohort, and where would you use one here?

> "A cohort is a group defined by when something happened to them — clients acquired in March, vacancies opened in June — that you then follow forward through time. It's the right tool whenever a metric depends on elapsed time, because a calendar-period average mixes groups that have had different amounts of time to mature and produces a number that describes nobody. The two uses here are the obvious ones. Vacancy cohorts by opening month, tracked to fill, which is how you handle the censoring problem properly rather than by exclusion — you can see that June's cohort is at 54% and still climbing while March's has plateaued. And client cohorts by signup month, tracked on cumulative requisitions, which tells you whether clients acquired recently are opening as many roles as clients acquired a year ago. If the recent cohorts are flatter, either the product changed or the acquisition channels are bringing in worse-fit clients, and that's a question worth raising before it shows up in revenue."

---

## The dozen figures, condensed

| | |
|---|---|
| Funnel | 3,918 submittals → 1,835 interviews scheduled → 1,719 completed → 482 offers → 362 hires |
| Ratios | 46.8% submittal→interview · 28.0% interview→offer · 75.1% acceptance |
| Vacancy status | 49.4% filled · 21.6% cancelled · 20.2% open · 8.9% on hold |
| Time to fill (median) | Technical 28d · Bookkeeping 22d · Executive VA 19d · Sales VA 18d · Customer Support 17d |
| Time to first submittal | Technical 5d · Customer Support 2d |
| English → hire rate | B1 2.9% · B2 7.9% · C1 13.4% · C2 13.4% |
| …reverses at offer | C2 accept 63.2% · B2 accept 78.9% |
| CPL | Outbound $83.78 (cheapest) · Paid Social $146.27 (dearest) |
| CAC | Paid Search $1,362 · Outbound $1,270 · Paid Social $3,625 |
| ROAS | Paid Search 1.79 · Outbound 1.73 · **Paid Social 0.60** |
| Referral | 22.3% lead→client, zero recorded spend, $198,434 in fees |
| Untouched leads | 256 (6.5%), 199 of them paid, ≈$24,000 wasted, 21 of them referrals |
| Reps | Best 11.1% win rate on closed vs worst 8.2% · best quota attainment 68% |
| Repeat clients | 58.7% open a second requisition |
| Censoring | July 11.9% vs stable ~55% · fixed 30-day window holds 42–51% on completed cohorts |
| Reconciliation | 12 vacancies filled with no placement record |

---

*Next: [04 SQL and BigQuery](04_sql_and_bigquery.md) · Back to [question bank index](README.md) · Source: [01 recruiting metrics](../01_recruiting_sales_marketing_metrics.md) · [06 sales lens](../06_sales_lens_and_objections.md)*
