"""
Velour API — Wardrobe service tests.
"""

import uuid
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.models.enums import Category, Occasion, Season
from app.models.wardrobe import WardrobeItem
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate
from app.services.wardrobe_service import WardrobeService


@pytest.fixture
def mock_user_id():
    return uuid.uuid4()


@pytest.fixture
def mock_item_id():
    return uuid.uuid4()


@pytest.fixture
def mock_item(mock_user_id, mock_item_id):
    item = WardrobeItem(
        user_id=mock_user_id,
        name="Test Shirt",
        category=Category.TOPS,
        subcategory="T-Shirt",
        color="Black",
        season=Season.ALL_SEASON,
        occasion=Occasion.CASUAL,
        image_url="http://example.com/image.jpg",
        thumbnail_url="http://example.com/thumb.jpg",
    )
    item.id = mock_item_id
    item.created_at = None
    item.updated_at = None
    return item


@pytest.mark.asyncio
@patch("app.services.wardrobe_service.WardrobeRepository")
async def test_create_item(mock_repo_cls, mock_user_id, mock_item):
    mock_repo = mock_repo_cls.return_value
    mock_repo.create.return_value = mock_item
    
    service = WardrobeService(AsyncMock())
    
    data = WardrobeItemCreate(
        name="Test Shirt",
        category=Category.TOPS,
        subcategory="T-Shirt",
        color="Black",
        season=Season.ALL_SEASON,
        occasion=Occasion.CASUAL,
        image_url="http://example.com/image.jpg",
        thumbnail_url="http://example.com/thumb.jpg",
    )
    
    result = await service.create_item(mock_user_id, data)
    assert result.name == "Test Shirt"
    assert result.user_id == str(mock_user_id)


@pytest.mark.asyncio
@patch("app.services.wardrobe_service.WardrobeRepository")
async def test_toggle_favorite_not_found(mock_repo_cls, mock_user_id, mock_item_id):
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_id_and_user.return_value = None
    
    service = WardrobeService(AsyncMock())
    
    with pytest.raises(NotFoundError):
        await service.toggle_favorite(mock_user_id, mock_item_id)


@pytest.mark.asyncio
@patch("app.services.wardrobe_service.WardrobeRepository")
async def test_update_item(mock_repo_cls, mock_user_id, mock_item_id, mock_item):
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_id_and_user.return_value = mock_item
    
    updated_item = WardrobeItem(
        user_id=mock_item.user_id,
        name="Updated Shirt",
        category=mock_item.category,
        subcategory=mock_item.subcategory,
        color=mock_item.color,
        season=mock_item.season,
        occasion=mock_item.occasion,
        image_url=mock_item.image_url,
        thumbnail_url=mock_item.thumbnail_url,
    )
    updated_item.id = mock_item.id
    updated_item.created_at = None
    updated_item.updated_at = None
    
    mock_repo.update_by_id.return_value = updated_item
    
    service = WardrobeService(AsyncMock())
    data = WardrobeItemUpdate(name="Updated Shirt")
    
    result = await service.update_item(mock_user_id, mock_item_id, data)
    assert result.name == "Updated Shirt"
