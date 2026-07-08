"""
Velour API — Celery Worker Tasks.

Contains background tasks for image processing (ImageUploaded event).
"""

import asyncio
import logging
import time

from app.db.session import async_session_factory
from app.models.enums import AIStatus, ProcessingStatus
from app.models.image_asset import ImageAsset

logger = logging.getLogger(__name__)


async def process_image_background(image_asset_id: str) -> None:
    """Async core logic to simulate AI processing and update DB."""
    logger.info(f"Worker started: Processing ImageAsset {image_asset_id}")

    try:
        async with async_session_factory() as session:
            from sqlalchemy import select
            
            # Fetch the ImageAsset to verify it exists first
            stmt = select(ImageAsset).where(ImageAsset.id == image_asset_id)
            result = await session.execute(stmt)
            asset = result.scalar_one_or_none()

            if not asset:
                logger.error(f"Worker failed: ImageAsset {image_asset_id} not found")
                return

            # Initialize and run the vision pipeline
            from app.services.vision_service import VisionService
            vision_service = VisionService(session)
            await vision_service.process_image(image_asset_id)
            
            logger.info(f"Worker finished: ImageAsset {image_asset_id} processed successfully")
    except Exception as exc:
        logger.error(f"Worker failed with exception: {exc}")
