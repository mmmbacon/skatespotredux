# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Kga8gtAb9vso7

ARG NODE_VERSION=20.19.2

FROM node:${NODE_VERSION}-alpine

# Use production node environment by default.
ENV NODE_ENV production

RUN corepack enable

WORKDIR /app

# Copy all the package manager files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/package.json ./frontend/

# Install dependencies
RUN --mount=type=cache,target=/root/.pnpm pnpm install --frozen-lockfile

# We are building the frontend service, so we change the workdir to the frontend package
WORKDIR /app/frontend

# Copy the rest of the source files into the image.
# Note that we are in /app/frontend now. The context for COPY is still the build context root.
COPY frontend/ .

# Run as non-root user
USER node

# Expose the port that the application listens on.
EXPOSE 5173

# Run the application.
CMD ["pnpm", "run", "dev", "--host"]