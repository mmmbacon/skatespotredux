# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and deployment. The CI pipeline automatically runs tests, builds Docker images, and performs code quality checks on every push and pull request.

## Workflows

### 1. Main CI Pipeline (`ci.yml`)

The main CI pipeline runs on:
- Push to `main`, `develop`, or any `feature/**` branch
- Pull requests to `main` or `develop`

#### Jobs:

1. **test-backend**: Runs backend unit tests with a real PostgreSQL/PostGIS database
2. **docker-build**: Builds Docker images for backend and frontend
3. **integration-tests**: Runs full integration tests using Docker Compose
4. **frontend-lint**: Checks frontend code formatting
5. **backend-lint**: Runs Python linting tools (Black, Flake8, isort)
6. **notify-status**: Reports overall CI status

### 2. Quick Tests (`quick-test.yml`)

A faster workflow that runs only when backend files are modified:
- Uses in-memory SQLite for quick unit tests
- Skips Docker builds and integration tests
- Ideal for rapid feedback during development

## Running Tests Locally

### Unit Tests Only
```bash
cd backend_py
python -m pytest tests/ -v
```

### With Docker Compose
```bash
./scripts/run-tests.sh --integration
```

## Environment Variables

The CI environment requires these variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `AWS_ACCESS_KEY_ID`: AWS credentials (for S3)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket for file uploads

## Docker Images

The pipeline builds two images:
1. **skatespot-backend**: Python FastAPI backend
2. **skatespot-frontend**: Vue.js frontend

Images are cached using GitHub Actions cache to speed up builds.

## Code Quality Tools

### Backend
- **Black**: Code formatter
- **Flake8**: Linter
- **isort**: Import sorter
- **mypy**: Type checker (optional)

### Frontend
- **Prettier**: Code formatter

## Troubleshooting

### Tests Failing in CI but Passing Locally

1. Check environment variables in the workflow
2. Ensure all test dependencies are in `requirements.txt`
3. Verify PostgreSQL version matches (15 with PostGIS 3.4)

### Docker Build Failures

1. Check Dockerfile syntax
2. Ensure all required files are not in `.dockerignore`
3. Verify build context paths in workflow

### Integration Test Failures

1. Check service health with `docker-compose ps`
2. Review container logs in the workflow output
3. Ensure `.env.local` has all required variables

## Best Practices

1. **Keep tests fast**: Use unit tests for most scenarios
2. **Mock external services**: Don't make real API calls in tests
3. **Use fixtures**: Share test data using pytest fixtures
4. **Clean up**: Always tear down test data and containers
5. **Parallel execution**: Tests should be able to run in parallel

## Adding New Tests

1. Create test files in `backend_py/tests/`
2. Follow the naming convention: `test_*.py`
3. Use async test functions with `pytest-asyncio`
4. Add new dependencies to `requirements.txt`

## Security

- Never commit real credentials
- Use GitHub Secrets for sensitive data
- Rotate test credentials regularly
- Keep dependencies updated