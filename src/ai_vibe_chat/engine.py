from __future__ import annotations

from typing import Protocol


class Personality(Protocol):
    name: str

    def style_prompt(self, user_text: str) -> str: ...
    def style_response(self, provider_text: str) -> str: ...


class Provider(Protocol):
    name: str

    def generate(self, prompt: str) -> str: ...


class Engine:
    def __init__(self, provider: Provider, personality: Personality) -> None:
        self.provider = provider
        self.personality = personality

    def respond(self, user_text: str) -> str:
        if not user_text.strip():
            return "Say something interesting."

        styled_prompt = self.personality.style_prompt(user_text)
        raw = self.provider.generate(styled_prompt)
        return self.personality.style_response(raw)


