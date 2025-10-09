from .base import BasePersonality
import random

class WholesomePersonality(BasePersonality):
    name = "wholesome"

    def transform(self, message: str) -> str:
        responses = [
            "You're doing amazing today! 💖",
            "Take a deep breath, everything is going great 🌸",
            "Every line of code you write matters! Keep going 💪",
            "Believe in yourself, you've got this 🌈",
            "You're capable of more than you think! ✨",
            "Keep smiling, your vibe is contagious 😄",
            "Small steps every day lead to big wins! 🌟",
            "You got this! Stay awesome 💖"
        ]
        return random.choice(responses)
