"""FastAPI router for Usage Goals and Application Limits."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.goals_limits.schemas import (
    AppLimitCreateRequest,
    AppLimitListResponse,
    AppLimitResponse,
    GoalCreateRequest,
    GoalListResponse,
    GoalResponse,
    ViolationItemResponse,
    ViolationListResponse,
)
from app.modules.goals_limits.service import GoalsLimitsService

router = APIRouter(tags=["Goals & Limits"])


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update daily usage goal",
)
async def set_usage_goal(
    payload: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upsert daily screen-time or category limit goal."""
    goal = await GoalsLimitsService.create_or_update_goal(db, current_user, payload)
    return GoalResponse(
        goal_id=goal.id,
        target_type=goal.target_type,
        category_id=goal.category_id,
        max_duration_seconds=goal.max_duration_seconds,
        is_active=goal.is_active,
    )


@router.get(
    "/goals",
    response_model=GoalListResponse,
    status_code=status.HTTP_200_OK,
    summary="List active usage goals",
)
async def list_usage_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all active goals defined by the current user."""
    goals = await GoalsLimitsService.list_goals(db, current_user)
    return GoalListResponse(
        goals=[
            GoalResponse(
                goal_id=g.id,
                target_type=g.target_type,
                category_id=g.category_id,
                max_duration_seconds=g.max_duration_seconds,
                is_active=g.is_active,
            )
            for g in goals
        ]
    )


@router.post(
    "/limits",
    response_model=AppLimitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update application daily limit",
)
async def set_app_limit(
    payload: AppLimitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Configure or adjust daily duration limit for a package name."""
    limit = await GoalsLimitsService.create_or_update_limit(db, current_user, payload)
    return AppLimitResponse(
        limit_id=limit.id,
        package_name=limit.package_name,
        max_duration_seconds=limit.max_duration_seconds,
        is_active=limit.is_active,
    )


@router.get(
    "/limits",
    response_model=AppLimitListResponse,
    status_code=status.HTTP_200_OK,
    summary="List active application limits",
)
async def list_app_limits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve configured daily limits for the authenticated user."""
    limits = await GoalsLimitsService.list_limits(db, current_user)
    return AppLimitListResponse(
        limits=[
            AppLimitResponse(
                limit_id=l.id,
                package_name=l.package_name,
                max_duration_seconds=l.max_duration_seconds,
                is_active=l.is_active,
            )
            for l in limits
        ]
    )


@router.get(
    "/limits/violations",
    response_model=ViolationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List limit breach audit logs",
)
async def list_violations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Audit log of application limit violations."""
    violations = await GoalsLimitsService.list_violations(db, current_user)
    return ViolationListResponse(
        violations=[
            ViolationItemResponse(
                id=v.id,
                package_name=v.package_name,
                violation_date=v.violation_date,
                actual_duration_seconds=v.actual_duration_seconds,
                limit_duration_seconds=v.limit_duration_seconds,
                created_at=v.created_at,
            )
            for v in violations
        ]
    )
