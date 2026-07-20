# Agile and Scrum: A Speakable Primer

Screening interviews at services companies almost always include one methodology question — "Have you worked in agile teams?" or "Walk me through how your team ran a sprint." It sounds like a formality, but it is a real filter: BairesDev embeds engineers into client teams that run Scrum or something like it, and they need to know you can slot in on day one without a vocabulary lesson. This primer gives you the concepts in plain language, the vocabulary a recruiter listens for, and — most importantly — your own work history retold in agile terms, because "yes, I know Scrum" is weak while "here is how my last three engagements actually ran" is convincing.

## The Problem Agile Solves (say this before any vocabulary)

Imagine a bank commissions a reporting system, the team disappears for eight months to build the full specification, and delivers exactly what was written — which by then is no longer what the bank needs, because regulations changed in month three and nobody adjusted. That is the waterfall failure mode: one big plan, one big delivery, and every wrong assumption discovered at the end, when it is most expensive.

Agile is the opposite bet: deliver the work in small, usable slices every one or two weeks, show each slice to the people who asked for it, and let what you learn from their reaction reshape the plan. The core insight is that feedback is cheaper than prediction. You do not eliminate planning; you shrink the distance between making a decision and finding out whether it was right.

## Scrum in Plain Language

Scrum is the most common concrete implementation of that idea, and its vocabulary is what recruiters listen for. The work to be done lives in the **product backlog**, a single ordered list owned by the **product owner**, who represents the business and decides what matters most. The team works in **sprints** — fixed windows, usually two weeks — and at **sprint planning** pulls the top items it can realistically finish into the sprint. Once the sprint starts, the goal does not change; scope stability inside the window is what makes short-term commitments meaningful.

Every day there is a **standup**, a fifteen-minute synchronization where each person says what they finished, what they are doing next, and what is blocking them. The standup's purpose is not status reporting to a manager — it is surfacing blockers early so someone can clear them the same day. At the end of the sprint, the **review** (or demo) shows the working result to stakeholders, and the **retrospective** asks the team itself what to improve about how it works. The **scrum master** facilitates all of this and removes impediments; they are a coach, not a boss. Progress across sprints is tracked with lightweight measures like **velocity** (how much the team typically completes per sprint) and visualized on boards; **Kanban** is the related approach that drops fixed sprints and instead limits work-in-progress on a continuous board — common for support and maintenance teams where work arrives unpredictably.

If you are asked what a **user story** is: it is a backlog item phrased from the user's point of view ("As an account holder, I want to see my transaction history filtered by date, so I can find a payment") with acceptance criteria that make "done" testable.

## Your Experience, Told in Agile Terms

You have never held a job with "Scrum" in the title, and that is fine — what matters is that your engagements genuinely ran on iterative delivery, and you can narrate them that way honestly.

At **Tekkod**, the STS modernization runs as incremental delivery on a live product: the migration from React Native 0.65 to 0.74 was decomposed into shippable stages — build-chain modernization first, then the New Architecture migration, then UI-component refactoring — each merged through Git-based review, so the app stayed releasable throughout rather than disappearing into a year-long rewrite branch. That is sprint thinking applied to a risky migration.

At **HANWASH**, a two-year remote engagement, work ran in short cycles against stakeholder feedback: deploy a survey iteration, review the field data quality with the program team, adjust the instruments and dashboards, repeat. The automated Power BI dashboards were effectively a continuous sprint review — stakeholders saw current state at any moment instead of waiting for a monthly report.

At **Caris Foundation**, the weekly KPI dashboard cadence functioned as the sprint heartbeat: every week the program team reviewed the numbers, decided what to fix in collection or reporting, and I delivered those adjustments before the next review. And across all the consulting work, the backlog discipline was real even when the word was not used: a prioritized list of deliverables negotiated with the client, re-ranked as field conditions changed.

## Interview Angles

**"Have you worked in agile environments?"** — "Yes, though mostly in the practical form rather than the ceremonial one. My consulting engagements ran on short delivery cycles with continuous stakeholder feedback — at HANWASH and Caris Foundation the cadence was weekly: deliver, review real data with the program team, re-prioritize, deliver again. At Tekkod, my current modernization project is deliberately sliced into shippable increments so the app stays releasable at every stage. I know the Scrum vocabulary and ceremonies — sprints, standups, reviews, retrospectives — and I'm completely comfortable joining a team that runs them formally."

**"What do you think makes a standup useful versus a waste of time?"** — "A standup is useful when it surfaces blockers while they're still cheap — someone says they're stuck, and the right person unblocks them the same morning. It becomes a waste when it turns into status reporting to a manager, with everyone narrating yesterday in detail. Fifteen minutes, three questions, and any real discussion taken offline with just the people involved — that's the version that earns its cost."

**"How do you handle changing requirements mid-sprint?"** — "Inside a sprint, I'd protect the commitment: the new request goes to the product owner to be prioritized against the backlog for the next sprint, because a team that accepts mid-sprint scope changes stops being able to promise anything. The honest exception is a genuine production emergency — then you swap scope explicitly rather than silently absorbing it. What I'd push back on is the silent version, where scope creeps in and the sprint quietly fails; the whole value of the ritual is that trade-offs are made out loud."
