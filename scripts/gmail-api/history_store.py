from __future__ import annotations

import sqlite3
from pathlib import Path


class HistoryStoreError(RuntimeError):
    pass


class GmailHistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def get_history_id(self) -> str | None:
        try:
            with sqlite3.connect(self.path) as connection:
                row = connection.execute(
                    "SELECT value FROM gmail_state WHERE key = 'history_id'"
                ).fetchone()
        except sqlite3.Error as exc:
            raise HistoryStoreError(f"Could not load Gmail history id from {self.path}") from exc

        return str(row[0]) if row else None

    def set_history_id(self, history_id: str) -> None:
        normalized = str(history_id).strip()
        if not normalized:
            return

        try:
            with sqlite3.connect(self.path) as connection:
                connection.execute(
                    """
                    INSERT INTO gmail_state (key, value)
                    VALUES ('history_id', ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (normalized,),
                )
        except sqlite3.Error as exc:
            raise HistoryStoreError(f"Could not persist Gmail history id to {self.path}") from exc

    def _ensure_schema(self) -> None:
        try:
            with sqlite3.connect(self.path) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS gmail_state (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise HistoryStoreError(f"Could not initialize Gmail history store at {self.path}") from exc
