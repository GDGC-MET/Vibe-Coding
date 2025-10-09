class BasePersonality:
    """Base personality that performs no styling.

    Subclasses should override style_prompt and style_response to modify
    how user prompts are sent to the provider and how provider responses
    are presented to the user.
    """

    name = "base"

    def style_prompt(self, user_text: str) -> str:
        """Decorate or transform the user's input prior to generation."""
        return user_text

    def style_response(self, provider_text: str) -> str:
        """Decorate or transform the provider's raw output for display."""
        return provider_text

