# Setup Next Steps

This PR has been created successfully! The workflow is in place and ready to use once you complete the setup.

## Current Status

✅ **Completed:**
- GitHub Actions workflow created (`.github/workflows/neon-branch.yml`)
- Documentation written (migration guide, workflow docs)
- Environment templates updated
- PR created: https://github.com/mmmbacon/skatespotredux/pull/2

⏳ **Pending (Requires User Action):**
- Install Neon GitHub Integration (creates `NEON_API_KEY` and `NEON_PROJECT_ID`)
- Optionally add `FLY_API_TOKEN` secret (if using Fly.io preview apps)

## Why is the Workflow Failing?

The workflow is currently failing with:
```
ERROR: Cannot run interactive auth in CI
ERROR: branch creation failed
```

**This is expected!** The workflow requires the `NEON_API_KEY` secret and `NEON_PROJECT_ID` variable, which are automatically created when you install the Neon GitHub Integration.

## Setup Instructions

### Step 1: Install Neon GitHub Integration

1. Go to [Neon Console](https://console.neon.tech)
2. Navigate to your project
3. Click on **Integrations** in the sidebar
4. Find the **GitHub** card
5. Click **Add** → **Install GitHub App**
6. Authorize the app for your GitHub account
7. Select the `mmmbacon/skatespotredux` repository
8. Click **Connect**

**What this does:**
- ✅ Creates `NEON_API_KEY` secret in your GitHub repository
- ✅ Creates `NEON_PROJECT_ID` variable in your GitHub repository
- ✅ Enables the workflow to create/delete database branches

### Step 2: Configure Workflow Permissions (If Not Already Set)

1. Go to your GitHub repository → Settings
2. Navigate to Actions → General → Workflow permissions
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### Step 3: Test the Workflow

Once the integration is installed:

1. Close and reopen PR #2 (or push a new commit)
2. The workflow will run successfully
3. You should see a comment on the PR with:
   - Preview database branch name
   - Information about the database

### Step 4 (Optional): Add Fly.io Token

If you want to destroy Fly.io preview apps on PR close:

1. Go to Settings → Secrets and variables → Actions
2. Click **New repository secret**
3. Name: `FLY_API_TOKEN`
4. Value: Your Fly.io API token
5. Click **Add secret**

## Verification

After installing the integration, you can verify it worked:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Check the **Secrets** tab: You should see `NEON_API_KEY`
3. Check the **Variables** tab: You should see `NEON_PROJECT_ID`

## What Happens Next?

Once configured, every PR will:

1. **On Open/Update:**
   - Automatically create a Neon database branch: `preview/pr-{number}-{branch-name}`
   - Post a comment with database information
   - Make connection strings available for deployments

2. **On Close:**
   - Automatically delete the Neon database branch
   - Optionally destroy the Fly.io preview app (if configured)
   - Post confirmation comments

## Need Help?

- See `docs/NEON_MIGRATION.md` for the complete migration guide
- See `.github/WORKFLOWS.md` for detailed workflow documentation
- Check [Neon's official docs](https://neon.com/docs/guides/neon-github-integration)

## Summary

This PR is **ready to merge** once you've installed the Neon GitHub Integration. The workflow will start working immediately after the integration is configured.
