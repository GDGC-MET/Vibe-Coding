from __future__ import annotations

import random
import re

from .base import BaseProvider


class LocalRulesProvider(BaseProvider):
    name = "local-rules"

    def __init__(self) -> None:
        self._motivation = [
            "Push one more rep. Future you says thanks.",
            "You don't skip leg day, do you?",  # contribution: diversify
            "Consistency beats intensity. Show up.",
        ]

    def generate(self, prompt: str) -> str:
        text = prompt.lower()

        if re.search(r"gym|lift|workout|exercise|fitness", text):
            return random.choice(self._motivation)

        if re.search(r"recursion|recursive", text):
            return "A thing defined in terms of a smaller version of itself."

        if re.search(r"hello|hi|hey", text):
            return "Hey there! What's vibing?"

        # contribution: add more rules, intents, and templates
        return "Tell me more."


