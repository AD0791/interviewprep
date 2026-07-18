from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine

# Auto-create tables for instant developer boot (in development environments)
# Note: For staging/production databases, use Alembic migrations instead.
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Incremental build core banking telemetry analytics",
    version="1.0.0"
)

# 1. Enable payload compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS configurations with browser OPTIONS preflight caching
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to targeted static domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600 # 10 minute OPTIONS caching
)

# 3. Mount versioned routes
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    if settings.ENVIRONMENT == "development":
        await init_models()
