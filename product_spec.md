# Product Specification: AI Vibe Chat - V1 Prototype
## 1. Overview & Goal
Product: AI Vibe Chat is a local, personality-driven command-line chatbot.

Goal for V1: To build a working prototype that enhances the chatbot's core functionality by implementing a persistent conversation memory. This serves as the foundational feature for a more interactive and context-aware user experience.

Target Audience: Developers (initially the core project developer) who need a working, stateful base to build upon for future features.

Success Metric: A user can close and restart the chat application using a --memory flag, and the previous conversation history is successfully loaded and appended to.

## 2. User Flow
The primary user flow revolves around enabling and using the conversation memory feature via a command-line flag.

Scenario 1: Running the Chatbot with Memory Enabled

GIVEN the user has the application installed and a virtual environment is active.

WHEN the user runs the CLI for the first time with the memory flag:

Shell

```
python -m ai_vibe_chat.cli --personality rizz --memory
```
THEN the application starts and checks for a conversation_history.json file. Since it doesn't exist, it creates an empty one.

AND the user engages in a conversation (e.g., two exchanges).

You: give me gym motivation

Bot: Bro, those weights aren’t gonna lift themselves. One more set. Own it.

You: what about focus?

Bot: Lock in. Zone out everything else. It's just you and the iron.

THEN each conversational turn (both user input and bot output) is appended to the conversation_history.json file in real-time or upon exit.

WHEN the user quits the application (e.g., using CTRL+C).

THEN the application closes, and the conversation_history.json file contains the full conversation.

WHEN the user restarts the application using the same command:

Shell

```
python -m ai_vibe_chat.cli --personality rizz --memory
```
THEN the application loads the existing content from conversation_history.json and is ready to continue the conversation.

## 3. Technical Requirements & Considerations
Environment Setup: All development must occur within a Python virtual environment (venv). All new dependencies must be added to requirements.txt.

CLI Argument:

Implement a new command-line argument: --memory.

Use Click (already in use in cli.py) to handle this new flag via @click.option.

This flag should be a boolean switch; its presence enables the memory feature.

Persistence Layer:

Conversation history must be stored in a simple, human-readable JSON file named conversation_history.json.

The file should be created in the current working directory (typically the project root when running from there).

The JSON structure should be a list of objects, where each object represents one conversational turn.

Data Schema: [ { "speaker": "user" | "bot", "text": "string" }, ... ]

Example conversation_history.json:

```json
[
  {
    "speaker": "user",
    "text": "give me gym motivation"
  },
  {
    "speaker": "bot",
    "text": "Bro, those weights aren’t gonna lift themselves. One more set. Own it."
  }
]
```
### Engine Integration:

The engine.Engine class should be modified to manage the conversation history.

It should handle loading the history from the JSON file upon initialization (if the --memory flag is active).

It should have a method to append new turns to the in-memory history and save the entire history back to the JSON file.

Crucially, the full conversation history object must be passed to the Provider's response generation method. While the current LocalRulesProvider will not use this context, this ensures the architecture is ready for future, more intelligent providers (like a Local LLM).

## 4. Acceptance Criteria (Definition of Done)
A --memory flag is successfully added to cli.py and is functional.

When the app is run with --memory, it creates a conversation_history.json file in the current working directory if one does not exist.

Each user input and bot response is correctly appended to the conversation_history.json file as a new object.

When the application is restarted with the --memory flag, the previous conversation is loaded.

The feature is cleanly integrated without breaking the existing --personality functionality.

The README.md is updated to briefly document the new --memory feature and its usage.

---

## V2: Perplexity API Integration

### 1. Overview & Goal

**Goal for V2:** To integrate the Perplexity API as a new provider, allowing the chatbot to generate more intelligent and context-aware responses.

**Success Metric:** A user can run the chatbot with `--provider perplexity` and have a conversation powered by the Perplexity API.

### 2. Providers

The chatbot uses a provider to generate responses. The provider can be selected using the `--provider` command-line argument.

#### LocalRulesProvider (default)

This is the default provider. It uses a simple set of rules to generate responses based on keywords in the user's input. It is not very intelligent and is mainly used for testing and demonstration purposes.

#### PerplexityProvider

This provider uses the Perplexity API to generate responses. It is much more intelligent than the `LocalRulesProvider` and can generate more context-aware and human-like responses.

To use this provider, you need to have a Perplexity API key.

### 3. Configuration

#### Perplexity API Key

To use the `PerplexityProvider`, you need to set the `PERPLEXITY_API_KEY` environment variable to your Perplexity API key.

