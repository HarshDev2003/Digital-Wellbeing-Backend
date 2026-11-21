"""Business logic service for managing Usage Goals, App Limits, and Violations."""
from typing import List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.goals_limits.models import AppLimit, AppLimitViolation, UsageGoal
from app.modules.goals_limits.schemas import AppLimitCreateRequest, GoalCreateRequest


class GoalsLimitsService:
    """Service providing CRUD and enforcement utilities for usage goals and app limits."""

    @staticmethod
    async def create_or_update_goal(
        db: AsyncSession,
        user: User,
        payload: GoalCreateRequest,
    ) -> UsageGoal:
        """Create or update an active usage goal for the authenticated user."""
        stmt = select(UsageGoal).where(
            UsageGoal.user_id == user.id,
            UsageGoal.target_type == payload.target_type,
            UsageGoal.category_id == payload.category_id,
        )
        res = await db.execute(stmt)
        goal = res.scalar_one_or_none()

        if goal:
            goal.max_duration_seconds = payload.max_duration_seconds
            goal.is_active = True
        else:
            goal = UsageGoal(
                id=uuid.uuid4(),
                user_id=user.id,
                target_type=payload.target_type,
                category_id=payload.category_id,
                max_duration_seconds=payload.max_duration_seconds,
                is_active=True,
            )
            db.add(goal)

        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def list_goals(
        db: AsyncSession,
        user: User,
    ) -> List[UsageGoal]:
        """Retrieve all active goals defined by the user."""
        stmt = (
            select(UsageGoal)
            .where(
                UsageGoal.user_id == user.id,
                UsageGoal.is_active.is_(True),
            )
            .order_by(UsageGoal.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_or_update_limit(
        db: AsyncSession,
        user: User,
        payload: AppLimitCreateRequest,
    ) -> AppLimit:
        """Create or update daily application limit for the user."""
        stmt = select(AppLimit).where(
            AppLimit.user_id == user.id,
            AppLimit.package_name == payload.package_name,
        )
        res = await db.execute(stmt)
        limit = res.scalar_one_or_none()

        if limit:
            limit.max_duration_seconds = payload.max_duration_seconds
            limit.is_active = True
        else:
            limit = AppLimit(
                id=uuid.uuid4(),
                user_id=user.id,
                package_name=payload.package_name,
                max_duration_seconds=payload.max_duration_seconds,
                is_active=True,
            )
            db.add(limit)

        await db.commit()
        await db.refresh(limit)
        return limit

    @staticmethod
    async def list_limits(
        db: AsyncSession,
        user: User,
    ) -> List[AppLimit]:
        """Retrieve all active application limits configured by user."""
        stmt = (
            select(AppLimit)
            .where(
                AppLimit.user_id == user.id,
                AppLimit.is_active.is_(True),
            )
            .order_by(AppLimit.created_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def list_violations(
        db: AsyncSession,
        user: User,
        limit: int = 50,
    ) -> List[AppLimitViolation]:
        """Retrieve audit log of limit breaches for user."""
        stmt = (
            select(AppLimitViolation)
            .where(AppLimitViolation.user_id == user.id)
            .order_by(
                AppLimitViolation.violation_date.desc(),
                AppLimitViolation.created_at.desc(),
            )
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())
