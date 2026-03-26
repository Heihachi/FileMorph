# FileMorph/core/history_manager.py
import sqlite3
from pathlib import Path
from typing import Any

from utils.app_paths import get_user_data_dir


class HistoryManager:

    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_path = get_user_data_dir() / "filemorph_history.db"

        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT NOT NULL,
                    source_format TEXT NOT NULL,
                    target_format TEXT NOT NULL,
                    target_path TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL
                )
            """)
            conn.commit()

    def add_record(
        self,
        source_path: str,
        source_format: str,
        target_format: str,
        target_path: str,
        status: str,
        created_at: str,
        duration_ms: int
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversion_history (
                    source_path,
                    source_format,
                    target_format,
                    target_path,
                    status,
                    created_at,
                    duration_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                source_path,
                source_format,
                target_format,
                target_path,
                status,
                created_at,
                duration_ms
            ))
            conn.commit()

    def get_all(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT
                    id,
                    source_path,
                    source_format,
                    target_format,
                    target_path,
                    status,
                    created_at,
                    duration_ms
                FROM conversion_history
                ORDER BY id DESC
            """).fetchall()

        return [dict(row) for row in rows]

    def get_record_by_id(self, record_id: int) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT
                    id,
                    source_path,
                    source_format,
                    target_format,
                    target_path,
                    status,
                    created_at,
                    duration_ms
                FROM conversion_history
                WHERE id = ?
            """, (record_id,)).fetchone()

        return dict(row) if row else None

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversion_history")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'conversion_history'")
            conn.commit()