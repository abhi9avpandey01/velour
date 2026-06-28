"""
Velour API — Storage tests.
"""

import io
from unittest.mock import patch
import uuid

import pytest
from PIL import Image

from app.core.exceptions import ValidationError
from app.core.storage import StorageService, MAX_FILE_SIZE_BYTES


def create_test_image(format="JPEG", size=(100, 100)) -> io.BytesIO:
    """Helper to create a valid image buffer."""
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color="red")
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return file_obj


@pytest.mark.asyncio
async def test_validate_image_success():
    """Test successful image validation."""
    file_obj = create_test_image(format="JPEG", size=(200, 300))
    
    meta = await StorageService.validate_image(file_obj, "test.jpg")
    
    assert meta["width"] == 200
    assert meta["height"] == 300
    assert meta["mime_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_validate_image_invalid_mime():
    """Test rejection of invalid mime types."""
    file_obj = io.BytesIO(b"not an image")
    
    with pytest.raises(ValidationError, match="Unsupported file type"):
        await StorageService.validate_image(file_obj, "test.txt")


@pytest.mark.asyncio
async def test_validate_image_corrupted():
    """Test rejection of corrupted image files with valid extensions."""
    file_obj = io.BytesIO(b"not an image but has jpg extension")
    
    with pytest.raises(ValidationError, match="not a valid image or is corrupted"):
        await StorageService.validate_image(file_obj, "test.jpg")


@pytest.mark.asyncio
async def test_validate_image_too_large():
    """Test rejection of files exceeding size limits."""
    # Create a mock file that reports a large size
    class LargeFile(io.BytesIO):
        def tell(self):
            return MAX_FILE_SIZE_BYTES + 1
            
    file_obj = LargeFile(b"data")
    
    with pytest.raises(ValidationError, match="exceeds maximum allowed size"):
        await StorageService.validate_image(file_obj, "test.jpg")


@patch("app.core.storage.supabase")
def test_upload_original_image(mock_supabase):
    """Test the storage path generation and supabase upload call."""
    # Mock supabase client responses
    mock_storage = mock_supabase.storage.from_.return_value
    mock_storage.get_public_url.return_value = "http://example.com/image.jpg"
    
    user_id = uuid.uuid4()
    item_id = uuid.uuid4()
    file_obj = create_test_image()
    
    url = StorageService.upload_original_image(
        user_id=user_id,
        item_id=item_id,
        file_obj=file_obj,
        mime_type="image/jpeg"
    )
    
    assert url == "http://example.com/image.jpg"
    
    # Verify the path format is correct
    expected_path = f"users/{user_id}/wardrobe/{item_id}/original.jpg"
    mock_storage.upload.assert_called_once()
    call_kwargs = mock_storage.upload.call_args.kwargs
    assert call_kwargs["path"] == expected_path
    assert call_kwargs["file_options"]["content-type"] == "image/jpeg"
