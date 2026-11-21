"""FastAPI router for Telemetry Ingestion endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.usage_ingestion.schemas import UsageSyncRequest, UsageSyncResponse
from app.modules.usage_ingestion.service import UsageIngestionService

router = APIRouter(prefix="/usage", tags=["Usage Ingestion"])


@router.post("/sync", response_model=UsageSyncResponse, status_code=status.HTTP_200_OK)
async def sync_usage(
    req: UsageSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Synchronize a batch of screen activity and application usage events idempotently."""
    return await UsageIngestionService.ingest_sync_batch(db, current_user, req)
