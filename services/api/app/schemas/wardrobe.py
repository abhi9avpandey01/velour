"""
Velour API — Wardrobe schemas.

Pydantic v2 schemas for wardrobe item creation, updates,
and API responses.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import Category, Occasion, Pattern, Season


class WardrobeItemBase(BaseModel):
    """Base schema for wardrobe items with shared fields."""

    name: str = Field(..., max_length=255)
    category: Category
    subcategory: str = Field(..., max_length=100)
    color: str = Field(..., max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    size: str | None = Field(default=None, max_length=50)
    material: str | None = Field(default=None, max_length=100)
    pattern: Pattern | None = Field(default=None)
    season: Season
    occasion: Occasion
    purchase_date: date | None = Field(default=None)
    purchase_price: float | None = Field(default=None, ge=0)
    image_url: str = Field(...)
    thumbnail_url: str = Field(...)
    notes: str | None = Field(default=None)


class WardrobeItemCreate(WardrobeItemBase):
    """Schema for creating a new wardrobe item."""

    pass


class WardrobeItemUpdate(BaseModel):
    """Schema for updating a wardrobe item. All fields are optional."""

    name: str | None = Field(default=None, max_length=255)
    category: Category | None = Field(default=None)
    subcategory: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=50)
    secondary_color: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    size: str | None = Field(default=None, max_length=50)
    material: str | None = Field(default=None, max_length=100)
    pattern: Pattern | None = Field(default=None)
    season: Season | None = Field(default=None)
    occasion: Occasion | None = Field(default=None)
    purchase_date: date | None = Field(default=None)
    purchase_price: float | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None)
    thumbnail_url: str | None = Field(default=None)
    notes: str | None = Field(default=None)


class WardrobeItemResponse(WardrobeItemBase):
    """Schema for public wardrobe item data in API responses."""

    id: str = Field(..., description="Wardrobe item UUID")
    user_id: str = Field(..., description="Owner's user UUID")
    wears_count: int = Field(default=0)
    favorite: bool = Field(default=False)
    archived: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WardrobeFilterParams(BaseModel):
    """Schema for filtering wardrobe items in list endpoints."""

    category: Category | None = None
    season: Season | None = None
    occasion: Occasion | None = None
    color: str | None = None
    favorite: bool | None = None
    archived: bool | None = False  # By default, hide archived items
    search: str | None = None
    brand: str | None = None
    
    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_desc: bool = Field(default=True, description="Sort descending")
