'''import speech_recognition as sr
import threading
from core.commands import process_command
from voice.tts import speak
import time

recognizer = sr.Recognizer()
wake_word = "hey jarvis"  # Set your wake word here
wake_word_active = False # Global variable to control wake word mode


# normal talk button usage
def listen_and_respond(output_text):
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            output_text.insert("end", "🎤 Listening...\n")
            output_text.see("end")
            audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio)
            process_command(command, output_text)

    except Exception as e:
        error_msg = "⚠️ Sorry, I couldn't process that."
        output_text.insert("end", f"{error_msg}\n")
        output_text.see("end")
        print("Error:", e)
        speak(error_msg)

# Thread wrapper
def threaded_listen_and_respond(output_text):
    thread = threading.Thread(target=listen_and_respond, args=(output_text,))
    thread.start()


# 🧠 Wake word mode
wake_word_active = False
def start_wake_word_listener(output_text, mode_flag_func):
    def listen_loop():
        global wake_word_active
        wake_word_active = True
        while wake_word_active:
            if not mode_flag_func():  # Check if wake word mode is on
                time.sleep(1)
                continue

            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("👂 Listening for wake word...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

                said = recognizer.recognize_google(audio).lower()
                print("Heard:", said)

                if wake_word in said:
                    speak("Yes SIR?")
                    with sr.Microphone() as source:
                        output_text.insert("end", "🎤 Awaiting your command...\n")
                        output_text.see("end")
                        command_audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(command_audio)
                        process_command(command, output_text)

            except Exception as e:
                print("Wake listener error:", e)
                time.sleep(2)

    threading.Thread(target=listen_loop, daemon=True).start()
    
    
def stop_wake_word_listener():
    global wake_word_active
    wake_word_active = False
    print("Wake word listener stopped.")'''
    
    
import speech_recognition as sr
import threading
import time
import os
from dotenv import load_dotenv
from core.commands import process_command
from voice.tts import speak
from langdetect import detect, detect_langs, DetectorFactory
import openai

# Load environment variables
load_dotenv()
DetectorFactory.seed = 0

recognizer = sr.Recognizer()
wake_word = "jarvis"
wake_word_active = False

# Initialize OpenAI with API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    print("[STT] OpenAI Whisper API configured")
else:
    print("[STT] Warning: OPENAI_API_KEY not found. Falling back to Google Speech Recognition")

# Enhanced recognizer settings for better accuracy
def setup_recognizer():
    """Setup recognizer with optimal settings for clear voice recognition"""
    recognizer.energy_threshold = 3000
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.operation_timeout = None
    recognizer.phrase_threshold = 0.3
    print("[STT] Recognizer configured for optimal voice clarity")

setup_recognizer()

# Hindi-like words written in Roman script
HINDI_KEYWORDS = [
    "kaise", "kya", "kyu", "aap", "tum", "hai", "ho", "nahi", "batao", "acha", "theek", "kar", "rakh",
    "mujhe", "tera", "mera", "bhi", "sab", "se", "ab", "main", "hai", "ki", "ka", "ke", "hota", "hona",
    "chalo", "karo", "karna", "jarurat", "kyunki", "kyon", "tumhara", "mera", "acha", "sahi"
]

def detect_language_smart(text):
    text = text.lower()
    hindi_score = sum(1 for word in HINDI_KEYWORDS if word in text)

    try:
        langs = detect_langs(text)
        if langs[0].lang == "hi" and langs[0].prob > 0.5:
            return "hi"
    except:
        pass

    if hindi_score >= 2:
        return "hi"

    return "en"

def transcribe_with_whisper(audio_data):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        if not OPENAI_API_KEY:
            return None
        
        print("[STT] Using OpenAI Whisper for transcription...")
        
        # Convert audio to WAV format for Whisper
        import io
        wav_data = audio_data.get_wav_data()
        
        # Create file-like object
        audio_file = io.BytesIO(wav_data)
        audio_file.name = "audio.wav"
        
        # Use Whisper API
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="en",
            temperature=0.2
        )
        
        text = transcript.get("text", "").strip()
        print(f"[STT] Whisper transcribed: {text}")
        return text
        
    except Exception as e:
        print(f"[STT] Whisper API error: {e}")
        return None

