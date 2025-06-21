# SkateSpot Redux

A full-stack skate spot locator web application.

## Monorepo Layout

```
/               # pnpm workspace root
  frontend/     # Vue 3 + Vite + Pinia
  backend_py/   # FastAPI API
  infra/        # Docker Compose & env files
```

## Quick Start (Local)

Prerequisites: Node 20+, pnpm, Docker.

```bash
# 1. Configure Environment
# Copy the sample environment file.
cp infra/sample.env infra/env/.env.local

# Now, open infra/env/.env.local and replace the placeholder values
# for GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET with your credentials.

# 2. Install dependencies
pnpm install

# 3. Spin up everything with Docker
cd infra && docker compose up --build
```

The application will be available at `http://localhost:5173`.

The backend health-check is at `http://localhost:3000/health`.

## Development

All `docker compose` commands should be run from the `infra/` directory.

- **Build all services:** `docker compose build`
- **Build a specific service:** `docker compose build <service_name>` (e.g., `backend`)
- **Start all services:** `docker compose up`
- **Stop and remove all services:** `docker compose down`
- **View logs for all services:** `docker compose logs -f`
- **View logs for a specific service:** `docker compose logs -f <service_name>`
- **Run a one-off command in a service:** `docker compose run --rm <service_name> <command>` (e.g., `docker compose run --rm backend pytest`)
- **Open a shell inside a running service:** `docker compose exec <service_name> /bin/sh`
