# ai_vibe_chat/personalities/rizz.py
import random

class RizzPersonality:
    name = "rizz"

    def style_prompt(self, user_text: str) -> str:
        return f"🔥 {user_text} Stay smooth."

    def style_response(self, provider_text: str, category: str = "general") -> str:
        variations = [
            provider_text,
            f"{provider_text} 😉",
            f"{provider_text} 😎",
            f"{provider_text} Stay vibing!"
        ]
        text = random.choice(variations)

        if category == "greeting":
            return f"😎 {text} What's good?"
        elif category == "motivation":
            return f"💪 {text} Keep grinding, champ!"
        elif category == "technical":
            return f"💻 {text} Nerd mode activated!"
        elif category == "joke":
            return f"😂 {text} Can't stop laughing!"
        elif category == "advice":
            return f"🧠 {text} Wise words, my friend."
        else:
            return f"🔥 {text} Stay smooth, my friend!"


