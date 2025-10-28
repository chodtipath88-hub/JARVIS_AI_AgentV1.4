# JARVIS AI Mini (V1.2)

Minimal, reliable web chat powered by your local Ollama model (default: phi3:mini). No V2 code — clean and simple.

## How to run (Windows)

1) Install deps once (PowerShell):
   - pip install -r requirements.txt

2) Start the mini server:
   - double-click start_mini_server.bat
   - Or run: python mini_server.py

3) Open the browser:
   - http://127.0.0.1:5001

## Configure

Use environment variables (batch sets safe defaults):
- OLLAMA_HOST: http://localhost:11434
- OLLAMA_MODEL: phi3:mini
- OLLAMA_TIMEOUT: 120 (read timeout seconds)
- OLLAMA_CONNECT_TIMEOUT: 5 (connect timeout seconds)
- OLLAMA_RETRIES: 2 (retry attempts)

You can also inspect runtime config and health:
- GET /health -> status, models, last_error
- GET /config -> active settings
- GET /api/models -> available Ollama models

## Troubleshooting

- If you see timeouts:
  - Increase OLLAMA_TIMEOUT (e.g., 180) or OLLAMA_RETRIES
  - Ensure Ollama is running: `ollama serve`
  - Pull the model if missing: `ollama pull phi3:mini`
- If port 5001 is busy, stop other servers or change the port in mini_server.py

## Notes

- This V1.2 folder is intentionally decoupled from V2 to avoid conflicts.
- If you also use the full web_server (login/history), run it from the original folder; this mini is standalone.
