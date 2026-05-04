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

- Neon account and project. Sign up at [neon.tech](https://neon.tech).
- GitHub repository for your application

### 2. Install the Neon GitHub Integration

The Neon GitHub Integration **automatically** sets up the required secrets and variables:

1. In the Neon Console, navigate to the **Integrations** page in your Neon project
2. Locate the **GitHub** card and click **Add**
3. Click **Install GitHub App**
4. Select your GitHub account and authorize the app
5. Choose whether to install for **All repositories** or **Only select repositories**
6. Select the GitHub repository to connect to your Neon project
7. Click **Connect**

This will automatically create:
- `NEON_API_KEY` secret in your GitHub repository
- `NEON_PROJECT_ID` variable in your GitHub repository

### 3. Configure Optional Secrets

If you're using Fly.io for preview apps, add this secret manually:

- `FLY_API_TOKEN`: Your Fly.io API token (Settings → Secrets → Actions)

### 4. Add the GitHub Actions Workflow

Copy the workflow file from this repository (`.github/workflows/neon-branch.yml`) to your repository's `.github/workflows/` directory. The workflow is based on Neon's official template and includes:

- Database branch creation on PR open/reopen/synchronize
- Automatic database branch deletion on PR close
- Optional Fly.io app cleanup on PR close

### 5. Update Environment Variables

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

### 6. Migrate Existing Data (One-time)

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

## Workflow

### Unified Branch Management Workflow

**File**: `.github/workflows/neon-branch.yml`

This is a unified workflow based on Neon's official GitHub Integration template that handles both creation and deletion of preview database branches.

**Triggers**: Pull request events (opened, reopened, synchronized, closed)

**Jobs**:

#### 1. setup
Extracts the branch name for use in other jobs.

#### 2. create_neon_branch
**Runs on**: PR opened, reopened, or synchronized

**Actions**:
1. Creates a Neon branch named `preview/pr-{number}-{branch-name}`
2. The branch is an instant copy-on-write snapshot of the main database
3. Posts a comment on the PR with information about the preview database
4. Database connection string is available in workflow outputs (not logged for security)

**Outputs**:
- `db_url`: Direct database connection string
- `db_url_with_pooler`: Connection string with connection pooling (recommended)

#### 3. delete_neon_branch
**Runs on**: PR closed (merged or not)

**Actions**:
1. Deletes the Neon database branch `preview/pr-{number}-{branch-name}`
2. Posts confirmation comment on the PR

#### 4. cleanup_fly_app (Optional)
**Runs on**: PR closed

**Actions**:
1. Attempts to destroy the Fly.io preview app `skatespot-pr-{number}`
2. Uses `continue-on-error` to gracefully handle non-existent apps
3. Posts confirmation comment if successful

**Required Configuration**:
- `NEON_PROJECT_ID` variable (auto-created by Neon GitHub Integration)
- `NEON_API_KEY` secret (auto-created by Neon GitHub Integration)
- `FLY_API_TOKEN` secret (optional, only if using Fly.io preview apps)

## Using Preview Databases in CI/CD

To use the preview database in your CI/CD pipeline, add steps to the `create_neon_branch` job. The database connection string is available in the workflow outputs:

```yaml
create_neon_branch:
  name: Create Neon Branch
  needs: setup
  if: |
    github.event_name == 'pull_request' && (
    github.event.action == 'synchronize'
    || github.event.action == 'opened'
    || github.event.action == 'reopened')
  runs-on: ubuntu-latest
  steps:
    - name: Create Neon Branch
      id: create_neon_branch
      uses: neondatabase/create-branch-action@v5
      with:
        project_id: ${{ vars.NEON_PROJECT_ID }}
        branch_name: preview/pr-${{ github.event.number }}-${{ needs.setup.outputs.branch }}
        api_key: ${{ secrets.NEON_API_KEY }}

    # Add your migration/test steps here
    - name: Run Migrations
      env:
        DATABASE_URL: ${{ steps.create_neon_branch.outputs.db_url_with_pooler }}
      run: |
        cd backend_py
        alembic upgrade head

    - name: Run Tests
      env:
        DATABASE_URL: ${{ steps.create_neon_branch.outputs.db_url_with_pooler }}
      run: |
        pytest
```

**Important**: Connection string outputs are only available within the same job. Add all migration and testing steps to the `create_neon_branch` job.

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
