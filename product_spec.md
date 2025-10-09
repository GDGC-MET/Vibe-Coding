roduct Specification: AI Vibe Chat - V1 Prototype
1. Overview & Goal
Product: AI Vibe Chat is a local, personality-driven command-line chatbot.

Goal for V1: To build a working prototype that enhances the chatbot's core functionality by implementing a persistent conversation memory. This serves as the foundational feature for a more interactive and context-aware user experience.

Target Audience: Developers (initially the core project developer) who need a working, stateful base to build upon for future features.

Success Metric: A user can close and restart the chat application using a --memory flag, and the previous conversation history is successfully loaded and appended to.

2. User Flow
The primary user flow revolves around enabling and using the conversation memory feature via a command-line flag.

Scenario 1: Running the Chatbot with Memory Enabled

GIVEN the user has the application installed and a virtual environment is active.

WHEN the user runs the CLI for the first time with the memory flag:

Bash

python -m ai_vibe_chat.cli --personality rizz --memory
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

Bash

python -m ai_vibe_chat.cli --personality rizz --memory
THEN the application loads the existing content from conversation_history.json and is ready to continue the conversation.

3. Technical Requirements & Considerations
Environment Setup: All development must occur within a Python virtual environment (venv). All new dependencies must be added to requirements.txt.

CLI Argument:

Implement a new command-line argument: --memory.

Use the argparse library in cli.py to handle this new flag.

This flag should be a boolean switch; its presence enables the memory feature.

Persistence Layer:

Conversation history must be stored in a simple, human-readable JSON file named conversation_history.json.

The file should be created in the root directory of the project.

The JSON structure should be a list of objects, where each object represents one conversational turn.

Data Schema: [ { "speaker": "user" | "bot", "text": "string" }, ... ]

Example conversation_history.json:

JSON

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
Engine Integration:

The engine.Engine class should be modified to manage the conversation history.

It should handle loading the history from the JSON file upon initialization (if the --memory flag is active).

It should have a method to append new turns to the in-memory history and save the entire history back to the JSON file.

Crucially, the full conversation history object must be passed to the Provider's response generation method. While the current LocalRulesProvider will not use this context, this ensures the architecture is ready for future, more intelligent providers (like a Local LLM).

4. Acceptance Criteria (Definition of Done)
A --memory flag is successfully added to cli.py and is functional.

When the app is run with --memory, it creates a conversation_history.json file in the project root if one does not exist.

Each user input and bot response is correctly appended to the conversation_history.json file as a new object.

When the application is restarted with the --memory flag, the previous conversation is loaded.

The feature is cleanly integrated without breaking the existing --personality functionality.

The README.md is updated to briefly document the new --memory feature and its usage.