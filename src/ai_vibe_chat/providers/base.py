from __future__ import annotations
from ..data_model import ConversationTurn

class BaseProvider:
    """Base provider for response generation.

    Implementations should override generate and may consult history
    for context-aware responses.
    """

    name = "base"

    def generate(self, prompt: str, history: list[ConversationTurn] | None = None) -> str:  # pragma: no cover - intentionally incomplete
        raise NotImplementedError("Providers must implement generate()")
