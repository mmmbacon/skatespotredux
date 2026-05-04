# Neon Migration Guide

This document describes the migration from Fly Postgres to Neon and the automated PR preview database workflow.

## Overview

We've migrated from Fly Postgres to Neon for the following benefits:

- **Serverless Postgres**: Automatic scaling and pay-per-use pricing
- **Database Branching**: Instant database branches for each PR
- **Better Developer Experience**: Preview databases for every pull request
- **Cost Efficiency**: No need to manage separate database instances

## Architecture

### Production Database

The main production database is hosted on Neon and connected via the `DATABASE_URL` environment variable.

### PR Preview Databases

When a pull request is opened, a GitHub Actions workflow automatically:

1. Creates a new Neon database branch from the main branch
2. Names it `pr-{number}` (e.g., `pr-123`)
3. Comments on the PR with the connection string
4. The preview database is an instant copy of production data

When the PR is closed, another workflow:

1. Deletes the Neon database branch
2. Destroys the associated Fly.io preview app (if exists)
3. Comments on the PR confirming cleanup

## Setup Instructions

### 1. Prerequisites

You need a Neon account and project. Sign up at [neon.tech](https://neon.tech).

### 2. Get Your Neon Credentials

From your Neon dashboard:

1. Go to your project settings
2. Copy the **Project ID**
3. Generate an **API Key** (Settings → API Keys → Create new API key)

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

- `NEON_PROJECT_ID`: Your Neon project ID
- `NEON_API_KEY`: Your Neon API key
- `FLY_API_TOKEN`: Your Fly.io API token (optional, if using Fly.io for apps)

### 4. Update Environment Variables

#### For Local Development

Continue using Docker Compose with local Postgres:

```bash
cp infra/sample.env infra/env/.env.local
```

No changes needed - local development still uses the Docker Compose Postgres instance.

#### For Production Deployment

Create a production environment file:

```bash
cp infra/sample.env.production infra/.env.production
```

Then update with your Neon connection string:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname?sslmode=require
```

You can get this connection string from:
- Your Neon dashboard
- PR comments (for preview branches)

### 5. Migrate Existing Data (One-time)

If you're migrating from Fly Postgres:

1. Export your Fly Postgres database:
   ```bash
   flyctl postgres connect -a your-fly-postgres-app
   pg_dump -Fc > backup.dump
   ```

2. Import to Neon:
   ```bash
   pg_restore -d "your-neon-connection-string" backup.dump
   ```

3. Run any pending migrations:
   ```bash
   cd backend_py
   alembic upgrade head
   ```

## Workflows

### PR Open Workflow

**File**: `.github/workflows/pr-open.yml`

**Triggers**: When a PR is opened, reopened, or synchronized

**Actions**:
1. Creates a Neon branch named `pr-{number}`
2. Comments on the PR with the database URL
3. Outputs branch information for debugging

### PR Close Workflow

**File**: `.github/workflows/pr-close.yml`

**Triggers**: When a PR is closed (merged or not)

**Actions**:
1. Deletes the Neon database branch `pr-{number}`
2. Attempts to destroy the Fly.io preview app `skatespot-pr-{number}`
3. Comments on the PR confirming cleanup

## Using Preview Databases in CI/CD

To use the preview database in your CI/CD pipeline, reference the output from the create-branch action:

```yaml
- name: Create Neon Branch
  id: create-branch
  uses: neondatabase/create-branch-action@v5
  with:
    project_id: ${{ secrets.NEON_PROJECT_ID }}
    parent: main
    branch_name: pr-${{ github.event.pull_request.number }}
    api_key: ${{ secrets.NEON_API_KEY }}

- name: Run Tests
  env:
    DATABASE_URL: ${{ steps.create-branch.outputs.db_url }}
  run: |
    pytest
```

## Troubleshooting

### Branch Already Exists

If you see an error that a branch already exists:

1. Close and reopen the PR, or
2. Manually delete the branch from Neon dashboard, or
3. Use a different branch name in the workflow

### Connection Issues

Ensure your connection string includes `?sslmode=require` for Neon:

```
postgresql+asyncpg://user:password@host.neon.tech/dbname?sslmode=require
```

### Workflow Permissions

Make sure GitHub Actions has permission to:
- Create comments on PRs (should be default)
- Access repository secrets

## Cost Considerations

Neon offers:
- **Free tier**: 0.5 GB storage, 1 compute hour per month
- **Pro tier**: Pay-as-you-go for additional usage

Database branches are:
- **Free** on Pro tier (instant copy-on-write)
- Share the same storage until data diverges

## Resources

- [Neon Documentation](https://neon.tech/docs)
- [Neon GitHub Actions](https://github.com/marketplace/actions/neon-database-actions)
- [Neon Branching Guide](https://neon.tech/docs/guides/branching)
