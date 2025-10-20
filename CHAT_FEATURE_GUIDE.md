# Chat Feature Implementation Guide

## Overview
A chat interface has been successfully added to the Hybrid RAG System, enabling conversational Q&A with uploaded documents using Google Gemini.

## What Was Added

### Backend Changes

1. **New Chat Service** (`backend/services/chat_service.py`)
   - Uses Google Gemini API (gemini-2.0-flash-exp)
   - Generates contextual responses based on retrieved document chunks
   - Supports conversation history for multi-turn conversations
   - Includes language support (EN, ES, AR)

2. **New API Endpoint** (`/api/chat`)
   - POST endpoint at `/api/chat`
   - Integrates with existing hybrid retrieval system (BM25 + ColBERT + Graph)
   - Returns AI-generated responses with source context
   - Includes timing metrics for retrieval and generation

3. **Updated Schemas** (`backend/models/schemas.py`)
   - Added `ChatMessage` model for conversation messages
   - Added `ChatRequest` model for chat API requests
   - Added `ChatResponse` model for chat API responses

### Frontend Changes

1. **New Chat Component** (`frontend/src/components/ChatInterface.jsx`)
   - Modern chat UI with message bubbles
   - Shows user and assistant messages
   - Expandable context sources for each response
   - Loading indicators during processing
   - Timing information display
   - Auto-scroll to latest message

2. **Updated App Component** (`frontend/src/App.jsx`)
   - Added new "Chat" tab in navigation
   - Integrated ChatInterface component
   - Added MessageSquare icon from lucide-react

## Configuration Requirements

### Environment Variables
Make sure your `.env` file has the following configured:

```bash
# Required for chat functionality
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp

# Other required configs
NEO4J_URI=your-neo4j-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

### Getting a Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

## How to Test

### 1. Start the Backend
```bash
cd /Users/rezazeraat/Desktop/KnowledgeGraph
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd /Users/rezazeraat/Desktop/KnowledgeGraph/frontend
npm run dev
```

### 3. Upload Documents
1. Open the application in your browser (usually http://localhost:5173)
2. Click on the "Upload" tab
3. Upload a document (PDF, TXT, etc.)
4. Wait for the document to be processed

### 4. Test the Chat
1. Click on the "Chat" tab
2. Type a question about your uploaded document
3. Press Enter or click Send
4. The system will:
   - Retrieve relevant context from your documents
   - Generate a response using Gemini
   - Show sources used for the answer
5. Continue the conversation with follow-up questions

## Chat Features

### Context-Aware Responses
- The chat uses your uploaded documents as context
- Retrieves top 5 most relevant chunks using hybrid search
- Gemini generates answers based only on the retrieved context

### Conversation History
- Maintains last 10 messages for context
- Allows for natural follow-up questions
- Each message is timestamped

### Source Citations
- Click "Sources" to see which document chunks were used
- Shows relevance scores for each chunk
- Displays retrieval and generation timing

### Multi-Language Support
Currently configured for:
- English (en)
- Spanish (es)
- Arabic (ar)

## API Endpoint Details

### POST /api/chat

**Request Body:**
```json
{
  "message": "What is the main topic of the document?",
  "conversation_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ],
  "top_k": 5,
  "language": "en",
  "retrieval_methods": ["bm25", "colbert", "graph"]
}
```

**Response:**
```json
{
  "message": "The main topic of the document is...",
  "retrieved_chunks": [
    {
      "doc_id": "abc123",
      "chunk_id": "abc123_chunk_0",
      "text": "Relevant text from document...",
      "rrf_score": 0.95,
      "rank": 1,
      "language": "en",
      "method_scores": {"bm25": 0.8, "colbert": 0.9, "graph": 0.7},
      "method_ranks": {"bm25": 2, "colbert": 1, "graph": 3}
    }
  ],
  "retrieval_time_ms": 150.5,
  "generation_time_ms": 1200.3,
  "total_time_ms": 1350.8
}
```

## Troubleshooting

### Chat service not available
**Error:** "Chat service not available. Please configure GEMINI_API_KEY."

**Solution:** 
- Check that `GEMINI_API_KEY` is set in your `.env` file
- Restart the backend server after adding the key

### No context found
**Symptoms:** Responses say "I don't have enough information"

**Solution:**
- Make sure you've uploaded documents first
- Check that ingestion completed successfully
- Verify documents were processed (check logs)

### Slow responses
**Symptoms:** Long wait times for responses

**Explanation:**
- Normal response time is 1-3 seconds
- First request may be slower (model initialization)
- Complex questions require more retrieval time

## Technical Architecture

### Flow Diagram
```
User Question
    ↓
Chat API Endpoint
    ↓
Hybrid Retrieval (BM25 + ColBERT + Graph)
    ↓
RRF Fusion (top 5 chunks)
    ↓
Chat Service (Gemini)
    ↓
Context-aware Response
    ↓
User Interface
```

### Key Components
1. **ChatService**: Handles Gemini API integration
2. **Hybrid Retrieval**: Finds relevant context
3. **RRF Fusion**: Combines results from multiple retrievers
4. **ChatInterface**: React component for UI

## Future Enhancements

Potential improvements:
- [ ] Streaming responses (real-time token generation)
- [ ] Conversation export/save functionality
- [ ] Custom system prompts
- [ ] Response regeneration
- [ ] Citation highlighting in source text
- [ ] Multi-document awareness in responses
- [ ] Feedback buttons (helpful/not helpful)

## Dependencies

### Backend
- `google-generativeai`: Gemini API client
- Already in requirements.txt

### Frontend
- `axios`: HTTP client
- `lucide-react`: Icons
- Already in package.json

## Summary

The chat feature seamlessly integrates with the existing RAG system, providing a natural language interface for querying documents. It combines the power of hybrid retrieval with Gemini's language generation capabilities to deliver accurate, context-aware responses.
