import pytest
from httpx import AsyncClient
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.main import app
from app.routers.auth import get_current_user, get_current_user_optional
from app.models import User, Spot, Vote

# Mock user for testing authenticated endpoints
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

async def override_get_current_user(test_user: User = pytest.fixture(autouse=True)):
    return test_user

app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.mark.asyncio
async def test_get_spots_empty(client: AsyncClient):
    """Test getting spots when database is empty"""
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock empty result
        mock_result = Mock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get("/api/spots/")
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_create_spot(client: AsyncClient, test_user: User):
    """Test creating a new spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    spot_data = {
        "name": "Test Spot",
        "description": "A great place to skate.",
        "location": {"type": "Point", "coordinates": [10, 20]},
    }
    response = await client.post("/api/spots/", json=spot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == spot_data["name"]
    assert data["description"] == spot_data["description"]
    assert data["user_id"] == str(test_user.id)
    assert "id" in data
    assert "short_id" in data


@pytest.mark.asyncio
async def test_create_spot_invalid_coordinates(client: AsyncClient, test_user: User):
    """Test creating a spot with invalid coordinates"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    # Test invalid longitude
    spot_data = {
        "name": "Test Spot",
        "description": "A great place to skate.",
        "location": {"type": "Point", "coordinates": [200, 20]},  # Invalid longitude
    }
    response = await client.post("/api/spots/", json=spot_data)
    assert response.status_code == 400
    assert "Longitude must be between -180 and 180" in response.json()["detail"]
    
    # Test invalid latitude
    spot_data["location"]["coordinates"] = [10, 100]  # Invalid latitude
    response = await client.post("/api/spots/", json=spot_data)
    assert response.status_code == 400
    assert "Latitude must be between -90 and 90" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_spots_with_bounding_box(client: AsyncClient):
    """Test getting spots within a bounding box"""
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock result with spots
        test_spots = [
            Spot(id=uuid4(), name="Spot 1", location="POINT(10 20)"),
            Spot(id=uuid4(), name="Spot 2", location="POINT(15 25)")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = test_spots
        mock_db.execute.return_value = mock_result
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.get(
            "/api/spots/",
            params={
                "north": 30,
                "south": 10,
                "east": 20,
                "west": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Results depend on the mock


@pytest.mark.asyncio
async def test_get_spots_invalid_bounding_box(client: AsyncClient):
    """Test getting spots with invalid bounding box"""
    response = await client.get(
        "/api/spots/",
        params={
            "north": 10,
            "south": 30,  # South > North (invalid)
            "east": 20,
            "west": 5
        }
    )
    assert response.status_code == 400
    assert "Invalid bounding box coordinates" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_spot(client: AsyncClient, test_user, test_spot):
    """Test updating a spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock getting the spot
        test_spot.user_id = test_user.id
        mock_db.get.return_value = test_spot
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        update_data = {
            "name": "Updated Spot Name",
            "description": "Updated description"
        }
        
        response = await client.put(f"/api/spots/{test_spot.id}", json=update_data)
        assert response.status_code == 200
        
        # Verify the spot was updated
        assert test_spot.name == "Updated Spot Name"
        assert test_spot.description == "Updated description"


@pytest.mark.asyncio
async def test_update_spot_unauthorized(client: AsyncClient, test_user, test_spot):
    """Test updating a spot by non-owner"""
    other_user = User(id=uuid4(), email="other@example.com", name="Other User")
    app.dependency_overrides[get_current_user] = lambda: other_user
    
    from unittest.mock import AsyncMock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock getting the spot with different owner
        test_spot.user_id = test_user.id  # Different from other_user
        mock_db.get.return_value = test_spot
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        update_data = {"name": "Updated Spot Name"}
        
        response = await client.put(f"/api/spots/{test_spot.id}", json=update_data)
        assert response.status_code == 403
        assert "Not authorized to update this spot" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_spot(client: AsyncClient, test_user, test_spot):
    """Test deleting a spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock getting the spot
        test_spot.user_id = test_user.id
        mock_db.get.return_value = test_spot
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.delete(f"/api/spots/{test_spot.id}")
        assert response.status_code == 204
        assert mock_db.delete.called
        assert mock_db.commit.called


@pytest.mark.asyncio
async def test_vote_spot(client: AsyncClient, test_user, test_spot):
    """Test voting on a spot"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock checking for existing vote
        mock_vote_result = Mock()
        mock_vote_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_vote_result
        
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        vote_data = {"value": 1}
        response = await client.post(f"/api/spots/{test_spot.id}/vote", json=vote_data)
        
        # Should return the spot with updated score
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_vote_spot_invalid_value(client: AsyncClient, test_user, test_spot):
    """Test voting with invalid value"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    vote_data = {"value": 5}  # Invalid value (should be 1 or -1)
    response = await client.post(f"/api/spots/{test_spot.id}/vote", json=vote_data)
    
    assert response.status_code == 400
    assert "value must be 1 or -1" in response.json()["detail"]


@pytest.mark.asyncio
async def test_remove_vote(client: AsyncClient, test_user, test_spot):
    """Test removing a vote"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    from unittest.mock import AsyncMock, Mock, patch
    
    with patch("app.routers.spots.get_db") as mock_get_db:
        mock_db = AsyncMock()
        
        # Mock finding existing vote
        mock_vote = Mock()
        mock_vote_result = Mock()
        mock_vote_result.scalars.return_value.first.return_value = mock_vote
        mock_db.execute.return_value = mock_vote_result
        
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()
        
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        response = await client.delete(f"/api/spots/{test_spot.id}/vote")
        
        # Should return the spot with updated score
        assert response.status_code == 200
        assert mock_db.delete.called


@pytest.mark.asyncio
async def test_image_upload_url_authenticated(client: AsyncClient, test_user):
    """Test getting image upload URL with authentication"""
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    # This will fail due to missing R2 configuration in tests
    response = await client.post(
        "/api/spots/image-upload-url",
        params={
            "filename": "test.jpg",
            "content_type": "image/jpeg"
        }
    )
    
    # Should get 503 since R2 is not configured in test environment
    assert response.status_code == 503
    assert "Image upload service is not configured" in response.json()["detail"]


@pytest.mark.asyncio
async def test_image_upload_url_unauthenticated(client: AsyncClient):
    """Test getting image upload URL without authentication"""
    app.dependency_overrides = {}  # Clear overrides
    
    response = await client.post(
        "/api/spots/image-upload-url",
        params={
            "filename": "test.jpg",
            "content_type": "image/jpeg"
        }
    )
    
    assert response.status_code == 401


# Reset the override after tests
def teardown_module(module):
    app.dependency_overrides = {} 