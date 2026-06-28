"""
Velour API — User management endpoint tests.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.user import User


@pytest.fixture
def mock_user():
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
    )
    user.id = "00000000-0000-0000-0000-000000000000"
    user.is_active = True
    return user


@pytest.fixture
def auth_headers(mock_user):
    token = create_access_token(str(mock_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
@patch("app.api.deps.UserRepository")
@patch("app.services.user_service.UserRepository")
@patch("app.api.deps.is_token_blacklisted")
async def test_get_me_success(mock_blacklisted, mock_user_repo_cls, mock_deps_repo_cls, client: AsyncClient, mock_user, auth_headers):
    """Test getting current user profile."""
    mock_blacklisted.return_value = False
    
    mock_deps_repo = mock_deps_repo_cls.return_value
    mock_deps_repo.get_by_id.return_value = mock_user
    
    mock_user_repo = mock_user_repo_cls.return_value
    mock_user_repo.get_by_id.return_value = mock_user

    response = await client.get("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test getting current user profile without token fails."""
    response = await client.get("/api/v1/users/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
@patch("app.api.deps.UserRepository")
@patch("app.services.user_service.UserRepository")
@patch("app.api.deps.is_token_blacklisted")
async def test_update_me_success(mock_blacklisted, mock_user_repo_cls, mock_deps_repo_cls, client: AsyncClient, mock_user, auth_headers):
    """Test updating current user profile."""
    mock_blacklisted.return_value = False
    
    mock_deps_repo = mock_deps_repo_cls.return_value
    mock_deps_repo.get_by_id.return_value = mock_user
    
    mock_user_repo = mock_user_repo_cls.return_value
    
    updated_user = User(
        email="test@example.com",
        username="testuser",
        first_name="Updated",
        last_name="User",
    )
    updated_user.id = mock_user.id
    updated_user.is_active = True
    
    mock_user_repo.update_by_id.return_value = updated_user

    payload = {
        "first_name": "Updated"
    }
    
    response = await client.patch("/api/v1/users/me", json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["first_name"] == "Updated"
