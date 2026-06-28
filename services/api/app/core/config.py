"""
Velour API — Application configuration.

Loads settings from environment variables with validation via Pydantic.
Supports development and production environments.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded and validated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────
    app_name: str = "Velour API"
    app_version: str = "0.1.0"
    api_env: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # ── Server ────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:3000"

    # ── Database (PostgreSQL) ─────────────────────
    database_url: str = "postgresql+asyncpg://velour:velour_secret@postgres:5432/velour"
    postgres_user: str = "velour"
    postgres_password: str = "velour_secret"
    postgres_db: str = "velour"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # ── Redis ─────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"

    # ── Celery ────────────────────────────────────
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # ── JWT ───────────────────────────────────────
    jwt_secret_key: str = "jwt-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Rate Limiting ─────────────────────────────
    rate_limit_auth: str = "5/minute"
    rate_limit_general: str = "60/minute"

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.api_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.api_env == "production"


settings = Settings()
