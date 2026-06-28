"""
Velour API — Authentication endpoints.

POST /api/v1/auth/register  — Create a new user account
POST /api/v1/auth/login     — Authenticate and receive JWT tokens
POST /api/v1/auth/logout    — Revoke the current JWT token
POST /api/v1/auth/refresh   — Exchange a refresh token for new tokens
"""

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, oauth2_scheme
from app.core.config import settings
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=201,
    summary="Register a new user",
    description="Create a new user account with email, username, and password.",
)
@limiter.limit(settings.rate_limit_auth)
async def register(
    request: Request,  # noqa: ARG001
    data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[UserResponse]:
    """Register a new user account.

    Validates input, checks uniqueness, hashes password, and creates the user.
    """
    service = AuthService(db)
    user = await service.register(data)
    return ApiResponse.ok(user)


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="Login",
    description="Authenticate with email and password to receive JWT tokens.",
)
@limiter.limit(settings.rate_limit_auth)
async def login(
    request: Request,  # noqa: ARG001
    data: UserLogin,
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[TokenResponse]:
    """Authenticate a user and return JWT tokens."""
    service = AuthService(db)
    tokens = await service.login(data.email, data.password)
    return ApiResponse.ok(tokens)


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="Logout",
    description="Revoke the current JWT access token.",
)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Revoke the current access token by adding it to the blacklist."""
    service = AuthService(db)
    await service.logout(token)
    return ApiResponse(success=True, data=None)


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    summary="Refresh tokens",
    description="Exchange a valid refresh token for a new access/refresh token pair.",
)
@limiter.limit(settings.rate_limit_auth)
async def refresh(
    request: Request,  # noqa: ARG001
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[TokenResponse]:
    """Exchange a refresh token for new tokens."""
    service = AuthService(db)
    tokens = await service.refresh_token(data.refresh_token)
    return ApiResponse.ok(tokens)
