"""
Velour API — Vision Service tests.
"""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import uuid

from app.services.vision_service import VisionService
from app.models.enums import AIStatus, ProcessingStatus


@pytest.fixture
def mock_asset():
    asset = MagicMock()
    asset.id = uuid.uuid4()
    asset.wardrobe_item_id = uuid.uuid4()
    asset.mime_type = "image/jpeg"
    asset.wardrobe_item.user_id = uuid.uuid4()
    return asset


@pytest.mark.asyncio
@patch("app.services.vision_service.supabase")
@patch("app.services.vision_service.AIService.analyzeClothing")
@patch("app.services.vision_service.AIGateway.execute_adapter")
async def test_process_image_success(mock_execute_adapter, mock_analyze_clothing, mock_supabase, mock_asset):
    """Test the full vision pipeline aggregation without running real models."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_asset
    mock_session.execute.return_value = mock_result
    
    # Mock supabase download/upload
    mock_supabase.storage.from_.return_value.download.return_value = b"raw bytes"
    mock_supabase.storage.from_.return_value.get_public_url.return_value = "http://processed.png"
    
    # Mock AI Gateway adapter results (side_effect returns sequential values for each call)
    mock_execute_adapter.side_effect = [
        b"processed PNG bytes", # BackgroundRemovalAdapter
        [0.1, 0.2, 0.3] * 170 + [0.4, 0.5] # CLIPAdapter (512 dims)
    ]
    
    # Mock AIService
    mock_analyze_clothing.return_value = {
        "description": "A black t-shirt",
        "category": "Tops",
        "color": "black",
        "pattern": "solid",
        "style": "Casual",
        "confidence": 0.95,
        "model_version": "gemini-1.5-pro"
    }
    
    service = VisionService(mock_session)
    await service.process_image(str(mock_asset.id))
    
    # Verify the asset statuses were updated correctly
    assert mock_asset.processing_status == ProcessingStatus.COMPLETED
    assert mock_asset.ai_status == AIStatus.COMPLETED
    
    # Verify session commit was called (once to mark running, once to finish)
    assert mock_session.commit.call_count == 2
    
    # Verify metadata was added
    mock_session.add.assert_called()
    added_obj = mock_session.add.call_args[0][0]
    
    # Check WardrobeMetadata fields
    assert added_obj.wardrobe_item_id == mock_asset.wardrobe_item_id
    assert added_obj.image_caption == "A black t-shirt"
    assert len(added_obj.embedding) == 512
    assert added_obj.category_attr["value"] == "Tops"
