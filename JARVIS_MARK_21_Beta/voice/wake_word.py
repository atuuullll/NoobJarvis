# wake_word.py - Voice wake word detection for JARVIS using OpenWakeWord
import speech_recognition as sr
import threading
import time
import numpy as np
from openwakeword.model import Model

wake_word = "jarvis"
listening = False
wake_detected_callback = None
wake_model = None

def initialize_wake_model():
    """Initialize OpenWakeWord model for better wake word detection"""
    global wake_model
    try:
        # Load the OpenWakeWord model
        # Using default 'hey google' model as base, but can be customized
        wake_model = Model(inference_framework="onnx")
        print("[WAKE] OpenWakeWord model initialized successfully")
        return True
    except Exception as e:
        print(f"[WAKE] Failed to initialize OpenWakeWord model: {e}")
        print("[WAKE] Falling back to Google Speech Recognition")
        return False

def set_wake_callback(callback):
    """Set callback function to execute when wake word is detected"""
    global wake_detected_callback
    wake_detected_callback = callback

def listen_for_wake_word():
    """Listen for wake word using OpenWakeWord for better accuracy"""
    global listening, wake_model
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000  # More sensitive
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    
    try:
        with sr.Microphone() as source:
            print("[WAKE] Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("[WAKE] Microphone calibrated. Listening for wake word...")
            
            while listening:
                try:
                    print("[WAKE] Listening for: 'Hey Jarvis' or speak your command...")
                    
                    # Listen with optimized settings
                    audio = recognizer.listen(
                        source, 
                        timeout=5, 
                        phrase_time_limit=3
                    )
                    print("[WAKE] Audio captured, processing...")
                    
                    try:
                        # Convert audio to numpy array for OpenWakeWord
                        audio_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0
                        
                        # If OpenWakeWord is available, use it for primary detection
                        if wake_model is not None:
                            try:
                                predictions = wake_model.predict(audio_data)
                                
                                # Check if any wake word score is high enough
                                max_score = max(predictions.values()) if predictions else 0
                                print(f"[WAKE] OpenWakeWord score: {max_score:.3f}")
                                
                                if max_score > 0.5:  # Threshold for wake word detection
                                    print(f"[WAKE] ✓ Wake word detected! (confidence: {max_score:.2%})")
                                    if wake_detected_callback:
                                        wake_detected_callback()
                                    time.sleep(2)  # Prevent multiple triggers
                                    continue
                            except Exception as e:
                                print(f"[WAKE] OpenWakeWord error: {e}")
                                # Fall through to Google Speech Recognition
                        
                        # Fallback: Use Google Speech Recognition
                        text = recognizer.recognize_google(audio, language='en-US').lower()
                        print(f"[WAKE] Heard: '{text}'")
                        
                        # Check for wake words with flexible matching
                        wake_words = ["jarvis", "hey jarvis", "jarvis hey", "o jarvis", "oh jarvis"]
                        
                        if any(word in text for word in wake_words):
                            # Wake word detected - open window and wait for command
                            print("[WAKE] ✓ Wake word detected!")
                            if wake_detected_callback:
                                wake_detected_callback()
                            
                            # Extract command after wake word (if any)
                            remaining_text = text
                            for word in wake_words:
                                if word in remaining_text:
                                    remaining_text = remaining_text.replace(word, "").strip()
                                    break
                            
                            # If there's a command after the wake word, process it
                            if remaining_text and len(remaining_text) > 2:
                                print(f"[WAKE] Command detected after wake word: '{remaining_text}'")
                                from core.commands import process_command
                                
                                # Create a simple text widget simulation for command processing
                                class SimpleTextWidget:
                                    def insert(self, pos, text):
                                        print(f"[GUI] {text}")
                                    def see(self, pos):
                                        pass
                                    def update(self):
                                        pass
                                    def winfo_exists(self):
                                        return True
                                
                                output_widget = SimpleTextWidget()
                                process_command(remaining_text, output_widget, language='en')
                                time.sleep(1)
                            
                            time.sleep(2)  # Prevent immediate re-trigger
                        else:
                            # No wake word detected - check if it's a standalone command
                            # If it's more than 2 words, treat it as a direct command
                            word_count = len(text.split())
                            
                            # List of common command keywords to detect commands without wake word
                            command_keywords = [
                                "open ", "close ", "launch ", "start ", "play ", 
                                "stop ", "what ", "how ", "tell ", "show ", "set ",
                                "create ", "add ", "delete ", "remove ", "search ",
                                "calculate ", "compute ", "turn ", "enable ", "disable ",
                                "help ", "assistant ", "reminder ", "note ", "reminder "
                            ]
                            
                            is_likely_command = any(text.startswith(keyword) for keyword in command_keywords) or word_count >= 2
                            
                            if is_likely_command:
                                print(f"[WAKE] Direct command detected (without wake word): '{text}'")
                                # Process this as a direct command
                                try:
                                    from core.commands import process_command
                                    
                                    # Create a simple text widget simulation for command processing
                                    class SimpleTextWidget:
                                        def insert(self, pos, text):
                                            print(f"[GUI] {text}")
                                        def see(self, pos):
                                            pass
                                        def update(self):
                                            pass
                                        def winfo_exists(self):
                                            return True
                                        def after(self, delay, func=None):
                                            # Execute immediately for direct command mode
                                            if func:
                                                func()
                                            return None
                                    
                                    output_widget = SimpleTextWidget()
                                    process_command(text, output_widget, language='en')
                                    time.sleep(1)
                                except Exception as e:
                                    print(f"[WAKE] Error processing direct command: {e}")
                            else:
                                print(f"[WAKE] Not a command - ignoring: '{text}'")
                            
                    except sr.UnknownValueError:
                        print("[WAKE] Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        print(f"[WAKE] API Error: {e}")
                        time.sleep(1)
                        
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
    """Start listening for wake word in background using OpenWakeWord"""
    global listening, wake_detected_callback
    
    # Initialize OpenWakeWord model on first run
    initialize_wake_model()
    
    if callback:
        wake_detected_callback = callback
    
    listening = True
    thread = threading.Thread(target=listen_for_wake_word, daemon=True)
    thread.start()
    print("[WAKE] Wake word listener started (OpenWakeWord enabled)")

def stop_wake_listener():
    """Stop listening for wake word"""
    global listening
    listening = False
    print("[WAKE] Wake word listener stopped")

