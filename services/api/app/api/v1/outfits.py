"""
Velour API — Outfits Endpoints.

REST APIs for fetching and viewing outfits.
"""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.outfit_repository import OutfitRepository
from app.schemas.common import ApiResponse
from app.schemas.recommendations import OutfitSchema

router = APIRouter(prefix="/outfits", tags=["Outfits"])


@router.get(
    "/",
    response_model=ApiResponse[List[OutfitSchema]],
    summary="List user outfits",
)
async def list_outfits(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[List[OutfitSchema]]:
    """Fetches all outfits belonging to the current user."""
    repo = OutfitRepository(db)
    outfits = await repo.list_by_user(user_id=current_user.id, limit=limit, offset=skip)
    
    # Normally we would serialize items too, but for scope we return base outfits
    # The Pydantic model will automatically extract fields due to `from_attributes=True`
    return ApiResponse.ok([OutfitSchema.model_validate(o) for o in outfits])
