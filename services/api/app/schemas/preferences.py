"""
Velour API — User Preference Schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import PreferenceSource, ChangedBy


def validate_array_length(value: list[str] | None) -> list[str] | None:
    """Validate that array length does not exceed maximum limit."""
    if value is not None and len(value) > 50:
        raise ValueError("Array exceeds maximum length of 50 items")
    return value


class PreferenceProfileBase(BaseModel):
    """Base fields for preference profile."""
    preferred_colors: list[str] = Field(default_factory=list, description="List of preferred colors")
    disliked_colors: list[str] = Field(default_factory=list, description="List of disliked colors")
    
    preferred_categories: list[str] = Field(default_factory=list, description="List of preferred categories")
    disliked_categories: list[str] = Field(default_factory=list, description="List of disliked categories")
    
    preferred_occasions: list[str] = Field(default_factory=list, description="List of preferred occasions")
    
    preferred_fit: str | None = Field(None, description="Preferred clothing fit")
    preferred_style: str | None = Field(None, description="Preferred clothing style (e.g. minimalist, vintage)")
    
    favorite_brands: list[str] = Field(default_factory=list, description="List of favorite brands")
    avoided_brands: list[str] = Field(default_factory=list, description="List of avoided brands")
    
    preferred_materials: list[str] = Field(default_factory=list, description="List of preferred materials")
    disliked_materials: list[str] = Field(default_factory=list, description="List of disliked materials")
    
    climate_preference: str | None = Field(None, description="Climate preference (e.g. hot, cold, mild)")

    # Validators
    _validate_preferred_colors = field_validator('preferred_colors')(validate_array_length)
    _validate_disliked_colors = field_validator('disliked_colors')(validate_array_length)
    _validate_preferred_categories = field_validator('preferred_categories')(validate_array_length)
    _validate_disliked_categories = field_validator('disliked_categories')(validate_array_length)
    _validate_preferred_occasions = field_validator('preferred_occasions')(validate_array_length)
    _validate_favorite_brands = field_validator('favorite_brands')(validate_array_length)
    _validate_avoided_brands = field_validator('avoided_brands')(validate_array_length)
    _validate_preferred_materials = field_validator('preferred_materials')(validate_array_length)
    _validate_disliked_materials = field_validator('disliked_materials')(validate_array_length)


class PreferenceProfileCreate(PreferenceProfileBase):
    """Schema for creating a preference profile."""
    pass


class PreferenceProfileUpdate(BaseModel):
    """Schema for updating a preference profile."""
    preferred_colors: list[str] | None = None
    disliked_colors: list[str] | None = None
    
    preferred_categories: list[str] | None = None
    disliked_categories: list[str] | None = None
    
    preferred_occasions: list[str] | None = None
    
    preferred_fit: str | None = None
    preferred_style: str | None = None
    
    favorite_brands: list[str] | None = None
    avoided_brands: list[str] | None = None
    
    preferred_materials: list[str] | None = None
    disliked_materials: list[str] | None = None
    
    climate_preference: str | None = None

    # Optional metadata that the client can provide (especially AI)
    reason: str | None = Field(None, description="Reason for update if changed by AI")
    changed_by: ChangedBy = Field(ChangedBy.USER, description="Who made the change")

    # Validators
    _validate_preferred_colors = field_validator('preferred_colors')(validate_array_length)
    _validate_disliked_colors = field_validator('disliked_colors')(validate_array_length)
    _validate_preferred_categories = field_validator('preferred_categories')(validate_array_length)
    _validate_disliked_categories = field_validator('disliked_categories')(validate_array_length)
    _validate_preferred_occasions = field_validator('preferred_occasions')(validate_array_length)
    _validate_favorite_brands = field_validator('favorite_brands')(validate_array_length)
    _validate_avoided_brands = field_validator('avoided_brands')(validate_array_length)
    _validate_preferred_materials = field_validator('preferred_materials')(validate_array_length)
    _validate_disliked_materials = field_validator('disliked_materials')(validate_array_length)


class PreferenceProfileResponse(PreferenceProfileBase):
    """Response schema for a preference profile."""
    id: UUID
    user_id: UUID
    confidence_score: float
    source: PreferenceSource
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreferenceHistoryResponse(BaseModel):
    """Response schema for preference history."""
    id: UUID
    preference_profile_id: UUID
    changed_field: str
    previous_value: str | None = None
    new_value: str | None = None
    reason: str | None = None
    changed_by: ChangedBy
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
