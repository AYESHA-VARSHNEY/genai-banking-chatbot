# BankAssist AI — GenAI Banking Support Chatbot

An AI-powered banking support chatbot built with RAG (Retrieval-Augmented Generation), FastAPI, ChromaDB, and React. It answers customer queries about loans, credit cards, savings accounts, and general banking topics by retrieving information from uploaded documents.

---

## Architecture

```
User Browser (React)
       │
       ▼
  Frontend (Vite + React)
       │  POST /chat, POST /upload, GET /health
       ▼
  Backend (FastAPI)
       │
       ├──► RAG Pipeline (LangChain)
       │         │
       │         ├──► ChromaDB (Vector Store)
       │         │       └── Embeddings (HuggingFace - free, no key needed)
       │         │
       │         └──► LLM (Groq - llama-3.3-70b-versatile)
       │                   └── Context-aware response generation
       │
       └──► Session Store (in-memory, per session_id)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5 |
| Backend | FastAPI, Python 3.10+ |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | HuggingFace sentence-transformers (free) |
| LLM | Groq (llama-3.3-70b-versatile) — free tier |
| Deployment | Render (free tier) |
| Document Parsing | PyPDF, LangChain TextLoader |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key — free at [console.groq.com](https://console.groq.com)

---

### 1. Clone the Repository

```bash
git clone https://github.com/AYESHA-VARSHNEY/genai-banking-chatbot.git
cd genai-banking-chatbot
```

---

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# Ingest sample banking data into ChromaDB (run once)
python ingest.py

# Start the backend server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
Swagger API docs at: http://localhost:8000/docs

---

### 3. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

Frontend runs at: http://localhost:3000

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /chat | Send message, get RAG response |
| POST | /upload | Upload PDF or TXT document |

### POST /chat — Example

```json
Request:
{
  "message": "What is the interest rate for personal loans?",
  "session_id": "optional-uuid"
}

Response:
{
  "reply": "Personal loan interest rates typically range from 10.5% to 24% per annum...",
  "session_id": "uuid-here",
  "sources": ["sample_banking_FAQ.txt"]
}
```

### POST /upload
```
Content-Type: multipart/form-data
Body: file = <PDF or TXT file>
```

---

## RAG Pipeline — How It Works

### 1. Document Ingestion (`ingest.py`)
- Load PDF/TXT files using LangChain document loaders
- Split into chunks (800 tokens, 150 overlap) using RecursiveCharacterTextSplitter
- Generate embeddings using HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- Store embeddings in ChromaDB with source metadata

### 2. Query Pipeline (`rag_pipeline.py`)
- User message is embedded using the same HuggingFace model
- Similarity search in ChromaDB returns top 4 relevant chunks
- A structured prompt is built: system role + context + conversation history + question
- Groq LLM generates a context-aware response

### 3. Context Retention
- Last 6 messages (3 turns) are included in every request
- Sessions stored in-memory per `session_id`

Example of context retention:
```
User:      "What is a personal loan?"
Assistant: "A personal loan is an unsecured loan..."
User:      "What is the interest rate for it?"   ← "it" resolved from history
Assistant: "Personal loan rates range from 10.5% to 24%..."
```

---

## Cloud Deployment (Render — Free Tier)

### Backend

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect GitHub repo
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python ingest.py && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   - `LLM_PROVIDER` = `groq`
   - `EMBEDDING_PROVIDER` = `huggingface`
   - `GROQ_API_KEY` = your key
5. Deploy!

### Frontend

1. New → Static Site → Connect same repo
2. Settings:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
3. Environment Variable:
   - `VITE_API_URL` = your backend Render URL
4. Deploy!

---

## Evaluation Coverage

| Area | Weight | Implementation |
|------|--------|---------------|
| RAG Implementation | 25% | LangChain + ChromaDB + HuggingFace embeddings |
| Vector DB Usage | 20% | ChromaDB similarity search, top-4 retrieval |
| Cloud Deployment | 15% | Render free tier (backend + frontend) |
| Code Quality | 15% | Modular structure, env vars, error handling |
| Chatbot Accuracy | 15% | Context-aware prompts, banking-specific FAQ data |
| API Design | 5% | FastAPI — /chat, /upload, /health + Swagger docs |
| UI/UX | 5% | Dark mode React UI, typing indicator, quick suggestions |

---

## Bonus Features

- Session-based conversation memory with context retention
- Source file attribution shown in every response
- Dynamic document upload and real-time ingestion via API
- Quick suggestion chips on first load
- Graceful error handling for invalid inputs
- Auto Swagger documentation at `/docs`
- Support for multiple LLM providers (Groq, Gemini, OpenAI, Anthropic, Ollama)

---

## Supported LLM Providers

The chatbot supports multiple providers — just change `.env`:

| Provider | Free? | Key Source |
|----------|-------|-----------|
| Groq (default) | Yes | console.groq.com |
| Gemini | Free tier | aistudio.google.com |
| OpenAI | Paid | platform.openai.com |
| Anthropic | Paid | console.anthropic.com |
| Ollama | Yes (local) | ollama.com |

---

## Sample Data

`backend/data/sample_banking_FAQ.txt` covers:
- Personal loans and home loans
- Credit cards and CIBIL scores
- Savings accounts and fixed deposits
- UPI and netbanking
- EMI calculations and loan policies
- RBI Banking Ombudsman process

---

## Security

- `.env` file is gitignored — never committed
- All API keys loaded from environment variables
- No hardcoded credentials anywhere in the codebase