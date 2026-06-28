"""
Velour API — Common response schemas.

Provides consistent JSON response envelopes used across all endpoints.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error information returned in API responses."""

    code: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context about the error.",
    )


class ApiResponse(BaseModel, Generic[T]):
    """Consistent JSON response envelope for all API endpoints.

    Success: { "success": true, "data": {...} }
    Error:   { "success": false, "error": {...} }
    """

    success: bool = Field(..., description="Whether the request succeeded.")
    data: T | None = Field(default=None, description="Response payload.")
    error: ErrorDetail | None = Field(default=None, description="Error details if request failed.")
    meta: dict[str, Any] | None = Field(
        default=None,
        description="Pagination or other metadata.",
    )

    @classmethod
    def ok(cls, data: T, meta: dict[str, Any] | None = None) -> "ApiResponse[T]":
        """Create a successful response.

        Args:
            data: The response payload.
            meta: Optional metadata (pagination, etc.).

        Returns:
            An ApiResponse with success=True.
        """
        return cls(success=True, data=data, meta=meta)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> "ApiResponse[None]":
        """Create a failure response.

        Args:
            code: Machine-readable error code.
            message: Human-readable error message.
            details: Additional error context.

        Returns:
            An ApiResponse with success=False.
        """
        return cls(
            success=False,
            error=ErrorDetail(code=code, message=message, details=details or {}),
        )
