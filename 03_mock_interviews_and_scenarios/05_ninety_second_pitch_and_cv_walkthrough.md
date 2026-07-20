# The 90-Second Pitch and the CV Walkthrough

The first interview at BairesDev is a recruiter screen, and it opens the same way almost every screen opens: "Tell me about yourself." This is not small talk. The recruiter is checking three things at once — whether your English flows, whether your story matches the CV they are holding, and whether you can be concise. A rambling five-minute answer fails the screen even if every fact in it is impressive. The material below gives you a word-for-word pitch to rehearse, a map from every line of your CV to a speakable proof point, and answers to the two probes a recruiter is most likely to throw at your profile.

Rehearse the pitch out loud, standing up, until you can deliver it without reading. It should take about ninety seconds at a calm conversational pace. Do not memorize it so rigidly that you sound like a recording — memorize the *sequence of beats* (current role, backend depth, the differentiator, why BairesDev) and let the sentences breathe.

## The 90-Second Pitch (word for word)

> I'm a fullstack engineer with a data-heavy background. Right now I'm at Tekkod, a US software company I've worked with remotely since 2021. My current project is leading the modernization of a production React Native app: I took it from version 0.65 to 0.74, migrated it to the New Architecture with Hermes and Bridgeless mode, and modernized the whole build chain along the way — Java 17, Gradle 8.8, and Firebase's modular API.
>
> Before that, on the backend side at Tekkod, I built secure RESTful services with FastAPI and JWT authentication using the repository pattern, and I built ETL pipelines with Apache Beam moving data from MongoDB into BigQuery on Google Cloud, all containerized with Docker and documented with OpenAPI.
>
> What makes my profile a little different is where I started. I'm an applied economist by training, and I spent years building monitoring-and-evaluation data systems for international development programs — Python and SQL automation that cut manual reporting time by forty percent, dashboards in Power BI and Looker Studio, infrastructure on AWS. So I'm the engineer who also understands the data and the business question behind it.
>
> I've worked remotely with US and international clients for over five years, in English, across time zones — which is exactly the BairesDev model — and I'm looking for a long-term fullstack Python role where I can go deep with one client team.

That is roughly 230 words, which lands at ninety seconds when spoken calmly. Every claim in it appears verbatim on your CV, so nothing can be challenged as embellishment.

## The 30-Second Version

Some recruiters cut the intro short, or ask for "a quick summary" late in the call. Have this compressed version ready:

> I'm a fullstack engineer at Tekkod, a US company I've worked with remotely since 2021 — currently leading a React Native modernization, and before that building FastAPI services and data pipelines into BigQuery. My original background is applied economics and data engineering for development programs, so I bring both the engineering and the data literacy. I've been fully remote with international clients for five years, which is exactly how BairesDev works.

## The CV-Coherence Map

The recruiter will have your CV open and will pick two or three entries to probe: "Tell me more about what you did at X." For each entry, here are the proof points to say out loud, phrased to connect back to the FastAPI, SQLAlchemy, Postgres, and React/TypeScript stack the role targets. Say the sentences, not the bullet points on the CV — the recruiter already read those.

**Tekkod LLC — Software Engineer, Fullstack (Feb 2026 – present).** "I lead the STS mobile app modernization. The app was on React Native 0.65, which is end-of-life, so I migrated it to 0.74 and onto the New Architecture — that means Hermes as the JavaScript engine and Bridgeless mode. It also meant modernizing everything underneath: Java 17, Gradle 8.8, Firebase's v22 modular API, and refactoring the UI components for Yoga 3.0, including fixing a class of bugs around asynchronous state updates." If asked about React specifically, add: "React Native and React share the component model, hooks, and state patterns — the rendering target is different, but the engineering is the same, and I keep a full React-with-TypeScript reference project alongside my backend work."

**Anseye Pou Ayiti — Data Analyst & MEAL Consultant (Jan – Mar 2026).** "A short consulting engagement in parallel with Tekkod: I designed KPI tracking for leadership programs, built collection tools on ODK and Google Forms with validation protocols, and maintained the Python scripts on AWS that kept the data pipeline honest."

**HANWASH — mWater & Data Analyst Consultant (Oct 2023 – Jan 2026).** "A two-year remote contract through Upwork — which matters here because it proves I can sustain a long-term remote client relationship. I refined their MEAL plan and indicator tracking, deployed complex mWater surveys, and built automated Power BI dashboards so stakeholders saw data in real time instead of waiting for monthly reports."

