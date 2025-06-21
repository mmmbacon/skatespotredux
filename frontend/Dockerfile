# ---- Build Stage ----
FROM node:20-alpine AS builder

RUN corepack enable && corepack prepare pnpm@10.12.1 --activate

WORKDIR /app

COPY . .

RUN pnpm install --no-frozen-lockfile

RUN pnpm run build

# ---- Production Stage ----
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 