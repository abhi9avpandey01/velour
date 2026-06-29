"""
Velour API — Application lifespan events.

Manages startup and shutdown logic for database connections,
Redis connections, and other resources.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown."""
    # ── Startup ───────────────────────────────────
    print(f"Velour API starting in {'development' if settings.is_development else 'production'} mode")
    print(f"Database: {settings.database_url}")
    print(f"Redis: {settings.redis_url}")

    yield

    # ── Shutdown ──────────────────────────────────
    print("Velour API shutting down")
    await async_engine.dispose()
    print("Database connections closed")
