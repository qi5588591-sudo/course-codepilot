import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class Store:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, created_at TEXT, kind TEXT, language TEXT,
                requirement TEXT, result TEXT NOT NULL)""")

    def connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def save(self, id: str, kind: str, language: str, requirement: str, result: dict):
        with self.connect() as db:
            db.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?)", (
                id, datetime.now(timezone.utc).isoformat(), kind, language, requirement,
                json.dumps(result, ensure_ascii=False),
            ))

    def list(self, limit: int = 30, offset: int = 0):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(r) for r in db.execute(
                "SELECT id,created_at,kind,language,requirement FROM tasks ORDER BY rowid DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )]

    def get(self, id: str):
        with self.connect() as db:
            row = db.execute("SELECT result FROM tasks WHERE id=?", (id,)).fetchone()
            return json.loads(row[0]) if row else None
