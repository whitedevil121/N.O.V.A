#!/usr/bin/env python3
# stt_vosk.py
# Record ~3-5 seconds from default microphone and transcribe using Vosk.

import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-en-us-0.15"  # update if different
SAMPLE_RATE = 16000
CHUNK = 4000  # bytes-ish; smaller chunk ok

q = queue.Queue()

def callback(indata, frames, time, status):
    """This callback runs in another thread — put raw data into queue."""
    if status:
        print("Audio status:", status, file=sys.stderr)
    q.put(bytes(indata))

def transcribe(duration_sec=4):
    """Record `duration_sec` seconds and transcribe the audio."""
    try:
        model = Model(MODEL_PATH)
    except Exception as e:
        raise SystemExit(f"Failed to load Vosk model at {MODEL_PATH}: {e}")

    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    print(f"Recording for {duration_sec} seconds... speak clearly.")
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK, dtype='int16',
                           channels=1, callback=callback):
        # Collect audio and feed to Vosk
        import time
        start = time.time()
        while True:
            if not q.empty():
                data = q.get()
                if rec.AcceptWaveform(data):
                    pass  # partial/full result available but we'll read final below
            if time.time() - start > duration_sec:
                break

    # After recording, get final result. Note: there may be partials lost if small audio
    final = rec.FinalResult()
    try:
        res = json.loads(final)
        text = res.get("text", "")
    except Exception:
        text = final
    print("Transcribed:", text)
    return text

if __name__ == "__main__":
    transcribe()
