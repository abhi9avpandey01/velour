"""
Velour API — Wardrobe service.

Handles all business logic for wardrobe management, including creating,
updating, toggling states, and deleting items. Ensures all operations
are strictly scoped to the authenticated user.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.wardrobe import WardrobeItem
from app.repositories.wardrobe_repository import WardrobeRepository
from app.schemas.wardrobe import (
    WardrobeFilterParams,
    WardrobeItemCreate,
    WardrobeItemResponse,
    WardrobeItemUpdate,
)


class WardrobeService:
    """Service layer for wardrobe operations.

    Encapsulates business logic and strictly enforces tenant isolation
    by requiring user_id on every operation.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = WardrobeRepository(session)

    async def create_item(
        self,
        user_id: uuid.UUID,
        data: WardrobeItemCreate,
    ) -> WardrobeItemResponse:
        """Create a new wardrobe item for the user.

        Args:
            user_id: The UUID of the authenticated user.
            data: The item creation data.

        Returns:
            The created wardrobe item profile.
        """
        item = WardrobeItem(
            user_id=user_id,
            name=data.name,
            category=data.category,
            subcategory=data.subcategory,
            color=data.color,
            secondary_color=data.secondary_color,
            brand=data.brand,
            size=data.size,
            material=data.material,
            pattern=data.pattern,
            season=data.season,
            occasion=data.occasion,
            purchase_date=data.purchase_date,
            purchase_price=data.purchase_price,
            image_url=data.image_url,
            thumbnail_url=data.thumbnail_url,
            notes=data.notes,
        )

        created_item = await self._repo.create(item)
        return self._to_response(created_item)

    async def get_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> WardrobeItemResponse:
        """Retrieve a specific wardrobe item by ID for the given user.

        Args:
            user_id: The UUID of the authenticated user.
            item_id: The UUID of the item to retrieve.

        Returns:
            The wardrobe item profile.

        Raises:
            NotFoundError: If the item doesn't exist or belongs to someone else.
        """
        item = await self._repo.get_by_id_and_user(item_id, user_id)
        if item is None:
            raise NotFoundError(message="Wardrobe item not found.")
        
        return self._to_response(item)

    async def list_items(
        self,
        user_id: uuid.UUID,
        filters: WardrobeFilterParams,
    ) -> tuple[list[WardrobeItemResponse], int]:
        """List wardrobe items for a user with filtering and pagination.

        Args:
            user_id: The UUID of the authenticated user.
            filters: Filter parameters.

        Returns:
            A tuple of (list of response schemas, total matched count).
        """
        items, total = await self._repo.list_by_user(user_id, filters)
        return [self._to_response(item) for item in items], total

    async def update_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
        data: WardrobeItemUpdate,
    ) -> WardrobeItemResponse:
        """Update a specific wardrobe item.

        Args:
            user_id: The UUID of the authenticated user.
            item_id: The UUID of the item to update.
            data: The update fields.

        Returns:
            The updated wardrobe item profile.

        Raises:
            NotFoundError: If the item doesn't exist or belongs to someone else.
        """
        # Ensure item exists and belongs to user
        item = await self._repo.get_by_id_and_user(item_id, user_id)
        if item is None:
            raise NotFoundError(message="Wardrobe item not found.")

        # Filter out None values
        update_data: dict[str, Any] = {
            key: value
            for key, value in data.model_dump(exclude_unset=True).items()
            if value is not None
        }

        if update_data:
            updated_item = await self._repo.update_by_id(item_id, update_data)
            if updated_item:
                item = updated_item

        return self._to_response(item)

    async def delete_item(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> None:
        """Soft-delete a specific wardrobe item.

        Args:
            user_id: The UUID of the authenticated user.
            item_id: The UUID of the item to delete.

        Raises:
            NotFoundError: If the item doesn't exist or belongs to someone else.
        """
        item = await self._repo.get_by_id_and_user(item_id, user_id)
        if item is None:
            raise NotFoundError(message="Wardrobe item not found.")

        await self._repo.soft_delete(item_id)

    async def toggle_favorite(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> WardrobeItemResponse:
        """Toggle the favorite status of a wardrobe item.

        Args:
            user_id: The UUID of the authenticated user.
            item_id: The UUID of the item.

        Returns:
            The updated wardrobe item profile.

        Raises:
            NotFoundError: If the item doesn't exist or belongs to someone else.
        """
        item = await self._repo.get_by_id_and_user(item_id, user_id)
        if item is None:
            raise NotFoundError(message="Wardrobe item not found.")

        new_status = not item.favorite
        updated_item = await self._repo.update_by_id(item_id, {"favorite": new_status})
        
        # We know updated_item is not None because we just found it
        return self._to_response(updated_item)  # type: ignore[arg-type]

    async def toggle_archive(
        self,
        user_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> WardrobeItemResponse:
        """Toggle the archived status of a wardrobe item.

        Args:
            user_id: The UUID of the authenticated user.
            item_id: The UUID of the item.

        Returns:
            The updated wardrobe item profile.

        Raises:
            NotFoundError: If the item doesn't exist or belongs to someone else.
        """
        item = await self._repo.get_by_id_and_user(item_id, user_id)
        if item is None:
            raise NotFoundError(message="Wardrobe item not found.")

        new_status = not item.archived
        updated_item = await self._repo.update_by_id(item_id, {"archived": new_status})
        
        return self._to_response(updated_item)  # type: ignore[arg-type]

    @staticmethod
    def _to_response(item: WardrobeItem) -> WardrobeItemResponse:
        """Convert a WardrobeItem ORM model to a WardrobeItemResponse schema."""
        return WardrobeItemResponse.model_validate(item)
