"""Unit tests for base API router and global exception handlers."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoints():
    """Verify root /health and /api/v1/health endpoints return 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        root_res = await client.get("/health")
        assert root_res.status_code == 200
        assert root_res.json()["status"] == "healthy"

        v1_res = await client.get("/api/v1/health")
        assert v1_res.status_code == 200
        assert v1_res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_404_error_contract():
    """Verify unmapped routes return standardized error JSON format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/nonexistent-route")
        assert res.status_code == 404
        data = res.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
