"""
Velour API — Celery worker tests.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.models.enums import AIStatus, ProcessingStatus
from app.models.image_asset import ImageAsset
from app.worker.tasks import _process_image_async


@pytest.fixture
def mock_asset():
    asset = ImageAsset(
        wardrobe_item_id=uuid.uuid4(),
        storage_path="path",
        original_url="url",
        mime_type="image/jpeg",
        file_size=100,
    )
    asset.id = uuid.uuid4()
    asset.processing_status = ProcessingStatus.NOT_STARTED
    asset.ai_status = AIStatus.WAITING
    return asset


@pytest.mark.asyncio
@patch("app.worker.tasks.async_session_factory")
@patch("app.worker.tasks.asyncio.sleep")
async def test_process_image_async_success(mock_sleep, mock_session_factory, mock_asset):
    """Test the async logic inside the Celery worker."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_asset
    mock_session.execute.return_value = mock_result
    
    # Run the worker function
    await _process_image_async(str(mock_asset.id))
    
    # Verify statuses were updated and committed
    assert mock_asset.processing_status == ProcessingStatus.COMPLETED
    assert mock_asset.ai_status == AIStatus.COMPLETED
    assert mock_session.commit.call_count == 2
    
    # Verify simulate sleep was called
    mock_sleep.assert_called_once_with(3)


@pytest.mark.asyncio
@patch("app.worker.tasks.async_session_factory")
async def test_process_image_async_not_found(mock_session_factory):
    """Test worker handles missing ImageAsset gracefully."""
    mock_session = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Should not raise exception
    await _process_image_async(str(uuid.uuid4()))
    
    # Verify no commits were made since it failed early
    mock_session.commit.assert_not_called()
