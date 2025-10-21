#!/bin/bash

# Setup script for Python virtual environment

set -e

echo "🚀 Setting up Python virtual environment for Hybrid RAG System..."

# Check for Python 3.11 (required for spaCy compatibility)
PYTHON_CMD=""

if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✓ Found Python 3.11 (recommended)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✓ Found Python $PYTHON_VERSION"
    
    if [ "$PYTHON_VERSION" == "3.12" ]; then
        echo "⚠️  Python 3.12 detected. This may cause spaCy compatibility issues."
        echo "⚠️  Recommend using Python 3.11. Install with: brew install python@3.11"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 is not installed. Please install Python 3.11."
    echo "   Install with: brew install python@3.11"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy models
echo "📥 Downloading spaCy language models..."
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download xx_ent_wiki_sm

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "   source venv/bin/activate"
echo ""
echo "To start the backend, run:"
echo "   python -m uvicorn backend.main:app --reload --port 8000"
