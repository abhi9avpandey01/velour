"""
Velour API — Image Asset Model.

Tracks image assets uploaded to Supabase, tying them to WardrobeItems
and orchestrating the async AI processing statuses.
"""

import uuid

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.enums import AIStatus, ProcessingStatus, UploadStatus


class ImageAsset(BaseModel):
    """Image Asset model.

    Tracks uploaded images and their processing status through
    the Celery queue and AI pipeline.
    """

    __tablename__ = "image_assets"

    # ── Relations ──────────────────────────────────
    wardrobe_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wardrobe_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    wardrobe_item = relationship("WardrobeItem", backref="image_assets")

    # ── Storage Info ───────────────────────────────
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── File Metadata ──────────────────────────────
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── Orchestration Statuses ─────────────────────
    upload_status: Mapped[UploadStatus] = mapped_column(
        SQLEnum(UploadStatus),
        default=UploadStatus.PENDING,
        nullable=False,
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus),
        default=ProcessingStatus.NOT_STARTED,
        nullable=False,
    )
    ai_status: Mapped[AIStatus] = mapped_column(
        SQLEnum(AIStatus),
        default=AIStatus.WAITING,
        nullable=False,
    )

    # ── Indexes ───────────────────────────────────
    __table_args__ = (
        Index("ix_image_assets_processing_status", "processing_status"),
        Index("ix_image_assets_ai_status", "ai_status"),
    )

    def __repr__(self) -> str:
        """Return a string representation of the ImageAsset."""
        return f"<ImageAsset id={self.id} wardrobe_item_id={self.wardrobe_item_id}>"
