"""
Velour API — Application Configuration.

Loads environment variables using Pydantic Settings.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded and validated from environment variables."""

    # ── Application ───────────────────────────────
    app_name: str = "Velour API"
    app_version: str = "0.1.0"
    is_development: bool = True

    # ── Server ────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:3000,https://velour-web-6gnz.vercel.app"

    # ── Database (PostgreSQL) ─────────────────────
    database_url: str = "postgresql+asyncpg://velour:velour_secret@postgres:5432/velour"

    # ── Redis (Caching) ───────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT Auth ──────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Rate Limiting ─────────────────────────────
    rate_limit_auth: str = "5/minute"
    rate_limit_general: str = "60/minute"

    # ── Celery & Redis Queue ──────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    # ── Supabase Storage ──────────────────────────
    supabase_url: str = "http://localhost:8000"
    supabase_key: str = "your-service-role-key"
    supabase_bucket: str = "wardrobe"

    # ── xAI (Grok Stylist Agent) ──────────────────
    xai_api_key: str = "xai-placeholder"

    # ── Google Gemini ─────────────────────────────
    gemini_api_key: str = "gemini-placeholder"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]


# Instantiate global settings object
settings = Settings()
