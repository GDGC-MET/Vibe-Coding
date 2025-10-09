import pytest
from pathlib import Path
from ai_vibe_chat.engine import Engine
from ai_vibe_chat.personalities import RizzPersonality, SarcasticPersonality
from ai_vibe_chat.providers import LocalRulesProvider


@pytest.mark.parametrize("personality", [RizzPersonality, SarcasticPersonality])
def test_engine_with_different_personalities(personality, tmp_path: Path):
    history_file = tmp_path / "conversation_history.json"
    provider = LocalRulesProvider()
    engine = Engine(provider=provider, personality=personality(), memory=True)
    assert engine.file_manager is not None
    engine.file_manager.history_file = history_file # Override the history file path
    engine.history = engine.file_manager.load_history() # Reload history

    # First interaction
    user_input_1 = "hello"
    response_1 = engine.respond(user_input_1)

    assert len(engine.history) == 2
    assert engine.history[0].speaker == "user"
    assert engine.history[0].text == user_input_1
    assert engine.history[1].speaker == "bot"
    assert engine.history[1].text == response_1

    # Second interaction
    user_input_2 = "tell me a joke"
    response_2 = engine.respond(user_input_2)

    assert len(engine.history) == 4
    assert engine.history[2].speaker == "user"
    assert engine.history[2].text == user_input_2
    assert engine.history[3].speaker == "bot"
    assert engine.history[3].text == response_2
