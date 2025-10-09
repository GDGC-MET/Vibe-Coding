from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from .data_model import ConversationTurn

logger = logging.getLogger(__name__)


@contextmanager
def _exclusive_lock(lock_file: Path):
    """Best-effort cross-platform file lock using a sidecar .lock file.

    On Windows, uses msvcrt.locking; on POSIX, uses fcntl.flock. If locking
    is unavailable for any reason, proceeds without locking (still safe due
    to atomic rename flow below).
    """
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_file, "a+")
    try:
        if sys.platform == "win32":
            try:
                import msvcrt  # type: ignore
                # lock 1 byte at start of file
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            except Exception:
                pass
        else:
            try:
                import fcntl  # type: ignore
                fcntl.flock(f, fcntl.LOCK_EX)
            except Exception:
                pass
        yield
    finally:
        try:
            if sys.platform == "win32":
                try:
                    import msvcrt  # type: ignore
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
            else:
                try:
                    import fcntl  # type: ignore
                    fcntl.flock(f, 0)
                except Exception:
                    pass
        finally:
            f.close()


class ConversationFileManager:
    """Manages persistent conversation history on disk.

    Uses JSON for human-readable history and performs atomic writes with a
    temporary file and backup. Includes basic path validation and optional
    history truncation via max_history_turns to prevent unbounded growth.
    """

    def __init__(self, history_file: Path | str = "conversation_history.json", max_history_turns: int = 1000) -> None:
        if ".." in str(history_file):
            raise ValueError("History file path must not contain '..'.")
        self.history_file = Path(history_file)
        self.max_history_turns = max_history_turns

    def load_history(self) -> list[ConversationTurn]:
        """Load history from disk; create an empty file on first run.

        Returns an empty list on any read/parse error.
        """
        if not self.history_file.exists():
            try:
                # Create an empty history file on first run to satisfy first-run expectations
                self.history_file.write_text("[]")
            except (IOError, OSError) as e:
                logger.error(f"Error creating conversation history file: {e}")
            return []
        try:
            with open(self.history_file, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise TypeError("History JSON must be a list")
                return [ConversationTurn(**item) for item in data]
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error loading conversation history: {e}")
            return []
        except (IOError, OSError) as e:
            logger.error(f"Error reading conversation history file: {e}")
            return []

    def save_history(self, history: list[ConversationTurn]) -> None:
        """Persist history to disk safely with atomic rename and backup.

        A best-effort exclusive lock prevents concurrent writers from
        interleaving writes in multi-process scenarios.
        """
        if len(history) > self.max_history_turns:
            logger.warning(f"Conversation history exceeds {self.max_history_turns} turns. Truncating history.")
            history = history[-self.max_history_turns:]

        backup_file = self.history_file.with_suffix(".bak")
        temp_file = self.history_file.with_suffix(".tmp")
        lock_file = self.history_file.with_suffix(".lock")
        try:
            with _exclusive_lock(lock_file):
                # Create/overwrite backup safely (Windows-friendly)
                if self.history_file.exists():
                    try:
                        os.replace(self.history_file, backup_file)
                    except (IOError, OSError):
                        # Fallback: remove stale backup, then replace
                        if backup_file.exists():
                            try:
                                backup_file.unlink()
                            except Exception:
                                pass
                        os.replace(self.history_file, backup_file)

                # Write to temporary file
                with open(temp_file, "w") as f:
                    json.dump([turn.__dict__ for turn in history], f, indent=2)

                # Finalize by renaming temp -> history. Use Path.rename so tests can monkeypatch failures.
                temp_file.rename(self.history_file)
        except (IOError, OSError) as e:
            logger.error(f"Error saving conversation history: {e}")
            # Attempt to restore from backup; prefer overwrite-safe replace
            try:
                if backup_file.exists():
                    os.replace(backup_file, self.history_file)
            except Exception:
                pass
            finally:
                # Clean up temp file if present
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except Exception:
                    pass