# 🔊 Normal talk button usage with language detection
def listen_and_respond(output_text):
    try:
        with sr.Microphone() as source:
            print("[STT] Calibrating microphone for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("[STT] Microphone calibrated. Listening for command...")
            
            output_text.insert("end", "[LISTENING] Speak your command clearly...\n")
            output_text.see("end")
            output_text.update()
            
            try:
                audio = recognizer.listen(
                    source,
                    timeout=15,
                    phrase_time_limit=15
                )
                print("[STT] Audio captured successfully")
            except sr.RequestError:
                output_text.insert("end", "[ERROR] Microphone not available\n")
                speak("I cannot access your microphone", lang='en')
                return

            output_text.insert("end", "[PROCESSING] Recognizing your voice...\n")
            output_text.see("end")
            output_text.update()

            command = None
            attempts = 0
            max_attempts = 2
            
            # First, try Whisper API if available
            if OPENAI_API_KEY:
                try:
                    command = transcribe_with_whisper(audio)
                    if command:
                        print(f"[STT] Successfully transcribed with Whisper: {command}")
                except Exception as e:
                    print(f"[STT] Whisper failed: {e}")
            
            # Fallback to Google Speech Recognition
            if command is None:
                while command is None and attempts < max_attempts:
                    try:
                        print(f"[STT] Recognition attempt {attempts + 1} (Google)...")
                        command = recognizer.recognize_google(audio, language='en-US')
                        print(f"[STT] Successfully recognized: {command}")
                        
                    except sr.UnknownValueError:
                        attempts += 1
                        if attempts < max_attempts:
                            print(f"[STT] Could not understand, trying alternative...")
                            try:
                                command = recognizer.recognize_google(audio)
                            except sr.UnknownValueError:
                                pass
                        if command is None and attempts >= max_attempts:
                            output_text.insert("end", "[ERROR] Could not understand. Please speak clearly.\n")
                            speak("I couldn't understand that. Please speak more clearly.", lang='en')
                            return
                            
                    except sr.RequestError as e:
                        output_text.insert("end", f"[ERROR] Network error: {e}\n")
                        speak("Network error. Please check your internet connection.", lang='en')
                        return

            if command:
                command = command.strip()
                print(f"[VOICE] Heard: {command}")
                
                language = detect_language_smart(command)
                print(f"[LANGUAGE] Detected: {language}")

                process_command(command, output_text, language)

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[STT] {error_msg}")
        output_text.insert("end", f"[ERROR] {error_msg}\n")
        speak("An error occurred during voice processing", lang='en')

# Threaded wrapper for Normal Mode
def threaded_listen_and_respond(output_text):
    thread = threading.Thread(target=listen_and_respond, args=(output_text,), daemon=True)
    thread.start()

# 🧠 Wake Word Mode
def start_wake_word_listener(output_text, mode_flag_func):
    def listen_loop():
        global wake_word_active
        wake_word_active = True
        consecutive_errors = 0
        max_consecutive_errors = 5
        last_wake_time = 0

        while wake_word_active:
            if not mode_flag_func():
                time.sleep(1)
                continue

            try:
                with sr.Microphone() as source:
                    if consecutive_errors == 0:
                        recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    print("[WAKE] Listening for wake word...")
                    
                    try:
                        audio = recognizer.listen(
                            source,
                            timeout=5,
                            phrase_time_limit=3
                        )
                    except sr.RequestError:
                        print("[WAKE] Microphone error")
                        consecutive_errors += 1
                        time.sleep(2)
                        continue

                    try:
                        said = None
                        
                        # Try Whisper first if available
                        if OPENAI_API_KEY:
                            try:
                                said = transcribe_with_whisper(audio)
                                if said:
                                    said = said.lower()
                            except Exception as e:
                                print(f"[WAKE] Whisper error: {e}")
                        
                        # Fallback to Google
                        if said is None:
                            said = recognizer.recognize_google(audio, language='en-US').lower()
                        
                        print(f"[WAKE] Heard: '{said}'")
                        consecutive_errors = 0

                        if "jarvis" in said:
                            current_time = time.time()
                            if current_time - last_wake_time > 1:
                                print("[WAKE] ✓ Wake word detected!")
                                last_wake_time = current_time
                                speak("Yes, I'm listening!", lang='en')
                                
                                print("[WAKE] Listening for command...")
                                output_text.insert("end", "[LISTENING] Say your command now...\n")
                                output_text.see("end")
                                output_text.update()
                                
                                with sr.Microphone() as source2:
                                    recognizer.adjust_for_ambient_noise(source2, duration=1)
                                    try:
                                        command_audio = recognizer.listen(
                                            source2,
                                            timeout=10,
                                            phrase_time_limit=10
                                        )
                                        
                                        command = None
                                        
                                        # Try Whisper for command
                                        if OPENAI_API_KEY:
                                            try:
                                                command = transcribe_with_whisper(command_audio)
                                            except Exception as e:
                                                print(f"[WAKE] Whisper command error: {e}")
                                        
                                        # Fallback to Google
                                        if command is None:
                                            try:
                                                command = recognizer.recognize_google(command_audio, language='en-US')
                                            except sr.UnknownValueError:
                                                print("[WAKE] Could not understand command")
                                                speak("I didn't catch that command", lang='en')
                                        
                                        if command:
                                            print(f"[COMMAND] Recognized: {command}")
                                            language = detect_language_smart(command)
                                            print(f"[LANGUAGE] {language}")
                                            process_command(command, output_text, language)
                                            time.sleep(1)
                                        
                                    except sr.RequestError:
                                        print("[WAKE] Command timeout")
                                        speak("Command timeout", lang='en')
                        else:
                            print(f"[WAKE] Not wake word: '{said}'")
                            if len(said.split()) > 2:
                                print(f"[WAKE] Processing as direct command: {said}")
                                language = detect_language_smart(said)
                                process_command(said, output_text, language)
                                time.sleep(1)

                    except sr.UnknownValueError:
                        print("[WAKE] Could not understand audio")
                        time.sleep(0.5)
                    except sr.RequestError as e:
                        print(f"[WAKE] API Error: {e}")
                        consecutive_errors += 1
                        time.sleep(2)

            except Exception as e:
                print(f"[WAKE] Error: {e}")
                consecutive_errors += 1
                time.sleep(2)
            
            if consecutive_errors > max_consecutive_errors:
                print("[WAKE] Too many errors. Restarting listener...")
                consecutive_errors = 0
                time.sleep(3)

    threading.Thread(target=listen_loop, daemon=True).start()

def stop_wake_word_listener():
    global wake_word_active
    wake_word_active = False
    print("[WAKE] Wake word listener stopped")