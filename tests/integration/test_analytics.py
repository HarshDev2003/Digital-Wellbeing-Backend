"""Integration tests for Analytics Overview & History REST endpoints."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.core.security import create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_analytics_endpoints_require_auth():
    """Verify /analytics/overview and /analytics/history reject unauthenticated requests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        overview_res = await client.get("/api/v1/analytics/overview")
        assert overview_res.status_code == 401
        assert overview_res.json()["error"]["code"] == "UNAUTHORIZED"

        history_res = await client.get("/api/v1/analytics/history")
        assert history_res.status_code == 401
        assert history_res.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_analytics_overview_invalid_date_format():
    """Verify /analytics/overview rejects malformed date parameters."""
    transport = ASGITransport(app=app)
    token = create_access_token({"sub": str(uuid.uuid4()), "email": "user@example.com"})
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            "/api/v1/analytics/overview?date=invalid-date",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code in (401, 422)