You can set the environment variable in your shell before launching the app, for example on PowerShell:

```
$env:PERPLEXITY_API_KEY = "your-api-key"
```

If you prefer a .env file, ensure the application loads it (e.g., via python-dotenv) before relying on it. Also add `.env` to `.gitignore` to avoid committing secrets.

### 4. CLI Argument and Model Selection

Implement a new command-line argument: `--provider`.

-   Use Click to handle this new flag via `@click.option`.
-   The default value should be `local-rules`.
-   The available options should be `local-rules` and `perplexity`.

Models

-   Perplexity requires using a permitted model identifier from their documentation.
-   Make the model configurable (e.g., via an environment variable like `PERPLEXITY_MODEL`).
-   If an invalid model is used, the API will return 4xx with details; select a permitted model from the docs.

### 5. Technical Requirements & Considerations

-   **New Dependency:** Add the `requests` library to `requirements.txt` to make HTTP requests to the Perplexity API.
-   **New Provider:** Create a new `PerplexityProvider` class in `src/ai_vibe_chat/providers/perplexity.py`.
-   **API Key Handling:** Use the `os` module to get the `PERPLEXITY_API_KEY` from the environment variables.
-   **Error Handling:** Handle potential errors from the Perplexity API, such as network errors or invalid API key errors.


Note: Ensure the configured model is permitted by Perplexity. If you encounter a 400 Bad Request indicating an invalid model, update the model configuration (e.g., `PERPLEXITY_MODEL`) to a permitted value per the documentation.



Of course. You need a formal, structured specification for Phase 2 that follows the same format as Phase 1, incorporates a fix for the current error, and covers all the remaining features from the README.

Here is the complete and proper spec.md for Phase 2.

Product Specification: AI Vibe Chat - Phase 2
Prerequisite: Fixing the Perplexity API Error
Before starting Phase 2 development, the existing V1 implementation must be corrected.

Problem: The application fails with a 400 Bad Request error when using the Perplexity provider.

Root Cause: The hardcoded model name llama-3.1-sonar-small-128k-online is not a valid model identifier for the Perplexity API.

Immediate Solution:

Open the provider file: src/ai_vibe_chat/providers/perplexity.py.

Locate the line where the model is defined.

Replace the incorrect model name with a valid one.

Python

# BEFORE
model="llama-3.1-sonar-small-128k-online"

# AFTER
model="llama-3-sonar-small-32k-online"
1. Overview & Goal for Phase 2
Goal for Phase 2: To evolve the V1 prototype into a feature-rich, configurable, and user-friendly application that fulfills the original project vision. This phase will focus on making the application production-ready by implementing a robust configuration system and adding all remaining features from the project README.

Phase 2 will be broken down into the following feature epics:

Epic 2.1: Production-Ready Configuration (YAML/TOML Support)

Epic 2.2: Dynamic Module System (Personalities & Providers)

Epic 2.3: Enhanced User Experience (UX Polish)

Epic 2.4: Advanced I/O (Text-to-Speech)

Epic 2.5: Smarter Local Provider (Improved Rule Engine)

Epic 2.1: Production-Ready Configuration
Goal: Replace environment variables with a user-friendly config.yaml file for better security, shareability, and ease of use.

User Flow
Scenario 1: First-Time User

GIVEN a user runs the app for the first time.

WHEN the application cannot find a config.yaml file.

THEN it creates config.yaml.example and prints a message instructing the user to copy it to config.yaml and add their API key. The app then exits gracefully.

Scenario 2: Configured User

GIVEN a user has created and populated config.yaml.

WHEN they run the application.

THEN the app loads all settings (API keys, model names) from the file and functions correctly.

Technical Requirements
Dependency: Add PyYAML to requirements.txt.

Security: config.yaml must be added to .gitignore.

Implementation: Create a ConfigManager module to handle loading and validating the config. Refactor providers to receive settings from the manager instead of using hardcoded values or environment variables.

Schema (config.yaml.example):

YAML

# Configuration for AI Vibe Chat
# Copy this to config.yaml and fill in your API key.
perplexity:
  api_key: "YOUR_PPLX_API_KEY"
  model_name: "llama-3-sonar-small-32k-online"
Acceptance Criteria
The app loads settings from config.yaml.

If the config is missing, an example is created, and the user is notified.

config.yaml is in .gitignore.

No secrets or keys are hardcoded in the Python source code.

Epic 2.2: Dynamic Module System
Goal: Make the application automatically discover personalities and providers, making it easily extensible for contributors.

User Flow
Scenario 1: Discovering Modules

WHEN a user runs python -m ai_vibe_chat.cli --list-personalities.

