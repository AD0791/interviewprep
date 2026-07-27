# Fullstack Technical Q&A & Behavioral Drills

An academic guide to structuring responses for technical evaluations, deploying the STAR methodology, and mastering performance question patterns.

---

## 1. Structured Communication Models (Why & What)

Interview evaluations assess not just what you know, but how you structure your technical explanations. Senior developers use structured templates to communicate complex architectural tradeoffs:

### The "Why, What, How" Framework (Technical Concept Questions)
When asked to explain a technology (e.g. "What is a transaction repository?"), structure your answer in three logical stages:
1. **Why (The Problem)**: Start by explaining the problem the pattern/technology solves (e.g. "Hardcoding SQL statements inside controllers creates tight coupling and makes unit testing difficult...").
2. **What (The Definition)**: Define the concept clearly (e.g. "A repository acts as an abstraction layer between domain logic and database operations...").
3. **How (The Implementation)**: Describe the concrete implementation steps and trade-offs (e.g. "We define a Python Protocol interface class and inject its implementation into our FastAPI router using dependency injection...").

### The "STAR" Framework (Behavioral Scenario Questions)
When asked about past situations (e.g. "Tell me about a time a migration broke production..."), structure your story using:
* **Situation**: Describe the context and technical environment (e.g. "We had a PostgreSQL database with 10M rows and deployed a new migration...").
* **Task**: Define the challenge or bug that needed to be resolved (e.g. "A table lock occurred, causing API requests to time out...").
* **Action**: Explain the concrete technical actions you took (e.g. "I canceled the migration, ran offline schema generation, applied the column as nullable first, and added the index concurrently...").
* **Result**: Share the quantitative results and lessons learned (e.g. "We resolved the outage in 10 minutes and updated our CI/CD pipeline to block non-nullable columns...").

---

## 2. Technical Q&A Reference (How)

### Core PostgreSQL & SQLAlchemy Optimization

#### Question: "How do you optimize a slow database query that aggregates transactions?"
* **Why**: The database is reading all rows from disk (sequential scan) because it lacks appropriate indexing, or it is downloading too much data to Python memory instead of aggregating in-place.
* **What**: We must analyze the query execution plan using `EXPLAIN ANALYZE`, add appropriate composite indexes, and write database-level aggregates.
* **How**:
  1. Run `EXPLAIN ANALYZE` on the query to find sequential scans and high-cost joins.
  2. Create a composite index matching the `WHERE` and `GROUP BY` columns:
     ```sql
     CREATE INDEX CONCURRENTLY idx_transactions_tenant_status ON transactions (tenant_id, status, created_at);
     ```
  3. Rewrite the query in SQLAlchemy v2 using subqueries and window functions (`func.sum().over()`), shifting the calculation load to PostgreSQL.

---

## 3. Behavioral Scenarios & STAR Templates (How)

### Gist: db_optimization_star_blueprint.md
A structured study template showing how to frame an optimization story for BairesDev interviewers.

```markdown
# Gist: Database Optimization STAR Story Reference

### Situation
Our core banking application dashboard was experiencing severe latency. The main `/analytics/overview` endpoint was taking 8 to 12 seconds to resolve during peak hours. This caused client charts to time out and blocked API gateways. The stack was FastAPI, SQLAlchemy, and a PostgreSQL database.

### Task
I was tasked with identifying the bottleneck and bringing load times under 1 second without modifying the dashboard UI widgets or risking database lockouts.

### Action
1. **Network Profiling**: Open Browser DevTools. Isolate latency to TTFB (Time to First Byte), confirming the issue was backend execution time.
2. **Backend APM Profiling**: Enabled SQLAlchemy query logging. Identified a classic **N+1 query database bottleneck**: the API was fetching 100 accounts, looping over them, and executing a new query for each account to count its transaction records.
3. **Database Profiling**: Logged raw SQL queries and ran `EXPLAIN ANALYZE` on PostgreSQL. Discovered a sequential scan on the `transactions` table (containing 5 million rows).
4. **Refactoring Steps**:
   * Resolved the N+1 issue by using SQLAlchemy's `selectinload` to fetch all transaction records in exactly two queries.
   * Shifted the loop aggregation logic to PostgreSQL using a single `GROUP BY` query.
   * Added a composite index concurrently to avoid locking production database writes:
     ```sql
     CREATE INDEX CONCURRENTLY idx_tx_account_status ON transactions (account_id, status, amount);
     ```

### Result
* Backend response times dropped from 10 seconds to **150 milliseconds**.
* Total query count dropped from 101 queries to **2 queries**.
* Database CPU utilization decreased by **40%**, saving infrastructure costs and securing the platform's stability.
```
