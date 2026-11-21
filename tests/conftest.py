"""Pytest fixtures for Digital Wellbeing backend test suite."""
import pytest
from app.core.database import engine


@pytest.fixture(autouse=True)
async def cleanup_database_connections():
    """Dispose connection pool between test cases to prevent Event loop is closed errors."""
    yield
    await engine.dispose()
