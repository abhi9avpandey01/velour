"""
Velour API — Wardrobe repository.

Data access layer for WardrobeItem entities. Extends BaseRepository
with wardrobe-specific query methods, filtering, and search.
"""

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wardrobe import WardrobeItem
from app.repositories.base import BaseRepository
from app.schemas.wardrobe import WardrobeFilterParams


class WardrobeRepository(BaseRepository[WardrobeItem]):
    """Repository for WardrobeItem CRUD and query operations.

    Provides methods for complex filtering, searching, and ensuring
    strict tenant isolation (user_id scoping).
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WardrobeItem, session)

    async def get_by_id_and_user(
        self,
        item_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WardrobeItem | None:
        """Find a wardrobe item by ID, scoped to the specific user.

        Args:
            item_id: The UUID of the wardrobe item.
            user_id: The UUID of the user who owns it.

        Returns:
            The WardrobeItem if found and not soft-deleted, None otherwise.
        """
        stmt = select(WardrobeItem).where(
            WardrobeItem.id == item_id,
            WardrobeItem.user_id == user_id,
            WardrobeItem.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        filters: WardrobeFilterParams,
    ) -> tuple[list[WardrobeItem], int]:
        """List wardrobe items for a specific user with filtering and pagination.

        Args:
            user_id: The UUID of the user.
            filters: Filter parameters including pagination and sorting.

        Returns:
            A tuple containing (list of items, total count matching filters).
        """
        # Base query scoped to the user and non-deleted items
        stmt = select(WardrobeItem).where(
            WardrobeItem.user_id == user_id,
            WardrobeItem.is_deleted.is_(False),
        )

        # Apply exact match filters
        if filters.category:
            stmt = stmt.where(WardrobeItem.category == filters.category)
        if filters.season:
            stmt = stmt.where(WardrobeItem.season == filters.season)
        if filters.occasion:
            stmt = stmt.where(WardrobeItem.occasion == filters.occasion)
        if filters.favorite is not None:
            stmt = stmt.where(WardrobeItem.favorite == filters.favorite)
        if filters.archived is not None:
            stmt = stmt.where(WardrobeItem.archived == filters.archived)
        if filters.color:
            stmt = stmt.where(WardrobeItem.color.ilike(f"%{filters.color}%"))
        if filters.brand:
            stmt = stmt.where(WardrobeItem.brand.ilike(f"%{filters.brand}%"))

        # Apply generic search across multiple fields
        if filters.search:
            search_term = f"%{filters.search}%"
            stmt = stmt.where(
                or_(
                    WardrobeItem.name.ilike(search_term),
                    WardrobeItem.notes.ilike(search_term),
                    WardrobeItem.brand.ilike(search_term),
                    # We cast category Enum to String for ilike search support
                    # Alternatively, if search doesn't need to hit enums, we can omit it
                    # or handle it in application logic. Omitting enum from ilike for simplicity.
                )
            )

        # Calculate total count before pagination
        # Using a subquery for count is robust across complex queries
        from sqlalchemy import func
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total_count = count_result.scalar_one_or_none() or 0

        # Apply sorting
        sort_column = getattr(WardrobeItem, filters.sort_by, WardrobeItem.created_at)
        if filters.sort_desc:
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Apply pagination
        stmt = stmt.offset(filters.skip).limit(filters.limit)

        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return items, total_count
