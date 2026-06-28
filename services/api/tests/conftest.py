"""
Velour API — Test fixtures and configuration.

Provides shared fixtures for the test suite including
an async HTTP client configured for the FastAPI application.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.db.base import Base
from app.db.session import async_session_factory
from app.main import app

# Create a test database URL by replacing the DB name with a test DB
# In a real environment, you'd use a separate test database or mock this
# For now we use the main URL but ensure it points to a safe test DB if configured


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()
