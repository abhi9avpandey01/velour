"""
Velour API — Rate limiting configuration.

Configures slowapi rate limiter with Redis as the storage backend.
Applied globally to the FastAPI application.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_general],
    storage_uri=settings.redis_url,
)


def setup_rate_limiting(app):  # type: ignore[no-untyped-def]
    """Configure rate limiting on the FastAPI application.

    Registers the slowapi limiter and its exception handler.

    Args:
        app: The FastAPI application instance.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
