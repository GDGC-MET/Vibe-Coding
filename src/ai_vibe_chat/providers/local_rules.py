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

        if re.search(r"how are you|how are u|how r u", text):
            return "I'm doing great! How about you?"

        if re.search(r"what.*name|who.*you", text):
            return "I'm your AI chat buddy! What's your name?"

        if re.search(r"prime.*minister|politics|government", text):
            return "That's interesting! Politics can be quite complex. What do you think about current events?"

        if re.search(r"good|great|awesome|amazing", text):
            return "That's awesome! I love the positive vibes!"

        # contribution: add more rules, intents, and templates
        return "That's interesting! Tell me more about that."


