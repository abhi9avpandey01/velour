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

    async def process_image(self, asset_id: str) -> dict:
        """The main vision pipeline triggered by the API."""
        # 1. Fetch Asset
        stmt = select(ImageAsset).where(ImageAsset.id == asset_id)
        result = await self.session.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            logger.error(f"VisionService: ImageAsset {asset_id} not found.")
            return {}

        item_id = asset.wardrobe_item_id
        start_time = time.time()

        # Mark as running
        asset.processing_status = ProcessingStatus.PROCESSING
        asset.ai_status = AIStatus.RUNNING
        await self.session.commit()

        try:
            # 2. Download original image bytes from Supabase
            # Fetch WardrobeItem to get user_id and to update it later
            item = await self.session.get(WardrobeItem, item_id)
            if not item:
                logger.error(f"VisionService: WardrobeItem {item_id} not found.")
                return {}

            # Convert public URL to internal storage path
            path = f"users/{item.user_id}/wardrobe/{item_id}/original.jpg"
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
            processed_path = f"users/{item.user_id}/wardrobe/{item_id}/processed.png"
            supabase.storage.from_(settings.supabase_bucket).upload(
                path=processed_path,
                file=processed_bytes,
                file_options={"content-type": "image/png", "x-upsert": "true"},
            )
            processed_url = supabase.storage.from_(settings.supabase_bucket).get_public_url(processed_path)

            # Update asset with thumbnail (using processed image for now)
            asset.thumbnail_url = processed_url

            # 5. Extract Attributes (Gemini)
            # Use processed (no-bg) bytes so the model focuses entirely on the clothing
            from app.services.ai_service import AIService
            ai_service = AIService()
            attributes = ai_service.analyzeClothing(processed_bytes)

            # 6. Generate Embeddings (CLIP)
            embedding = self.gateway.execute_adapter(
                CLIPAdapter, "generate_embedding", processed_bytes
            )

            # 7. Persist Metadata
            inference_time = (time.time() - start_time) * 1000  # ms
            
            conf = attributes.get("confidence", 1.0)
            
            stmt = select(WardrobeMetadata).where(WardrobeMetadata.wardrobe_item_id == item_id)
            existing_metadata = (await self.session.execute(stmt)).scalar_one_or_none()
            
            if existing_metadata:
                existing_metadata.embedding = embedding
                existing_metadata.image_caption = attributes.get("description")
                existing_metadata.category_attr = {"value": attributes.get("category"), "confidence": conf}
                existing_metadata.subcategory_attr = {"value": attributes.get("subcategory"), "confidence": conf}
                existing_metadata.primary_color = {"value": attributes.get("color"), "confidence": conf}
                existing_metadata.material = {"value": attributes.get("material", "Unknown"), "confidence": conf}
                existing_metadata.pattern = {"value": attributes.get("pattern"), "confidence": conf}
                existing_metadata.overall_confidence = conf
                existing_metadata.model_version = attributes.get("model_version")
                existing_metadata.inference_time_ms = inference_time
            else:
                metadata = WardrobeMetadata(
                    wardrobe_item_id=item_id,
                    embedding=embedding,
                    image_caption=attributes.get("description"),
                    category_attr={"value": attributes.get("category"), "confidence": conf},
                    subcategory_attr={"value": attributes.get("subcategory"), "confidence": conf},
                    primary_color={"value": attributes.get("color"), "confidence": conf},
                    material={"value": attributes.get("material", "Unknown"), "confidence": conf},
                    pattern={"value": attributes.get("pattern"), "confidence": conf},
                    overall_confidence=conf,
                    model_version=attributes.get("model_version"),
                    inference_time_ms=inference_time,
                )
                self.session.add(metadata)

            # Update WardrobeItem
            if attributes.get("color"):
                item.color = attributes.get("color")
            if attributes.get("category"):
                item.category = attributes.get("category")
            if attributes.get("subcategory"):
                item.subcategory = attributes.get("subcategory")
                
            item.thumbnail_url = processed_url
            self.session.add(item)

            # Update final statuses
            asset.processing_status = ProcessingStatus.COMPLETED
            asset.ai_status = AIStatus.COMPLETED
            
            # Commit the transaction
            await self.session.commit()
            
            logger.info(f"Vision Pipeline completed for {item_id} in {inference_time:.0f}ms")
            return {
                "category": attributes.get("category"),
                "primary_color": attributes.get("color"),
                "pattern": attributes.get("pattern"),
                "material": attributes.get("style", "Unknown"),
                "caption": attributes.get("description"),
                "overall_confidence": attributes.get("confidence", 1.0),
                "outfit_suggestions": attributes.get("outfit_suggestions"),
                "model_version": attributes.get("model_version"),
            }

        except Exception as e:
            logger.error(f"Vision Pipeline failed for {item_id}: {e}", exc_info=True)
            asset.processing_status = ProcessingStatus.FAILED
            asset.ai_status = AIStatus.FAILED
            await self.session.commit()
            raise
