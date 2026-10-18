"""Task lifecycle agent; all task access is mediated by repository tools."""

from __future__ import annotations

from typing import Any

from tools.repository import TaskRepositoryTools


class TaskAgent:
    def __init__(self, tools: TaskRepositoryTools) -> None:
        self.tools = tools

    def create(self, title: str, *, priority: str = "normal", due_date: str | None = None) -> dict[str, Any]:
        return self.tools.create_task(title, priority=priority, due_date=due_date)

    def update(self, task_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        return self.tools.update_task(task_id, changes)

    def complete(self, task_id: int) -> dict[str, Any]:
        return self.tools.complete_task(task_id)

    def reopen(self, task_id: int) -> dict[str, Any]:
        return self.tools.reopen_task(task_id)

    def delete(self, task_id: int) -> None:
        self.tools.delete_task(task_id)

    def find_by_title(self, title: str) -> dict[str, Any] | None:
        normalized = title.casefold().strip()
        return next((task for task in self.tools.list_tasks() if task["title"].casefold() == normalized), None)
