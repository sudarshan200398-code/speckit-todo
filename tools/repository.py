"""SQLite persistence and the exclusive agent-facing task tool boundary."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


PRIORITIES = {"high", "normal", "low"}
EDITABLE_FIELDS = {"title", "completed", "priority", "due_date"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_title(title: Any) -> str:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    return title.strip()


def _validate_priority(priority: Any) -> str:
    if priority not in PRIORITIES:
        raise ValueError("priority must be one of: high, normal, low")
    return priority


def _validate_due_date(due_date: Any) -> str | None:
    if due_date is None:
        return None
    if not isinstance(due_date, str):
        raise ValueError("due_date must be an ISO date or null")
    try:
        parsed = date.fromisoformat(due_date)
    except ValueError as exc:
        raise ValueError("due_date must be a valid ISO date (YYYY-MM-DD)") from exc
    if parsed.isoformat() != due_date:
        raise ValueError("due_date must use YYYY-MM-DD format")
    return due_date


def _as_task(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    task = dict(row)
    task["completed"] = bool(task["completed"])
    return task


class TaskRepository:
    """Short-connection SQLite repository for task records."""

    def __init__(self, database: str | Path | None = None) -> None:
        configured = database or os.getenv("TODO_DATABASE")
        self.database = Path(configured) if configured else Path(__file__).resolve().parents[1] / "tasks.sqlite3"

    def _connect(self) -> sqlite3.Connection:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _transaction(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._transaction() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY CHECK (id > 0),
                    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
                    priority TEXT NOT NULL DEFAULT 'normal'
                        CHECK (priority IN ('high', 'normal', 'low')),
                    due_date TEXT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT NULL,
                    CHECK ((completed = 0 AND completed_at IS NULL) OR
                           (completed = 1 AND completed_at IS NOT NULL))
                )"""
            )

    def create(
        self,
        title: str,
        *,
        priority: str = "normal",
        due_date: str | None = None,
        completed: bool = False,
    ) -> dict[str, Any]:
        clean_title = _validate_title(title)
        clean_priority = _validate_priority(priority)
        clean_due_date = _validate_due_date(due_date)
        if not isinstance(completed, bool):
            raise ValueError("completed must be a boolean")
        now = _utc_now()
        completed_at = now if completed else None
        with self._transaction() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, completed, priority, due_date, created_at, completed_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (clean_title, int(completed), clean_priority, clean_due_date, now, completed_at),
            )
            task_id = cursor.lastrowid
        return self.get(int(task_id))

    def get(self, task_id: int) -> dict[str, Any]:
        with self._transaction() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        task = _as_task(row)
        if task is None:
            raise LookupError(f"task {task_id} not found")
        return task

    def list(self) -> list[dict[str, Any]]:
        with self._transaction() as connection:
            rows = connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [_as_task(row) for row in rows]

    def update(self, task_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(changes, dict) or not changes:
            raise ValueError("at least one editable field is required")
        unknown = set(changes) - EDITABLE_FIELDS
        if unknown:
            raise ValueError(f"unsupported task fields: {', '.join(sorted(unknown))}")
        values = dict(changes)
        if "title" in values:
            values["title"] = _validate_title(values["title"])
        if "priority" in values:
            values["priority"] = _validate_priority(values["priority"])
        if "due_date" in values:
            values["due_date"] = _validate_due_date(values["due_date"])
        if "completed" in values and not isinstance(values["completed"], bool):
            raise ValueError("completed must be a boolean")
        with self._transaction() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise LookupError(f"task {task_id} not found")
            assignments: list[str] = []
            parameters: list[Any] = []
            for field, value in values.items():
                assignments.append(f"{field} = ?")
                parameters.append(int(value) if field == "completed" else value)
                if field == "completed":
                    assignments.append("completed_at = ?")
                    parameters.append(_utc_now() if value else None)
            parameters.append(task_id)
            connection.execute(
                f"UPDATE tasks SET {', '.join(assignments)} WHERE id = ?", parameters
            )
            updated = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _as_task(updated)

    def delete(self, task_id: int) -> None:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount == 0:
                raise LookupError(f"task {task_id} not found")


class TaskRepositoryTools:
    """Tool functions passed to agents; agents never receive a connection."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create_task(self, title: str, *, priority: str = "normal", due_date: str | None = None) -> dict[str, Any]:
        return self._repository.create(title, priority=priority, due_date=due_date)

    def get_task(self, task_id: int) -> dict[str, Any]:
        return self._repository.get(task_id)

    def list_tasks(self) -> list[dict[str, Any]]:
        return self._repository.list()

    def update_task(self, task_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        return self._repository.update(task_id, changes)

    def complete_task(self, task_id: int) -> dict[str, Any]:
        return self._repository.update(task_id, {"completed": True})

    def reopen_task(self, task_id: int) -> dict[str, Any]:
        return self._repository.update(task_id, {"completed": False})

    def delete_task(self, task_id: int) -> None:
        self._repository.delete(task_id)
