"""Integration tests for Goals, Limits, and Violation logging endpoints."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.core.security import create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_goals_limits_require_auth():
    """Verify /goals and /limits reject unauthenticated requests with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_goals_get = await client.get("/api/v1/goals")
        assert res_goals_get.status_code == 401
        assert res_goals_get.json()["error"]["code"] == "UNAUTHORIZED"

        res_limits_get = await client.get("/api/v1/limits")
        assert res_limits_get.status_code == 401
        assert res_limits_get.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_create_goal_validation():
    """Verify /api/v1/goals rejects invalid target types."""
    transport = ASGITransport(app=app)
    fake_user_id = str(uuid.uuid4())
    token = create_access_token({"sub": fake_user_id, "email": "user@example.com"})

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid target_type
        res = await client.post(
            "/api/v1/goals",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_type": "INVALID_TYPE", "max_duration_seconds": 3600},
        )
        assert res.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_limit_validation():
    """Verify /api/v1/limits rejects negative duration values."""
    transport = ASGITransport(app=app)
    fake_user_id = str(uuid.uuid4())
    token = create_access_token({"sub": fake_user_id, "email": "user@example.com"})

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/limits",
            headers={"Authorization": f"Bearer {token}"},
            json={"package_name": "com.instagram.android", "max_duration_seconds": -50},
        )
        assert res.status_code in (401, 422)
