# wake_word.py - Voice wake word detection for JARVIS
import speech_recognition as sr
import threading
import time

wake_word = "jarvis"
listening = False
wake_detected_callback = None

def set_wake_callback(callback):
    """Set callback function to execute when wake word is detected"""
    global wake_detected_callback
    wake_detected_callback = callback

def listen_for_wake_word():
    """Listen for wake word 'Hey Jarvis' or 'Jarvis'"""
    global listening
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000  # Sensitivity level (lower = more sensitive)
    recognizer.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            print("[WAKE] Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[WAKE] Microphone calibrated. Listening for wake word...")
            
            while listening:
                try:
                    print("[WAKE] Listening for: 'Hey Jarvis' or 'Jarvis'...")
                    # Set timeout to continuously listen
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    print("[WAKE] Audio captured, processing...")
                    
                    try:
                        # Use Google Speech Recognition with language specified
                        text = recognizer.recognize_google(audio, language='en-US').lower()
                        print(f"[WAKE] Heard: '{text}'")
                        
                        # Check for wake words with more flexible matching
                        if "jarvis" in text or "hey jarvis" in text or "jarvis hey" in text:
                            print("[WAKE] ✓ Wake word detected! Opening JARVIS...")
                            if wake_detected_callback:
                                wake_detected_callback()
                            time.sleep(2)  # Prevent multiple triggers
                        else:
                            print(f"[WAKE] No wake word detected in: '{text}'")
                            
                    except sr.UnknownValueError:
                        print("[WAKE] Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        print(f"[WAKE] API Error: {e}")
                        time.sleep(2)
                        
                except sr.RequestError:
                    print("[WAKE] Network error, retrying...")
                    time.sleep(2)
                    continue
                except Exception as e:
                    print(f"[WAKE] Error: {e}")
                    time.sleep(1)
                    
    except Exception as e:
        print(f"[WAKE] Microphone error: {e}")

def start_wake_listener(callback=None):
    """Start listening for wake word in background"""
    global listening, wake_detected_callback
    
    if callback:
        wake_detected_callback = callback
    
    listening = True
    thread = threading.Thread(target=listen_for_wake_word, daemon=True)
    thread.start()
    print("[WAKE] Wake word listener started")

def stop_wake_listener():
    """Stop listening for wake word"""
    global listening
    listening = False
    print("[WAKE] Wake word listener stopped")
