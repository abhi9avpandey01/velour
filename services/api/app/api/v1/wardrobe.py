"""
Velour API — Wardrobe endpoints.

CRUD and management routes for WardrobeItem entities.
Every route is protected and scoped to the authenticated user.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.wardrobe import (
    WardrobeFilterParams,
    WardrobeItemCreate,
    WardrobeItemResponse,
    WardrobeItemUpdate,
)
from app.services.wardrobe_service import WardrobeService

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])


@router.post(
    "",
    response_model=ApiResponse[WardrobeItemResponse],
    status_code=201,
    summary="Create a wardrobe item",
    description="Add a new clothing item to the user's wardrobe.",
)
async def create_wardrobe_item(
    data: WardrobeItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[WardrobeItemResponse]:
    """Create a new wardrobe item."""
    service = WardrobeService(db)
    item = await service.create_item(current_user.id, data)
    return ApiResponse.ok(item)


@router.get(
    "",
    response_model=ApiResponse[list[WardrobeItemResponse]],
    summary="List wardrobe items",
    description="Get a paginated, filterable list of wardrobe items.",
)
async def list_wardrobe_items(
    filters: WardrobeFilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[list[WardrobeItemResponse]]:
    """List wardrobe items with filters."""
    service = WardrobeService(db)
    items, total = await service.list_items(current_user.id, filters)
    
    meta = {
        "total": total,
        "skip": filters.skip,
        "limit": filters.limit,
    }
    return ApiResponse.ok(items, meta=meta)


@router.get(
    "/{item_id}",
    response_model=ApiResponse[WardrobeItemResponse],
    summary="Get a wardrobe item",
    description="Retrieve a specific wardrobe item by its UUID.",
)
async def get_wardrobe_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[WardrobeItemResponse]:
    """Get a wardrobe item by ID."""
    service = WardrobeService(db)
    item = await service.get_item(current_user.id, item_id)
    return ApiResponse.ok(item)


@router.patch(
    "/{item_id}",
    response_model=ApiResponse[WardrobeItemResponse],
    summary="Update a wardrobe item",
    description="Partially update a wardrobe item.",
)
async def update_wardrobe_item(
    item_id: uuid.UUID,
    data: WardrobeItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[WardrobeItemResponse]:
    """Update a wardrobe item."""
    service = WardrobeService(db)
    item = await service.update_item(current_user.id, item_id, data)
    return ApiResponse.ok(item)


@router.delete(
    "/{item_id}",
    response_model=ApiResponse[None],
    summary="Delete a wardrobe item",
    description="Soft-delete a wardrobe item.",
)
async def delete_wardrobe_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[None]:
    """Delete a wardrobe item."""
    service = WardrobeService(db)
    await service.delete_item(current_user.id, item_id)
    return ApiResponse(success=True, data=None)


@router.post(
    "/{item_id}/favorite",
    response_model=ApiResponse[WardrobeItemResponse],
    summary="Toggle favorite status",
    description="Toggle whether this item is favorited.",
)
async def toggle_favorite(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[WardrobeItemResponse]:
    """Toggle the favorite status of an item."""
    service = WardrobeService(db)
    item = await service.toggle_favorite(current_user.id, item_id)
    return ApiResponse.ok(item)


@router.post(
    "/{item_id}/archive",
    response_model=ApiResponse[WardrobeItemResponse],
    summary="Toggle archived status",
    description="Toggle whether this item is archived.",
)
async def toggle_archive(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[WardrobeItemResponse]:
    """Toggle the archived status of an item."""
    service = WardrobeService(db)
    item = await service.toggle_archive(current_user.id, item_id)
    return ApiResponse.ok(item)
