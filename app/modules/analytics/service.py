"""Analytics service retrieving aggregated usage metrics and historical trends."""
from datetime import date, datetime, timedelta, timezone
from typing import Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User
from app.modules.devices.models import Device
from app.modules.usage_processing.models import AppDailySummary, DailyUsageSummary
from app.modules.usage_processing.service import format_seconds_to_human
from app.modules.analytics.schemas import (
    AnalyticsHistoryResponse,
    AnalyticsOverviewResponse,
    CategoryBreakdownItem,
    GoalsStatusOverview,
    HeadlineMetrics,
    HistoricalTrendItem,
    NetworkTelemetryOverview,
    PaginationInfo,
    TopAppItem,
)


def _get_display_name(package_name: str) -> str:
    """Derive user-friendly app name from reverse-domain package identifier."""
    parts = package_name.split(".")
    if len(parts) >= 1:
        return parts[-1].capitalize()
    return package_name


class AnalyticsService:
    """Service serving dashboard overview and multi-day historical analytics."""

    @staticmethod
    async def get_overview(
        db: AsyncSession,
        current_user: User,
        target_date: Optional[date] = None,
        device_id: Optional[uuid.UUID] = None,
    ) -> AnalyticsOverviewResponse:
        """Fetch headline metrics, top apps, and category breakdown for a specific date."""
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()

        # Build query for daily summaries
        query = (
            select(DailyUsageSummary)
            .where(
                DailyUsageSummary.user_id == current_user.id,
                DailyUsageSummary.calendar_date == target_date,
            )
            .options(selectinload(DailyUsageSummary.app_summaries))
        )
        if device_id:
            query = query.where(DailyUsageSummary.device_id == device_id)

        result = await db.execute(query)
        summaries = result.scalars().all()

        total_screen_time = sum(s.total_screen_time_seconds for s in summaries)
        total_unlocks = sum(s.total_unlocks for s in summaries)
        total_sessions = sum(s.total_sessions for s in summaries)

        # Aggregate app breakdown across summaries
        app_durations: dict[str, int] = {}
        for s in summaries:
            for app in s.app_summaries:
                app_durations[app.package_name] = (
                    app_durations.get(app.package_name, 0) + app.total_foreground_seconds
                )

        top_apps: list[TopAppItem] = []
        for pkg, dur in sorted(app_durations.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = round((dur / total_screen_time * 100), 1) if total_screen_time > 0 else 0.0
            top_apps.append(
                TopAppItem(
                    package_name=pkg,
                    display_name=_get_display_name(pkg),
                    category="General",
                    duration_seconds=dur,
                    duration_formatted=format_seconds_to_human(dur),
                    percentage_of_total=pct,
                )
            )

        category_breakdown = [
            CategoryBreakdownItem(
                category="General",
                duration_seconds=total_screen_time,
                percentage=100.0 if total_screen_time > 0 else 0.0,
            )
        ] if total_screen_time > 0 else []

        # Check device platform for network capability notice
        platform_restricted = False
        if device_id:
            dev_stmt = select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
            dev_res = await db.execute(dev_stmt)
            dev = dev_res.scalar_one_or_none()
            if dev and dev.platform.lower() == "ios":
                platform_restricted = True

        net_telemetry = NetworkTelemetryOverview(
            supported=not platform_restricted,
            platform_restricted=platform_restricted,
            message="Per-app network telemetry is restricted by Apple operating system policies."
            if platform_restricted
            else None,
        )

        return AnalyticsOverviewResponse(
            calendar_date=target_date,
            timezone=current_user.timezone,
            headline_metrics=HeadlineMetrics(
                total_screen_time_seconds=total_screen_time,
                total_screen_time_formatted=format_seconds_to_human(total_screen_time),
                total_unlocks=total_unlocks,
                total_app_sessions=total_sessions,
            ),
            top_apps=top_apps,
            category_breakdown=category_breakdown,
            goals_status=GoalsStatusOverview(
                daily_goal_seconds=14400,
                consumed_seconds=total_screen_time,
                status="EXCEEDED" if total_screen_time > 14400 else "ON_TRACK",
            ),
            network_telemetry=net_telemetry,
        )

    @staticmethod
    async def get_history(
        db: AsyncSession,
        current_user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        device_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AnalyticsHistoryResponse:
        """Fetch historical daily screen time and unlock trends across a date window."""
        today = datetime.now(timezone.utc).date()
        if end_date is None:
            end_date = today
        if start_date is None:
            start_date = end_date - timedelta(days=29)

        query = select(
            DailyUsageSummary.calendar_date,
            func.sum(DailyUsageSummary.total_screen_time_seconds).label("screen_time"),
            func.sum(DailyUsageSummary.total_unlocks).label("unlocks"),
        ).where(
            DailyUsageSummary.user_id == current_user.id,
            DailyUsageSummary.calendar_date >= start_date,
            DailyUsageSummary.calendar_date <= end_date,
        )

        if device_id:
            query = query.where(DailyUsageSummary.device_id == device_id)

        query = query.group_by(DailyUsageSummary.calendar_date).order_by(
            DailyUsageSummary.calendar_date.desc()
        )

        result = await db.execute(query)
        rows = result.all()

        total_records = len(rows)
        total_pages = max(1, (total_records + page_size - 1) // page_size)
        offset = (page - 1) * page_size
        paged_rows = rows[offset : offset + page_size]

        items = [
            HistoricalTrendItem(
                calendar_date=r.calendar_date,
                total_screen_time_seconds=int(r.screen_time or 0),
                total_unlocks=int(r.unlocks or 0),
                top_category="General",
                goal_met=int(r.screen_time or 0) <= 14400,
            )
            for r in paged_rows
        ]

        return AnalyticsHistoryResponse(
            start_date=start_date,
            end_date=end_date,
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total_records=total_records,
                total_pages=total_pages,
            ),
            items=items,
        )
