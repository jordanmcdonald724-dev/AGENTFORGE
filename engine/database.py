from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from .config import Settings, get_settings


class Database:
    """Lightweight SQLite wrapper for bootstrapping AgentForgeOS."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def database_path(self) -> Path:
        if not self.settings.database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite URLs are supported in the bootstrap engine")
        path_str = self.settings.database_url.replace("sqlite:///", "", 1)
        return Path(path_str).expanduser().resolve()

    def connect(self) -> sqlite3.Connection:
        if self._connection:
            return self._connection

        db_path = self.database_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self._connection.commit()
        return self._connection

    def record_event(self, event: str) -> None:
        conn = self.connect()
        conn.execute(
            "INSERT INTO system_events (event, created_at) VALUES (?, datetime('now'))",
            (event,),
        )
        conn.commit()

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.commit()

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None


def init_database(settings: Optional[Settings] = None) -> Database:
    return Database(settings)

