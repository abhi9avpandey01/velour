"""
Velour API — Authentication schemas.

Pydantic v2 schemas for JWT token responses, token payloads,
and password reset flows.
"""

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Schema for JWT token pair returned after login or refresh."""

    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer').")


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""

    sub: str = Field(..., description="Subject (user ID).")
    exp: int = Field(..., description="Expiration timestamp.")
    type: str = Field(..., description="Token type ('access' or 'refresh').")
    jti: str = Field(..., description="Unique token identifier.")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh requests."""

    refresh_token: str = Field(..., description="The refresh token to exchange.")


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset email."""

    email: EmailStr = Field(..., description="Email address of the account.")


class PasswordResetConfirm(BaseModel):
    """Schema for confirming a password reset with a new password."""

    token: str = Field(..., description="Password reset token.")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (8-128 characters).",
    )
