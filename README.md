# AI-AutoReply-Chatbot

A production-quality Python automation framework designed to monitor chat logs, generate contextual, personality-driven AI replies using Google's Gemini Models, and automatically paste the replies back into messaging windows.

---

## 🌟 Project Overview

**AI-AutoReply-Chatbot** acts as an autonomous chat companion. By combining desktop automation techniques (using PyAutoGUI and Pyperclip) with Google's advanced Gemini Large Language Models, the bot identifies incoming messages, interprets the conversational flow, and sends responses.

## ✨ Key Features

- **Automated Desktop Interaction**: Directly interacts with web interfaces or desktop applications via GUI coordinate tracking and simulated typing.
- **Dynamic AI Response Generation**: Integrates with the official Google Gen AI SDK to produce replies using the `gemini-2.5-flash` model.
- **Robust Configuration Management**: Implements structured configurations via a unified `settings.py` module backed by `python-dotenv`.
- **Zero-Hardcoding Security**: Environment variable separation ensures API keys and secrets are never committed to version control.
- **Clean Architecture**: Designed with modular components representing configuration, automation, utilities, and AI reasoning.

## 📂 Project Structure

```text
AI-AutoReply-Chatbot/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Loads configuration and validates GEMINI_API_KEY
│   ├── ai_reply.py             # Interfaces with the Google Gemini API (GeminiReplyGenerator)
│   ├── automation.py           # Handles mouse movements, keyboard simulation, clipboard (Placeholder/Planned)
│   ├── utils.py                # Helper utilities (Placeholder/Planned)
│   └── main.py                 # Application entrypoint coordinating automation and AI logic
├── .env                        # Local environment settings (ignored by Git)
├── .env.example                # Template for required environment variables
├── .gitignore                  # Keeps virtual environments, secrets, and IDE configs untracked
├── README.md                   # Project documentation
└── requirements.txt            # Project dependencies
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.9+**
- Visual capabilities (this framework relies on desktop screen interaction; running in headless environments requires virtual displays)

### 1. Clone the Repository
```bash
git clone https://github.com/VishakhaVB/AI-AutoReply-Chatbot.git
cd AI-AutoReply-Chatbot
```

### 2. Set Up a Virtual Environment
It is highly recommended to isolate dependencies using a virtual environment:
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
Create a file named `.env` in the root of the project using the structure from `.env.example`:

```env
# Debug Mode (True/False)
DEBUG=True

# Gemini API Key (Required for chat response generation)
# Obtain your key from: https://aistudio.google.com
GEMINI_API_KEY=your_gemini_api_key_here

# Configuration Settings
POLLING_INTERVAL_SECONDS=5.0
TARGET_SENDER_NAME=Rohan Das
```

---

## 🚀 Usage

Since the system interacts with the GUI, prepare the target chat screen (e.g., web-browser messenger) in the correct desktop coordinates before executing:

```bash
python src/main.py
```

*Note: Coordinates and interaction coordinates are configured in `src/main.py` and can be adjusted depending on screen resolution.*

---

## 🗺️ Future Roadmap

- [ ] **Cross-Platform API Integrations**: Transition from GUI coordinates (`pyautogui`) to official APIs/Headless wrappers for platforms like WhatsApp, Discord, or Telegram.
- [ ] **Adaptive Coordinates Engine**: Automatically locate messaging inputs using OpenCV computer vision instead of hardcoded coordinates.
- [ ] **Enhanced Personality Profiles**: Support for multiple selectable personality templates (e.g., professional, sarcastic, educational).
- [ ] **Database Logging**: Log message history and model tokens for analysis, auditing, and fine-tuning.
- [ ] **Web Dashboard**: Provide a visual interface to manage targets, edit prompts, and view active chatbot logs.

---

## 📄 License

This project is licensed under the MIT License.
