"""
Velour API — Image Service.

Coordinates image validation, Supabase upload, database record creation,
and event publishing to the Celery queue.
"""

import logging
import uuid
from typing import IO

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import StorageService
from app.models.enums import Category, Occasion, Season, UploadStatus
from app.models.image_asset import ImageAsset
from app.models.wardrobe import WardrobeItem
from app.worker.tasks import process_image_upload

logger = logging.getLogger(__name__)


class ImageService:
    """Service layer for handling image uploads and queue events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def handle_upload(
        self,
        user_id: uuid.UUID,
        file_obj: IO[bytes],
        filename: str,
    ) -> dict[str, str]:
        """Process an image upload, create pending records, and trigger worker.

        Args:
            user_id: The authenticated user's ID.
            file_obj: The file stream.
            filename: The uploaded filename.

        Returns:
            Dictionary with item_id and processing_status.
        """
        logger.info(f"Upload started for user {user_id}: {filename}")

        # 1. Validate image (size, mime, dimensions)
        meta = await StorageService.validate_image(file_obj, filename)
        mime_type = str(meta["mime_type"])
        width = int(meta.get("width", 0))
        height = int(meta.get("height", 0))
        
        file_obj.seek(0, 2)
        file_size = file_obj.tell()

        # 2. Pre-generate IDs
        item_id = uuid.uuid4()
        asset_id = uuid.uuid4()

        # 3. Upload to Supabase Storage
        public_url = StorageService.upload_original_image(
            user_id=user_id,
            item_id=item_id,
            file_obj=file_obj,
            mime_type=mime_type,
        )
        logger.info(f"Upload completed to storage: {public_url}")

        # 4. Create pending WardrobeItem placeholder
        # Note: AI worker will update Category, Season, Occasion later.
        # We assign defaults for the strict Enums right now.
        item = WardrobeItem(
            id=item_id,
            user_id=user_id,
            name="Pending Item",
            category=Category.TOPS,  # Placeholder
            subcategory="Pending",
            color="Pending",
            season=Season.ALL_SEASON,
            occasion=Occasion.CASUAL,
            image_url=public_url,
            thumbnail_url=public_url,  # Temporary until worker resizes
        )
        self._session.add(item)
        await self._session.flush()

        # 5. Create ImageAsset record
        asset = ImageAsset(
            id=asset_id,
            wardrobe_item_id=item_id,
            storage_path=public_url,
            original_url=public_url,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size=file_size,
            upload_status=UploadStatus.COMPLETED,
        )
        self._session.add(asset)
        await self._session.flush()

        # Commit the transaction so Celery worker can find the records
        await self._session.commit()

        # 6. Publish Event to Celery (ImageUploaded)
        # We use .delay() to send it to the Redis queue asynchronously.
        process_image_upload.delay(str(asset.id))
        logger.info(f"Queue published: ImageUploaded event for asset {asset.id}")

        return {
            "item_id": str(item_id),
            "processing_status": "PENDING"
        }
