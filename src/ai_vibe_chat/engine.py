from __future__ import annotations

from typing import Protocol

from .data_model import ConversationTurn
from .file_manager import ConversationFileManager


class Personality(Protocol):
    name: str

    def style_prompt(self, user_text: str) -> str: ...
    def style_response(self, provider_text: str) -> str: ...


class Provider(Protocol):
    name: str

    def generate(self, prompt: str, history: list[ConversationTurn]) -> str: ...


class Engine:
    """Coordinates the conversation between a Provider and a Personality.

    Responsibilities:
    - Optionally initialize and maintain a conversation history when memory is enabled.
    - Style user prompts and provider responses through the selected Personality.
    - Persist conversation turns via ConversationFileManager when memory is enabled.
    """

    def __init__(self, provider: Provider, personality: Personality, memory: bool = False) -> None:
        """Create an Engine.

        Args:
            provider: Response generator implementation.
            personality: Styling strategy for prompts and responses.
            memory: If True, enable persistent conversation history.
        """
        self.provider = provider
        self.personality = personality
        self.memory_enabled = memory
        self.history: list[ConversationTurn] = []
        self.file_manager = ConversationFileManager() if self.memory_enabled else None

        # Load existing history on startup if memory is enabled
        if self.memory_enabled and self.file_manager:
            self.history = self.file_manager.load_history()

    def respond(self, user_text: str) -> str:
        """Generate a response to user_text, updating history if enabled.

        Returns a user-friendly fallback if user_text is blank.
        """
        if not user_text.strip():
            return "Say something interesting."

        styled_prompt = self.personality.style_prompt(user_text)
        raw = self.provider.generate(styled_prompt, history=self.history)
        response = self.personality.style_response(raw)

        if self.memory_enabled:
            self.history.append(ConversationTurn(speaker="user", text=user_text))
            self.history.append(ConversationTurn(speaker="bot", text=response))
            if self.file_manager:
                self.file_manager.save_history(self.history)

        return response
