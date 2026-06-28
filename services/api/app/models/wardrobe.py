"""
Velour API — Wardrobe ORM model.

Defines the WardrobeItem table. Represents a single physical
clothing item belonging to a specific user.
"""

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.enums import Category, Occasion, Pattern, Season


class WardrobeItem(BaseModel):
    """Wardrobe Item model.

    Represents a physical clothing item managed by a user.
    """

    __tablename__ = "wardrobe_items"

    # ── Relations ──────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user = relationship("User", backref="wardrobe_items")

    # ── Basic Attributes ───────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # ── Visual & Physical ──────────────────────────
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    secondary_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pattern: Mapped[Pattern | None] = mapped_column(SQLEnum(Pattern), nullable=True)

    # ── Usage Context ──────────────────────────────
    season: Mapped[Season] = mapped_column(SQLEnum(Season), nullable=False)
    occasion: Mapped[Occasion] = mapped_column(SQLEnum(Occasion), nullable=False)

    # ── Purchase Info ──────────────────────────────
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # ── Media ──────────────────────────────────────
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Metadata ───────────────────────────────────
    wears_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    # ── Indexes ───────────────────────────────────
    __table_args__ = (
        Index("ix_wardrobe_items_category", "category"),
        Index("ix_wardrobe_items_season", "season"),
        Index("ix_wardrobe_items_occasion", "occasion"),
        Index("ix_wardrobe_items_favorite", "favorite"),
        Index("ix_wardrobe_items_created_at", "created_at"),
        Index("ix_wardrobe_items_user_category", "user_id", "category"),
    )

    def __repr__(self) -> str:
        """Return a string representation of the WardrobeItem."""
        return f"<WardrobeItem id={self.id} user_id={self.user_id} name={self.name}>"
