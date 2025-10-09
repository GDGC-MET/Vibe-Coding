from unittest.mock import MagicMock, patch

import pytest
from ai_vibe_chat.data_model import ConversationTurn
from ai_vibe_chat.engine import Engine, Personality, Provider


@pytest.fixture
def mock_provider() -> MagicMock:
    return MagicMock(spec=Provider)


@pytest.fixture
def mock_personality() -> MagicMock:
    return MagicMock(spec=Personality)


@pytest.fixture
def sample_history() -> list[ConversationTurn]:
    return [
        ConversationTurn("user", "Hello"),
        ConversationTurn("bot", "Hi there!"),
    ]


def test_engine_initialization_with_history(mock_provider, mock_personality, sample_history):
    with patch("ai_vibe_chat.engine.ConversationFileManager") as mock_file_manager:
        mock_file_manager.return_value.load_history.return_value = sample_history
        engine = Engine(provider=mock_provider, personality=mock_personality, memory=True)
        assert engine.history == sample_history
        mock_file_manager.return_value.load_history.assert_called_once()


def test_engine_appends_to_history(mock_provider, mock_personality):
    with patch("ai_vibe_chat.engine.ConversationFileManager") as mock_file_manager:
        mock_file_manager.return_value.load_history.return_value = []
        engine = Engine(provider=mock_provider, personality=mock_personality, memory=True)

        mock_provider.generate.return_value = "I am a bot."
        mock_personality.style_prompt.return_value = "user: Hi"
        mock_personality.style_response.return_value = "Bot: I am a bot."

        engine.respond("Hi")

        assert len(engine.history) == 2
        assert engine.history[0].speaker == "user"
        assert engine.history[0].text == "Hi"
        assert engine.history[1].speaker == "bot"
        assert engine.history[1].text == "Bot: I am a bot."
        mock_file_manager.return_value.save_history.assert_called_once_with(engine.history)
