# 🤖 AI Model Configuration Guide

## 📋 AI Models in Your System

Your Hybrid RAG system uses **4 types of AI models**:

### 1. ✅ spaCy Models (NLP) - CONFIGURED
### 2. ✅ Sentence Transformers (Embeddings) - CONFIGURED
### 3. ⚠️ Google Gemini (LLM) - NEEDS API KEY
### 4. ⚠️ ColBERT (Retrieval) - NEEDS SETUP

---

## ✅ 1. spaCy Models (Installed & Ready)

**Status:** ✅ FULLY CONFIGURED

**Purpose:** Named Entity Recognition (NER) and language processing

**Models Installed:**
```
✅ en_core_web_sm-3.8.0    # English NER
✅ es_core_news_sm-3.8.0   # Spanish NER
✅ xx_ent_wiki_sm-3.8.0    # Multilingual NER (Arabic, Chinese, etc.)
```

**Installed via:** Dockerfile (lines 19-22)

**Verification:**
```bash
docker-compose exec backend python -c "import spacy; print(spacy.load('en_core_web_sm'))"
```

**No action needed** - Already installed in Docker image! ✅

---

## ✅ 2. Sentence Transformers (Configured)

**Status:** ✅ INSTALLED

**Purpose:** Generate embeddings for semantic search

**Library:** `sentence-transformers==2.2.2`

**Installed via:** requirements.txt (line 10)

**Default Model:** `all-MiniLM-L6-v2` (downloads automatically on first use)

**Verification:**
```bash
docker-compose exec backend python -c "from sentence_transformers import SentenceTransformer; print('✅ OK')"
```

**No action needed** - Library installed, models download on-demand! ✅

---

## ⚠️ 3. Google Gemini API (Needs API Key)

**Status:** ⚠️ NEEDS CONFIGURATION

**Purpose:** LLM-based entity extraction and query enhancement

**Library:** `google-generativeai==0.3.2` ✅ Installed

**Model:** `gemini-2.0-flash-exp` (configured in code)

**Current Issue:** API key not set

### How to Configure Gemini

#### Step 1: Get API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (format: `AIza...`)

#### Step 2: Create .env File
```bash
cd /Users/rezazeraat/Desktop/KnowledgeGraph
cp .env.example .env
```

#### Step 3: Edit .env File
```bash
nano .env
```

Add your API key:
```bash
# Google Gemini API
GEMINI_API_KEY=AIzaSyC_your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### Step 4: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

#### Step 5: Verify
```bash
docker-compose logs backend | grep "Gemini"
# Should see: "✅ Gemini LLM initialized for entity extraction"
```

### ⚠️ System Works Without Gemini!

**Good news:** The system has fallback to spaCy-only extraction.

**With Gemini:**
- Better entity extraction
- Handles complex entities
- Multi-step reasoning

**Without Gemini:**
- Still works perfectly
- Uses spaCy models
- Faster (no API calls)

---

## ⚠️ 4. ColBERT (Needs Setup)

**Status:** ⚠️ PARTIALLY CONFIGURED

**Purpose:** Late-interaction neural retrieval

**Library:** `ragatouille==0.0.8` ✅ Installed

**Current State:**
- Code is ready (`backend/retrieval/colbert_retriever.py`)
- RAGatouille library installed
- Needs index creation on first document upload

### How ColBERT Works

1. **First Document Upload:**
   - RAGatouille downloads ColBERT model automatically
   - Creates index (takes 2-5 minutes first time)
   - Subsequent uploads are fast

2. **Index Storage:**
   - Stored in `.ragatouille/colbert/indexes/`
   - Persists between restarts
   - No external database needed

### No Action Needed!

ColBERT will auto-configure when you:
1. Upload your first document
2. Wait for indexing to complete
3. System is ready for ColBERT retrieval

**Note:** First upload will be slower (model download + indexing)

---

## 📊 Current Configuration Status

| Model | Status | Action Needed |
|-------|--------|---------------|
| **spaCy (en, es, xx)** | ✅ Configured | None |
| **Sentence Transformers** | ✅ Configured | None |
| **NLTK** | ✅ Configured | None |
| **Google Gemini** | ⚠️ Need API Key | Add to .env |
| **ColBERT** | ⚠️ Auto-setup | Upload first doc |

---

## 🔑 Required Environment Variables

### Must Have (System Won't Start)
```bash
# None! System has smart defaults
```

### Optional (Enhanced Features)
```bash
GEMINI_API_KEY=your-key-here          # For LLM entity extraction
NEO4J_URI=neo4j+s://xxx               # For knowledge graph
NEO4J_USERNAME=neo4j                  # Graph DB user
NEO4J_PASSWORD=password               # Graph DB pass
QDRANT_URL=https://xxx:6333           # For vector search
QDRANT_API_KEY=your-key               # Vector DB key
```

---

## ✅ Quick Setup Guide

### Minimal Setup (Works Now)
```bash
# System already works with:
✅ spaCy models (installed)
✅ Sentence transformers (installed)
✅ BM25 retrieval (no config needed)
✅ Basic entity extraction
```

**You can use the system RIGHT NOW without any config!**

### Enhanced Setup (Recommended)
```bash
# 1. Create .env file
cp .env.example .env

