#!/bin/bash

# Stop local development environment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Hybrid RAG System (Local Development Mode)${NC}"
echo "=================================================="
echo ""

# Stop Docker services
echo -e "${YELLOW}Stopping Docker services...${NC}"
docker compose -f docker-compose.services.yml down

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
echo "To start again, run:"
echo -e "  ${YELLOW}./run-local.sh${NC}"
