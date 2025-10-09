class BasePersonality:
    name = "base"

    def style_prompt(self, user_text: str) -> str:
        return user_text

    def style_response(self, provider_text: str) -> str:
        return provider_text


