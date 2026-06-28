"""
Velour API — User repository.

Data access layer for User entities. Extends BaseRepository
with user-specific query methods.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User CRUD and query operations.

    Provides methods for looking up users by email/username,
    checking existence, and updating authentication-related fields.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email address.

        Args:
            email: The email address to search for (case-insensitive).

        Returns:
            The User if found and not soft-deleted, None otherwise.
        """
        stmt = select(User).where(
            User.email == email.lower(),
            User.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Find a user by username.

        Args:
            username: The username to search for (case-insensitive).

        Returns:
            The User if found and not soft-deleted, None otherwise.
        """
        stmt = select(User).where(
            User.username == username.lower(),
            User.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists.

        Args:
            email: The email address to check.

        Returns:
            True if a non-deleted user with this email exists.
        """
        stmt = select(User.id).where(
            User.email == email.lower(),
            User.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if a user with the given username exists.

        Args:
            username: The username to check.

        Returns:
            True if a non-deleted user with this username exists.
        """
        stmt = select(User.id).where(
            User.username == username.lower(),
            User.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update the last_login timestamp for a user.

        Args:
            user_id: The UUID of the user who just logged in.
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def update_password(self, user_id: uuid.UUID, password_hash: str) -> None:
        """Update the password hash for a user.

        Args:
            user_id: The UUID of the user whose password is being changed.
            password_hash: The new Argon2id password hash.
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
        )
        await self._session.execute(stmt)
        await self._session.flush()
