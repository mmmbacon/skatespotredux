import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.main import app
from app.routers.auth import get_current_user
from app.models import User

# Mock user for testing authenticated endpoints
@pytest.fixture
def test_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        avatar_url="http://example.com/avatar.png",
    )

async def override_get_current_user(test_user: User = pytest.fixture(autouse=True)):
    return test_user

app.dependency_overrides[get_current_user] = override_get_current_user


async def test_get_spots_empty(client: AsyncClient):
    response = await client.get("/spots/")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_spot(client: AsyncClient, test_user: User):
    app.dependency_overrides[get_current_user] = lambda: test_user
    spot_data = {
        "name": "Test Spot",
        "description": "A great place to skate.",
        "location": {"type": "Point", "coordinates": [10, 20]},
    }
    response = await client.post("/spots/", json=spot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == spot_data["name"]
    assert data["description"] == spot_data["description"]
    assert data["user_id"] == str(test_user.id)
    assert "id" in data


async def test_get_spots_with_one_spot(client: AsyncClient):
    response = await client.get("/spots/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Spot"

# Reset the override after tests
def teardown_module(module):
    app.dependency_overrides = {} 