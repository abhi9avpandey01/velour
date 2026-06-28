"""
Velour API — Vision Service (Metadata Aggregator).

Orchestrates the AI Gateway adapters to process uploaded images,
extract metadata, generate embeddings, and persist them via pgvector.
"""

import logging
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.adapters.clip_adapter import CLIPAdapter
from app.ai.adapters.florence_adapter import FlorenceAdapter
from app.ai.adapters.rembg_adapter import BackgroundRemovalAdapter
from app.ai.gateway import AIGateway
from app.core.storage import supabase, settings
from app.models.enums import AIStatus, ProcessingStatus
from app.models.image_asset import ImageAsset
from app.models.wardrobe_metadata import WardrobeMetadata
from app.models.wardrobe import WardrobeItem

logger = logging.getLogger(__name__)


class VisionService:
    """Aggregates metadata from various AI models and persists it."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.gateway = AIGateway()

    async def process_image(self, asset_id: str) -> None:
        """The main vision pipeline triggered by the Celery worker."""
        # 1. Fetch Asset
        stmt = select(ImageAsset).where(ImageAsset.id == asset_id)
        result = await self.session.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            logger.error(f"VisionService: ImageAsset {asset_id} not found.")
            return

        item_id = asset.wardrobe_item_id
        start_time = time.time()

        # Mark as running
        asset.processing_status = ProcessingStatus.PROCESSING
        asset.ai_status = AIStatus.RUNNING
        await self.session.commit()

        try:
            # 2. Download original image bytes from Supabase
            # Convert public URL to internal storage path
            path = f"users/{asset.wardrobe_item.user_id}/wardrobe/{item_id}/original.jpg"
            if asset.mime_type == "image/png":
                path = path.replace(".jpg", ".png")
            elif asset.mime_type == "image/webp":
                path = path.replace(".jpg", ".webp")

            logger.info(f"Downloading original image: {path}")
            res = supabase.storage.from_(settings.supabase_bucket).download(path)
            original_bytes = res

            # 3. Background Removal
            processed_bytes = self.gateway.execute_adapter(
                BackgroundRemovalAdapter, "remove_background", original_bytes
            )

            # 4. Upload processed image back to Supabase
            processed_path = f"users/{asset.wardrobe_item.user_id}/wardrobe/{item_id}/processed.png"
            supabase.storage.from_(settings.supabase_bucket).upload(
                path=processed_path,
                file=processed_bytes,
                file_options={"content-type": "image/png"},
            )
            processed_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(processed_path)

            # Update asset with thumbnail (using processed image for now)
            asset.thumbnail_url = processed_url

            # 5. Extract Attributes (Florence-2)
            # Use processed (no-bg) bytes so the model focuses entirely on the clothing
            attributes = self.gateway.execute_adapter(
                FlorenceAdapter, "extract_attributes", processed_bytes
            )

            # 6. Generate Embeddings (CLIP)
            embedding = self.gateway.execute_adapter(
                CLIPAdapter, "generate_embedding", processed_bytes
            )

            # 7. Persist Metadata
            inference_time = (time.time() - start_time) * 1000  # ms
            
            metadata = WardrobeMetadata(
                wardrobe_item_id=item_id,
                embedding=embedding,
                image_caption=attributes.get("caption"),
                category_attr=attributes.get("category"),
                primary_color=attributes.get("primary_color"),
                material=attributes.get("material"),
                pattern=attributes.get("pattern"),
                overall_confidence=attributes.get("overall_confidence"),
                model_version=attributes.get("model_version"),
                inference_time_ms=inference_time,
            )
            self.session.add(metadata)

            # Update final statuses
            asset.processing_status = ProcessingStatus.COMPLETED
            asset.ai_status = AIStatus.COMPLETED
            
            # Commit the transaction
            await self.session.commit()
            
            logger.info(f"Vision Pipeline completed for {item_id} in {inference_time:.0f}ms")

        except Exception as e:
            logger.error(f"Vision Pipeline failed for {item_id}: {e}", exc_info=True)
            asset.processing_status = ProcessingStatus.FAILED
            asset.ai_status = AIStatus.FAILED
            await self.session.commit()
            raise
