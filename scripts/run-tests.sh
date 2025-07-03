#!/bin/bash
set -e

echo "🚀 Starting test environment..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "infra/docker-compose.yml" ]; then
    echo -e "${RED}Error: Must run this script from the project root directory${NC}"
    exit 1
fi

# Create env file if it doesn't exist
if [ ! -f "infra/env/.env.local" ]; then
    echo -e "${YELLOW}Creating test environment file...${NC}"
    mkdir -p infra/env
    cat > infra/env/.env.local << EOF
DATABASE_URL=postgresql://skateuser:skatepassword@postgres:5432/skatespot
JWT_SECRET_KEY=local-test-secret-key
GOOGLE_CLIENT_ID=test-client-id
GOOGLE_CLIENT_SECRET=test-client-secret
FRONTEND_URL=http://localhost:5173
AWS_ACCESS_KEY_ID=test-key
AWS_SECRET_ACCESS_KEY=test-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=test-bucket
EOF
fi

# Parse command line arguments
RUN_INTEGRATION=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--integration]"
            exit 1
            ;;
    esac
done

# Run unit tests without Docker
echo -e "${YELLOW}Running backend unit tests...${NC}"
cd backend_py
python -m pytest tests/ -v --tb=short || { echo -e "${RED}Unit tests failed${NC}"; exit 1; }
cd ..

# Run integration tests with Docker if requested
if [ "$RUN_INTEGRATION" = true ]; then
    echo -e "${YELLOW}Starting Docker containers for integration tests...${NC}"
    cd infra
    
    # Stop any existing containers
    docker-compose down -v
    
    # Start containers
    docker-compose up -d
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U skateuser -d skatespot &>/dev/null; then
            echo -e "${GREEN}PostgreSQL is ready!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    
    # Check backend health
    sleep 5
    if ! docker-compose ps backend | grep -q "Up"; then
        echo -e "${RED}Backend failed to start. Showing logs:${NC}"
        docker-compose logs backend
        docker-compose down -v
        exit 1
    fi
    
    # Run tests in container
    echo -e "${YELLOW}Running integration tests in container...${NC}"
    docker-compose exec -T backend pip install pytest httpx pytest-asyncio aiosqlite
    docker-compose exec -T backend python -m pytest /app/tests/ -v || { 
        echo -e "${RED}Integration tests failed${NC}"
        docker-compose logs backend
        docker-compose down -v
        exit 1
    }
    
    # Clean up
    echo -e "${YELLOW}Cleaning up containers...${NC}"
    docker-compose down -v
    cd ..
fi

echo -e "${GREEN}✅ All tests passed!${NC}"