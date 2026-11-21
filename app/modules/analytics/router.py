"""FastAPI router for Analytics endpoints."""
from datetime import date
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.analytics.schemas import (
    AnalyticsHistoryResponse,
    AnalyticsOverviewResponse,
)
from app.modules.analytics.service import AnalyticsService
from app.modules.auth.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse, status_code=status.HTTP_200_OK)
async def get_overview(
    date: Optional[date] = Query(default=None, description="Local calendar date (YYYY-MM-DD)"),
    device_id: Optional[uuid.UUID] = Query(default=None, description="Optional device filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve daily summary overview including screen time, unlocks, top apps, and goals."""
    return await AnalyticsService.get_overview(db, current_user, target_date=date, device_id=device_id)


@router.get("/history", response_model=AnalyticsHistoryResponse, status_code=status.HTTP_200_OK)
async def get_history(
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    device_id: Optional[uuid.UUID] = Query(default=None, description="Optional device filter"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve multi-day historical usage trends across a date window."""
    return await AnalyticsService.get_history(
        db,
        current_user,
        start_date=start_date,
        end_date=end_date,
        device_id=device_id,
        page=page,
        page_size=page_size,
    )
