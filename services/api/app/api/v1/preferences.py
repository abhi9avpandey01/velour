"""
Velour API — User Preference Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.preferences import (
    PreferenceProfileResponse,
    PreferenceProfileUpdate,
    PreferenceHistoryResponse,
)
from app.services.preferences_service import PreferencesService

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get(
    "",
    response_model=ApiResponse[PreferenceProfileResponse],
    summary="Get user preferences",
    description="Retrieve the authenticated user's fashion preferences.",
)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[PreferenceProfileResponse]:
    """Get user preference profile."""
    service = PreferencesService(db)
    profile = await service.get_profile(current_user.id)
    return ApiResponse.ok(profile)


@router.patch(
    "",
    response_model=ApiResponse[PreferenceProfileResponse],
    summary="Update user preferences",
    description="Update the authenticated user's fashion preferences. Automatically tracks history.",
)
async def update_preferences(
    data: PreferenceProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[PreferenceProfileResponse]:
    """Update user preference profile."""
    service = PreferencesService(db)
    profile = await service.update_preferences(current_user.id, data)
    return ApiResponse.ok(profile)


@router.get(
    "/history",
    response_model=ApiResponse[list[PreferenceHistoryResponse]],
    summary="Get preference change history",
    description="Retrieve the history of changes made to the user's preferences.",
)
async def get_preference_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[list[PreferenceHistoryResponse]]:
    """Get preference change history."""
    service = PreferencesService(db)
    history = await service.get_history(current_user.id, skip=skip, limit=limit)
    meta = {
        "skip": skip,
        "limit": limit,
    }
    return ApiResponse.ok(history, meta=meta)


@router.post(
    "/reset",
    response_model=ApiResponse[PreferenceProfileResponse],
    summary="Reset user preferences",
    description="Reset the user's preferences to defaults. History is preserved.",
)
async def reset_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[PreferenceProfileResponse]:
    """Reset user preference profile."""
    service = PreferencesService(db)
    profile = await service.reset_preferences(current_user.id)
    return ApiResponse.ok(profile)
