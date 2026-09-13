import json
import sqlite3
from pathlib import Path
from threading import Lock


class CheckpointStore:
    """Small durable checkpoint store; replaceable with Postgres in production."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS checkpoints (session_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            connection.commit()
        finally:
            connection.close()

    def save(self, session_id: str, payload: dict) -> None:
        with self._lock:
            connection = sqlite3.connect(self.path)
            try:
                connection.execute(
                    "INSERT OR REPLACE INTO checkpoints VALUES (?, ?)",
                    (session_id, json.dumps(payload)),
                )
                connection.commit()
            finally:
                connection.close()

    def load(self, session_id: str) -> dict | None:
        with self._lock:
            connection = sqlite3.connect(self.path)
            try:
                row = connection.execute(
                    "SELECT payload FROM checkpoints WHERE session_id = ?", (session_id,)
                ).fetchone()
            finally:
                connection.close()
        return json.loads(row[0]) if row else None
