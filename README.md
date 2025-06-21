# SkateSpot Redux

A full-stack skate spot locator web application.

## Monorepo Layout

```
/               # pnpm workspace root
  frontend/     # Vue 3 + Vite + Pinia
  backend/      # NestJS API
  infra/        # Docker Compose & env files
```

## Quick Start (Local)

Prerequisites: Node 20+, pnpm, Docker.

```bash
# 1. Install dependencies
pnpm install -r

# 2. Run services without Docker (two terminals)
cd backend && pnpm run start:dev       # http://localhost:3000/health
cd frontend && pnpm run dev -- --host  # http://localhost:5173

# 3. Or spin up everything with Docker
cd infra && docker compose up --build
```

The frontend Home page should display the API health status returned from `GET /health`.
