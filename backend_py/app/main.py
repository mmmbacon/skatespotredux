import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .config import get_settings
from .routers import auth, spots
from .database import Base, engine

app = FastAPI(title="SkateSpot API", version="0.1.0")

# Allow frontend origin during dev
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=get_settings().JWT_SECRET)

app.include_router(auth.router)
app.include_router(spots.router)

@app.get("/health")
async def health():
    """Simple health-check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["/app"],
        reload_excludes=["/app/alembic"],
    ) 