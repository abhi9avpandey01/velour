"""
Velour API — User management endpoints.

GET   /api/v1/users/me  — Get the current user's profile
PATCH /api/v1/users/me  — Update the current user's profile
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.storage import StorageService
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Get current user",
    description="Retrieve the authenticated user's profile information.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[UserResponse]:
    """Get the current authenticated user's profile."""
    service = UserService(db)
    user = await service.get_current_user(current_user.id)
    return ApiResponse.ok(user)


@router.patch(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Update profile",
    description="Update the authenticated user's profile. Only provided fields are modified.",
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[UserResponse]:
    """Update the current authenticated user's profile."""
    service = UserService(db)
    user = await service.update_profile(current_user.id, data)
    return ApiResponse.ok(user)


@router.post(
    "/me/avatar",
    response_model=ApiResponse[UserResponse],
    summary="Upload profile picture",
    description="Upload a new profile picture and update the user's profile.",
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[UserResponse]:
    """Upload and set the current user's profile picture."""
    meta = await StorageService.validate_image(file.file, file.filename or "avatar.jpg")
    
    public_url = StorageService.upload_profile_picture(
        user_id=current_user.id,
        file_obj=file.file,
        mime_type=str(meta["mime_type"]),
    )
    
    service = UserService(db)
    user = await service.update_profile(
        current_user.id, 
        UserUpdate(profile_picture_url=public_url)
    )
    return ApiResponse.ok(user)
