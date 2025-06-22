# SkateSpot Backend (FastAPI)

This service powers the REST / JSON APIs for the SkateSpot Redux application.

## Tech stack

- **FastAPI 0.111** – modern Python web framework with async support.
- **SQLAlchemy 2 (async)** – ORM / query builder.
- **PostgreSQL 15 + PostGIS** – spatial queries for skate-spot coordinates.
- **Authlib** – Google OAuth 2.0 flow.
- **PyJWT / jose** – signs first-party JWTs returned to the frontend.

## Local dev

```bash
# Run only the backend container (database must already be running)
cd infra && docker compose up backend

# Hot-reload outside Docker (uses your host Python venv)
cd backend_py
uvicorn app.main:app --reload  # make sure .env is present
```

### Important environment variables (set in `infra/env/.env.local`)

| Variable                    | Description                                                            |
| --------------------------- | ---------------------------------------------------------------------- |
| `DATABASE_URL`              | Async SQLAlchemy URL, already set to connect to the `postgres` service |
| `GOOGLE_CLIENT_ID / SECRET` | OAuth creds from Google Cloud Console                                  |
| `JWT_SECRET`                | HMAC secret used to sign JWTs                                          |

## Tests

```bash
# one-off inside Docker
cd infra && docker compose run --rm backend pytest
# or, on host
pytest backend_py/tests
```

## Database migrations

Alembic is **not** wired yet – tracked in project planning doc.
