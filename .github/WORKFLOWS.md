# GitHub Actions Workflows

This directory contains automated workflows for the SkateSpot Redux project.

## Workflows

### 1. PR Open - Create Neon Branch

**File**: `workflows/pr-open.yml`

**Trigger**: Pull request opened, reopened, or synchronized

**Purpose**: Automatically creates a preview database for each pull request using Neon's database branching feature.

**What it does**:
1. Creates a new Neon database branch named `pr-{number}`
2. The branch is an instant copy of the main production database
3. Posts a comment on the PR with the connection string
4. Developers can use this preview database to test changes without affecting production

**Required Secrets**:
- `NEON_PROJECT_ID`: Your Neon project ID
- `NEON_API_KEY`: Neon API key with branch management permissions

**Example Comment**:
```
## 🚀 Neon Preview Branch Created

Your preview database is ready!

**Branch Name:** `pr-123`
**Connection String:** `postgresql://user:pass@host.neon.tech/dbname`

> ⚠️ This database branch will be automatically deleted when the PR is closed.
```

### 2. PR Close - Cleanup Resources

**File**: `workflows/pr-close.yml`

**Trigger**: Pull request closed (merged or not)

**Purpose**: Cleans up all resources associated with a PR to avoid unnecessary costs.

**What it does**:
1. **Neon Cleanup**: Deletes the database branch `pr-{number}`
2. **Fly.io Cleanup**: Destroys the preview app `skatespot-pr-{number}` (if exists)
3. Posts confirmation comments on the PR

**Required Secrets**:
- `NEON_PROJECT_ID`: Your Neon project ID
- `NEON_API_KEY`: Neon API key with branch management permissions
- `FLY_API_TOKEN`: Fly.io API token (optional, only if using Fly.io preview apps)

**Jobs**:

#### cleanup-neon-branch
Always runs. Deletes the Neon database branch associated with the PR.

#### cleanup-fly-app
Conditionally runs (skipped for main/master branches). Attempts to destroy the Fly.io preview app. Uses `continue-on-error` to gracefully handle non-existent apps.

## Setup Instructions

### 1. Add Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

```
NEON_PROJECT_ID=your-project-id-here
NEON_API_KEY=your-api-key-here
FLY_API_TOKEN=your-fly-token-here  # Optional
```

### 2. Enable GitHub Actions

Ensure GitHub Actions is enabled for your repository:
- Settings → Actions → General
- Allow all actions and reusable workflows

### 3. Configure Workflow Permissions

Ensure workflows have permission to comment on PRs:
- Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

## Workflow Behavior

### On PR Open/Update
```mermaid
graph LR
    A[PR Opened] --> B[Create Neon Branch]
    B --> C[Comment with DB URL]
    C --> D[Ready for Testing]
```

### On PR Close
```mermaid
graph LR
    A[PR Closed] --> B[Delete Neon Branch]
    A --> C[Destroy Fly App]
    B --> D[Comment Confirmation]
    C --> D
```

## Best Practices

### Database Migrations

When using preview databases, consider:

1. **Run migrations automatically** in your preview deployment pipeline
2. **Test migrations** against preview branches before merging
3. **Keep migrations idempotent** so they can run multiple times safely

### Cost Management

- Preview branches are **free** on Neon Pro tier
- Branches share storage via copy-on-write
- Clean up happens automatically on PR close
- Consider setting branch retention policies in Neon

### Testing with Preview Databases

Example workflow step to run tests with preview DB:

```yaml
- name: Run Integration Tests
  env:
    DATABASE_URL: ${{ steps.create-branch.outputs.db_url }}
  run: |
    cd backend_py
    pytest tests/
```

## Troubleshooting

### Workflow Fails with "Branch already exists"

**Cause**: The branch wasn't cleaned up properly from a previous PR with the same number.

**Solution**: Manually delete the branch from Neon dashboard, or close/reopen the PR.

### Workflow Fails with "Unauthorized"

**Cause**: Invalid or expired API keys.

**Solution**: 
1. Verify secrets are set correctly
2. Regenerate API keys in Neon dashboard
3. Update GitHub secrets

### Comment Not Posted

**Cause**: Insufficient workflow permissions.

**Solution**: 
1. Check Settings → Actions → General → Workflow permissions
2. Ensure "Read and write permissions" is selected

### Fly App Not Destroyed

**Cause**: App name doesn't match expected pattern or already deleted.

**Solution**: This is expected behavior. The workflow uses `continue-on-error: true` to handle missing apps gracefully.

## Monitoring

To view workflow runs:
1. Go to the **Actions** tab in your repository
2. Select a workflow from the left sidebar
3. Click on a specific run to see logs and details

## Future Enhancements

Potential improvements to consider:

- [ ] Add workflow to run migrations on preview databases
- [ ] Add workflow to seed preview databases with test data
- [ ] Add deployment workflow for production
- [ ] Add workflow to run E2E tests against preview environments
- [ ] Add Slack/Discord notifications for workflow status

## Resources

- [Neon GitHub Actions](https://github.com/marketplace/actions/neon-database-actions)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Fly.io GitHub Actions](https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/)
