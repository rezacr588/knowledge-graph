#!/bin/bash

# Hybrid RAG System - Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "🚀 Setting up Hybrid RAG System..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    echo "Please install Python 3.11 or higher"
    exit 1
fi
echo "✅ Python version: $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
echo "This may take 5-10 minutes..."
pip install -r requirements.txt -q
echo "✅ Python dependencies installed"
echo ""

# Download spaCy models
echo "📥 Downloading spaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm
echo "✅ spaCy models downloaded"
echo ""

# Download NLTK data
echo "📥 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"
echo "✅ NLTK data downloaded"
echo ""

# Create logs directory
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p evaluation/results
echo "✅ Directories created"
echo ""

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - Neo4j URI, username, password"
    echo "   - Qdrant URL and API key"
    echo "   - Gemini API key"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Verify installation
echo "🔍 Verifying installation..."
python -c "import fastapi, uvicorn, nltk, spacy; print('✅ Core imports successful')"
echo ""

echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo "   # Option A: Using Docker Compose (recommended)"
echo "   docker-compose up -d"
echo ""
echo "   # Option B: Run locally"
echo "   source venv/bin/activate"
echo "   uvicorn backend.main:app --reload"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "4. Open API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Read the documentation:"
echo "   - README.md: Quick start and usage"
echo "   - DESIGN_DOCUMENT.md: Architecture details"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
