import threading
import queue
import time
import webbrowser
import os
from flask import Flask, render_template, jsonify, request

# Try to import SpeechRecognition
try:
    import speech_recognition as sr
    HAS_SPEECH_REC = True
except ImportError:
    sr = None
    HAS_SPEECH_REC = False

# Try to import pyttsx3
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    pyttsx3 = None
    HAS_TTS = False

# Initialize Flask
app = Flask(__name__, template_folder='templates')

# Shared State
state = {
    "status": "Idle",  # Idle, Listening, Processing, Speaking
    "history": [],     # List of {"sender": "user"|"jarvis", "text": "..."}
    "logs": []         # List of {"type": "sys"|"err"|"wake", "text": "..."}
}
state_lock = threading.Lock()

# Control flags
wake_word_enabled = True
force_listen_flag = False

# Queue for typed/incoming commands
command_queue = queue.Queue()

# Wake words list
WAKE_WORDS = ["hey jarvis", "jarvis", "ok jarvis"]

def add_history(sender, text):
    with state_lock:
        state["history"].append({"sender": sender, "text": text})

def add_system_log(text, log_type="sys"):
    with state_lock:
        state["logs"].append({"type": log_type, "text": text})
    print(f"[{log_type.upper()}] {text}")

def update_status(status_text):
    with state_lock:
        state["status"] = status_text

# Background Assistant Loop
def voice_assistant_worker():
    global force_listen_flag, wake_word_enabled
    
    # Initialize COM on Windows for this thread
    try:
        import pythoncom
        pythoncom.CoInitialize()
        add_system_log("COM initialized successfully.")
    except Exception as e:
        add_system_log(f"COM initialization skipped/failed: {str(e)}", "sys")

    # Initialize Voice Engine
    engine = None
    if HAS_TTS and pyttsx3:
        try:
            engine = pyttsx3.init()
            add_system_log("Voice engine initialized.")
        except Exception as e:
            add_system_log(f"Failed to initialize pyttsx3 engine: {str(e)}", "err")
            engine = None
    else:
        add_system_log("Voice engine (TTS) is not available or disabled.", "sys")

    def speak(text):
        update_status("Speaking")
        add_history("jarvis", text)
        add_system_log(f"Jarvis spoke: {text}")
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as ex:
                add_system_log(f"TTS error: {str(ex)}", "err")
        else:
            add_system_log("(TTS synthesis skipped: No voice engine available)", "sys")
        update_status("Idle")

    # Welcome message
    speak("Jarvis System online and connected to Web UI.")

    # Initialize Speech Recognizer and test microphone access
    r = None
    mic_available = False
    if HAS_SPEECH_REC and sr:
        try:
            r = sr.Recognizer()
            add_system_log("Speech Recognizer initialized.")
            try:
                with sr.Microphone() as source:
                    pass
                mic_available = True
                add_system_log("Microphone access verified. Voice mode active.")
            except Exception as mic_err:
                add_system_log(f"Microphone not accessible: {str(mic_err)}. Running in Web/Text-only mode.", "sys")
        except Exception as e:
            add_system_log(f"Failed to initialize Speech Recognizer: {str(e)}", "err")
            r = None
    else:
        add_system_log("Speech Recognizer not available. Running in Web/Text-only mode.", "sys")

    while True:
        # 1. Process typed command queue first
        if not command_queue.empty():
            cmd = command_queue.get()
            update_status("Processing")
            process_command_logic(cmd, speak)
            continue

        # 2. Check if user clicked mic button
        should_force_listen = False
        with state_lock:
            if force_listen_flag:
                should_force_listen = True
                force_listen_flag = False

        if should_force_listen:
            if not r or not mic_available:
                add_system_log("Microphone input is not available on this server.", "err")
                speak("Voice recognition is not available or supported on this system.")
                continue
                
            add_system_log("Voice trigger activated from Web UI.")
            update_status("Listening")
            try:
                with sr.Microphone() as source:
                    add_system_log("Calibrating microphone ambient noise...")
                    r.adjust_for_ambient_noise(source, duration=0.8)
                    add_system_log("Listening for command...")
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                
                update_status("Processing")
                command = r.recognize_google(audio)
                add_history("user", command)
                process_command_logic(command, speak)
            except sr.WaitTimeoutError:
                add_system_log("Microphone timeout. No voice detected.", "err")
                update_status("Idle")
            except sr.UnknownValueError:
                add_system_log("Could not understand the audio.", "err")
                speak("I did not catch that. Could you please repeat?")
            except Exception as e:
                add_system_log(f"Microphone error: {str(e)}", "err")
                update_status("Idle")
            continue

        # 3. Continuous wake word scanner (if enabled)
        if wake_word_enabled:
            if not r or not mic_available:
                update_status("Idle (Web/Text Mode)")
                time.sleep(1.0)
                continue
                
            update_status("Idle (Wake Word Active)")
            try:
                with sr.Microphone() as source:
                    # Quick calibration on first run, then fast listening
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=1.5, phrase_time_limit=2.5)
                
                word = r.recognize_google(audio).lower()
                if any(w in word for w in WAKE_WORDS):
                    add_system_log(f"Wake word detected: '{word}'", "wake")
                    speak("Yes?")
                    
                    # Direct listen for the following command
                    update_status("Listening")
                    with sr.Microphone() as source:
                        audio = r.listen(source, timeout=5, phrase_time_limit=5)
                    command = r.recognize_google(audio)
                    add_history("user", command)
                    process_command_logic(command, speak)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                # Expected during normal background scanning
                pass
            except Exception as e:
                # Catch any unexpected mic issues without crashing loop
                time.sleep(1)
        else:
            if not r or not mic_available:
                update_status("Idle (Web/Text Mode)")
            else:
                update_status("Idle")
            time.sleep(0.3)

