from __future__ import annotations
import logging
from typing import Protocol

# Set up logging
logger = logging.getLogger(__name__)

class Personality(Protocol):
    name: str
    def style_prompt(self, user_text: str) -> str: ...
    def style_response(self, provider_text: str) -> str: ...

class BasePersonality:
    """Base personality with input validation and logging."""
    
    name = "base"

    def style_prompt(self, user_text: str) -> str:
        """Style user prompt with validation."""
        if not isinstance(user_text, str):
            logger.warning(f"Non-string user_text received: {type(user_text)}")
            user_text = str(user_text)
        
        if not user_text.strip():
            logger.debug("Empty user input received")
            return user_text
            
        logger.debug(f"Styling prompt: {user_text[:50]}...")
        return user_text

    def style_response(self, provider_text: str) -> str:
        """Style provider response with validation."""
        if not isinstance(provider_text, str):
            logger.warning(f"Non-string provider_text received: {type(provider_text)}")
            provider_text = str(provider_text)
        
        if not provider_text.strip():
            logger.warning("Empty provider response received")
            return "I'm not sure how to respond to that."
            
        logger.debug(f"Styling response: {provider_text[:50]}...")
        return provider_text

    def __str__(self) -> str:
        return f"Personality(name={self.name})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    # Ai promed: add a functionality of login in base.py