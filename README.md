AI VIBE CHAT / Personality Bot — Full Project Guide

Overview
- A local-first chatbot with pluggable “Personalities” (rizz, sarcastic, …) and “Providers” (local rules, Perplexity, Gemini) wrapped by a simple Engine and exposed via:
  - CLI for quick REPL
  - Flask web server with JSON API
  - Production-ready React (Vite + TypeScript) frontend that talks to the JSON API
- Security-conscious: API keys live only on the backend (.env), never in the browser.

Key Features
- Personality + Provider pipeline coordinated by an Engine
- Providers: local-rules (no API), Perplexity, Gemini (Google Generative AI)
- Personalities: rizz, sarcastic (easy to extend)
- Optional conversation memory persisted to disk
- Web JSON API + modern React UI (dev proxy + production build served by Flask)

Architecture
- Backend (Flask, Python)
  - webapp.py: Flask app exposing HTML + JSON API, loads .env and serves the built frontend
  - engine.py: Orchestrates Provider and Personality, handles optional memory persistence
  - providers/: LocalRulesProvider, PerplexityProvider, GeminiProvider
  - personalities/: RizzPersonality, SarcasticPersonality
  - file_manager.py: manages conversation_history.json when memory is enabled
  - data_model.py: ConversationTurn dataclass
- Frontend (Vite + React + TypeScript)
  - src/components: Settings panel and Chat UI
  - Uses /api endpoints via axios, no secrets in client

Directory Layout
```text path=null start=null
AI-VIBE-CHAT-Personality-Bot--Vibe-Coding/
  requirements.txt
  pyproject.toml
  README.md   <— this file
  src/
    ai_vibe_chat/
      __init__.py
      cli.py
      engine.py
      data_model.py
      file_manager.py
      webapp.py
      personalities/
        __init__.py
        base.py
        rizz.py
        sarcastic.py
      providers/
        __init__.py
        base.py
        local_rules.py
        perplexity.py
        gemini.py
  frontend/
    package.json
    tsconfig.json
    vite.config.ts
    index.html
    src/
      main.tsx
      App.tsx
      api.ts
      types.ts
      components/
        Chat.tsx
        Settings.tsx
      styles.css
```

Backend: Setup and Run
Prerequisites
- Python 3.11+ (3.12 recommended)
- Windows PowerShell or any shell

Install dependencies
```powershell path=null start=null
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Environment variables (.env supported)
- Create a .env file in the project root if you prefer not to export variables in the shell.
- Gemini (recommended):
```text path=null start=null
GEMINI_API_KEY=your-api-key
# optional
GEMINI_MODEL=gemini-1.5-flash
```
- Alternatively use GOOGLE_API_KEY as the key variable name.
- Perplexity (optional):
```text path=null start=null
PERPLEXITY_API_KEY=your-api-key
PERPLEXITY_MODEL=llama-3.1-mini
```

Run the backend (Flask web server)
```powershell path=null start=null
# from project root
python -m ai_vibe_chat.webapp
# then open http://127.0.0.1:5000
```
- PORT can be customized via PORT env var.
- The server auto-loads .env at startup.

Backend: JSON API
- Base URL: http://127.0.0.1:5000/api
- Endpoints:
  - GET /settings → current configuration and available options
  - POST /settings → apply { personality?, provider?, memory? }
  - POST /chat → send { text } and receive { reply }

Example requests
```bash path=null start=null
# get settings
curl http://127.0.0.1:5000/api/settings

# update settings
curl -X POST http://127.0.0.1:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"personality":"rizz","provider":"gemini","memory":true}'

# chat
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello!"}'
```

Providers
- local-rules: built-in, no keys needed
- perplexity: requires PERPLEXITY_API_KEY
- gemini: requires GEMINI_API_KEY or GOOGLE_API_KEY; optional GEMINI_MODEL (default: gemini-1.5-flash)

Personalities
- rizz: playful, confident
- sarcastic: witty, dry
- How to add your own: create a new file under src/ai_vibe_chat/personalities/ implementing style_prompt and style_response, then register it.

Memory Persistence
- Enable memory via CLI flag --memory or by toggling in the frontend settings
- When enabled, conversation_history.json is created in the current working directory; a .bak is used for resilience

CLI Usage (optional)
```powershell path=null start=null
# basic
python -m ai_vibe_chat.cli --personality rizz

# with memory
python -m ai_vibe_chat.cli --personality rizz --memory

# choose provider
python -m ai_vibe_chat.cli --personality rizz --provider gemini
```

Frontend: Setup and Run
Prerequisites
- Node.js 18+ and npm

Install and run in dev
```powershell path=null start=null
cd frontend
npm install
npm run dev
# open http://localhost:5173
```
- The dev server proxies /api to http://127.0.0.1:5000.
- You can override the API base with VITE_API_BASE if needed.

Build for production
```powershell path=null start=null
cd frontend
npm run build
# creates frontend/dist
```
- When frontend/dist exists, the Flask app will serve it automatically at /.

Security Notes
- Do not expose API keys in the frontend or commit them to git.
- Keep keys in .env (loaded server-side) or your process environment.
- The browser talks only to your backend; the backend talks to Gemini/Perplexity.

Testing and Quality
```powershell path=null start=null
# Python tests
pytest

# Linting / type checking
ruff .
mypy .
```

Deployment (basic guidance)
- Small deployments can use the built-in Flask server for local/network testing.
- For production, consider running behind a proper HTTP server (e.g., nginx) and a WSGI server (gunicorn/uwsgi on Linux). On Windows, consider waitress.
- Ensure .env or environment variables are configured in your host environment.

Troubleshooting
- Python opens Microsoft Store on Windows: disable App execution aliases or install Python via winget.
```powershell path=null start=null
winget install --id Python.Python.3.12 -e
```
- Cannot find API key: ensure GEMINI_API_KEY or GOOGLE_API_KEY is present in your environment or .env.
- File permission errors: make sure the working directory is writable for conversation_history.json when memory is enabled.

Roadmap Ideas
- Advanced memory (summarization, multi-session)
- More personalities and dynamic discovery
- Provider options (temperature, top_p, system prompts)
- TTS/Speech I/O
- In-app help commands

Contributing
- Fork the repo, create a feature branch, keep PRs focused, add tests when reasonable, and describe how to test your change.

License
MIT

