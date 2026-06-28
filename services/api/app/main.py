"""
Velour API — FastAPI Application.

Production-grade FastAPI application with:
- Versioned API routes (auth, users, health)
- CORS middleware
- Request ID middleware
- Rate limiting
- Centralized exception handling
- Async SQLAlchemy database sessions
- Redis integration for token blacklisting
- JWT authentication
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth as auth_v1
from app.api.v1 import health as health_v1
from app.api.v1 import upload as upload_v1
from app.api.v1 import users as users_v1
from app.api.v1 import wardrobe as wardrobe_v1
from app.api.v1 import recommendations as recommendations_v1
from app.api.v1 import outfits as outfits_v1
from app.api.v1 import chat as chat_v1
from app.core.config import settings
from app.core.events import lifespan
from app.core.exceptions import register_exception_handlers
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.request_id import RequestIdMiddleware

app = FastAPI(
    title=settings.app_name,
    description="AI-powered wardrobe management and outfit recommendation API.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# ── Exception Handling ────────────────────────────────────────
register_exception_handlers(app)

# ── Rate Limiting ─────────────────────────────────────────────
setup_rate_limiting(app)

# ── Middleware (order matters — outermost first) ──────────────
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ────────────────────────────────────────────────
app.include_router(health_v1.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth_v1.router, prefix="/api/v1")
app.include_router(users_v1.router, prefix="/api/v1")
app.include_router(wardrobe_v1.router, prefix="/api/v1")
app.include_router(upload_v1.router, prefix="/api/v1")
app.include_router(recommendations_v1.router, prefix="/api/v1")
app.include_router(outfits_v1.router, prefix="/api/v1")
app.include_router(chat_v1.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning service info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Your AI Personal Stylist",
    }
