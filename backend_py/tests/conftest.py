import pytest
import asyncio
from httpx import AsyncClient
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import JSON
from geoalchemy2.types import Geometry

from app.main import app
from app.database import Base, get_db

# Use a separate in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL)

# Mock PostGIS types for SQLite
@event.listens_for(Base.metadata, "before_create")
def _mock_spatialite(target, connection, **kw):
    if connection.dialect.name == "sqlite":
        from sqlalchemy.dialects.postgresql import JSONB

        # For Geometry and JSONB
        for table in target.tables.values():
            for column in table.c:
                if isinstance(column.type, Geometry):
                    column.type = JSON()
                if isinstance(column.type, JSONB):
                    column.type = JSON()


TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Apply migrations to the in-memory database
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    async def setup_db_async():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(setup_db_async())
    yield
    # Teardown can be added here if needed

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac 