from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .exceptions import DuplicateMemoryError, MemoryNotFoundError
from .models import Memory


class Storage:
    """Small SQLite repository with safe connections and explicit transactions."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        return connection

    def _init_schema(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    repository_id TEXT NOT NULL,
                    repository_path TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context_file TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    importance TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(repository_id, topic, content)
                );
                CREATE INDEX IF NOT EXISTS idx_mem_repo_status
                    ON memories(repository_id, status);
                CREATE INDEX IF NOT EXISTS idx_mem_repo_type
                    ON memories(repository_id, memory_type);
                CREATE INDEX IF NOT EXISTS idx_mem_repo_updated
                    ON memories(repository_id, updated_at DESC);
                """
            )

    def add(self, memory: Memory) -> Memory:
        try:
            with self.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO memories (
                        id, repository_id, repository_path, memory_type, topic,
                        content, context_file, tags, importance, status, source,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        memory.id,
                        memory.repository_id,
                        memory.repository_path,
                        memory.memory_type,
                        memory.topic,
                        memory.content,
                        memory.context_file,
                        json.dumps(memory.tags),
                        memory.importance,
                        memory.status,
                        memory.source,
                        memory.created_at.isoformat(),
                        memory.updated_at.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise DuplicateMemoryError(
                "An identical memory already exists in this repository."
            ) from error
        return memory

    @staticmethod
    def _from_row(row: sqlite3.Row | None) -> Memory:
        if row is None:
            raise MemoryNotFoundError("Memory was not found in this repository.")
        data: dict[str, Any] = dict(row)
        try:
            data["tags"] = json.loads(data["tags"])
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("The memory database contains invalid tag data.") from error
        return Memory.model_validate(data)

    def get(self, memory_id: str, repository_id: str) -> Memory:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM memories WHERE id = ? AND repository_id = ?",
                (memory_id, repository_id),
            ).fetchone()
        return self._from_row(row)

    def list(
        self,
        repository_id: str,
        memory_type: str | None = None,
        status: str | None = "active",
        limit: int | None = 50,
    ) -> list[Memory]:
        query = "SELECT * FROM memories WHERE repository_id = ?"
        arguments: list[Any] = [repository_id]
        if memory_type:
            query += " AND memory_type = ?"
            arguments.append(memory_type)
        if status:
            query += " AND status = ?"
            arguments.append(status)
        query += """
            ORDER BY CASE importance
                WHEN 'critical' THEN 4
                WHEN 'high' THEN 3
                WHEN 'normal' THEN 2
                ELSE 1 END DESC,
                updated_at DESC
        """
        if limit is not None:
            bounded_limit = max(1, min(int(limit), 5000))
            query += " LIMIT ?"
            arguments.append(bounded_limit)
        with self.connect() as connection:
            rows = connection.execute(query, arguments).fetchall()
        return [self._from_row(row) for row in rows]

    def update(
        self, memory_id: str, repository_id: str, fields: dict[str, Any]
    ) -> Memory:
        current = self.get(memory_id, repository_id)
        data = current.model_dump()
        data.update({key: value for key, value in fields.items() if value is not None})
        data["updated_at"] = Memory.now()
        updated = Memory.model_validate(data)
        try:
            with self.connect() as connection:
                connection.execute(
                    """
                    UPDATE memories SET topic = ?, content = ?, context_file = ?,
                        tags = ?, importance = ?, status = ?, updated_at = ?
                    WHERE id = ? AND repository_id = ?
                    """,
                    (
                        updated.topic,
                        updated.content,
                        updated.context_file,
                        json.dumps(updated.tags),
                        updated.importance,
                        updated.status,
                        updated.updated_at.isoformat(),
                        memory_id,
                        repository_id,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise DuplicateMemoryError(
                "The update would create a duplicate memory in this repository."
            ) from error
        return updated

    def integrity_check(self) -> str:
        with self.connect() as connection:
            result = connection.execute("PRAGMA integrity_check").fetchone()
        return str(result[0]) if result else "unknown"

    def count(self, repository_id: str, status: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM memories WHERE repository_id = ?"
        arguments: list[Any] = [repository_id]
        if status:
            query += " AND status = ?"
            arguments.append(status)
        with self.connect() as connection:
            return int(connection.execute(query, arguments).fetchone()[0])