def process_command_logic(c, speak_func):
    c = c.lower().strip()
    if not c:
        return
        
    add_system_log(f"Processing: '{c}'")
    
    if "open google" in c:
        webbrowser.open("http://www.google.com")
        speak_func("Google is open now")
    elif "open youtube" in c:
        webbrowser.open("http://www.youtube.com")
        speak_func("Youtube is open now")
    elif "what is your name" in c:
        speak_func("My name is Jarvis")
    elif "open linkedin" in c:
        webbrowser.open("http://www.linkedin.com")
        speak_func("Linkedin is open now")
    elif "open gemini" in c:
        webbrowser.open("https://gemini.google.com/app")
        speak_func("Gemini is open now")
    elif "open github" in c:
        webbrowser.open("http://www.github.com")
        speak_func("Github is open now")
    elif "time" in c:
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        speak_func(f"The current time is {now}")
    elif "date" in c:
        from datetime import datetime
        today = datetime.now().strftime("%A, %B %d, %Y")
        speak_func(f"Today's date is {today}")
    else:
        speak_func(f"I heard you say: {c}. I can help you open Google, YouTube, GitHub, Gemini, or LinkedIn.")


# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    with state_lock:
        return jsonify({
            "status": state["status"],
            "history": state["history"],
            "logs": state["logs"],
            "wake_word_enabled": wake_word_enabled
        })

@app.route('/api/command', methods=['POST'])
def post_command():
    data = request.get_json() or {}
    command = data.get("command", "")
    if command:
        command_queue.put(command)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Empty command"})

@app.route('/api/trigger-listen', methods=['POST'])
def trigger_listen():
    global force_listen_flag
    with state_lock:
        force_listen_flag = True
    return jsonify({"status": "success"})

@app.route('/api/toggle-wake', methods=['POST'])
def toggle_wake():
    global wake_word_enabled
    wake_word_enabled = not wake_word_enabled
    add_system_log(f"Wake word scanning: {'Enabled' if wake_word_enabled else 'Disabled'}")
    return jsonify({
        "status": "success",
        "wake_word_enabled": wake_word_enabled
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    with state_lock:
        state["history"] = []
        state["logs"] = []
    return jsonify({"status": "success"})

# Start voice assistant thread at module level so it runs under WSGI servers like Gunicorn
assistant_thread = threading.Thread(target=voice_assistant_worker, daemon=True)
assistant_thread.start()

# Start Flask app
if __name__ == "__main__":
    # Start Flask server using environment PORT for deployment readiness
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask Web UI server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
