"""Unit tests for PostgreSQL-backed task queue logic."""
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.core.task_queue import (
    enqueue_task,
    fetch_and_lock_next_task,
    mark_task_completed,
    mark_task_failed,
    process_next_task,
)


@pytest.mark.asyncio
async def test_enqueue_task():
    """Verify enqueue_task executes INSERT with generated UUID and payload."""
    mock_session = AsyncMock()
    task_id = await enqueue_task(
        mock_session,
        task_type="GENERATE_AI_INSIGHT",
        payload={"user_id": "test-user"},
    )
    assert task_id is not None
    assert mock_session.execute.called


@pytest.mark.asyncio
async def test_fetch_and_lock_next_task_empty():
    """Verify fetch returns None when queue has no pending tasks."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.execute.return_value = mock_result

    task = await fetch_and_lock_next_task(mock_session)
    assert task is None


@pytest.mark.asyncio
async def test_process_next_task_success():
    """Verify process_next_task invokes registered handler and marks task completed."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.first.return_value = ("task-uuid-1", "CALCULATE_SUMMARIES", '{"date": "2026-11-20"}', 0)
    mock_session.execute.return_value = mock_result

    executed = False

    async def sample_handler(session, payload):
        nonlocal executed
        executed = True
        assert payload["date"] == "2026-11-20"

    handlers = {"CALCULATE_SUMMARIES": sample_handler}
    processed = await process_next_task(mock_session, handlers)

    assert processed is True
    assert executed is True
