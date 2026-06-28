"""
Velour API — Wardrobe API integration tests.
"""

from unittest.mock import patch
import uuid

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.enums import Category, Occasion, Season
from app.models.user import User


@pytest.fixture
def mock_user():
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
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
@patch("app.api.v1.wardrobe.WardrobeService")
@patch("app.api.deps.is_token_blacklisted")
async def test_create_wardrobe_item(mock_blacklisted, mock_service_cls, mock_repo_cls, client: AsyncClient, mock_user, auth_headers):
    mock_blacklisted.return_value = False
    
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_id.return_value = mock_user
    
    mock_service = mock_service_cls.return_value
    
    # Mock service return value
    class MockResponse:
        id = str(uuid.uuid4())
        user_id = str(mock_user.id)
        name = "New Jacket"
        category = Category.OUTERWEAR
        subcategory = "Jacket"
        color = "Blue"
        season = Season.WINTER
        occasion = Occasion.CASUAL
        image_url = "url"
        thumbnail_url = "url"
        wears_count = 0
        favorite = False
        archived = False
        
        # Pydantic requires dict output for serialization in test mock
        def model_dump(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "name": self.name,
                "category": self.category,
                "subcategory": self.subcategory,
                "color": self.color,
                "season": self.season,
                "occasion": self.occasion,
                "image_url": self.image_url,
                "thumbnail_url": self.thumbnail_url,
                "wears_count": 0,
                "favorite": False,
                "archived": False,
            }
            
    mock_service.create_item.return_value = MockResponse()

    payload = {
        "name": "New Jacket",
        "category": "Outerwear",
        "subcategory": "Jacket",
        "color": "Blue",
        "season": "Winter",
        "occasion": "Casual",
        "image_url": "url",
        "thumbnail_url": "url"
    }
    
    response = await client.post("/api/v1/wardrobe", json=payload, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "New Jacket"
    assert data["data"]["category"] == "Outerwear"
