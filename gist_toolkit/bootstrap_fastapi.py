# Gist: bootstrap_fastapi.py
# A production-ready, modular FastAPI main gateway template.

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1. Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 2. Database Session Manager Setup
DATABASE_URL = "postgresql+asyncpg://admin_user:secure_db_password@postgres:5432/main_database"
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# 3. Application Lifespan Handler
# Why: Manages startup/shutdown hook lifecycles cleanly
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing application, verifying DB pool connections...")
    # Add startup logic (e.g. seed cache, connect to redis) here
    yield
    logger.info("Closing application database engine connection pool...")
    await engine.dispose()

app = FastAPI(
    title="Production Core Gateway API",
    version="1.0.0",
    lifespan=lifespan
)

# ---------------------------------------------------------
# MIDDLEWARE STACK
# ---------------------------------------------------------
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600, # Cache preflight options in browser
)

# ---------------------------------------------------------
# GLOBAL EXCEPTION HANDLING
# ---------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal system exception encountered on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal Server Error"},
    )

# ---------------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection helper to yield active async database sessions.
    Cleans up connections automatically on endpoint return.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ---------------------------------------------------------
# BASE HEALHCHECK ROUTE
# ---------------------------------------------------------
@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["System"])
async def system_health_check(db: AsyncSession = Depends(get_db_session)):
    try:
        # Run dummy check to verify DB connectivity
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Healthcheck failed database connectivity check: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": "Database disconnected"}
        )
