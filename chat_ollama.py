#!/usr/bin/env python3
# chat_ollama.py
# Simple wrapper to send prompts to Ollama and print responses.

import subprocess
import shlex
import sys

MODEL = "mistral"  # change if you pulled a different model

def ask(prompt: str) -> str:
    """
    Uses `ollama run <model> <prompt>` to get a response.
    Returns the response string (stdout).
    """
    # We use subprocess.run for simplicity. If you want streaming later, we'll adapt.
    try:
        # Build command: ollama run <model> --prompt "<prompt>"
        # Some ollama versions accept prompt as an argument; using shlex to be safe.
        cmd = ["ollama", "run", MODEL, prompt]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        if proc.returncode != 0:
            print("ERROR from ollama:", proc.stderr, file=sys.stderr)
            return proc.stderr
        return proc.stdout
    except Exception as e:
        return f"Exception calling ollama: {e}"

def main():
    print("Local AI chat via Ollama (type 'exit' to quit)\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            print("Bye.")
            break
        resp = ask(q)
        print("AI:", resp.strip())

if __name__ == "__main__":
    main()
