from __future__ import annotations

import os
from pathlib import Path
from flask import Flask, request, redirect, url_for, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from .engine import Engine
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider
try:
    from .providers import PerplexityProvider
except Exception:  # pragma: no cover
    PerplexityProvider = None  # type: ignore

try:
    from .providers.gemini import GeminiProvider
except Exception:  # pragma: no cover
    GeminiProvider = None  # type: ignore

# Load environment variables (e.g., GEMINI_API_KEY) from .env if present
load_dotenv()

# Attempt to serve built frontend if available
_FE_DIST = (Path(__file__).resolve().parents[2] / "frontend" / "dist")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

PERSONALITIES = {
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}

DEFAULT_PROVIDER = "local-rules"

# Simple in-process engine instance; rebuilt when options change
_engine: Engine | None = None
_current_personality = "rizz"
_current_provider = DEFAULT_PROVIDER
_memory_enabled = False

def build_engine() -> Engine:
    global _engine
    PersonalityCls = PERSONALITIES[_current_personality]

    provider_name = _current_provider
    provider = None

    # Provider resolution with fallbacks
    if provider_name == "gemini" and GeminiProvider is not None:
        provider = GeminiProvider()
    elif provider_name == "perplexity" and PerplexityProvider is not None:
        provider = PerplexityProvider()
    else:
        provider = LocalRulesProvider()

    _engine = Engine(provider=provider, personality=PersonalityCls(), memory=_memory_enabled)
    return _engine


def html_page(body: str) -> str:
    return f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>AI Vibe Chat</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }}
    .row {{ margin: 0.5rem 0; }}
    textarea {{ width: 100%; height: 200px; }}
    input[type=text] {{ width: 100%; }}
    .msg {{ border-bottom: 1px solid #eee; padding: 0.25rem 0; }}
    .you {{ color: #0aa; }}
    .bot {{ color: #a0a; }}
  </style>
</head>
<body>
  <h1>AI Vibe Chat 🌀</h1>
  {body}
</body>
</html>
"""


def settings_form(error_msg: str | None = None) -> str:
    err = f"<div style='color:#b00'>{error_msg}</div>" if error_msg else ""
    return html_page(f"""
  {err}
  <form method=\"post\" action=\"{url_for('configure')}\">
    <div class=\"row\">
      <label>Personality:&nbsp;
        <select name=\"personality\">
          <option value=\"rizz\" {'selected' if _current_personality=='rizz' else ''}>rizz</option>
          <option value=\"sarcastic\" {'selected' if _current_personality=='sarcastic' else ''}>sarcastic</option>
        </select>
      </label>
    </div>
    <div class=\"row\">
      <label>Provider:&nbsp;
        <select name=\"provider\">
          <option value=\"local-rules\" {'selected' if _current_provider=='local-rules' else ''}>local-rules</option>
          <option value=\"perplexity\" {'selected' if _current_provider=='perplexity' else ''}>perplexity</option>
          <option value=\"gemini\" {'selected' if _current_provider=='gemini' else ''}>gemini</option>
        </select>
      </label>
    </div>
    <div class=\"row\">
      <label><input type=\"checkbox\" name=\"memory\" value=\"1\" {'checked' if _memory_enabled else ''}/> Memory</label>
    </div>
    <div class=\"row\">
      <button type=\"submit\">Apply</button>
    </div>
  </form>
  <hr />
  <form method=\"post\" action=\"{url_for('chat')}\">
    <div class=\"row\"><input type=\"text\" name=\"text\" placeholder=\"Type a message...\" /></div>
    <div class=\"row\"><button type=\"submit\">Send</button></div>
  </form>
  <div class=\"row\"><a href=\"{url_for('index')}\">Refresh</a></div>
""")


@app.get("/")
def index():
    # If a built frontend exists, serve it as the main UI
    if _FE_DIST.exists():
        return send_from_directory(_FE_DIST, "index.html")
    return settings_form()


@app.post("/configure")
def configure():
    global _current_personality, _current_provider, _memory_enabled
    _current_personality = request.form.get("personality", "rizz")
    _current_provider = request.form.get("provider", DEFAULT_PROVIDER)
    _memory_enabled = bool(request.form.get("memory"))
    try:
        build_engine()
        return redirect(url_for("index"))
    except Exception as e:
        return settings_form(str(e))


@app.post("/chat")
def chat():
    if _engine is None:
        build_engine()
    text = (request.form.get("text") or "").strip()
    if not text:
        return redirect(url_for("index"))
    try:
        reply = _engine.respond(text)  # type: ignore[union-attr]
        body = f"<div class='msg you'>You: {text}</div><div class='msg bot'>Bot: {reply}</div>" + settings_form()
        return body
    except Exception as e:
        return settings_form(str(e))


# -------- JSON API for production frontend --------
@app.get("/api/settings")
def api_get_settings():
    return jsonify({
        "personalities": list(PERSONALITIES.keys()),
        "providers": [p for p in ["local-rules", "perplexity", "gemini"] if (
            (p == "perplexity" and PerplexityProvider is not None) or
            (p == "gemini" and GeminiProvider is not None) or
            (p == "local-rules")
        )],
        "current": {
            "personality": _current_personality,
            "provider": _current_provider,
            "memory": _memory_enabled,
        },
    })


@app.post("/api/settings")
def api_set_settings():
    global _current_personality, _current_provider, _memory_enabled
    data = request.get_json(silent=True) or {}
    personality = data.get("personality", _current_personality)
    provider = data.get("provider", _current_provider)
    memory = bool(data.get("memory", _memory_enabled))

    if personality not in PERSONALITIES:
        return jsonify({"error": f"Unknown personality: {personality}"}), 400

    valid_providers = ["local-rules"]
    if PerplexityProvider is not None:
        valid_providers.append("perplexity")
    if GeminiProvider is not None:
        valid_providers.append("gemini")

    if provider not in valid_providers:
        return jsonify({"error": f"Unknown or unavailable provider: {provider}"}), 400

    _current_personality = personality
    _current_provider = provider
    _memory_enabled = memory

    try:
        build_engine()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"ok": True, "current": {
        "personality": _current_personality,
        "provider": _current_provider,
        "memory": _memory_enabled,
    }})


@app.post("/api/chat")
def api_chat():
    if _engine is None:
        build_engine()
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400
    try:
        reply = _engine.respond(text)  # type: ignore[union-attr]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Static asset serving for built frontend
if _FE_DIST.exists():
    @app.get("/assets/<path:filename>")
    def assets(filename: str):
        assets_dir = _FE_DIST / "assets"
        return send_from_directory(assets_dir, filename)


def main() -> None:
    # Host locally; user can set PORT env if desired
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
