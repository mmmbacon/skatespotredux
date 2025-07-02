#!/bin/bash

# Script to run backend tests

set -e  # Exit on error

echo "Running backend tests..."

# Set test environment variables
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export GOOGLE_CLIENT_ID="test_client_id"
export GOOGLE_CLIENT_SECRET="test_client_secret"
export JWT_SECRET="test_jwt_secret_key_for_testing"
export TESTING=true

# Change to backend directory
cd "$(dirname "$0")"

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    echo "Coverage report generated in htmlcov/index.html"
else
    echo "Tests failed!"
    exit 1
fi