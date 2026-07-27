# Aesthetix Virtual Banking Dashboard (Reference Blueprint)

A complete, dockerized fullstack boilerplate project representing a live telemetry control panel for a Virtual Bank. This serves as a reference application representing all guidelines, architectural designs, and optimization configs covered in the interview prep guides.

---

## 1. Directory Blueprint & Pattern References

This project contains clean-code patterns separated across backend and frontend directories:

* **12-Factor Config Separation**:
  * Backend Pydantic-settings loaded at [backend/app/core/config.py](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/backend/app/core/config.py)
  * Frontend Zod build validations loaded at [frontend/src/config/env.ts](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/frontend/src/config/env.ts)
* **SQLAlchemy 2.0 Async Repository Mapping**:
  * Abstracted protocols and data mutations implemented at [backend/app/repositories/banking.py](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/backend/app/repositories/banking.py)
  * Decoupled FastAPI Route bindings executed at [backend/app/api/v1/endpoints/banking.py](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/backend/app/api/v1/endpoints/banking.py)
* **React Feature-Based Architecture & Smart/Dumb Colocation**:
  * Unified SWR hook managing caches located at [frontend/src/features/banking/hooks/useBankingSWR.ts](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/frontend/src/features/banking/hooks/useBankingSWR.ts)
  * Presentational state and Formik forms at [frontend/src/features/banking/components/BankingDashboard.tsx](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/frontend/src/features/banking/components/BankingDashboard.tsx)
* **Multi-Stage Container Pipelines**:
  * Multi-stage builder utilizing the Rust-based `uv` package manager at [backend/Dockerfile](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/backend/Dockerfile)
  * Static compiler bundling deploying static React bundles to Nginx at [frontend/Dockerfile](file:///Users/ad0791/Desktop/theCrest/interviewprep/virtual_banking_dashboard/frontend/Dockerfile)

---

## 2. Step-by-Step Execution Guide (Incremental Bootstrapping)

### Step 1: Clone and Environment check
Ensure you have Docker and Docker Compose installed on your system.

### Step 2: Spin Up Infrastructure Containers
Start the PostgreSQL database and Redis caching engines in detached mode:
```bash
docker compose up -d postgres redis
```

### Step 3: Local Backend Development (Optional dry run)
To run the backend without Docker (locally for quick iteration):
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies using `uv` (Rust-based manager):
   ```bash
   uv pip install -r pyproject.toml
   ```
3. Boot the local Uvicorn development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4. Run backend tests to verify sqlite memory overrides:
   ```bash
   pytest
   ```

### Step 4: Run the Complete Dockerized Stack
Build and launch the entire stack (Postgres + Redis + Backend API + Nginx React Frontend):
```bash
docker compose up --build
```

Access the systems locally:
* **Frontend Web Dashboard**: Open [http://localhost](http://localhost) in your browser.
* **Backend Swagger API docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs).
* **Database Connection**: `postgresql://postgres:secretpassword@localhost:5432/core_banking`.

---

## 3. Key Optimization Strategies Implemented
1. **OPTIONS CORS caching**: The backend CORS middleware configuration contains `max_age=600`, reducing preflight query overhead.
2. **Database pre-aggregations**: Cumulative transaction metrics are processed directly in the database engine using SQL Window Functions (`SUM() OVER`) rather than parsing collections inside Python memory.
3. **Payload Compression**: FastAPI `GZipMiddleware` compresses responses above 1KB, decreasing rendering start times.
4. **Memoized Calculations**: React `useMemo` hooks ensure total deposit balance calculations only update when account objects change.
