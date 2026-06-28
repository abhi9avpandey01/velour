"""
Velour API — Upload endpoint tests.
"""

import io
from unittest.mock import AsyncMock, patch
import uuid

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.user import User


@pytest.fixture
def mock_user():
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.id = uuid.uuid4()
    user.is_active = True
    return user


@pytest.fixture
def auth_headers(mock_user):
    token = create_access_token(str(mock_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
@patch("app.api.deps.UserRepository")
@patch("app.api.v1.upload.ImageService")
@patch("app.api.deps.is_token_blacklisted")
async def test_upload_image_success(mock_blacklisted, mock_service_cls, mock_repo_cls, client: AsyncClient, mock_user, auth_headers):
    """Test a successful image upload through the API."""
    mock_blacklisted.return_value = False
    
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_id.return_value = mock_user
    
    mock_service = mock_service_cls.return_value
    
    # Mock service return value
    expected_item_id = str(uuid.uuid4())
    mock_service.handle_upload.return_value = {
        "item_id": expected_item_id,
        "processing_status": "PENDING"
    }

    # Create a dummy file for the multipart request
    files = {
        "file": ("test.jpg", io.BytesIO(b"dummy image data"), "image/jpeg")
    }
    
    response = await client.post("/api/v1/wardrobe/upload", files=files, headers=auth_headers)
    
    assert response.status_code == 202
    data = response.json()
    assert data["success"] is True
    assert data["data"]["item_id"] == expected_item_id
    assert data["data"]["processing_status"] == "PENDING"
    
    # Verify the service was called
    mock_service.handle_upload.assert_called_once()
