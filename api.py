#!/usr/bin/env python3
# api.py - FastAPI server exposing /chat and /stt endpoints

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Load environment variables
load_dotenv()

# Default model — can be overridden with MODEL env var
MODEL = os.getenv("MODEL", "gemma:2b")

app = FastAPI(title="personal-ai")

# Allow all origins for testing — change for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"status": "running", "model": MODEL}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(q: Query):
    if not q.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    try:
        prompt = f"You are a helpful assistant. User said: {q.text}"
        proc = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # Lower timeout for faster failures
        )
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Ollama error: {proc.stderr.strip()}")
        return {"response": proc.stdout.strip()}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Model timed out")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def stt_record():
    try:
        from stt_vosk import transcribe
        text = transcribe(duration_sec=4)
        return {"text": text}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )

