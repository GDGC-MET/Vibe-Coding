from .base import BasePersonality


class RizzPersonality(BasePersonality):
    name = "rizz"

    def style_prompt(self, user_text: str) -> str:
        return f"Spice it up with confidence: {user_text}"

    def style_response(self, provider_text: str) -> str:
        return f"🔥 {provider_text} Stay smooth."


