"""Service layer for idempotent batch usage telemetry ingestion."""
from datetime import datetime, timezone
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.task_queue import enqueue_task
from app.modules.auth.models import User
from app.modules.devices.models import Device
from app.modules.usage_ingestion.models import AppUsageEvent, ScreenActivityEvent
from app.modules.usage_ingestion.schemas import UsageSyncRequest, UsageSyncResponse


class UsageIngestionService:
    """Handles validation, idempotent deduplication, and persistence of client telemetry."""

    @staticmethod
    async def ingest_sync_batch(
        db: AsyncSession,
        current_user: User,
        req: UsageSyncRequest,
    ) -> UsageSyncResponse:
        """Process incoming batch of screen and application usage events idempotently."""
        # 1. Validate device ownership
        device_stmt = select(Device).where(
            Device.id == req.device_id,
            Device.user_id == current_user.id,
        )
        device_result = await db.execute(device_stmt)
        device = device_result.scalar_one_or_none()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found or not registered to the authenticated user",
            )

        now = datetime.now(timezone.utc)
        total_incoming = len(req.screen_events) + len(req.app_events)
        inserted_count = 0

        # 2. Ingest screen activity events with ON CONFLICT DO NOTHING
        if req.screen_events:
            for se in req.screen_events:
                stmt = (
                    pg_insert(ScreenActivityEvent)
                    .values(
                        id=uuid.uuid4(),
                        device_id=req.device_id,
                        event_uuid=se.event_uuid,
                        event_type=se.event_type,
                        timestamp=se.timestamp,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["device_id", "event_uuid"]
                    )
                    .returning(ScreenActivityEvent.id)
                )
                res = await db.execute(stmt)
                if res.scalar_one_or_none() is not None:
                    inserted_count += 1

        # 3. Ingest app usage events with ON CONFLICT DO NOTHING
        if req.app_events:
            for ae in req.app_events:
                stmt = (
                    pg_insert(AppUsageEvent)
                    .values(
                        id=uuid.uuid4(),
                        device_id=req.device_id,
                        event_uuid=ae.event_uuid,
                        package_name=ae.package_name,
                        start_time=ae.start_time,
                        end_time=ae.end_time,
                        duration_seconds=ae.duration_seconds,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["device_id", "event_uuid"]
                    )
                    .returning(AppUsageEvent.id)
                )
                res = await db.execute(stmt)
                if res.scalar_one_or_none() is not None:
                    inserted_count += 1

        # 4. Update device last_sync_at timestamp
        device.last_sync_at = now
        await db.flush()

        # 5. Enqueue background aggregation job in app_tasks
        await enqueue_task(
            db,
            task_type="RECALCULATE_SUMMARIES",
            payload={
                "user_id": str(current_user.id),
                "device_id": str(req.device_id),
                "sync_batch_id": str(req.sync_batch_id),
            },
        )

        duplicate_count = total_incoming - inserted_count

        return UsageSyncResponse(
            status="success",
            sync_batch_id=req.sync_batch_id,
            processed_events=inserted_count,
            duplicate_events_ignored=duplicate_count,
            server_timestamp=now,
        )
