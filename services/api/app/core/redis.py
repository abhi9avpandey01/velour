"""
Velour API — Redis client utilities.

Provides a shared async Redis client and token blacklisting functions.
Used for JWT token revocation on logout.
"""

import redis.asyncio as aioredis

from app.core.config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Get or create the shared async Redis client.

    Returns:
        An async Redis client instance connected to the configured Redis URL.
    """
    global _redis_client  # noqa: PLW0603
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    """Close the shared Redis client connection."""
    global _redis_client  # noqa: PLW0603
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


async def blacklist_token(jti: str, expires_in: int) -> None:
    """Add a JWT token ID to the blacklist in Redis.

    Blacklisted tokens are stored with a TTL matching the token's
    remaining lifetime, so they are automatically cleaned up.

    Args:
        jti: The unique JWT token identifier (jti claim).
        expires_in: Time in seconds until the blacklist entry expires.
    """
    client = await get_redis_client()
    await client.setex(f"token_blacklist:{jti}", expires_in, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a JWT token ID has been blacklisted.

    Args:
        jti: The unique JWT token identifier (jti claim).

    Returns:
        True if the token is blacklisted (revoked), False otherwise.
    """
    client = await get_redis_client()
    result = await client.get(f"token_blacklist:{jti}")
    return result is not None
