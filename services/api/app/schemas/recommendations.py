"""
Velour API — Recommendation Schemas.

Pydantic schemas for the recommendation API boundaries.
"""

import uuid
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Occasion, Season, WeatherContext


# ── Requests ───────────────────────────────────────

class GenerateRecommendationsRequest(BaseModel):
    """The JSON payload required to request an outfit."""
    weather: WeatherContext
    temperature_celsius: float | None = None
    season: Season
    occasion: Occasion
    prefer_favorites: bool = True
    include_archived: bool = False


# ── Responses ──────────────────────────────────────

class OutfitItemSchema(BaseModel):
    wardrobe_item_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class OutfitSchema(BaseModel):
    id: uuid.UUID
    name: str | None
    is_user_created: bool
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    id: uuid.UUID
    outfit_id: uuid.UUID
    overall_score: float
    reasons: List[str]
    
    # Optional nested outfit for convenience
    outfit: OutfitSchema | None = None
    
    model_config = ConfigDict(from_attributes=True)
