"""Base API v1 router consolidating all submodules."""
from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["System"])
async def api_health():
    """API v1 health status endpoint."""
    return {"status": "ok", "version": "v1"}
