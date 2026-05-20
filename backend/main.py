from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil, os, uuid
from rag_pipeline import get_rag_response, load_vectorstore
from ingest import ingest_document

app = FastAPI(title="Banking Support Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

    class Config:
        protected_namespaces = () # Prevent pydantic namespace collision

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: list[str] = []

    class Config:
        protected_namespaces = ()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Banking Chatbot API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = []
    
    history = sessions[session_id]
    
    try:
        # Extract plain string to bypass any hidden proxies
        user_msg = str(request.message)
        reply, sources = get_rag_response(user_msg, history)
    except Exception as e:
        print(f"CRITICAL BACKEND ERROR: {str(e)}") # Force log inside terminal
        raise HTTPException(status_code=500, detail=str(e))
    
    # Update history
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": str(reply)})
    sessions[session_id] = history[-20:]
    
    return {"reply": str(reply), "session_id": str(session_id), "sources": sources}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    upload_dir = "uploaded_docs"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        chunks_added = ingest_document(file_path)
        return {"message": f"Document ingested successfully. {chunks_added} chunks added.", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")