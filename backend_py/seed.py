import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models.spot import Spot
from app.database import Base


async def seed_data():
    async with engine.begin() as conn:
        # Optional: Drop all tables and recreate them
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        user_result = await session.execute(select(User).filter_by(email="testuser@example.com"))
        user = user_result.scalars().first()

        if not user:
            print("Creating a new user...")
            user = User(
                email="testuser@example.com",
                name="Test User",
                picture="https://example.com/avatar.png"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"User created with ID: {user.id}")
        else:
            print(f"User already exists with ID: {user.id}")

        # Remove the old spot if it exists
        spot_result = await session.execute(select(Spot).filter_by(name="Downtown Ledges"))
        spot = spot_result.scalars().first()
        if spot:
            print("Deleting old spot 'Downtown Ledges'...")
            await session.delete(spot)
            await session.commit()
            print("Old spot deleted.")

        # Check if spot already exists
        spot_result = await session.execute(select(Spot).filter_by(name="Shaw Millennium Park"))
        spot = spot_result.scalars().first()

        if not spot:
            print("Creating a new spot in Calgary...")
            # Coordinates for Calgary, AB
            new_spot = Spot(
                name="Shaw Millennium Park",
                description="A large, well-known skate park in Calgary.",
                location='SRID=4326;POINT(-114.09 51.05)', # Longitude, Latitude
                user_id=user.id,
                photos=[{"url": "https://example.com/calgary_spot.jpg"}]
            )
            session.add(new_spot)
            await session.commit()
            await session.refresh(new_spot)
            print(f"Spot created with ID: {new_spot.id}")
        else:
            print(f"Spot 'Shaw Millennium Park' already exists with ID: {spot.id}")


if __name__ == "__main__":
    # Add imports for select here to avoid polluting the global namespace
    from sqlalchemy import select
    print("Seeding database...")
    asyncio.run(seed_data())
    print("Seeding complete.") 