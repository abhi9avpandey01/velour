"""
Velour API — User management service.

Handles user profile retrieval and updates.
Business logic for user operations is isolated here.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    """Service layer for user profile operations.

    Provides read and update access to user profiles.

    Args:
        session: The async database session for this request.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        """Retrieve the current user's profile.

        Args:
            user_id: The UUID of the authenticated user.

        Returns:
            The user's public profile data.

        Raises:
            NotFoundError: If the user does not exist or is soft-deleted.
        """
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(message="User not found.")
        return self._to_response(user)

    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: UserUpdate,
    ) -> UserResponse:
        """Update the current user's profile.

        Only fields explicitly provided in the update data are modified.
        None values in optional fields are preserved (not overwritten).

        Args:
            user_id: The UUID of the authenticated user.
            data: The profile fields to update.

        Returns:
            The updated user profile.

        Raises:
            NotFoundError: If the user does not exist.
        """
        # Filter out None values — only update fields that were explicitly set
        update_data: dict[str, Any] = {
            key: value
            for key, value in data.model_dump(exclude_unset=True).items()
            if value is not None
        }

        if not update_data:
            # Nothing to update — return current profile
            return await self.get_current_user(user_id)

        updated_user = await self._repo.update_by_id(user_id, update_data)
        if updated_user is None:
            raise NotFoundError(message="User not found.")

        return self._to_response(updated_user)

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
