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
