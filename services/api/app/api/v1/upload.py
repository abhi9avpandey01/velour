"""
Velour API — Image Upload endpoint.

Exposes a fast multipart upload route that immediately pushes
image processing to a background worker queue.
"""

from fastapi import APIRouter, Depends, File, UploadFile, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.services.image_service import ImageService

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/upload",
    response_model=ApiResponse[dict[str, str]],
    status_code=202,
    summary="Upload wardrobe image",
    description="Uploads an image, provisions a wardrobe item, and queues AI processing asynchronously.",
)
@limiter.limit(settings.rate_limit_general)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[dict[str, str]]:
    """Multipart upload endpoint for wardrobe images."""
    service = ImageService(db)
    
    # We must access the internal file buffer directly to read/seek bytes
    result = await service.handle_upload(
        user_id=current_user.id,
        file_obj=file.file,
        filename=file.filename or "unknown.jpg",
    )
    
    return ApiResponse.ok(result)
