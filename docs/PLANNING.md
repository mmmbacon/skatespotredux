# SkateSpot Redux – Product & Engineering Plan

_Last updated: {{DATE}}_

## Vision

A community-driven map where skaters can discover, share, and discuss the best spots in their city.

## 2025 Q3 Milestones

| #   | Epic                | Outcome                                                                     |
| --- | ------------------- | --------------------------------------------------------------------------- |
| M1  | **Auth & Profiles** | Google OAuth login, basic user profile page                                 |
| M2  | **Spots CRUD**      | Create/read/update/delete skate-spot records (lat/lng, description, photos) |
| M3  | **Interactive Map** | Frontend map with clustered markers & detail popovers                       |
| M4  | **Engagement**      | Comments + upvote/downvote                                                  |
| M5  | **Mobile polish**   | PWA install, offline tiles cache                                            |

## Tech decisions

- **Vue 3 + Vite + Tailwind/shadcn** for fast iteration and accessible design tokens.
- **FastAPI + SQLAlchemy 2 async** gives Pythonic productivity and strong typing.
- **PostGIS** because spatial queries (distance, bounding boxes) are first-class.
- **Docker Compose** for local; target Fly.io or K8s for prod.

## Backlog (icebox)

- Spot moderation / flagging
- Social share deep-links
- S3 image storage + CDN
- Email digests of new spots nearby
- OAuth providers: Apple, Instagram

---

_This file is the single source of truth for roadmap discussions. PRs welcome!_
