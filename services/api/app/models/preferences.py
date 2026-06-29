"""
Velour API — User Preference Models.
"""

from sqlalchemy import ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.enums import PreferenceSource, ChangedBy


class PreferenceProfile(BaseModel):
    """
    User preference profile storing fashion preferences.
    """
    __tablename__ = "preference_profiles"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Color preferences
    preferred_colors: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    disliked_colors: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Category preferences
    preferred_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    disliked_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Occasion preferences
    preferred_occasions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Fit and Style
    preferred_fit: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_style: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Brand preferences
    favorite_brands: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    avoided_brands: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Material preferences
    preferred_materials: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    disliked_materials: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Climate and scoring
    climate_preference: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Metadata
    source: Mapped[str] = mapped_column(String, default=PreferenceSource.MANUAL.value)
    
    # Relationships
    user = relationship("User", backref="preference_profile", lazy="joined")
    history = relationship("PreferenceHistory", back_populates="profile", cascade="all, delete-orphan")


class PreferenceHistory(BaseModel):
    """
    History log for tracking preference changes over time.
    """
    __tablename__ = "preference_history"

    preference_profile_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("preference_profiles.id", ondelete="CASCADE"), nullable=False)
    
    changed_field: Mapped[str] = mapped_column(String, nullable=False)
    previous_value: Mapped[str | None] = mapped_column(String, nullable=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)
    
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    changed_by: Mapped[str] = mapped_column(String, default=ChangedBy.USER.value)
    
    # Relationships
    profile = relationship("PreferenceProfile", back_populates="history")

