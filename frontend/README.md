# SkateSpot Frontend (Vue 3 + Vite)

This directory contains the single-page application that users interact with.

## Tech stack

- **Vue 3** with `<script setup>` and TypeScript
- **Vite 6** – lightning-fast dev server & build
- **Pinia** – state management
- **Tailwind CSS** + **shadcn-vue** – component library & utility classes
- **Leaflet** + `@vue-leaflet/vue-leaflet` for interactive maps

## Local dev

```bash
# Hot-reload dev server (ports 5173)
pnpm -F frontend dev
```

The SPA proxies API calls directly to `http://localhost:3000` (backend) – no extra config needed while running via Docker Compose.

## Build for production

```bash
pnpm -F frontend build
# output in dist/ – automatically copied into the nginx image during docker build
```

## Project structure (src/)

```
components/   # reusable UI pieces (e.g. Map, Button)
composables/  # shared logic (e.g. useAuth)
assets/       # static icons/images
App.vue       # root component
main.ts       # app bootstrap
style.css     # Tailwind entry + global utilities
```
