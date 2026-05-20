# 🏗️ BankAssist AI — Architecture Documentation

## Overview

BankAssist AI is a Retrieval-Augmented Generation (RAG) based banking support chatbot.
Instead of relying solely on LLM knowledge, it retrieves relevant information from
banking documents and generates grounded, context-aware responses.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              React Frontend (Vite)                  │   │
│   │                                                     │   │
│   │   ┌──────────────┐     ┌───────────────────────┐   │   │
│   │   │  ChatWindow  │     │     UploadPanel        │   │   │
│   │   │  - Messages  │     │  - PDF/TXT upload      │   │   │
│   │   │  - Typing UI │     │  - Ingestion trigger   │   │   │
│   │   │  - Suggestions│    └───────────────────────┘   │   │
│   │   └──────────────┘                                  │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP REST API
                       │ POST /chat
                       │ POST /upload
                       │ GET  /health
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                 Session Manager                      │  │
│   │         (In-memory, per session_id)                  │  │
│   │         Stores last 20 messages per session          │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                  RAG Pipeline                        │  │
│   │                                                      │  │
│   │   User Query                                         │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   Embed Query (OpenAI text-embedding-3-small)        │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   Similarity Search ──► ChromaDB Vector Store        │  │
│   │       │                      (Top 4 chunks)          │  │
│   │       ▼                                              │  │
│   │   Build Prompt                                       │  │
│   │   [System role + Context + History + Question]       │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   GPT-3.5-turbo ──► Final Response                   │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │              Document Ingestion Pipeline             │  │
│   │                                                      │  │
│   │   Upload PDF/TXT                                     │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   LangChain Loader (PyPDFLoader / TextLoader)        │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   Text Splitter                                      │  │
│   │   (chunk_size=800, overlap=150)                      │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   OpenAI Embeddings                                  │  │
│   │       │                                              │  │
│   │       ▼                                              │  │
│   │   ChromaDB (Persistent Storage)                      │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Components Breakdown

### 1. Frontend (React + Vite)

| Component | Purpose |
|-----------|---------|
| App.jsx | Root component, tab switching between Chat and Upload |
| ChatWindow.jsx | Message list, input box, suggestion chips |
| MessageBubble.jsx | Individual message rendering with source attribution |
| UploadPanel.jsx | File upload UI, calls POST /upload |
| index.css | Full dark-mode styling with CSS variables |

Tech: React 18, Vite 5, plain CSS (no UI library dependency)

---

### 2. Backend (FastAPI)

| File | Purpose |
|------|---------|
| main.py | API routes: /chat, /upload, /health. Session management. |
| rag_pipeline.py | Query embedding, vector search, prompt building, LLM call |
| ingest.py | Document loading, chunking, embedding, ChromaDB storage |

Tech: FastAPI, Uvicorn, LangChain, OpenAI SDK

---

### 3. Vector Database (ChromaDB)

- Runs locally / persisted to disk at `./chroma_db`
- Collection name: `banking_docs`
- Embedding model: `text-embedding-3-small` (OpenAI)
- Search type: Cosine similarity
- Top-K retrieval: 4 chunks per query
- Metadata stored: source filename, page number

---

### 4. LLM (GPT-3.5-turbo)

- Model: `gpt-3.5-turbo`
- Temperature: 0.3 (low = more factual, less creative)
- Prompt structure:
  - System role: Banking assistant persona
  - Retrieved context: Top 4 chunks from ChromaDB
  - Conversation history: Last 6 messages (3 turns)
  - User question

---

## RAG Flow — Step by Step

```
Step 1: User sends message → POST /chat
Step 2: session_id checked → history loaded
Step 3: Query embedded via OpenAI embeddings
Step 4: ChromaDB similarity search → top 4 relevant chunks retrieved
Step 5: Prompt assembled:
        [Banking assistant system prompt]
        [Retrieved document chunks as context]
        [Last 6 messages as conversation history]
        [Current user question]
Step 6: GPT-3.5-turbo generates response
Step 7: Response + sources returned to frontend
Step 8: History updated in session store
```

---

## Context Retention

Every API call includes the last 6 messages (3 user + 3 assistant turns) in the prompt.
This allows follow-up questions like:

```
User:      "What is a personal loan?"
Assistant: "A personal loan is an unsecured loan..."

User:      "What is the interest rate for it?"
           ↑ "it" resolved via conversation history in prompt
Assistant: "Personal loan interest rates range from 10.5% to 24%..."
```

---

## Deployment Architecture (Render Free Tier)

```
GitHub Repository
       │
       ├──► Render Web Service (Backend)
       │         - Python environment
       │         - FastAPI + Uvicorn
       │         - ChromaDB (ephemeral disk on free tier)
       │         - OPENAI_API_KEY via env var
       │         - URL: https://your-backend.onrender.com
       │
       └──► Render Static Site (Frontend)
                 - npm run build → dist/
                 - VITE_API_URL points to backend URL
                 - URL: https://your-frontend.onrender.com
```

Note: On Render free tier, disk is ephemeral. For production,
use a managed vector DB like Pinecone or Qdrant Cloud (both have free tiers).

---

## API Design

### POST /chat
```
Request:  { "message": "string", "session_id": "string (optional)" }
Response: { "reply": "string", "session_id": "string", "sources": ["string"] }
```

### POST /upload
```
Request:  multipart/form-data, field name: "file" (PDF or TXT)
Response: { "message": "string", "filename": "string" }
```

### GET /health
```
Response: { "status": "ok", "message": "Banking Chatbot API is running" }
```

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5 |
| Backend | FastAPI, Python 3.10+ |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | GPT-3.5-turbo |
| Deployment | Render (free tier) |
| Document Parsing | PyPDF, LangChain TextLoader |

---

## Future Improvements

1. Streaming responses (Server-Sent Events)
2. Redis for session persistence across restarts
3. Pinecone / Qdrant for production vector storage
4. Reranking with Cohere or cross-encoder models
5. Authentication (JWT-based)
6. CI/CD pipeline (GitHub Actions)
7. Prompt caching to reduce API costs
8. Support for DOCX files