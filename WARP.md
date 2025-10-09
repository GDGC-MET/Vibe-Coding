# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project overview
- Name: ai-vibe-chat (Python, Click-based CLI)
- Purpose: Local, themed chatbot with pluggable Personality and Provider layers. Optional conversation memory persisted to a JSON file.
- Entry points: module runner python -m ai_vibe_chat.cli and console script ai-vibe-chat (via pyproject.toml)

Development commands

Environment setup (Windows PowerShell)
- Create venv and install deps
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1
  - pip install -r requirements.txt
- Optional: editable install to enable the ai-vibe-chat console command
  - pip install -e .

Run the CLI
- Via module
  - python -m ai_vibe_chat.cli --personality rizz
- Via console script (after editable install)
  - ai-vibe-chat --personality sarcastic
- Useful flags (from cli.py)
  - --personality [rizz|sarcastic] (default: rizz)
  - --memory to enable conversation memory (persists conversation_history.json in CWD)
  - --inject-error [startup|personality|provider|response] to simulate failures for testing

Testing
- Run all tests
  - pytest
- Run tests quietly
  - pytest -q
- Run a single test
  - pytest tests/test_engine.py::test_engine_appends_to_history -q
- Notes
  - Tests use pytest and cover Engine behavior, file persistence, and integration across personalities.

Linting and type checking
- Ruff (no repo-specific config; defaults apply)
  - ruff check .
  - ruff check . --fix  # apply autofixes
- MyPy (types in src; stubs for colorama included)
  - mypy src

Packaging (optional)
- Build wheels/sdist using PEP 517
  - pip install build
  - python -m build

High-level architecture

Layers and flow
- CLI (src/ai_vibe_chat/cli.py)
  - Parses flags via Click, sets up colorized I/O, selects a Personality, instantiates a Provider, and constructs Engine(..., memory=...).
  - REPL loop: prompt user → engine.respond(user_text) → print styled reply.
  - Error injection modes are available for testing robustness (--inject-error).

- Engine (src/ai_vibe_chat/engine.py)
  - Contracts: Personality and Provider are Protocols with minimal required methods.
  - respond(user_text):
    - Optionally appends user turn to in-memory history (if memory enabled).
    - personality.style_prompt(user_text) → provider.generate(styled_prompt, history) → personality.style_response(raw)
    - Optionally appends bot turn and persists history.

- Persistence (src/ai_vibe_chat/file_manager.py)
  - ConversationFileManager manages JSON persistence to conversation_history.json in the current working directory by default.
  - Safe writes using .bak and .tmp; truncates if history exceeds max_history_turns.
  - Defensive read handling: returns [] on corrupted/invalid data and logs errors.

- Data model (src/ai_vibe_chat/data_model.py)
  - ConversationTurn dataclass: speaker, text.

- Personalities (src/ai_vibe_chat/personalities)
  - BasePersonality defines pass-through styling methods.
  - RizzPersonality and SarcasticPersonality implement style_prompt/style_response to decorate prompts and responses.
  - Registry: CLI maintains a PERSONALITIES dict mapping flag values to classes. Adding a new personality requires adding an implementation and registering it in cli.PERSONALITIES.

- Providers (src/ai_vibe_chat/providers)
  - BaseProvider declares generate(prompt, history) and raises NotImplementedError by default.
  - LocalRulesProvider: simple regex- and keyword-based generator with a small set of canned responses. Receives history for future extensibility, though current rules do not leverage it deeply.

Tooling and project metadata
- pyproject.toml
  - Project metadata (name, version, dependencies)
  - Console script entry: ai-vibe-chat = ai_vibe_chat.cli:main
  - Setuptools configuration with src layout.
- requirements.txt
  - Runtime: click, colorama
  - Dev: pytest, ruff, mypy, types-colorama (optional extras commented out)
- No pytest.ini or ruff/mypy config files found; defaults are used.

Key behaviors to know
- Memory flag
  - --memory enables persistent conversation history in conversation_history.json in the current working directory. Tests override this path via Engine.file_manager for isolation.
- Error injection flag
  - --inject-error can force failures at key phases (startup/personality/provider/response) to exercise error handling in the CLI and Engine pipeline.

What to read first (for orientation)
- README.md: quickstart, current features, and contribution ideas.
- src/ai_vibe_chat/cli.py: REPL and wiring of personalities/providers.
- src/ai_vibe_chat/engine.py: core orchestration and memory handling.
- src/ai_vibe_chat/providers/local_rules.py and personalities/*: extension points and current behaviors.
- tests/: examples of usage, file persistence behavior, and integration coverage.
