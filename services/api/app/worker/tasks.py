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
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _process_image_async(image_asset_id: str) -> None:
    """Async core logic to simulate AI processing and update DB."""
    logger.info(f"Worker started: Processing ImageAsset {image_asset_id}")

    async with async_session_factory() as session:
        from sqlalchemy import select
        
        # Fetch the ImageAsset
        stmt = select(ImageAsset).where(ImageAsset.id == image_asset_id)
        result = await session.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            logger.error(f"Worker failed: ImageAsset {image_asset_id} not found")
            return

        # Mark as processing
        asset.processing_status = ProcessingStatus.PROCESSING
        asset.ai_status = AIStatus.RUNNING
        await session.commit()
        
        # ── Simulate AI processing (e.g., resizing, classification) ──
        logger.info(f"Simulating AI processing for 3 seconds...")
        await asyncio.sleep(3)  # Sleep without blocking async loop

        # Mark as completed
        asset.processing_status = ProcessingStatus.COMPLETED
        asset.ai_status = AIStatus.COMPLETED
        await session.commit()

        logger.info(f"Worker finished: ImageAsset {image_asset_id} processed successfully")


@celery_app.task(bind=True, max_retries=3)
def process_image_upload(self, image_asset_id: str) -> None:  # type: ignore[no-untyped-def]
    """Celery task triggered by ImageUploaded event.

    Args:
        image_asset_id: The UUID of the created ImageAsset.
    """
    logger.info(f"Queue consumed: process_image_upload for {image_asset_id}")
    try:
        # Run the async code inside the synchronous celery worker
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(_process_image_async(image_asset_id))
    except Exception as exc:
        logger.error(f"Worker failed with exception: {exc}")
        self.retry(exc=exc, countdown=5)
