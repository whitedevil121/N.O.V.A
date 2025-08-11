#!/usr/bin/env python3
# assistant.py
# Pipeline: record audio -> Vosk STT -> Ollama model -> pyttsx3 TTS

import subprocess
import time
from stt_vosk import transcribe
import pyttsx3
import threading

MODEL = "gemma:2b"
  # change if you used another model
TTS_BLOCKING = True

def ask_model(prompt: str, timeout=120) -> str:
    """Call Ollama run <MODEL> <prompt> and return stdout as string."""
    try:
        proc = subprocess.run(["ollama", "run", MODEL, prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        if proc.returncode != 0:
            return f"[MODEL-ERROR] {proc.stderr.strip()}"
        return proc.stdout.strip()
    except Exception as e:
        return f"[EXCEPTION] {e}"

def speak_text(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speak_async(text: str):
    t = threading.Thread(target=speak_text, args=(text,), daemon=True)
    t.start()
    return t

def run_once_record_and_respond(record_seconds=4):
    print("Recording...")
    user_text = transcribe(duration_sec=record_seconds)
    if not user_text or user_text.strip() == "":
        print("No speech detected.")
        return
    print("You said:", user_text)
    prompt = f"You are a helpful personal assistant. User said: {user_text}"
    print("Asking model...")
    resp = ask_model(prompt)
    print("Model response:", resp)
    # TTS
    print("Speaking response...")
    if TTS_BLOCKING:
        speak_text(resp)
    else:
        speak_async(resp)

if __name__ == "__main__":
    print("Assistant pipeline. Press Ctrl+C to exit.")
    try:
        while True:
            run_once_record_and_respond(record_seconds=4)
            time.sleep(0.3)  # brief pause
    except KeyboardInterrupt:
        print("\nExiting assistant.")
