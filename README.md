# BankAssist AI — GenAI Banking Support Chatbot

A production-ready AI-powered banking support chatbot built with **RAG (Retrieval-Augmented Generation)**, FastAPI, ChromaDB, and React.

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
       │         │       └── Embeddings (OpenAI text-embedding-3-small)
       │         │
       │         └──► LLM (GPT-3.5-turbo)
       │                   └── Context-aware response generation
       │
       └──► Session Store (in-memory, per session)
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (get free credits at platform.openai.com)

---

### 1. Clone & Navigate

```bash
git clone https://github.com/YOUR_USERNAME/banking-chatbot.git
cd banking-chatbot
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
# Edit .env and add your OPENAI_API_KEY

# Ingest the sample banking data (FIRST TIME SETUP)
python ingest.py

# Start the backend server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

---

### 3. Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:8000

# Start frontend dev server
npm run dev
```

Frontend runs at: http://localhost:3000

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /chat | Send a message, get RAG response |
| POST | /upload | Upload PDF or TXT document |

### POST /chat
```json
Request:
{
  "message": "What is the interest rate for personal loans?",
  "session_id": "optional-session-id"
}

Response:
{
  "reply": "Personal loan interest rates typically range from 10.5% to 24% per annum...",
  "session_id": "uuid-here",
  "sources": ["sample_banking_faq.txt"]
}
```

### POST /upload
```
Content-Type: multipart/form-data
Body: file=<your_pdf_or_txt>
```

---

## RAG Pipeline Flow

1. **Document Ingestion** (`ingest.py`)
   - Load PDF/TXT files using LangChain loaders
   - Split into chunks (800 tokens, 150 overlap)
   - Generate embeddings via OpenAI `text-embedding-3-small`
   - Store in ChromaDB with source metadata

2. **Query Pipeline** (`rag_pipeline.py`)
   - Embed user query
   - Similarity search → top 4 relevant chunks
   - Build prompt with retrieved context + conversation history
   - Generate response via GPT-3.5-turbo

3. **Context Retention**
   - Last 6 messages (3 turns) included in every prompt
   - Session stored in-memory per `session_id`

---

## Cloud Deployment (Render — Free Tier)

### Backend on Render

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variable:
   - `OPENAI_API_KEY` = your key
5. Deploy!

### Frontend on Render (Static Site)

1. New → Static Site
2. Connect same repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = your backend Render URL
5. Deploy!

---

## Evaluation Coverage

| Area | Implementation |
|------|---------------|
| RAG Implementation (25%) | LangChain + ChromaDB + OpenAI embeddings |
| Vector DB Usage (20%) | ChromaDB with similarity search, top-k retrieval |
| Cloud Deployment (15%) | Render free tier (backend + frontend) |
| Code Quality (15%) | Modular structure, env vars, error handling |
| Chatbot Accuracy (15%) | Context-aware prompts, banking-specific data |
| API Design (5%) | FastAPI with /chat, /upload, /health |
| UI/UX (5%) | Dark mode React UI, typing indicator, suggestions |

---

## Bonus Features Implemented

- Session-based conversation memory (context retention)
- Source attribution in responses
- Dynamic document upload via API
- Quick suggestion chips for new users
- Error handling for invalid inputs
- API documentation at /docs (Swagger UI)

---

## Sample Data

The `backend/data/sample_banking_faq.txt` contains comprehensive FAQs covering:
- Personal loans & home loans
- Credit cards & CIBIL score
- Savings accounts & FDs
- UPI & netbanking
- EMI calculations & loan policies
- RBI Banking Ombudsman information

---

## Security Notes

- Never commit `.env` files
- API key is loaded from environment variables only
- CORS configured (restrict origins in production)