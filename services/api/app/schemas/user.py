"""
Velour API — User schemas.

Pydantic v2 schemas for user registration, profile display,
and profile updates with input validation.
"""

import re
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User's email address.")
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Unique username (3-100 characters, alphanumeric and underscores).",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters).",
    )
    first_name: str | None = Field(
        default=None,
        max_length=100,
        description="User's first name.",
    )
    last_name: str | None = Field(
        default=None,
        max_length=100,
        description="User's last name.",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Validate that username contains only allowed characters."""
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            msg = "Username must contain only letters, numbers, and underscores."
            raise ValueError(msg)
        return value.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email to lowercase."""
        return value.lower()


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., description="User's password.")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email to lowercase."""
        return value.lower()


class UserUpdate(BaseModel):
    """Schema for updating user profile.

    All fields are optional — only provided fields are updated.
    """

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Unique username (3-100 characters, alphanumeric and underscores).",
    )
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    profile_picture_url: str | None = Field(default=None)
    gender: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = Field(default=None)
    timezone: str | None = Field(default=None, max_length=50)
    preferred_language: str | None = Field(default=None, max_length=10)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        """Validate that username contains only allowed characters."""
        if value is None:
            return None
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            msg = "Username must contain only letters, numbers, and underscores."
            raise ValueError(msg)
        return value.lower()

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str | None) -> str | None:
        """Validate gender value if provided."""
        if value is None:
            return None
        allowed = {"male", "female", "non-binary", "prefer-not-to-say", "other"}
        if value.lower() not in allowed:
            msg = f"Gender must be one of: {', '.join(sorted(allowed))}."
            raise ValueError(msg)
        return value.lower()

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        """Validate language code format (ISO 639-1)."""
        if value is None:
            return None
        if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", value):
            msg = "Language must be a valid ISO 639-1 code (e.g., 'en', 'fr', 'es')."
            raise ValueError(msg)
        return value


class UserResponse(BaseModel):
    """Schema for public user data in API responses.

    Excludes sensitive fields like password_hash.
    """

    id: str = Field(..., description="User UUID.")
    email: str = Field(..., description="User's email address.")
    username: str = Field(..., description="User's username.")
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    profile_picture_url: str | None = Field(default=None)
    gender: str | None = Field(default=None)
    date_of_birth: date | None = Field(default=None)
    timezone: str = Field(default="UTC")
    preferred_language: str = Field(default="en")
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    last_login: datetime | None = Field(default=None)

    model_config = {"from_attributes": True}
