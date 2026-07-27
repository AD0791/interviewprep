from fastapi import APIRouter
from app.api.v1.endpoints import banking

api_router = APIRouter()

# Mount API versioning routes
api_router.include_router(banking.router, prefix="/v1", tags=["Banking v1"])
