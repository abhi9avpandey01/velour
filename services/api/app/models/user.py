"""
Velour API — User ORM model.

Defines the User table with all profile fields, authentication data,
and audit columns. Inherits UUID PK, timestamps, and soft delete
from BaseModel.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class User(BaseModel):
    """User account model for authentication and profile management."""

    __tablename__ = "users"

    # ── Identity ──────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ── Profile ───────────────────────────────────
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    profile_picture_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # ── Preferences ───────────────────────────────
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        server_default="UTC",
        nullable=False,
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        server_default="en",
        nullable=False,
    )

    # ── Status ────────────────────────────────────
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    # ── Soft Delete Audit ─────────────────────────
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Indexes ───────────────────────────────────
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_is_deleted", "is_deleted"),
    )

    def __repr__(self) -> str:
        """Return a string representation of the User."""
        return f"<User id={self.id} email={self.email} username={self.username}>"
