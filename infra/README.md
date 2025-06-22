# Infrastructure (Docker Compose)

This directory stitches the whole stack together for local development.

```
services:
  postgres   # Bitnami PostgreSQL 15 + PostGIS
  backend    # FastAPI API (hot-reload)
  frontend   # Vue SPA served by nginx
```

## Commands

```bash
# Build images only
docker compose build

# Start everything in foreground (logs combined)
docker compose up --build

# Start in detached mode
docker compose up -d

# Stop & remove containers (keep db volume)
docker compose down

# Wipe database volume
docker compose down -v
```

## Environment files

`env/.env.local` (git-ignored) is injected into **both** postgres and backend.

> Copy `sample.env` to `env/.env.local` and fill in your Google OAuth creds before first run.
