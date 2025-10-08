from .base import BasePersonality


class SarcasticPersonality(BasePersonality):
    name = "sarcastic"

    def style_prompt(self, user_text: str) -> str:
        return f"Obviously, the user said: {user_text}. Make it sound clever."

    def style_response(self, provider_text: str) -> str:
        return f"Sure, because that was super hard: {provider_text} 🙃"


