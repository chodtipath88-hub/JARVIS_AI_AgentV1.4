# Changelog

All notable changes to this project will be documented in this file.

## 2025-10-28

### Added
- New Streamlit desktop app: `desktop_app_streamlit.py` with chat, model selection, stats.
- New PyQt5 desktop app: `desktop_app_pyqt5.py` with ChatGPT-like bubbles and workflow logging.
- Batch launchers:
  - `start_desktop_streamlit.bat`
  - `start_desktop_pyqt5.bat`
- Web diagnostics endpoints:
  - `GET /health` – system status (Ollama/models/DB)
  - `GET /config` – runtime configuration
- Web user registration: `POST /register` (JSON: username, password, email)
- Registration UI in `jarvis_unified.html` with toggle (login/register)

### Changed
- `web_server.py`: root serves `jarvis_unified.html` by default; Socket.IO connect accepts `auth.session_id`.
- `jarvis_unified.html`: fixed socket event names, added logout call, file:// warning, and auth via Socket.IO.
- `ai_agent.py`: made SQLite connection thread-safe (`check_same_thread=False`) and added a DB lock; wrapped `process_request` with robust error handling; best-effort logging.
- `.github/copilot-instructions.md`: updated to reflect V1.2 architecture and workflows.
- `requirements.txt`: added `streamlit` and `PyQt5`.

### Fixed
- Prevented backend 500 errors on AI processing by handling exceptions in `process_request`.
- Resolved "SQLite objects created in a thread..." by enabling cross-thread access and using a lock.

### Notes
- Streamlit opens in the browser by design at `http://localhost:8501`. For a native window, use the PyQt5 app or Tkinter (`Local_AI_Agent_main.py`).
