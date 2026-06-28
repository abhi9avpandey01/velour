"""
Velour API — Health check endpoints.

Provides health and readiness checks for the API,
including database and Redis connectivity verification.
"""

from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint.

    Returns the service status without checking dependencies.
    Used by load balancers for simple liveness probes.
    """
    return {
        "status": "healthy",
        "service": "velour-api",
        "version": settings.app_version,
    }


@router.get("/health/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Readiness check that verifies all dependencies are available.

    Checks:
    - PostgreSQL connectivity
    - Redis connectivity

    Used by orchestrators to determine if the service can accept traffic.
    """
    checks: dict[str, Any] = {
        "status": "healthy",
        "service": "velour-api",
        "version": settings.app_version,
        "checks": {},
    }

    # ── PostgreSQL ────────────────────────────────
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["checks"]["postgres"] = {"status": "connected"}
    except Exception as exc:
        checks["status"] = "degraded"
        checks["checks"]["postgres"] = {
            "status": "disconnected",
            "error": str(exc),
        }

    # ── Redis ─────────────────────────────────────
    try:
        redis_client = aioredis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.aclose()
        checks["checks"]["redis"] = {"status": "connected"}
    except Exception as exc:
        checks["status"] = "degraded"
        checks["checks"]["redis"] = {
            "status": "disconnected",
            "error": str(exc),
        }

    return checks
