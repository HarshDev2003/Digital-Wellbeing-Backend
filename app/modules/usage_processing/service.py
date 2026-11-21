"""Usage processing service for session calculation, debouncing, and daily summarization."""
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.usage_ingestion.models import AppUsageEvent, ScreenActivityEvent
from app.modules.usage_processing.models import AppDailySummary, DailyUsageSummary


def format_seconds_to_human(seconds: int) -> str:
    """Format total seconds into human-readable 'Xh Ym' or 'Ym'."""
    if seconds <= 0:
        return "0m"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def debounce_app_intervals(
    intervals: List[Dict[str, Any]],
    debounce_threshold_seconds: float = 2.0,
) -> List[Dict[str, Any]]:
    """Merge micro-interruptions (< debounce_threshold_seconds) between consecutive sessions of the same app."""
    if not intervals:
        return []

    # Sort intervals by start_time
    sorted_intervals = sorted(intervals, key=lambda x: x["start_time"])
    merged: List[Dict[str, Any]] = []

    for item in sorted_intervals:
        if not merged:
            merged.append(item.copy())
            continue

        prev = merged[-1]
        gap = (item["start_time"] - prev["end_time"]).total_seconds()

        if item["package_name"] == prev["package_name"] and gap <= debounce_threshold_seconds:
            # Merge interval
            new_end = max(prev["end_time"], item["end_time"])
            prev["end_time"] = new_end
            prev["duration_seconds"] = int((new_end - prev["start_time"]).total_seconds())
        else:
            merged.append(item.copy())

    return merged


def calculate_active_screen_time(
    screen_events: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """Calculate cumulative active screen-unlocked duration (seconds) and unlock count."""
    if not screen_events:
        return 0, 0

    sorted_events = sorted(screen_events, key=lambda x: x["timestamp"])
    total_screen_time = 0
    unlock_count = 0

    is_unlocked = False
    unlock_start: datetime | None = None

    for ev in sorted_events:
        event_type = ev["event_type"]
        ts = ev["timestamp"]

        if event_type == "USER_UNLOCKED":
            unlock_count += 1
            if not is_unlocked:
                is_unlocked = True
                unlock_start = ts
        elif event_type in ("SCREEN_OFF", "SCREEN_LOCK"):
            if is_unlocked and unlock_start:
                duration = int((ts - unlock_start).total_seconds())
                if duration > 0:
                    total_screen_time += duration
                is_unlocked = False
                unlock_start = None

    return total_screen_time, unlock_count


class UsageProcessingService:
    """Service orchestrating daily summary aggregations from raw telemetry events."""

    @staticmethod
    async def recalculate_daily_summary(
        db: AsyncSession,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
        target_date: date,
    ) -> DailyUsageSummary:
        """Aggregate raw events for a given calendar date and upsert daily summary."""
        day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        # 1. Fetch screen events
        screen_stmt = (
            select(ScreenActivityEvent)
            .where(
                ScreenActivityEvent.device_id == device_id,
                ScreenActivityEvent.timestamp >= day_start,
                ScreenActivityEvent.timestamp <= day_end,
            )
            .order_by(ScreenActivityEvent.timestamp.asc())
        )
        screen_res = await db.execute(screen_stmt)
        screen_events = [
            {"event_type": se.event_type, "timestamp": se.timestamp}
            for se in screen_res.scalars().all()
        ]

        total_screen_time, total_unlocks = calculate_active_screen_time(screen_events)

        # 2. Fetch app events
        app_stmt = (
            select(AppUsageEvent)
            .where(
                AppUsageEvent.device_id == device_id,
                AppUsageEvent.start_time >= day_start,
                AppUsageEvent.start_time <= day_end,
            )
            .order_by(AppUsageEvent.start_time.asc())
        )
        app_res = await db.execute(app_stmt)
        raw_app_events = [
            {
                "package_name": ae.package_name,
                "start_time": ae.start_time,
                "end_time": ae.end_time,
                "duration_seconds": ae.duration_seconds,
            }
            for ae in app_res.scalars().all()
        ]

        debounced_events = debounce_app_intervals(raw_app_events)
        total_sessions = len(debounced_events)

        # 3. Aggregate per-package stats
        pkg_stats: Dict[str, Dict[str, int]] = {}
        for de in debounced_events:
            pkg = de["package_name"]
            if pkg not in pkg_stats:
                pkg_stats[pkg] = {"duration": 0, "sessions": 0}
            pkg_stats[pkg]["duration"] += de["duration_seconds"]
            pkg_stats[pkg]["sessions"] += 1

        # 4. Upsert DailyUsageSummary
        summary_stmt = (
            pg_insert(DailyUsageSummary)
            .values(
                id=uuid.uuid4(),
                user_id=user_id,
                device_id=device_id,
                calendar_date=target_date,
                total_screen_time_seconds=total_screen_time,
                total_unlocks=total_unlocks,
                total_sessions=total_sessions,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "device_id", "calendar_date"],
                set_={
                    "total_screen_time_seconds": total_screen_time,
                    "total_unlocks": total_unlocks,
                    "total_sessions": total_sessions,
                    "updated_at": func.now(),
                },
            )
            .returning(DailyUsageSummary)
        )
        summary_res = await db.execute(summary_stmt)
        summary = summary_res.scalar_one()

        # 5. Upsert AppDailySummary rows
        for pkg, stats in pkg_stats.items():
            app_sum_stmt = (
                pg_insert(AppDailySummary)
                .values(
                    id=uuid.uuid4(),
                    daily_summary_id=summary.id,
                    package_name=pkg,
                    total_foreground_seconds=stats["duration"],
                    session_count=stats["sessions"],
                )
                .on_conflict_do_update(
                    index_elements=["daily_summary_id", "package_name"],
                    set_={
                        "total_foreground_seconds": stats["duration"],
                        "session_count": stats["sessions"],
                    },
                )
            )
            await db.execute(app_sum_stmt)

        await db.flush()
        return summary
