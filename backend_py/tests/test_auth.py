import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime, timedelta
from jose import jwt

from app.main import app
from app.models.user import User
from app.config import get_settings


@pytest.fixture
def mock_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        avatar_url="http://example.com/avatar.png",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_google_login_redirect(client: AsyncClient):
    """Test that the Google login endpoint returns a redirect"""
    response = await client.get("/api/auth/google/login", follow_redirects=False)
    assert response.status_code == 302
    assert "accounts.google.com" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_google_callback_success(client: AsyncClient, mock_user):
    """Test successful OAuth callback"""
    settings = get_settings()
    
    # Mock the OAuth token exchange
    mock_token = {
        "userinfo": {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "http://example.com/avatar.png"
        }
    }
    
    with patch("app.routers.auth.oauth.google.authorize_access_token", new_callable=AsyncMock) as mock_oauth:
        mock_oauth.return_value = mock_token
        
        # Create a mock request with necessary attributes
        response = await client.get("/api/auth/google/callback?code=test_code", follow_redirects=False)
        
        assert response.status_code == 302
        # Check that JWT token is in the redirect URL
        location = response.headers.get("location", "")
        assert "token=" in location
        
        # Verify the cookie was set
        assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_google_callback_oauth_failure(client: AsyncClient):
    """Test OAuth callback failure"""
    with patch("app.routers.auth.oauth.google.authorize_access_token", new_callable=AsyncMock) as mock_oauth:
        mock_oauth.side_effect = Exception("OAuth error")
        
        response = await client.get("/api/auth/google/callback?code=test_code")
        assert response.status_code == 400
        assert "OAuth authentication failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_valid_token(client: AsyncClient, mock_user):
    """Test getting current user with valid token"""
    settings = get_settings()
    
    # Create a valid JWT token
    payload = {
        "sub": str(mock_user.id),
        "name": mock_user.name,
        "email": mock_user.email,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    # Mock the database query
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get(
            "/api/auth/google/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["name"] == mock_user.name


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token"""
    response = await client.get(
        "/api/auth/google/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(client: AsyncClient):
    """Test getting current user with expired token"""
    settings = get_settings()
    
    # Create an expired JWT token
    payload = {
        "sub": str(uuid4()),
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    response = await client.get(
        "/api/auth/google/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test getting current user without token"""
    response = await client.get("/api/auth/google/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_optional_with_token(client: AsyncClient, mock_user):
    """Test get_current_user_optional with valid token"""
    settings = get_settings()
    
    # Create a valid JWT token
    payload = {
        "sub": str(mock_user.id),
        "name": mock_user.name,
        "email": mock_user.email,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    # Test that optional auth works with valid token
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        # This would be used in an endpoint that uses get_current_user_optional
        from app.routers.auth import get_current_user_optional
        from fastapi.security import HTTPAuthorizationCredentials
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user_optional(credentials, mock_db)
        assert user == mock_user


@pytest.mark.asyncio
async def test_get_current_user_optional_without_token(client: AsyncClient):
    """Test get_current_user_optional without token returns None"""
    from app.routers.auth import get_current_user_optional
    
    with patch("app.routers.auth.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        user = await get_current_user_optional(None, mock_db)
        assert user is None