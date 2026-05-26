# 🤖 JARVIS AI

**JARVIS AI** is a voice-enabled AI assistant web application inspired by Iron Man's J.A.R.V.I.S. It combines a Flask-powered backend with a real-time Web UI, supporting both voice commands (via microphone) and text input. Designed to run locally on Windows and seamlessly in the cloud (Render) where it automatically switches to text/web mode.

🔗 **Live Demo:** [jarvis-ai-tuo9.onrender.com](https://jarvis-ai-tuo9.onrender.com)
📁 **Repository:** [github.com/dwivediadarsh496-commits/JARVIS-AI](https://github.com/dwivediadarsh496-commits/JARVIS-AI)

---

## ✨ Features

- **Voice Recognition** — Wake-word detection (`"Hey Jarvis"`, `"Jarvis"`, `"Ok Jarvis"`) with Google Speech Recognition
- **Text-to-Speech (TTS)** — Responds verbally via `pyttsx3` on local environments
- **Text Command Input** — Full web UI for sending commands without a microphone
- **Real-Time State Polling** — UI continuously polls `/api/state` to reflect live status, chat history, and system logs
- **Smart Cloud/Local Detection** — Automatically disables voice hardware on cloud deployments (Render), switching to Web/Text-only mode
- **Wake Word Toggle** — Enable or disable passive wake-word listening from the UI
- **Threaded Architecture** — Background assistant thread runs independently from the Flask web server
- **Command History** — Full chat log between user and JARVIS, clearable from the UI
- **System Logs** — Real-time internal logs streamed to the dashboard

---

## 🗣️ Supported Voice Commands

| Command | Action |
|---|---|
| `"Open Google"` | Opens google.com in the browser |
| `"Open YouTube"` | Opens youtube.com in the browser |
| `"Open LinkedIn"` | Opens linkedin.com in the browser |
| `"Open Gemini"` | Opens gemini.google.com |
| `"Open GitHub"` | Opens the JARVIS-AI GitHub repository |
| `"What is your name?"` | Responds with "My name is Jarvis" |
| `"Time"` | Speaks and displays the current time |
| `"Date"` | Speaks and displays today's date |
| Any other input | Echoes back what JARVIS heard with a help prompt |

---

## 🏗️ Architecture

```
JARVIS-AI/
├── app.py              # Flask backend + voice assistant worker thread
├── templates/
│   └── index.html      # Web UI (chat interface + controls)
├── requirements.txt    # Python dependencies
├── Procfile            # Render/Heroku process definition
├── render.yaml         # Render deployment config
└── .gitignore
```

### How It Works

```
Browser  ──[POST /api/command]──►  command_queue
                                        │
         ◄──[GET  /api/state]──  Flask  │  voice_assistant_worker()
                                 App    │  (background thread)
                                        │
                             ┌──────────▼───────────┐
                             │  process_command_logic │
                             │  • open websites       │
                             │  • tell time/date      │
                             │  • speak response      │
                             └────────────────────────┘
```

The Flask server and the voice assistant run in **separate threads**. The assistant thread continuously:
1. Checks the `command_queue` for web-submitted text commands
2. Listens for the wake word (if enabled and mic is available)
3. Processes commands and updates shared `state` (history, logs, status)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Microphone (optional — for voice mode)
- A modern web browser

### Installation

```bash
# Clone the repository
git clone https://github.com/dwivediadarsh496-commits/JARVIS-AI.git
cd JARVIS-AI

# Create a virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
python app.py
```

Open your browser and navigate to: https://jarvis-ai-tuo9.onrender.com/

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|---|---|
| GET | `/api/state` | Returns current status, chat history, system logs, and wake-word state |
| POST | `/api/command` | Submit a text command to JARVIS |
| POST | `/api/trigger-listen` | Trigger a one-shot microphone listen from the UI |
| POST | `/api/toggle-wake` | Toggle passive wake-word listening on/off |
| POST | `/api/clear-history` | Clear chat history and system logs |

### Example: Send a Command

```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "open google"}'
```

**Response:**
```json
{ "status": "success" }
```

### Example: Get State

```bash
curl http://localhost:5000/api/state
```

**Response:**
```json
{
  "status": "Idle",
  "history": [
    { "sender": "jarvis", "text": "Jarvis System online and connected to Web UI." }
  ],
  "logs": [
    { "type": "sys", "text": "Voice engine initialized." }
  ],
  "wake_word_enabled": true
}
```

---

## ☁️ Cloud vs Local Behaviour

JARVIS AI automatically detects its environment using the `RENDER` environment variable and OS checks:

| Feature | Local (Windows) | Cloud (Render) |
|---|---|---|
| Speech Recognition | ✅ Active | ❌ Disabled |
| Text-to-Speech (TTS) | ✅ Active | ❌ Disabled |
| Wake Word Listening | ✅ Active | ❌ Disabled |
| Text Command Input | ✅ Active | ✅ Active |
| Web UI | ✅ Active | ✅ Active |
| Status Display | `Idle (Wake Word Active)` | `Idle (Web/Text Mode)` |

---

## 🚢 Deployment (Render)

The repo includes a `render.yaml` and `Procfile` for one-click deployment on [Render](https://render.com).

```yaml
# render.yaml
services:
  - type: web
    name: jarvis-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

The app will run in **Web/Text-only mode** on Render since cloud environments don't have microphone access.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Voice Recognition | `speech_recognition` + Google Speech API |
| Text-to-Speech | `pyttsx3` |
| Frontend | HTML, CSS, JavaScript |
| Threading | Python `threading` + `queue` |
| Deployment | Render (cloud), local Flask dev server |

---

## 📊 Languages

- HTML — 67.8%
- Python — 32.1%
- Procfile — 0.1%

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a pull request.

```bash
git checkout -b feature/my-new-command
# Add your command to process_command_logic() in app.py
git commit -m "Add new command: ..."
git push origin feature/my-new-command
```

---

## 📄 License

This project is open source. See the repository for license details.

---

> *"At your service."* — JARVIS 🤖
