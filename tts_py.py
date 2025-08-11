#!/usr/bin/env python3
# tts_py.py - quick TTS test using pyttsx3

import pyttsx3
import sys

def speak(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    txt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello Rudra. TTS is ready."
    print("Speaking:", txt)
    speak(txt)
