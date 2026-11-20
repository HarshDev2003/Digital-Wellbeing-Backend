"""PostgreSQL-backed asynchronous task queue worker replacing Redis."""
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def enqueue_task(
    session: AsyncSession,
    task_type: str,
    payload: Dict[str, Any],
    scheduled_at: Optional[datetime] = None,
) -> uuid.UUID:
    """Enqueue an asynchronous task into PostgreSQL app_tasks queue."""
    task_id = uuid.uuid4()
    if scheduled_at is None:
        scheduled_at = datetime.now(timezone.utc)

    stmt = text("""
        INSERT INTO app_tasks (id, task_type, payload, status, scheduled_at, retry_count, created_at)
        VALUES (:id, :task_type, :payload, 'PENDING', :scheduled_at, 0, NOW())
    """)
    await session.execute(
        stmt,
        {
            "id": str(task_id),
            "task_type": task_type,
            "payload": json.dumps(payload),
            "scheduled_at": scheduled_at,
        },
    )
    return task_id


async def fetch_and_lock_next_task(
    session: AsyncSession,
    lock_duration_minutes: int = 5,
) -> Optional[Dict[str, Any]]:
    """Fetch next eligible task and acquire exclusive lock using FOR UPDATE SKIP LOCKED."""
    now = datetime.now(timezone.utc)
    lock_until = now + timedelta(minutes=lock_duration_minutes)

    stmt = text("""
        SELECT id, task_type, payload, retry_count
        FROM app_tasks
        WHERE (status = 'PENDING' AND scheduled_at <= :now)
           OR (status = 'PROCESSING' AND locked_until IS NOT NULL AND locked_until < :now)
        ORDER BY scheduled_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    """)
    result = await session.execute(stmt, {"now": now})
    row = result.first()
    if not row:
        return None

    task_id, task_type, raw_payload, retry_count = row
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)

    # Mark as PROCESSING with locked_until timestamp
    update_stmt = text("""
        UPDATE app_tasks
        SET status = 'PROCESSING', locked_until = :lock_until
        WHERE id = :id
    """)
    await session.execute(update_stmt, {"id": task_id, "lock_until": lock_until})

    return {
        "id": task_id,
        "task_type": task_type,
        "payload": payload,
        "retry_count": retry_count,
    }


async def mark_task_completed(session: AsyncSession, task_id: Any) -> None:
    """Mark task as successfully completed."""
    stmt = text("""
        UPDATE app_tasks
        SET status = 'COMPLETED', locked_until = NULL
        WHERE id = :id
    """)
    await session.execute(stmt, {"id": str(task_id)})


async def mark_task_failed(
    session: AsyncSession,
    task_id: Any,
    error_message: str = "",
    max_retries: int = 3,
) -> None:
    """Record task failure; either reschedule for retry with backoff or mark FAILED."""
    stmt = text("""
        SELECT retry_count FROM app_tasks WHERE id = :id
    """)
    result = await session.execute(stmt, {"id": str(task_id)})
    row = result.first()
    current_retries = row[0] if row else 0
    next_retry = current_retries + 1

    if next_retry >= max_retries:
        update_stmt = text("""
            UPDATE app_tasks
            SET status = 'FAILED', locked_until = NULL, retry_count = :retries
            WHERE id = :id
        """)
        await session.execute(update_stmt, {"id": str(task_id), "retries": next_retry})
    else:
        # Exponential backoff: 2^retry minutes
        delay_minutes = 2 ** current_retries
        next_schedule = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
        update_stmt = text("""
            UPDATE app_tasks
            SET status = 'PENDING',
                locked_until = NULL,
                retry_count = :retries,
                scheduled_at = :scheduled_at
            WHERE id = :id
        """)
        await session.execute(
            update_stmt,
            {"id": str(task_id), "retries": next_retry, "scheduled_at": next_schedule},
        )


async def process_next_task(
    session: AsyncSession,
    handlers: Dict[str, Callable[[AsyncSession, Dict[str, Any]], Any]],
) -> bool:
    """Lock, execute, and settle the next pending task. Returns True if a task was processed."""
    task = await fetch_and_lock_next_task(session)
    if not task:
        return False

    task_id = task["id"]
    task_type = task["task_type"]
    payload = task["payload"]

    handler = handlers.get(task_type)
    if not handler:
        logger.error("No registered handler for task type: %s", task_type)
        await mark_task_failed(session, task_id, error_message=f"No handler for {task_type}")
        return True

    try:
        await handler(session, payload)
        await mark_task_completed(session, task_id)
        logger.info("Successfully executed background task %s (%s)", task_id, task_type)
    except Exception as exc:
        logger.exception("Error executing task %s (%s): %s", task_id, task_type, exc)
        await mark_task_failed(session, task_id, error_message=str(exc))

    return True