THEN the console prints a list of all available personalities (e.g., rizz, sarcastic, pirate).

Scenario 2: Selecting a Provider

WHEN a user runs python -m ai_vibe_chat.cli --provider perplexity.

THEN the Engine initializes and uses the PerplexityProvider instead of the default LocalRulesProvider.

Technical Requirements
CLI: Add new Click options: --provider <name>, --list-personalities, and --list-providers.

Discovery: Implement logic that scans the src/ai_vibe_chat/personalities and src/ai_vibe_chat/providers directories on startup to build a registry of available modules.

Engine: The Engine must be updated to use the registry to select the appropriate personality and provider classes based on the user's CLI input.

Acceptance Criteria
New .py files dropped into the personalities or providers folders are automatically available for use without code changes to the engine.

The --list- commands accurately display all discovered modules.

The --provider flag successfully switches the response generation logic.

Epic 2.3: Enhanced User Experience (UX)
Goal: Improve the command-line interface with in-app commands and better visual formatting.

User Flow
Scenario 1: Using Commands

GIVEN the user is in a chat session.

WHEN they type /clear and press Enter.

THEN the current session's conversation history is erased, and the screen is cleared.

Scenario 2: Visuals

GIVEN the user is in a chat session.

THEN their input is displayed in one color (e.g., green), and the bot's response is in another (e.g., blue), with timestamps.

Technical Requirements
Dependency: Add rich to requirements.txt for colored and formatted output.

REPL (Read-Eval-Print Loop): The main loop in cli.py must be updated to parse user input. If the input starts with /, it should be treated as a command; otherwise, it's treated as a prompt for the bot.

Commands to Implement:

/help: Prints a list of available commands.

/clear: Clears the terminal and the in-memory conversation history.

/save: Saves the current conversation to a text file (e.g., chatlog-YYYY-MM-DD.txt).

/load: (Optional) Loads a previously saved chat log into memory.

Acceptance Criteria
All specified slash commands (/help, /clear, /save) are functional.

Chat output is color-coded for speakers (user vs. bot).

Timestamps are displayed for each message.

Epic 2.4: Advanced I/O (Text-to-Speech)
Goal: Add an optional feature to speak the bot's responses aloud.

User Flow
GIVEN a user wants audible responses.

WHEN they launch the app with the --speak flag: python -m ai_vibe_chat.cli --speak.

THEN after the bot generates a text response, the application plays it as audio through the user's speakers.

Technical Requirements
Dependencies: Add a TTS library like gTTS (and a player like playsound) or pyttsx3 to requirements.txt.

CLI: Implement a new boolean flag: --speak.

Implementation: In the main REPL, after a response is received from the engine but before it is printed to the console, check if the --speak flag is active. If so, pass the response text to the TTS engine.

Acceptance Criteria
The --speak flag successfully enables/disables audio output.

The bot's text responses are converted to speech and played back clearly.

Epic 2.5: Smarter Local Provider
Goal: Improve the default LocalRulesProvider to be more interactive and less repetitive, providing a better offline experience.

Technical Requirements
No new user flow, only backend logic.

Refactor LocalRulesProvider:

Move away from simple if "keyword" in text: logic.

Implement a more robust system using regular expressions (regex) to identify user intents.

Use a dictionary or JSON file to map intents and keywords to a list of possible templated responses. This allows for variety.

Example: { "intent": "ask_motivation", "keywords": ["gym", "motivation", "lift"], "responses": ["Those weights won't lift themselves.", "One more set. You got this!"] }.

Add "Small Talk": Implement responses for common greetings (hello, how are you?) and farewells (bye, quit).

Acceptance Criteria
The LocalRulesProvider can handle a wider range of inputs beyond the original examples.

For the same input, the provider can give varied responses instead of always the same one.

The provider can respond to basic greetings and small talk.


How to use in PowerShell (Windows)
•  Editable install (optional but recommended for console scripts):
◦  pip install -e .
•  Run CLI
◦  Default provider (local-rules):
▪  python -m ai_vibe_chat.cli --personality rizz
◦  With memory:
▪  python -m ai_vibe_chat.cli --personality rizz --memory
◦  Perplexity provider:
▪  $env:PERPLEXITY_API_KEY = "your-api-key"
▪  $env:PERPLEXITY_MODEL = "llama-3.1-mini"  (example; pick a permitted model)
▪  python -m ai_vibe_chat.cli --personality rizz --provider perplexity
•  Run GUI
◦  ai-vibe-chat-gui
◦  Or:
▪  python -m ai_vibe_chat.gui
