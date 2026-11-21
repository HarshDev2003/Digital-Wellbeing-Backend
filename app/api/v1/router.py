"""Base API v1 router consolidating all submodules."""
from fastapi import APIRouter

from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.consent.router import router as consent_router
from app.modules.devices.router import router as devices_router
from app.modules.goals_limits.router import router as goals_limits_router
from app.modules.usage_ingestion.router import router as usage_router

api_router = APIRouter()

# System / Diagnostics
@api_router.get("/health", tags=["System"])
async def api_health():
    """API v1 health status endpoint."""
    return {"status": "ok", "version": "v1"}

# User Story 1: Identity, Devices & Consent
api_router.include_router(auth_router)
api_router.include_router(devices_router)
api_router.include_router(consent_router)

# User Story 3: Usage Telemetry Ingestion & Idempotent Sync
api_router.include_router(usage_router)

# User Story 2: Centralized Usage History & Daily Aggregation
api_router.include_router(analytics_router)

# User Story 4: Goal Setting & App Usage Guardrails
api_router.include_router(goals_limits_router)
