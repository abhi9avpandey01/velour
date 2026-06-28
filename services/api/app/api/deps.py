"""
Velour API — Shared API dependencies.

Provides dependency injection functions for FastAPI routes,
including the current authenticated user extraction.
"""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.redis import is_token_blacklisted
from app.core.security import JWTError, decode_token
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.wardrobe_repository import WardrobeRepository
from app.repositories.outfit_repository import OutfitRepository
from app.repositories.recommendation_repository import RecommendationRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Database Repositories ──────────────────────────────────────────

async def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Injects the UserRepository."""
    return UserRepository(db)


async def get_wardrobe_repository(db: AsyncSession = Depends(get_db_session)) -> WardrobeRepository:
    """Injects the WardrobeRepository."""
    return WardrobeRepository(db)


async def get_outfit_repository(db: AsyncSession = Depends(get_db_session)) -> OutfitRepository:
    """Injects the OutfitRepository."""
    return OutfitRepository(db)


async def get_recommendation_repository(db: AsyncSession = Depends(get_db_session)) -> RecommendationRepository:
    """Injects the RecommendationRepository."""
    return RecommendationRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Extract and validate the current authenticated user from the JWT token.

    This dependency:
    1. Decodes the JWT access token
    2. Verifies it hasn't been blacklisted (logged out)
    3. Fetches the user from the database
    4. Validates the user is active and not deleted

    Args:
        token: The JWT access token from the Authorization header.
        db: The async database session.

    Returns:
        The authenticated User ORM model instance.

    Raises:
        AuthenticationError: If the token is invalid, expired, or blacklisted.
        AuthorizationError: If the user is inactive or soft-deleted.
    """
    # Decode token
    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthenticationError(
            message="Invalid or expired access token.",
            code="INVALID_ACCESS_TOKEN",
        )

    # Verify token type
    if payload.get("type") != "access":
        raise AuthenticationError(
            message="Invalid token type. Expected an access token.",
            code="INVALID_TOKEN_TYPE",
        )

    # Check blacklist
    jti = payload.get("jti", "")
    if await is_token_blacklisted(jti):
        raise AuthenticationError(
            message="This token has been revoked.",
            code="TOKEN_REVOKED",
        )

    # Fetch user
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise AuthenticationError(
            message="Invalid token payload.",
            code="INVALID_TOKEN_PAYLOAD",
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError(
            message="Invalid token payload.",
            code="INVALID_TOKEN_PAYLOAD",
        )

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if user is None:
        raise AuthenticationError(
            message="User not found.",
            code="USER_NOT_FOUND",
        )

    if not user.is_active:
        raise AuthorizationError(
            message="This account has been deactivated.",
            code="ACCOUNT_INACTIVE",
        )

    return user