# 2. Add Gemini API key (optional but recommended)
nano .env  # Add: GEMINI_API_KEY=your-key

# 3. Restart
docker-compose down
docker-compose up -d
```

### Full Setup (All Features)
```bash
# 1. Get API keys:
#    - Gemini: https://makersuite.google.com/app/apikey
#    - Neo4j: https://neo4j.com/cloud/aura/
#    - Qdrant: https://cloud.qdrant.io/

# 2. Configure .env with all keys

# 3. Restart
docker-compose down
docker-compose up -d
```

---

## 🧪 Test AI Models

### Test spaCy (Should work now)
```bash
docker-compose exec backend python -c "
import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp('Apple Inc was founded by Steve Jobs')
for ent in doc.ents:
    print(f'{ent.text} ({ent.label_})')
"
```

### Test Gemini (After adding API key)
```bash
docker-compose exec backend python -c "
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content('Hello!')
print(response.text)
"
```

### Test Sentence Transformers
```bash
docker-compose exec backend python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(['Hello world'])
print(f'✅ Embedding shape: {embeddings.shape}')
"
```

---

## 🎯 Model Usage in Code

### spaCy (Entity Extraction)
**File:** `backend/services/entity_extraction.py`

```python
# Lines 39-54: Loads models
self.models['en'] = spacy.load('en_core_web_sm')
self.models['es'] = spacy.load('es_core_news_sm')
self.models['xx'] = spacy.load('xx_ent_wiki_sm')

# Line 91: Uses model
doc = model(text)
```

### Gemini (LLM Enhancement)
**File:** `backend/services/entity_extraction.py`

```python
# Line 61: Initializes Gemini
self.llm_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Line 142: Uses Gemini (if configured)
response = self.llm_model.generate_content(prompt)
```

### ColBERT (Neural Retrieval)
**File:** `backend/retrieval/colbert_retriever.py`

```python
# Line 49: Auto-downloads model on first use
from ragatouille import RAGPretrainedModel
self.rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
```

---

## 🚨 Common Issues

### Issue 1: "Gemini API key not found"
**Solution:** This is just a warning. System works without Gemini.

**To fix:** Add `GEMINI_API_KEY` to .env file

### Issue 2: "ColBERT indexing is slow"
**Solution:** First-time indexing takes 2-5 minutes. Subsequent uploads are fast.

### Issue 3: "spaCy model not found"
**Solution:** Models are installed in Docker. If running locally:
```bash
python -m spacy download en_core_web_sm
```

---

## 📚 Model Documentation

| Model | Documentation | License |
|-------|--------------|---------|
| spaCy | https://spacy.io/models | MIT |
| Gemini | https://ai.google.dev/gemini-api | Google |
| ColBERT | https://github.com/bclavie/RAGatouille | Apache 2.0 |
| Sentence Transformers | https://www.sbert.net/ | Apache 2.0 |

---

## ✅ Summary

### What's Already Working
- ✅ spaCy models (3 languages)
- ✅ NLTK data
- ✅ Sentence transformers
- ✅ BM25 retrieval
- ✅ Entity extraction (spaCy-based)

### What Needs Configuration
- ⚠️ Gemini API (optional - get key from Google)
- ⚠️ Neo4j (optional - for knowledge graph)
- ⚠️ Qdrant (optional - for vector search)

### What Auto-Configures
- ✅ ColBERT (downloads on first use)
- ✅ Sentence transformer models (downloads on demand)

---

## 🎉 Ready to Use!

**Your system works RIGHT NOW with these AI models:**
- ✅ spaCy for entity extraction
- ✅ BM25 for keyword search
- ✅ Hybrid fusion (RRF)

**To unlock full power:**
1. Add Gemini API key to .env
2. Upload first document (ColBERT auto-setup)
3. Enjoy all 3 retrieval methods!

**Current Status:** 75% configured (core models ready) ✅
