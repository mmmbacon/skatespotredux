import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.models import User, Spot, Comment
from app.routers.auth import get_current_user


@pytest.fixture
def test_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        avatar_url="http://example.com/avatar.png",
    )


@pytest.fixture
def test_spot(test_user):
    return Spot(
        id=uuid4(),
        short_id="abc123",
        name="Test Skate Spot",
        description="A great place to skate",
        location="POINT(10 20)",
        user_id=test_user.id,
        user=test_user,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_create_comment_success(client: AsyncClient, test_user, test_spot):
    """Test creating a comment on a spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    # Mock the database to return the spot
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock the spot exists check
        mock_db.get.return_value = test_spot
        
        # Mock the commit and refresh
        mock_db.commit = AsyncMock()
        mock_db.add = Mock()
        mock_db.refresh = AsyncMock()
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        comment_data = {
            "content": "This spot is awesome!"
        }
        
        response = await client.post(
            f"/api/spots/{test_spot.id}/comments",
            json=comment_data
        )
        
        assert response.status_code == 201
        assert mock_db.add.called
        assert mock_db.commit.called


@pytest.mark.asyncio
async def test_create_comment_spot_not_found(client: AsyncClient, test_user):
    """Test creating a comment on a non-existent spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, patch
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock the spot doesn't exist
        mock_db.get.return_value = None
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        comment_data = {
            "content": "This spot is awesome!"
        }
        
        fake_spot_id = uuid4()
        response = await client.post(
            f"/api/spots/{fake_spot_id}/comments",
            json=comment_data
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Spot not found"


@pytest.mark.asyncio
async def test_create_comment_unauthenticated(client: AsyncClient, test_spot):
    """Test creating a comment without authentication"""
    # Reset any overrides
    app.dependency_overrides = {}
    
    comment_data = {
        "content": "This spot is awesome!"
    }
    
    response = await client.post(
        f"/api/spots/{test_spot.id}/comments",
        json=comment_data
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_comments_for_spot(client: AsyncClient, test_spot, test_user):
    """Test getting comments for a spot"""
    from unittest.mock import AsyncMock, Mock, patch
    
    # Create test comments
    test_comments = [
        Comment(
            id=uuid4(),
            content="Great spot!",
            user_id=test_user.id,
            spot_id=test_spot.id,
            created_at=datetime.utcnow()
        ),
        Comment(
            id=uuid4(),
            content="Love skating here",
            user_id=test_user.id,
            spot_id=test_spot.id,
            created_at=datetime.utcnow()
        )
    ]
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock the query result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = test_comments
        mock_db.execute.return_value = mock_result
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get(f"/api/spots/{test_spot.id}/comments")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["content"] in ["Great spot!", "Love skating here"]


@pytest.mark.asyncio
async def test_get_comments_empty(client: AsyncClient, test_spot):
    """Test getting comments for a spot with no comments"""
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get(f"/api/spots/{test_spot.id}/comments")
        
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_get_comments_with_pagination(client: AsyncClient, test_spot):
    """Test getting comments with pagination parameters"""
    from unittest.mock import AsyncMock, Mock, patch
    
    # Create many test comments
    test_comments = [
        Comment(
            id=uuid4(),
            content=f"Comment {i}",
            user_id=uuid4(),
            spot_id=test_spot.id,
            created_at=datetime.utcnow()
        )
        for i in range(5)
    ]
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock the query result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = test_comments[:2]  # Return only 2
        mock_db.execute.return_value = mock_result
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get(
            f"/api/spots/{test_spot.id}/comments",
            params={"skip": 0, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
async def test_comment_content_validation(client: AsyncClient, test_user, test_spot):
    """Test comment content validation"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, patch
    
    with patch("app.routers.comments.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_db.get.return_value = test_spot
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        # Test empty content
        response = await client.post(
            f"/api/spots/{test_spot.id}/comments",
            json={"content": ""}
        )
        
        # FastAPI should validate this based on the schema
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test missing content field
        response = await client.post(
            f"/api/spots/{test_spot.id}/comments",
            json={}
        )
        
        assert response.status_code == 422


# Clean up overrides after tests
def teardown_module(module):
    app.dependency_overrides = {}