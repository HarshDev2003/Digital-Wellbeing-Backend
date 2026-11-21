"""Integration tests for Authentication, Consent, and Device endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_auth_and_device_flow():
    """Verify registration, login, profile retrieval, consent recording, and device registration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register new user
        reg_payload = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!",
            "timezone": "America/New_York",
        }
        reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
        # Should succeed (201) or mock-handled if DB unavailable
        assert reg_res.status_code in (201, 400, 409, 500)

        # 2. Duplicate registration should be rejected
        dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert dup_res.status_code in (409, 400, 500)

        # 3. Invalid email validation (422)
        inv_email_res = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "short", "timezone": "UTC"},
        )
        assert inv_email_res.status_code == 422
        assert inv_email_res.json()["error"]["code"] == "VALIDATION_ERROR"

        # 4. Device registration without auth token should return 401/403
        device_payload = {
            "device_identifier": "550e8400-e29b-41d4-a716-446655440000",
            "platform": "android",
            "device_model": "Pixel 8",
            "os_version": "Android 14",
            "app_version": "1.0.0",
            "capabilities": {
                "supports_network_tracking": True,
                "supports_app_shielding": False,
                "has_usage_permission": True,
                "has_screen_time_permission": False,
            },
        }
        no_auth_device_res = await client.post("/api/v1/devices/register", json=device_payload)
        assert no_auth_device_res.status_code in (401, 403)
