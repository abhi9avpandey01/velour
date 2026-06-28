"""
Velour API — Recommendation Context.

Defines the context injected into the engine for generating outfits.
"""

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import Occasion, Season, WeatherContext


class RecommendationContext(BaseModel):
    """The full state context required to generate an outfit recommendation."""
    
    user_id: uuid.UUID
    
    # ── Environment ──────────────────────────────
    weather: WeatherContext = Field(..., description="Abstracted weather status (Hot, Cold, etc)")
    temperature_celsius: Optional[float] = Field(None, description="Exact temperature in Celsius")
    season: Season = Field(..., description="The current season")
    
    # ── User Intent ──────────────────────────────
    occasion: Occasion = Field(..., description="What the outfit is being generated for")
    
    # ── Preferences ──────────────────────────────
    prefer_favorites: bool = Field(default=True, description="Whether to boost score of favorite items")
    include_archived: bool = Field(default=False, description="Whether to allow archived items")
    
    # ── Wardrobe State ───────────────────────────
    # The engine will query the database for these, but they can be mocked in tests
    recently_worn_item_ids: list[uuid.UUID] = Field(default_factory=list)
