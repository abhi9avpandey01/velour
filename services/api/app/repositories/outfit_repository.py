"""
Velour API — Outfit Repository.

Handles database transactions for viewing user-saved and generated outfits.
"""

import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.recommendation import Outfit


class OutfitRepository:
    """Repository for querying Outfits."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user(self, user_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Outfit]:
        """Fetch all outfits belonging to a user."""
        stmt = (
            select(Outfit)
            .options(selectinload(Outfit.items).selectinload(OutfitItem.wardrobe_item))
            .where(Outfit.user_id == user_id, Outfit.is_deleted == False)
            .order_by(Outfit.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, outfit_id: uuid.UUID, user_id: uuid.UUID) -> Outfit | None:
        """Fetch a specific outfit."""
        stmt = (
            select(Outfit)
            .options(selectinload(Outfit.items).selectinload(OutfitItem.wardrobe_item))
            .where(Outfit.id == outfit_id, Outfit.user_id == user_id, Outfit.is_deleted == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
