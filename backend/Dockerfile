# ---- Build Stage ----
FROM node:20-alpine AS builder

# Enable pnpm via corepack
RUN corepack enable && corepack prepare pnpm@10.12.1 --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

RUN pnpm run build

# ---- Production Stage ----
FROM node:20-alpine
RUN corepack enable && corepack prepare pnpm@10.12.1 --activate
WORKDIR /app

# Copy only the built artifacts and node_modules from previous stage
COPY --from=builder /app .

EXPOSE 3000
CMD ["node", "dist/main.js"] 