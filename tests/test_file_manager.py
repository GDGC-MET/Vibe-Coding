import json
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest
from ai_vibe_chat.data_model import ConversationTurn
from ai_vibe_chat.file_manager import ConversationFileManager


@pytest.fixture
def history_file(tmp_path: Path) -> Path:
    return tmp_path / "conversation_history.json"


@pytest.fixture
def sample_history() -> List[ConversationTurn]:
    return [
        ConversationTurn("user", "Hello"),
        ConversationTurn("bot", "Hi there!"),
    ]


def test_save_history(history_file: Path, sample_history: List[ConversationTurn]):
    file_manager = ConversationFileManager(history_file)
    file_manager.save_history(sample_history)

    assert history_file.exists()
    with open(history_file, "r") as f:
        data = json.load(f)
        assert data == [
            {"speaker": "user", "text": "Hello"},
            {"speaker": "bot", "text": "Hi there!"},
        ]


def test_load_history(history_file: Path, sample_history: List[ConversationTurn]):
    file_manager = ConversationFileManager(history_file)
    file_manager.save_history(sample_history)

    loaded_history = file_manager.load_history()
    assert loaded_history == sample_history


def test_load_history_file_not_found(history_file: Path):
    file_manager = ConversationFileManager(history_file)
    loaded_history = file_manager.load_history()
    assert loaded_history == []


def test_invalid_history_path():
    with pytest.raises(ValueError):
        ConversationFileManager("../history.json")


def test_backup_and_restore(history_file: Path, sample_history: List[ConversationTurn]):
    file_manager = ConversationFileManager(history_file)
    file_manager.save_history(sample_history)

    with patch("pathlib.Path.rename", side_effect=IOError("Test error")):
        new_history = sample_history + [ConversationTurn("user", "Another turn")]
        file_manager.save_history(new_history)

    # Check that the original history is restored
    loaded_history = file_manager.load_history()
    assert loaded_history == sample_history


def test_history_truncation(history_file: Path):
    file_manager = ConversationFileManager(history_file, max_history_turns=2)
    long_history = [
        ConversationTurn("user", "1"),
        ConversationTurn("bot", "1"),
        ConversationTurn("user", "2"),
        ConversationTurn("bot", "2"),
        ConversationTurn("user", "3"),
    ]
    file_manager.save_history(long_history)

    loaded_history = file_manager.load_history()
    assert len(loaded_history) == 2
    assert loaded_history[0].text == "2"
    assert loaded_history[1].text == "3"

def test_load_corrupted_history(history_file: Path):
    history_file.write_text("not a valid json")
    file_manager = ConversationFileManager(history_file)
    loaded_history = file_manager.load_history()
    assert loaded_history == []

def test_load_invalid_schema_history(history_file: Path):
    invalid_data = [{"speaker": "user"}, {"text": "Hi"}]
    history_file.write_text(json.dumps(invalid_data))
    file_manager = ConversationFileManager(history_file)
    loaded_history = file_manager.load_history()
    assert loaded_history == []
