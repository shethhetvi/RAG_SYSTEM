import os
import time
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .services.retrieval import init_retrieval
from .services.orchestrator import process_rag_query
from .services.stt import transcribe_audio

# Load environment variables
load_dotenv()

app = FastAPI(title="Bioluminescent RAG System")

# Initialize retrieval on startup
@app.on_event("startup")
async def startup_event():
    init_retrieval()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": "online"}

@app.post("/query/text")
async def handle_text_query(query: str = Form(...)):
    start_time = time.time()
    timings = {}
    
    answer, context = process_rag_query(query, timings)
    
    total_time = time.time() - start_time
    timings["total"] = total_time
    
    return {
        "query": query,
        "answer": answer,
        "timings": timings
    }

@app.post("/query/audio")
async def handle_audio_query(audio: UploadFile = File(...)):
    start_time = time.time()
    timings = {}
    
    # 1. STT
    stt_start = time.time()
    audio_bytes = await audio.read()
    transcribed_text = transcribe_audio(audio_bytes)
    timings["stt"] = time.time() - stt_start
    
    # 2. RAG Orchestration
    answer, context = process_rag_query(transcribed_text, timings)
    
    total_time = time.time() - start_time
    timings["total"] = total_time
    
    return {
        "query": transcribed_text,
        "answer": answer,
        "timings": timings
    }

