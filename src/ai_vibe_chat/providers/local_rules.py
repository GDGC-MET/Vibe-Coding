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
        
        self._emoji_keywords = {
            "happy": ["😄", "😊", "😃", "😁", "🥳"],
            "sad": ["😢", "😭", "😔", "😞", "💔"],
            "angry": ["😡", "😠", "🤬", "😤", "💢"],
            "love": ["❤️", "💕", "💖", "💗", "😍"],
            "excited": ["🤩", "😆", "🎉", "✨", "🌟"],
            "confused": ["😕", "🤔", "😵", "😶", "🤷"],
            "tired": ["😴", "😪", "🥱", "😑", "😐"],
            "surprised": ["😲", "😮", "😯", "🤯", "😱"],
            "cool": ["😎", "🤘", "🔥", "💯", "✨"],
            "thinking": ["🤔", "💭", "🧠", "🤓", "📚"]
        }

    def _detect_emoji(self, text: str) -> str:
        """Detect keywords and return appropriate emoji."""
        text_lower = text.lower()
        
        for emotion, emojis in self._emoji_keywords.items():
            if emotion in text_lower:
                return random.choice(emojis)
        
        return ""

    def generate(self, prompt: str) -> str:
        text = prompt.lower()
        
        # Detect emoji based on keywords
        emoji = self._detect_emoji(prompt)

        if re.search(r"gym|lift|workout|exercise|fitness", text):
            response = random.choice(self._motivation)
            return f"{response} {emoji}" if emoji else response

        if re.search(r"recursion|recursive", text):
            response = "A thing defined in terms of a smaller version of itself."
            return f"{response} {emoji}" if emoji else response

        if re.search(r"hello|hi|hey", text):
            response = "Hey there! What's vibing?"
            return f"{response} {emoji}" if emoji else response

        # contribution: add more rules, intents, and templates
        response = "Tell me more."
        return f"{response} {emoji}" if emoji else response


