import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "leads.db"


def init_db() -> None:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    name TEXT,
                    contact TEXT NOT NULL,
                    source TEXT,
                    comment TEXT
                )
            """)


def save_lead(name: str, contact: str, source: str, comment: str) -> int:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO leads (created_at, name, contact, source, comment) VALUES (?, ?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), name, contact, source, comment),
            )
            return cursor.lastrowid
