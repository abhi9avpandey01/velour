"""
Velour API — Authentication service.

Handles all authentication business logic: registration, login,
token refresh, logout, and password reset. Uses dependency injection
for the repository and Redis client.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.redis import blacklist_token, is_token_blacklisted
from app.core.security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """Service layer for authentication operations.

    Encapsulates all business logic for user registration,
    login, token management, and password reset flows.

    Args:
        session: The async database session for this request.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, data: UserCreate) -> UserResponse:
        """Register a new user account.

        Validates password strength, checks email/username uniqueness,
        hashes the password, and creates the user record.

        Args:
            data: Registration data including email, username, and password.

        Returns:
            The newly created user's public profile.

        Raises:
            ValidationError: If the password does not meet strength requirements.
            ConflictError: If the email or username is already taken.
        """
        # Validate password strength
        password_errors = validate_password_strength(data.password)
        if password_errors:
            raise ValidationError(
                message="Password does not meet requirements.",
                details={"errors": password_errors},
            )

        # Check email uniqueness
        if await self._repo.exists_by_email(data.email):
            raise ConflictError(
                message="A user with this email already exists.",
                code="EMAIL_TAKEN",
            )

        # Check username uniqueness
        if await self._repo.exists_by_username(data.username):
            raise ConflictError(
                message="A user with this username already exists.",
                code="USERNAME_TAKEN",
            )

        # Create user
        user = User(
            email=data.email.lower(),
            username=data.username.lower(),
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )

        created_user = await self._repo.create(user)
        return self._to_response(created_user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user and issue JWT tokens.

        Verifies the email and password, updates the last login timestamp,
        and returns an access/refresh token pair.

        Args:
            email: The user's email address.
            password: The user's plaintext password.

        Returns:
            A JWT token pair (access + refresh).

        Raises:
            AuthenticationError: If the credentials are invalid or the account is inactive.
        """
        user = await self._repo.get_by_email(email.lower())

        if user is None:
            raise AuthenticationError(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )

        if not verify_password(password, user.password_hash):
            raise AuthenticationError(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise AuthenticationError(
                message="This account has been deactivated.",
                code="ACCOUNT_INACTIVE",
            )

        # Update last login
        await self._repo.update_last_login(user.id)

        # Issue tokens
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """Exchange a valid refresh token for a new token pair.

        Validates the refresh token, checks blacklist status,
        blacklists the old refresh token, and issues new tokens.

        Args:
            refresh_token_str: The refresh token to exchange.

        Returns:
            A new JWT token pair.

        Raises:
            AuthenticationError: If the refresh token is invalid, expired, or blacklisted.
        """
        try:
            payload = decode_token(refresh_token_str)
        except JWTError:
            raise AuthenticationError(
                message="Invalid or expired refresh token.",
                code="INVALID_REFRESH_TOKEN",
            )

        if payload.get("type") != "refresh":
            raise AuthenticationError(
                message="Invalid token type. Expected a refresh token.",
                code="INVALID_TOKEN_TYPE",
            )

        jti = payload.get("jti", "")
        if await is_token_blacklisted(jti):
            raise AuthenticationError(
                message="This refresh token has been revoked.",
                code="TOKEN_REVOKED",
            )

        # Blacklist the old refresh token
        exp = payload.get("exp", 0)
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = max(exp - now, 0)
        if ttl > 0:
            await blacklist_token(jti, ttl)

        user_id = payload["sub"]

        # Verify user still exists and is active
        user = await self._repo.get_by_id(uuid.UUID(user_id))
        if user is None or not user.is_active:
            raise AuthenticationError(
                message="User account not found or inactive.",
                code="USER_INACTIVE",
            )

        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def logout(self, token: str) -> None:
        """Revoke a JWT token by adding it to the blacklist.

        Args:
            token: The JWT access or refresh token to revoke.

        Raises:
            AuthenticationError: If the token is malformed.
        """
        try:
            payload = decode_token(token)
        except JWTError:
            raise AuthenticationError(
                message="Invalid token.",
                code="INVALID_TOKEN",
            )

        jti = payload.get("jti", "")
        exp = payload.get("exp", 0)
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = max(exp - now, 0)

        if ttl > 0:
            await blacklist_token(jti, ttl)

    async def request_password_reset(self, email: str) -> None:
        """Initiate a password reset flow.

        Generates a reset token for the user. The actual email
        delivery is deferred to a future email service integration.

        Args:
            email: The email address of the account to reset.

        Note:
            This method intentionally does not reveal whether the email
            exists to prevent user enumeration attacks.
        """
        user = await self._repo.get_by_email(email.lower())
        if user is None:
            # Silently return — do not reveal whether the email exists
            return

        # Generate a short-lived reset token (15 minutes)
        _reset_token = create_access_token(
            str(user.id),
        )

        # Email delivery will be implemented when email service is added.
        # The reset token would be sent via email.

    async def reset_password(self, token: str, new_password: str) -> None:
        """Complete a password reset using a reset token.

        Args:
            token: The password reset token.
            new_password: The new password to set.

        Raises:
            AuthenticationError: If the reset token is invalid or expired.
            ValidationError: If the new password doesn't meet requirements.
            NotFoundError: If the user associated with the token no longer exists.
        """
        # Validate new password
        password_errors = validate_password_strength(new_password)
        if password_errors:
            raise ValidationError(
                message="New password does not meet requirements.",
                details={"errors": password_errors},
            )

        try:
            payload = decode_token(token)
        except JWTError:
            raise AuthenticationError(
                message="Invalid or expired reset token.",
                code="INVALID_RESET_TOKEN",
            )

        user_id = payload["sub"]
        user = await self._repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise NotFoundError(message="User not found.")

        await self._repo.update_password(user.id, hash_password(new_password))

    @staticmethod
    def _to_response(user: User) -> UserResponse:
        """Convert a User ORM model to a UserResponse schema.

        Args:
            user: The User ORM model instance.

        Returns:
            A UserResponse with all public fields.
        """
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_picture_url=user.profile_picture_url,
            gender=user.gender,
            date_of_birth=user.date_of_birth,
            timezone=user.timezone,
            preferred_language=user.preferred_language,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )
