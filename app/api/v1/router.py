"""Base API v1 router consolidating all submodules."""
from fastapi import APIRouter

from app.modules.admin.router import (
    admin_auth_router,
    admin_router,
    admin_users_router,
    admin_applications_router,
    admin_devices_router,
    admin_analytics_router,
    admin_sync_router,
    admin_reports_router,
    admin_audit_logs_router,
    admin_administrators_router,
)
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

# Admin Analytics Dashboard, User Management, Applications, Devices & Analytics
api_router.include_router(admin_auth_router)
api_router.include_router(admin_router)
api_router.include_router(admin_users_router)
api_router.include_router(admin_applications_router)
api_router.include_router(admin_devices_router)
api_router.include_router(admin_analytics_router)
api_router.include_router(admin_sync_router)
api_router.include_router(admin_reports_router)
api_router.include_router(admin_audit_logs_router)
api_router.include_router(admin_administrators_router)

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
