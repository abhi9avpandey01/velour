"""
Velour API — Authentication endpoint tests.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.fixture
def mock_user():
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("ValidPassword123!"),
        first_name="Test",
        last_name="User",
    )
    user.id = "00000000-0000-0000-0000-000000000000"
    user.is_active = True
    return user


@pytest.mark.asyncio
@patch("app.services.auth_service.UserRepository")
async def test_register_success(mock_repo_cls, client: AsyncClient, mock_user):
    """Test successful user registration."""
    mock_repo = mock_repo_cls.return_value
    mock_repo.exists_by_email.return_value = False
    mock_repo.exists_by_username.return_value = False
    mock_repo.create.return_value = mock_user

    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "ValidPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["username"] == "testuser"
    assert "password_hash" not in data["data"]


@pytest.mark.asyncio
@patch("app.services.auth_service.UserRepository")
async def test_register_weak_password(mock_repo_cls, client: AsyncClient):
    """Test registration with weak password fails validation."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak",
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "errors" in data["error"]["details"]


@pytest.mark.asyncio
@patch("app.services.auth_service.UserRepository")
async def test_register_duplicate_email(mock_repo_cls, client: AsyncClient):
    """Test registration with duplicate email fails with conflict."""
    mock_repo = mock_repo_cls.return_value
    mock_repo.exists_by_email.return_value = True
    
    payload = {
        "email": "test@example.com",
        "username": "testuser2",
        "password": "ValidPassword123!",
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMAIL_TAKEN"


@pytest.mark.asyncio
@patch("app.services.auth_service.UserRepository")
async def test_login_success(mock_repo_cls, client: AsyncClient, mock_user):
    """Test successful user login."""
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_email.return_value = mock_user

    payload = {
        "email": "test@example.com",
        "password": "ValidPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
@patch("app.services.auth_service.UserRepository")
async def test_login_invalid_password(mock_repo_cls, client: AsyncClient, mock_user):
    """Test login with wrong password fails."""
    mock_repo = mock_repo_cls.return_value
    mock_repo.get_by_email.return_value = mock_user

    payload = {
        "email": "test@example.com",
        "password": "WrongPassword123!",
    }
    
    response = await client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"
