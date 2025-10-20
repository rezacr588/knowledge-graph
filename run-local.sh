#!/bin/bash

# Run backend locally in venv
# Services (Redis) run in Docker

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Hybrid RAG Backend (Local Development Mode)${NC}"
echo "=================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run ./setup-local.sh first${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Run ./setup-local.sh first${NC}"
    exit 1
fi

# Check if Docker services are running
if ! docker compose -f docker-compose.services.yml ps | grep -q "redis"; then
    echo -e "${YELLOW}⚠️  Docker services not running. Starting them...${NC}"
    docker compose -f docker-compose.services.yml up -d
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 3
fi

# Check Redis connection
echo -e "${YELLOW}Checking Redis connection...${NC}"
if ! docker exec hybrid-rag-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not responding!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Redis is ready${NC}"

echo ""
echo -e "${GREEN}Starting FastAPI backend...${NC}"
echo ""

# Activate venv and run
source venv/bin/activate

# Set environment variables for local development
export REDIS_URL=redis://localhost:6379/0

# Run uvicorn with reload for development
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
