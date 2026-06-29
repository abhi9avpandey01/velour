"""
Velour API — Preference Service Tests.
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ChangedBy
from app.schemas.preferences import PreferenceProfileUpdate
from app.services.preferences_service import PreferencesService


@pytest.mark.asyncio
async def test_get_profile_creates_default_if_missing(db_session: AsyncSession, test_user) -> None:
    """Test getting a profile creates one if it doesn't exist."""
    service = PreferencesService(db_session)
    profile = await service.get_profile(test_user.id)
    
    assert profile is not None
    assert profile.user_id == test_user.id
    assert profile.preferred_colors == []
    assert profile.confidence_score == 1.0


@pytest.mark.asyncio
async def test_update_preferences_records_history(db_session: AsyncSession, test_user) -> None:
    """Test updating preferences generates correct history records."""
    service = PreferencesService(db_session)
    
    # First, ensure profile exists
    await service.get_profile(test_user.id)
    
    # Update preferences
    update_data = PreferenceProfileUpdate(
        preferred_colors=["red", "blue"],
        preferred_style="casual",
        changed_by=ChangedBy.USER,
        reason="Initial setup",
    )
    profile = await service.update_preferences(test_user.id, update_data)
    
    assert profile.preferred_colors == ["red", "blue"]
    assert profile.preferred_style == "casual"
    
    # Verify history
    history = await service.get_history(test_user.id)
    assert len(history) == 2  # One for preferred_colors, one for preferred_style
    
    fields_changed = [h.changed_field for h in history]
    assert "preferred_colors" in fields_changed
    assert "preferred_style" in fields_changed


@pytest.mark.asyncio
async def test_reset_preferences(db_session: AsyncSession, test_user) -> None:
    """Test resetting preferences clears values but preserves history."""
    service = PreferencesService(db_session)
    
    # Setup values
    await service.update_preferences(
        test_user.id,
        PreferenceProfileUpdate(preferred_colors=["red"], changed_by=ChangedBy.USER)
    )
    
    # Reset
    profile = await service.reset_preferences(test_user.id)
    
    assert profile.preferred_colors == []
    
    # History should have 1 setup change + 1 reset change
    history = await service.get_history(test_user.id)
    assert len(history) > 1
