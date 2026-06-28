"""
Velour API — Wardrobe Metadata Model.

Stores AI-generated metadata and CLIP embeddings for wardrobe items.
Uses pgvector for the embedding column to support future similarity search.
"""

import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class WardrobeMetadata(BaseModel):
    """AI Metadata for a WardrobeItem.

    Contains extracted clothing attributes with confidence scores,
    generated captions, and a 512-dimensional CLIP embedding vector.
    """

    __tablename__ = "wardrobe_metadata"

    # ── Relations ──────────────────────────────────
    wardrobe_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wardrobe_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    wardrobe_item = relationship("WardrobeItem", backref="ai_metadata")

    # ── AI Embeddings ──────────────────────────────
    # Using pgvector's Vector column for similarity search
    # CLIP standard dimensions = 512
    embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=True)

    # ── Text Features ──────────────────────────────
    image_caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Structured Attributes (JSONB) ──────────────
    # Each attribute is a JSON object: {"value": str, "confidence": float}
    category_attr: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    subcategory_attr: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    primary_color: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    secondary_color: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    pattern: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    material: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    fit: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    gender_neutral_score: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    season: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    occasion: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # ── AI Observability ───────────────────────────
    overall_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    inference_time_ms: Mapped[int | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<WardrobeMetadata item_id={self.wardrobe_item_id} conf={self.overall_confidence}>"
