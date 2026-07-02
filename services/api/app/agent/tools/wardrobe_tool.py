"""
Velour API — Wardrobe Tool.

Allows the Stylist Agent to search the user's wardrobe using category and color.
"""

import uuid
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agent.tools.base import BaseTool
from app.models.enums import Category
from app.models.wardrobe import WardrobeItem


class SearchWardrobeTool(BaseTool):
    """Tool for querying the user's wardrobe items."""

    def __init__(self, session: AsyncSession, user_id: uuid.UUID):
        self.session = session
        self.user_id = user_id

    @property
    def name(self) -> str:
        return "search_wardrobe"

    @property
    def description(self) -> str:
        return "Search the user's wardrobe for items matching specific criteria."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [e.value for e in Category],
                    "description": "Optional category filter."
                },
                "color": {
                    "type": "string",
                    "description": "Optional color filter (e.g. 'black', 'white')."
                },
                "query": {
                    "type": "string",
                    "description": "Optional keyword search for name, brand, subcategory, or notes (e.g. 'nike', 'jeans', 'striped')."
                }
            }
        }

    async def execute(self, category: str = None, color: str = None, query: str = None, **kwargs) -> Any:
        """Search the wardrobe."""
        stmt = select(WardrobeItem).where(
            WardrobeItem.user_id == self.user_id,
            WardrobeItem.is_deleted == False
        )
        
        if category:
            stmt = stmt.where(WardrobeItem.category == Category(category))
        if color:
            # Case insensitive match for simple colors
            stmt = stmt.where(WardrobeItem.color.ilike(f"%{color}%"))
        if query:
            from sqlalchemy import or_
            stmt = stmt.where(
                or_(
                    WardrobeItem.name.ilike(f"%{query}%"),
                    WardrobeItem.brand.ilike(f"%{query}%"),
                    WardrobeItem.subcategory.ilike(f"%{query}%"),
                    WardrobeItem.notes.ilike(f"%{query}%")
                )
            )
            
        stmt = stmt.limit(10) # Prevent LLM context bloat
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        
        if not items:
            return {"result": "No items found matching the criteria."}
            
        return {
            "items": [
                {
                    "id": str(item.id),
                    "category": item.category.value,
                    "color": item.color,
                    "brand": item.brand,
                    "name": item.name
                }
                for item in items
            ]
        }
