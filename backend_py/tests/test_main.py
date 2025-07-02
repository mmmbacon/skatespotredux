import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test that CORS headers are properly set"""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
    
    # Verify allowed origin
    allowed_origin = response.headers.get("access-control-allow-origin")
    assert allowed_origin in ["http://localhost:5173", "*"]


@pytest.mark.asyncio
async def test_nonexistent_endpoint(client: AsyncClient):
    """Test accessing a non-existent endpoint"""
    response = await client.get("/api/nonexistent")
    assert response.status_code == 404
    assert "Not Found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_method_not_allowed(client: AsyncClient):
    """Test using wrong HTTP method"""
    # Try to POST to a GET-only endpoint
    response = await client.post("/health")
    assert response.status_code == 405
    assert "Method Not Allowed" in response.json()["detail"]