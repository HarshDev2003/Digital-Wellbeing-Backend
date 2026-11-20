"""Unit tests for Settings and environment configuration."""
import pytest
from app.core.config import Settings


def test_default_settings():
    """Verify default configurations adhere to architectural requirements."""
    settings = Settings()
    assert "postgresql+asyncpg" in settings.DATABASE_URL
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 30
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_cors_origins_parsing():
    """Verify comma-separated and JSON string formats parse cleanly into lists."""
    settings_str = Settings(CORS_ORIGINS="http://localhost:3000, https://app.example.com")
    assert "http://localhost:3000" in settings_str.CORS_ORIGINS
    assert "https://app.example.com" in settings_str.CORS_ORIGINS
    assert len(settings_str.CORS_ORIGINS) == 2

    settings_json = Settings(CORS_ORIGINS='["http://localhost:3000", "https://app.example.com"]')
    assert len(settings_json.CORS_ORIGINS) == 2
