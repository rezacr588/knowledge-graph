#!/bin/bash

# Setup script for local development
# Backend runs in venv, services run in Docker

set -e

echo "🚀 Setting up Hybrid RAG System for Local Development"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please edit it with your credentials.${NC}"
    echo ""
fi

# Step 1: Start Docker services
echo -e "${GREEN}Step 1: Starting Docker services (Redis)...${NC}"
docker compose -f docker-compose.services.yml up -d

# Wait for Redis to be ready
echo -e "${YELLOW}Waiting for Redis to be ready...${NC}"
sleep 3
docker compose -f docker-compose.services.yml ps

echo ""
echo -e "${GREEN}✅ Docker services started!${NC}"
echo ""

# Step 2: Setup Python virtual environment
echo -e "${GREEN}Step 2: Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

echo ""
echo -e "${GREEN}Step 3: Activating virtual environment and installing dependencies...${NC}"

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

echo ""
echo -e "${GREEN}Step 4: Downloading spaCy models...${NC}"

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "=================================================="
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   - NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD"
echo "   - QDRANT_URL, QDRANT_API_KEY"
echo "   - GEMINI_API_KEY"
echo ""
echo "2. Start the backend:"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "3. Or use the run script:"
echo -e "   ${YELLOW}./run-local.sh${NC}"
echo ""
echo "4. Access the API:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "5. Stop Docker services when done:"
echo -e "   ${YELLOW}docker compose -f docker-compose.services.yml down${NC}"
echo ""
echo "=================================================="
