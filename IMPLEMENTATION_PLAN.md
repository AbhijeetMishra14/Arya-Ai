# ARYA (Advanced Responsive Yielding Assistant) Implementation Plan

## 1. Architecture Overview
ARYA will be built using a modular Python architecture to allow independent development and testing of its various capabilities.

```text
d:\Jarvis\
├── .env                  # API keys (Gemini, Tavily, etc.)
├── requirements.txt      # Dependencies
├── main.py               # Entry point for CUI / GUI
├── arya/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── brain.py      # Gemini API integration & prompt engineering (Personality)
│   │   ├── memory.py     # Short-term and long-term conversation history
│   │   └── config.py     # Configuration and environment variable loading
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── search.py     # Tavily API search and summarization
│   │   ├── voice.py      # Speech-to-text (SpeechRecognition) & Text-to-speech (pyttsx3)
│   │   ├── system.py     # OS control (app launching, file search, typing)
│   │   ├── internet.py   # Web automation (Chrome, YouTube)
│   │   └── cybersec.py   # Defensive cybersecurity (process monitoring, local vulnerability scanning)
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cui.py        # Command-line interface with rich text
│   │   └── gui.py        # Graphical user interface using CustomTkinter
```

## 2. Technical Stack
- **AI Brain**: `google-generativeai` (Gemini API)
- **Search**: `tavily-python` (Tavily API)
- **Voice**: `SpeechRecognition` (STT), `pyttsx3` (Offline TTS)
- **System**: `psutil` (Process monitoring), `os`/`subprocess` (System control)
- **GUI**: `customtkinter` (Modern, responsive UI)
- **Web**: `webbrowser`, `yt-dlp` (YouTube)
- **Cybersecurity**: `psutil` (Monitoring), `socket` (Port scanning localhost)

## 3. Development Phases

### Phase 1: Core Intelligence & Search
- Setup `.env` and `config.py`.
- Implement `core/brain.py` to route prompts to Gemini with the "JARVIS" system instruction.
- Implement `modules/search.py` using Tavily for real-time data fetching.

### Phase 2: Voice & System Control
- Implement `modules/voice.py` for "Hey ARYA" wake-word detection and TTS playback.
- Implement `modules/system.py` to execute tasks like opening Notepad, Chrome, finding files.

### Phase 3: Defensive Cybersecurity Mode
- Implement `modules/cybersec.py` to monitor active processes, scan local network ports, and provide security advice.
- *Note on safety guidelines: ARYA will strictly act as a defensive assistant. Offensive tools (DDoS, exploitation) will not be implemented.*

### Phase 4: Interfaces
- Build `interfaces/cui.py` for terminal-based interaction.
- Build `interfaces/gui.py` using `customtkinter` for a polished visual interface.

### Phase 5: Integration
- Connect the Brain to the dynamic modules (letting Gemini decide when to use a tool via Function Calling).
- Finalize `main.py` to switch between CUI and GUI modes.

### Phase 6: Advanced Next-Gen Capabilities (Current Focus)
### Phase 6: Advanced Next-Gen Capabilities (Complete)
- **Daily Personal Dashboard**: Real-time integration of sensors.
- **Code Copilot Mode**: Secure file-system read/write via AI.
- **Natural Voice Personality**: Dynamic TTS rate shifting based on mood tagging.
- **Smart Reminders**: Asynchronous background threading.
- **Computer Vision**: Spatial bounding box analysis.

### Phase 7: Ultimate 'Life OS' Roadmap (In Progress)
- **Productivity Automation**: Bulk file organization (Downloads cleanup), Macro setup launching.
- **Developer Mode Extension**: Raw CLI Terminal Execution (`run_terminal_command`).
- **Autonomous Agent Patterns**: Looping goal-oriented web research without user interruption.
- **Better Memory Structure**: Moving from string logs to vector graph embeddings.
- **Mobile Companion Sync**: Remote REST APIs to allow off-network pinging of ARYA.
- **Real Product Path**: GUI improvements, install binaries, executable build wrapping without console noise.
