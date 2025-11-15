import threading
import pyttsx3
import os
import time

from core.config import is_tts_enabled

# Global variables for TTS control
tts_engine = None
tts_lock = threading.Lock()

def init_engine():
    """Initialize pyttsx3 engine with better settings"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0-1)
        
        # Try to use best available voice
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        print("[TTS] Engine initialized successfully")
        return engine
    except Exception as e:
        print(f"[TTS] Error initializing engine: {e}")
        return None

# Initialize on import
tts_engine = init_engine()

def speak(text, lang="en"):
    """Speak text immediately in a background thread (non-blocking)"""
    global tts_engine
    
    # Check if TTS is enabled
    if not is_tts_enabled():
        return
    
    # Validate text
    if not text or not isinstance(text, str):
        return
    
    text = str(text).strip()
    if not text:
        return
    
    # Ensure engine exists
    if tts_engine is None:
        tts_engine = init_engine()
        if tts_engine is None:
            return
    
    def speak_async():
        """Run TTS in background thread to avoid blocking"""
        try:
            with tts_lock:  # Thread-safe access to engine
                if is_tts_enabled():
                    tts_engine.say(text)
                    tts_engine.runAndWait()
                    print(f"[TTS] Speaking: {text[:50]}...")
        except Exception as e:
            print(f"[TTS] Error: {e}")
    
    # Run in daemon thread so it doesn't block GUI
    thread = threading.Thread(target=speak_async, daemon=True)
    thread.start()

def stop_speaking():
    """Stop current speech and clear queue"""
    global tts_engine
    try:
        if tts_engine:
            with tts_lock:
                tts_engine.stop()
    except Exception as e:
        print(f"[TTS] Error stopping: {e}")
