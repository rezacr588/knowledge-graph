# Dependency Issue and Fix

## Current Problem

There's a known compatibility issue between:
- Python 3.12
- spaCy 3.8.x 
- Pydantic v1 (used internally by spaCy)

Error:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

## Solution Options

### Option 1: Use Python 3.11 (Recommended)

```bash
# Remove current venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv

# Activate and install
source venv/bin/activate
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm  
python -m spacy download xx_ent_wiki_sm

# Start backend
python -m uvicorn backend.main:app --reload --port 8000
```

### Option 2: Use System Python (if 3.11)

```bash
# Check your system Python version
/usr/bin/python3 --version

# If it's 3.11, use it
rm -rf venv
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option 3: Install Python 3.11 via Homebrew

```bash
# Install Python 3.11
brew install python@3.11

# Create venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Fix for Current Session

If you need to run immediately without reinstalling Python:

**Temporarily disable spaCy-dependent features:**

Edit `backend/services/entity_extraction.py` and comment out spaCy import:

```python
# import spacy  # Temporarily disabled
```

This will disable entity extraction but allow the system to run for basic document search.

## Long-term Solution

The spaCy team is working on full Pydantic v2 and Python 3.12 support. Once spaCy 3.9+ is released, this issue should be resolved.

##Current Setup Status

✅ Redis: Running in Docker  
❌ Backend: Python 3.12 incompatibility  
⏳ Frontend: Waiting for backend  

## Next Steps

1. Choose one of the solutions above
2. Recreate your virtual environment  
3. Start the backend successfully
4. Start the frontend

Run:
```bash
# After fixing Python version:
./start_dev.sh
```
