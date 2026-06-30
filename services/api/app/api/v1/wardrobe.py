"""
Velour API — Wardrobe endpoints.

CRUD and management routes for WardrobeItem entities.
Every route is protected and scoped to the authenticated user.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.image_asset import ImageAsset
from app.models.user import User
from app.models.wardrobe import WardrobeItem
from app.schemas.common import ApiResponse
from app.schemas.wardrobe import (
    WardrobeFilterParams,
    WardrobeItemCreate,
    WardrobeItemResponse,
    WardrobeItemUpdate,
)
from app.services.wardrobe_service import WardrobeService

logger = logging.getLogger(__name__)

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


@router.post(
    "/{item_id}/analyze",
    response_model=ApiResponse[dict[str, Any]],
    summary="Analyze wardrobe item with AI",
    description=(
        "Runs the full AI vision pipeline (background removal, Florence-2 attribute "
        "extraction, CLIP embedding) synchronously and returns the extracted attributes."
    ),
)
async def analyze_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[dict[str, Any]]:
    """Trigger synchronous AI analysis for a wardrobe item.

    Looks up the ImageAsset linked to the given item and runs the
    VisionService pipeline.  Returns extracted attributes such as
    category, color, material, and pattern.
    """
    # Verify ownership
    item = await db.get(WardrobeItem, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Wardrobe item not found.")

    # Find the image asset for this item
    stmt = (
        select(ImageAsset)
        .where(ImageAsset.wardrobe_item_id == item_id)
        .order_by(ImageAsset.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=404, detail="No image asset found for this item."
        )

    logger.info(f"Starting AI analysis for item {item_id}, asset {asset.id}")

    # Lazy import to avoid loading heavy AI dependencies at module level
    from app.services.vision_service import VisionService

    vision = VisionService(db)
    attributes = await vision.process_image(str(asset.id))

    return ApiResponse.ok({
        "item_id": str(item_id),
        "asset_id": str(asset.id),
        "attributes": attributes,
    })
