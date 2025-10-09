from click.testing import CliRunner
from ai_vibe_chat.cli import main


def test_cli_memory_flag_parses_and_starts():
    runner = CliRunner()
    # Use an isolated FS so any conversation_history.json is created in a temp dir
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["--personality", "rizz", "--memory"], input="quit\n")
        assert result.exit_code == 0, result.output
        # Memory status should be printed when --memory is enabled
        assert "Memory:" in result.output
