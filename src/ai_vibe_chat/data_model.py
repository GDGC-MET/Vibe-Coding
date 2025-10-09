from dataclasses import dataclass

@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    speaker: str
    text: str
