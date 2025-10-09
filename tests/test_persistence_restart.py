from pathlib import Path

from ai_vibe_chat.engine import Engine
from ai_vibe_chat.personalities import RizzPersonality
from ai_vibe_chat.providers import LocalRulesProvider


def test_persistence_across_restart(tmp_path: Path):
    history_file = tmp_path / "conversation_history.json"

    provider = LocalRulesProvider()
    personality = RizzPersonality()

    # First run: create engine, talk twice, ensure history is saved
    engine1 = Engine(provider=provider, personality=personality, memory=True)
    assert engine1.file_manager is not None
    engine1.file_manager.history_file = history_file
    engine1.history = engine1.file_manager.load_history()

    engine1.respond("hello")
    engine1.respond("tell me a joke")

    assert history_file.exists()

    # Second run (restart): new engine loads existing history automatically
    engine2 = Engine(provider=provider, personality=personality, memory=True)
    assert engine2.file_manager is not None
    engine2.file_manager.history_file = history_file
    engine2.history = engine2.file_manager.load_history()

    # Expect at least the two user/bot pairs
    assert len(engine2.history) >= 4
    assert engine2.history[0].speaker == "user"
    assert engine2.history[1].speaker == "bot"
    assert engine2.history[-1].speaker == "bot"
