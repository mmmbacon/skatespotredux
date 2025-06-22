import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.spot import Spot


async def seed_data():
    async with engine.begin() as conn:
        # Optional: Drop all tables and recreate them
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # ----------- Create or fetch seed users ------------------
        seed_users_data = [
            {
                "email": "skater1@example.com",
                "name": "Alex Skater",
                "avatar_url": "https://randomuser.me/api/portraits/men/32.jpg",
            },
            {
                "email": "skater2@example.com",
                "name": "Bailey Shred",
                "avatar_url": "https://randomuser.me/api/portraits/women/44.jpg",
            },
        ]

        users: list[User] = []
        for udata in seed_users_data:
            result = await session.execute(select(User).where(User.email == udata["email"]))
            user = result.scalars().first()
            if not user:
                user = User(**udata)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                print(f"Created user {user.email} -> {user.id}")
            users.append(user)

        # ------------- Seed spots for those users ----------------
        seed_spots_data = [
            {
                "name": "Shaw Millennium Park",
                "description": "Iconic downtown skatepark with bowls and street sections.",
                "lon": -114.068986,
                "lat": 51.045002,
                "user": users[0],
            },
            {
                "name": "Southwood Skatepark",
                "description": "Neighborhood park with fun ledges and rails.",
                "lon": -114.07137,
                "lat": 50.96993,
                "user": users[1],
            },
            {
                "name": "Huntington Hills DIY",
                "description": "Small DIY spot under the bridge.",
                "lon": -114.0715,
                "lat": 51.1069,
                "user": users[0],
            },
        ]

        for sdata in seed_spots_data:
            # Skip if spot already exists
            result = await session.execute(select(Spot).where(Spot.name == sdata["name"]))
            if result.scalars().first():
                continue

            spot = Spot(
                name=sdata["name"],
                description=sdata["description"],
                location=f"SRID=4326;POINT({sdata['lon']} {sdata['lat']})",
                user_id=sdata["user"].id,
                photos=[],
            )
            session.add(spot)

        await session.commit()
        print("Seed spots inserted (if they didn't already exist).")


# ------------------ Entrypoint -----------------------

if __name__ == "__main__":
    print("Seeding database with demo users and Calgary spots…")
    asyncio.run(seed_data())
    print("Seeding complete.") 