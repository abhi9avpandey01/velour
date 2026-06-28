"""
Velour API — Wardrobe repository tests.
"""

import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.enums import Category, Occasion, Season
from app.models.wardrobe import WardrobeItem
from app.repositories.wardrobe_repository import WardrobeRepository
from app.schemas.wardrobe import WardrobeFilterParams


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_user_id():
    return uuid.uuid4()


@pytest.fixture
def mock_wardrobe_item(mock_user_id):
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
    item.id = uuid.uuid4()
    return item


@pytest.mark.asyncio
async def test_get_by_id_and_user_found(mock_session, mock_wardrobe_item, mock_user_id):
    repo = WardrobeRepository(mock_session)
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_wardrobe_item
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id_and_user(mock_wardrobe_item.id, mock_user_id)
    assert result is not None
    assert result.name == "Test Shirt"


@pytest.mark.asyncio
async def test_list_by_user_with_filters(mock_session, mock_wardrobe_item, mock_user_id):
    repo = WardrobeRepository(mock_session)
    
    # Mock for count query and list query
    mock_count_result = AsyncMock()
    mock_count_result.scalar_one_or_none.return_value = 1
    
    mock_list_result = AsyncMock()
    mock_list_result.scalars.return_value.all.return_value = [mock_wardrobe_item]
    
    mock_session.execute.side_effect = [mock_count_result, mock_list_result]
    
    filters = WardrobeFilterParams(
        category=Category.TOPS,
        search="Test",
        limit=10,
    )
    
    items, total = await repo.list_by_user(mock_user_id, filters)
    assert total == 1
    assert len(items) == 1
    assert items[0].name == "Test Shirt"
