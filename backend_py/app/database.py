from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# NOTE: we use the asyncpg driver for full async support
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://skateuser:skatepass@postgres:5432/skatespot",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session and ensures it is closed."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 