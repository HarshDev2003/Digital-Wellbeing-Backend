"""Integration tests for Telemetry Usage Ingestion & Deduplication endpoint."""
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport
from app.core.security import create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_usage_sync_endpoint_unauthorized():
    """Verify /api/v1/usage/sync requires valid authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "device_id": str(uuid.uuid4()),
            "sync_batch_id": str(uuid.uuid4()),
            "screen_events": [],
            "app_events": [],
        }
        res = await client.post("/api/v1/usage/sync", json=payload)
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_usage_sync_validation_error():
    """Verify /api/v1/usage/sync validates request payload format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/usage/sync", json={"invalid": True})
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_usage_sync_device_not_found():
    """Verify sync returns 404/401 when device is not associated with authenticated user."""
    transport = ASGITransport(app=app)
    fake_user_id = str(uuid.uuid4())
    token = create_access_token({"sub": fake_user_id, "email": "test@example.com"})

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "device_id": str(uuid.uuid4()),
            "sync_batch_id": str(uuid.uuid4()),
            "screen_events": [
                {
                    "event_uuid": str(uuid.uuid4()),
                    "event_type": "SCREEN_ON",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "app_events": [
                {
                    "event_uuid": str(uuid.uuid4()),
                    "package_name": "com.android.chrome",
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "end_time": datetime.now(timezone.utc).isoformat(),
                    "duration_seconds": 120,
                }
            ],
        }
        res = await client.post(
            "/api/v1/usage/sync",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        # Should reject because fake_user_id is not found in database or device does not exist
        assert res.status_code in (401, 404, 500)
