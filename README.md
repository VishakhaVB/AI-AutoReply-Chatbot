# AI-AutoReply-Chatbot

A production-quality, modular Python automation and artificial intelligence framework. The bot monitors chat windows on WhatsApp Web, persists profiles in SQLite, detects user emotion and language, generates tone-based safe reply alternatives using Google Gemini, and performs vision/local audio speech processing.

---

## 🌟 Project Overview

**AI-AutoReply-Chatbot** acts as an autonomous assistant. By combining GUI coordinate automation, localized database history tracking, sentiment classifier analysis, Whisper local speech models, and Google's Gemini LLMs, the bot handles incoming text, image, and speech inputs with safety guardrails and personalized responses.

## ✨ Key Features

- **Daemon Automation Loop (`main.py`)**: Runs a robust background thread that regularly checks chat history, ignoring duplicate messages and self-messages.
- **WhatsApp GUI Controller (`automation.py`)**: Simulates user desktop mouse clicks and copy-paste routines via PyAutoGUI and Pyperclip.
- **Gemini Content Generator (`ai_reply.py`)**: Harnesses Gemini 2.5 Flash to generate responses.
- **Regex Chat Parser (`utils.py`)**: Extracts timestamps, sender names, and multiline message contents from copied chat history using robust regexes and hashes them for deduplication.
- **SQLite Memory Manager (`database/memory.py`)**: Tracks user preference profiles (language, tone, running summary) and records conversation context in a local database.
- **Multimodal Sentiment Classifier (`analyzer.py`)**: Detects sender language (English, Hindi, Marathi, Hinglish) and emotion (Happy, Sad, Angry, Excited, Neutral, Stressed).
- **Safety Checker & Reply Multi-Toner (`safety.py`)**: Filters incoming/outgoing text for toxicity/PII and generates three response options (casual, funny, professional).
- **Local Vision Analyzer (`vision.py`)**: Inspects local image files using Gemini's visual intelligence, categorizing image types (Handwritten, Meme, etc.), generating descriptions, and extracting text.
- **Whisper Speech Processor (`audio/speech.py`)**: Runs local OpenAI Whisper models to transcribe audio inputs (MP3, WAV, OGG) and detect spoken languages, with custom preprocessing handled via `ffmpeg`.

## 📂 Project Structure

```text
AI-AutoReply-Chatbot/
├── src/
│   ├── audio/
│   │   └── speech.py           # Whisper transcription and language detection with ffmpeg preprocessing
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configures API keys and loads .env properties
│   ├── database/
│   │   └── memory.py           # SQLite local storage for user preferences and message logs
│   ├── ai_reply.py             # Reusable Gemini response generation class
│   ├── analyzer.py             # Classifies message language, emotion, and recommended style
│   ├── automation.py           # Controls keyboard/mouse copy-paste sequences
│   ├── main.py                 # Core orchestration bot loop running every 5 seconds
│   ├── safety.py               # Inspects content risks and generates casual/funny/formal replies
│   ├── utils.py                # Regex extraction and SHA-256 message ID hashing
│   └── vision.py               # Image category detector, describer, and OCR
├── .env                        # Local settings and Gemini secrets (ignored by Git)
├── .env.example                # Template settings for setting up environment variables
├── .gitignore                  # Prevents committing dependencies, DB files, and key files
├── README.md                   # Project documentation documentation
└── requirements.txt            # Python dependencies (Pillow, openai-whisper, google-genai, etc.)
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.9+**
- **ffmpeg** installed on the system and configured in the system PATH.
- Visual display (required for PyAutoGUI mouse coordinate control).

### 1. Clone the Repository
```bash
git clone https://github.com/VishakhaVB/AI-AutoReply-Chatbot.git
cd AI-AutoReply-Chatbot
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` into a new file named `.env` and fill in your details:
```env
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key_here
MY_NAME=Me
POLLING_INTERVAL_SECONDS=5.0
```

---

## 🚀 Running the Bot

To start the auto-reply daemon, align your WhatsApp Web window on screen matching the coordinates specified in `src/automation.py`, then run:

```bash
python src/main.py
```

*Note: Screen coordinates are fully configurable via class variables inside `src/automation.py`.*

---

## 📄 License

This project is licensed under the MIT License.
