"""
Velour API — User Preference Repository.
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preferences import PreferenceProfile, PreferenceHistory
from app.repositories.base import BaseRepository


class PreferencesRepository(BaseRepository[PreferenceProfile]):
    """Repository for managing user preference profiles and history."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=PreferenceProfile, session=session)
        self._history_model = PreferenceHistory

    async def get_by_user_id(self, user_id: uuid.UUID) -> PreferenceProfile | None:
        """Retrieve a user's preference profile."""
        stmt = select(self._model).where(
            self._model.user_id == user_id,
            self._model.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(
        self,
        profile_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[PreferenceHistory]:
        """Retrieve the change history for a preference profile."""
        stmt = (
            select(self._history_model)
            .where(
                self._history_model.preference_profile_id == profile_id,
                self._history_model.is_deleted.is_(False),
            )
            .order_by(self._history_model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add_history_record(self, record: PreferenceHistory) -> PreferenceHistory:
        """Insert a single history record."""
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def hard_delete_profile(self, user_id: uuid.UUID) -> bool:
        """Hard delete a preference profile to allow reset/recreate."""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return False
        
        await self._session.delete(profile)
        await self._session.flush()
        return True
