"""
Velour API — Preference Repository Tests.
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preferences import PreferenceProfile, PreferenceHistory
from app.models.enums import PreferenceSource, ChangedBy
from app.repositories.preferences_repository import PreferencesRepository


@pytest.mark.asyncio
async def test_create_and_get_preference_profile(db_session: AsyncSession, test_user) -> None:
    """Test creating and retrieving a preference profile."""
    repo = PreferencesRepository(db_session)
    
    profile = PreferenceProfile(
        user_id=test_user.id,
        preferred_colors=["black", "navy"],
        disliked_colors=["yellow"],
        preferred_style="minimalist",
        source=PreferenceSource.MANUAL.value,
    )
    
    created = await repo.create(profile)
    assert created.id is not None
    assert created.user_id == test_user.id
    assert "black" in created.preferred_colors
    
    # Retrieve
    retrieved = await repo.get_by_user_id(test_user.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.preferred_colors == ["black", "navy"]


@pytest.mark.asyncio
async def test_add_and_get_history_records(db_session: AsyncSession, test_user) -> None:
    """Test adding and retrieving history records."""
    repo = PreferencesRepository(db_session)
    
    # Create profile
    profile = PreferenceProfile(user_id=test_user.id)
    created_profile = await repo.create(profile)
    
    # Add history
    history = PreferenceHistory(
        preference_profile_id=created_profile.id,
        changed_field="preferred_colors",
        previous_value="[]",
        new_value='["red"]',
        changed_by=ChangedBy.USER.value,
    )
    await repo.add_history_record(history)
    
    # Retrieve history
    history_records = await repo.get_history(created_profile.id)
    assert len(history_records) == 1
    assert history_records[0].changed_field == "preferred_colors"
    assert history_records[0].new_value == '["red"]'


@pytest.mark.asyncio
async def test_hard_delete_profile(db_session: AsyncSession, test_user) -> None:
    """Test hard deleting a preference profile."""
    repo = PreferencesRepository(db_session)
    
    # Create profile
    profile = PreferenceProfile(user_id=test_user.id)
    await repo.create(profile)
    
    # Assert exists
    assert await repo.get_by_user_id(test_user.id) is not None
    
    # Delete
    result = await repo.hard_delete_profile(test_user.id)
    assert result is True
    
    # Assert deleted
    assert await repo.get_by_user_id(test_user.id) is None
