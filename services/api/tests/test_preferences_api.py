"""
Velour API — Preference API Tests.
"""

import pytest
from httpx import AsyncClient

from app.models.enums import ChangedBy


@pytest.mark.asyncio
async def test_get_preferences(authorized_client: AsyncClient) -> None:
    """Test fetching preferences returns a profile."""
    response = await authorized_client.get("/api/v1/preferences")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert "preferred_colors" in data
    assert "confidence_score" in data


@pytest.mark.asyncio
async def test_update_preferences(authorized_client: AsyncClient) -> None:
    """Test updating preferences."""
    payload = {
        "preferred_colors": ["black", "grey"],
        "preferred_style": "minimalist",
        "changed_by": ChangedBy.USER.value,
    }
    
    response = await authorized_client.patch("/api/v1/preferences", json=payload)
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert data["preferred_colors"] == ["black", "grey"]
    assert data["preferred_style"] == "minimalist"


@pytest.mark.asyncio
async def test_get_preference_history(authorized_client: AsyncClient) -> None:
    """Test retrieving preference history."""
    # Ensure there's some history
    payload = {
        "preferred_colors": ["green"],
        "changed_by": ChangedBy.USER.value,
        "reason": "testing"
    }
    await authorized_client.patch("/api/v1/preferences", json=payload)
    
    # Get history
    response = await authorized_client.get("/api/v1/preferences/history")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert len(data) > 0
    assert data[0]["changed_field"] == "preferred_colors"
    assert data[0]["reason"] == "testing"


@pytest.mark.asyncio
async def test_reset_preferences(authorized_client: AsyncClient) -> None:
    """Test resetting preferences."""
    # Setup
    payload = {"preferred_colors": ["red"]}
    await authorized_client.patch("/api/v1/preferences", json=payload)
    
    # Reset
    response = await authorized_client.post("/api/v1/preferences/reset")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert data["preferred_colors"] == []
