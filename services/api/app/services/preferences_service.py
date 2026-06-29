"""
Velour API — User Preference Service.
"""

import json
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ChangedBy
from app.models.preferences import PreferenceProfile, PreferenceHistory
from app.repositories.preferences_repository import PreferencesRepository
from app.schemas.preferences import PreferenceProfileCreate, PreferenceProfileUpdate


class PreferencesService:
    """Service for managing user preferences and their change history."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = PreferencesRepository(session)

    async def get_profile(self, user_id: uuid.UUID) -> PreferenceProfile:
        """Get or create the preference profile for a user."""
        profile = await self.repository.get_by_user_id(user_id)
        if not profile:
            profile = await self.create_profile(user_id, PreferenceProfileCreate())
        return profile

    async def create_profile(
        self, user_id: uuid.UUID, data: PreferenceProfileCreate
    ) -> PreferenceProfile:
        """Create a new preference profile for a user."""
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise ValueError("Preference profile already exists for user.")

        profile = PreferenceProfile(
            user_id=user_id,
            **data.model_dump(exclude_unset=True)
        )
        await self.repository.create(profile)
        return profile

    async def update_preferences(
        self,
        user_id: uuid.UUID,
        data: PreferenceProfileUpdate,
    ) -> PreferenceProfile:
        """Update a user's preference profile and record history of changes."""
        profile = await self.get_profile(user_id)
        update_data = data.model_dump(exclude_unset=True, exclude={"changed_by", "reason"})

        # Record changes for history
        for field, new_value in update_data.items():
            old_value = getattr(profile, field, None)
            
            # Compare JSON serializable versions if necessary (lists vs lists)
            if old_value != new_value:
                await self.record_change(
                    profile_id=profile.id,
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=data.changed_by,
                    reason=data.reason,
                )

        # Apply updates
        for field, value in update_data.items():
            setattr(profile, field, value)
            
        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

    async def record_change(
        self,
        profile_id: uuid.UUID,
        field: str,
        old_value: any,
        new_value: any,
        changed_by: ChangedBy,
        reason: str | None,
    ) -> None:
        """Record a single field change into the history table."""
        def _serialize(val: any) -> str | None:
            if val is None:
                return None
            if isinstance(val, list):
                return json.dumps(val)
            return str(val)

        history = PreferenceHistory(
            preference_profile_id=profile_id,
            changed_field=field,
            previous_value=_serialize(old_value),
            new_value=_serialize(new_value),
            changed_by=changed_by.value,
            reason=reason,
        )
        await self.repository.add_history_record(history)

    async def get_history(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[PreferenceHistory]:
        """Retrieve the change history for a user's preferences."""
        profile = await self.get_profile(user_id)
        return await self.repository.get_history(profile.id, skip=skip, limit=limit)

    async def reset_preferences(self, user_id: uuid.UUID) -> PreferenceProfile:
        """Reset a user's preferences to defaults without losing history."""
        # This will update all fields to their defaults and log changes
        reset_data = PreferenceProfileUpdate(
            preferred_colors=[],
            disliked_colors=[],
            preferred_categories=[],
            disliked_categories=[],
            preferred_occasions=[],
            preferred_fit=None,
            preferred_style=None,
            favorite_brands=[],
            avoided_brands=[],
            preferred_materials=[],
            disliked_materials=[],
            climate_preference=None,
            changed_by=ChangedBy.USER,
            reason="User initiated reset",
        )
        return await self.update_preferences(user_id, reset_data)