**Tekkod LLC — Backend Developer & Data Engineer (Mar 2021 – May 2024).** This is your Python backend anchor — lead with it whenever backend depth is questioned. "I built secure RESTful services in FastAPI with JWT authentication, structured with the repository pattern so the data layer was swappable and testable. On the data side I built ETL pipelines with Apache Beam migrating MongoDB data into BigQuery. Everything ran in Docker, was documented with OpenAPI, and went through Git-based review."

**Caris Foundation International — Monitoring & Evaluation Officer (Oct 2021 – Aug 2024).** "I ran the data systems for a youth health program: digital collection through CommCare, automated reporting in Python and SQL that cut manual processing time by forty percent, data-quality protocols over a MySQL backend, and dashboards on AWS with Quarto and Power BI."

**CassionSoft, UNOPS project — Software Consultant & Data Integration Specialist (Nov 2015 – Mar 2021).** "My longest engagement: REST API services with role-based access control on OAuth2 and JWT, complex data-integration logic validated with rigorous unit tests, and OpenAPI documentation. It is where I learned that authentication and testing are not afterthoughts."

**Ministry of Planning — Economist (2014 – 2015).** "My first career: macroeconomic indicator monitoring and public-policy reporting. It is why I default to asking what question the data is supposed to answer before writing any code."

## The Two Probes You Should Expect

**"Your background mixes economics, M&E, and software engineering — walk me through that."** Do not apologize for the mix; sell it as a straight line. Say: "It is one continuous story about data. I started as an economist doing statistical modeling for policy. That pulled me into building the data systems behind the analysis — collection tools, pipelines, dashboards — for development organizations. Building those systems properly meant becoming a real engineer, so I trained formally through Flatiron School and moved into backend and then fullstack work at Tekkod. Each step added a layer: the economics gives me the analytical rigor, the M&E years gave me data engineering under messy real-world conditions, and the last five years made me a production software engineer. For a role centered on dashboards and data aggregation, that combination is the whole job."

**"Your fullstack title is only a few months old — how deep is your Python backend experience really?"** The title is recent; the experience is not. Say: "The fullstack title dates from February, but I have been shipping Python backends since 2021 — FastAPI services with JWT auth and the repository pattern, plus Apache Beam ETL pipelines at Tekkod for three years — and before that I spent five years at CassionSoft building REST APIs with OAuth2 and role-based access control. The recent title reflects adding mobile and frontend leadership on top of an existing backend foundation, not starting from zero."

## Explaining Your Work to a Non-Technical Recruiter

The recruiter is usually not an engineer, and part of what they grade is whether you can make a client's product manager understand you. Rehearse these one-breath plain-English explanations until they come out naturally:

**What is FastAPI?** "It's the modern Python framework for building the server side of an application — the part that receives requests, applies the business rules, talks to the database, and sends back answers. It's known for being fast and for catching data errors automatically."

**What did your ETL pipeline actually do?** "The company's data lived in one database that was good for running the app but bad for analysis. I built an automated conveyor belt that continuously moved and reshaped that data into a warehouse where analysts could query it in seconds."

**What is the virtual banking dashboard project?** "It's a full banking application I built end to end as a reference project: accounts, transfers, and transactions in a Postgres database, a Python API on top, and a React dashboard in front showing live balances and metrics — the same shape as most client work: data, an API, and a screen that makes it useful."

**What did you do as an M&E officer, in one sentence?** "I made sure a health program could prove, with trustworthy numbers, that it was actually helping people — by building the systems that collected, cleaned, and displayed those numbers."

## Interview Angles

**"Why do you want to work at BairesDev?"** — "Three reasons. First, the model fits how I already work: I've been a remote contractor for US and international clients for over five years, so distributed, English-speaking, timezone-aligned work is my normal, not an adjustment. Second, I want sustained depth with one client team rather than the context-switching of freelancing — BairesDev places you long-term, and that is the part of Tekkod I have enjoyed most. Third, the roles here center on exactly my strongest ground: Python backends, data, and dashboards."

**"What are you looking for in your next role?"** — "A long-term fullstack Python position where the data matters — dashboards, aggregation, reporting — because that is where my engineering and my analytics background compound each other. I want one team, one product, and enough time to own outcomes rather than handing off deliverables."
