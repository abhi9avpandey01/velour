"""
Velour API — Recommendation Models.

Contains the ORM models for Outfits, OutfitItems (junction), Recommendations,
and the history tracking table.
"""

import uuid
from typing import Any

from sqlalchemy import (
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.enums import RecommendationAction


class Outfit(BaseModel):
    """An outfit composed of multiple wardrobe items."""
    __tablename__ = "outfits"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Is this outfit user-created or AI-generated?
    is_user_created: Mapped[bool] = mapped_column(default=False, nullable=False)

    user = relationship("User", backref="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(BaseModel):
    """Junction table connecting Outfits to WardrobeItems."""
    __tablename__ = "outfit_items"

    outfit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("outfits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    wardrobe_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wardrobe_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Optional styling metadata (e.g. "tucked in", "layered over")
    styling_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    outfit = relationship("Outfit", back_populates="items")
    wardrobe_item = relationship("WardrobeItem")

    __table_args__ = (
        Index("ix_outfit_items_unique", "outfit_id", "wardrobe_item_id", unique=True),
    )


class Recommendation(BaseModel):
    """A specific recommendation of an outfit for a user context."""
    __tablename__ = "recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    outfit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("outfits.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Scores ─────────────────────────────────────
    score_color_harmony: Mapped[float] = mapped_column(Float, nullable=False)
    score_occasion: Mapped[float] = mapped_column(Float, nullable=False)
    score_weather: Mapped[float] = mapped_column(Float, nullable=False)
    score_preferences: Mapped[float] = mapped_column(Float, nullable=False)
    score_recency: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    # ── Explanations & Context ─────────────────────
    # JSON array of string reasons why it was recommended
    reasons: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    # The context it was generated for (weather, temp, occasion)
    context_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    user = relationship("User")
    outfit = relationship("Outfit")


class RecommendationHistory(BaseModel):
    """Tracks user feedback/actions on a generated recommendation."""
    __tablename__ = "recommendation_history"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[RecommendationAction] = mapped_column(
        SQLEnum(RecommendationAction), 
        nullable=False
    )
    
    recommendation = relationship("Recommendation", backref="history")

    __table_args__ = (
        Index("ix_recommendation_history_action", "action"),
    )
