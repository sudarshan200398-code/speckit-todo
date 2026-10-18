"""Planning and deterministic interpretation helpers."""

from __future__ import annotations

from datetime import date
from typing import Any

from tools.repository import TaskRepositoryTools


class PlannerAgent:
    def __init__(self, tools: TaskRepositoryTools, today: date | None = None) -> None:
        self.tools = tools
        self.today = today or date.today()

    def interpret(self, title: str, priority: str | None = None, due_date: str | None = None) -> dict[str, Any]:
        return {
            "title": title.strip(),
            "priority": priority or "normal",
            "due_date": due_date,
        }

    def suggest_next(self) -> dict[str, Any] | None:
        tasks = [task for task in self.tools.list_tasks() if not task["completed"]]
        if not tasks:
            return None
        priority_order = {"high": 0, "normal": 1, "low": 2}

        def rank(task: dict[str, Any]) -> tuple[Any, ...]:
            due = date.fromisoformat(task["due_date"]) if task["due_date"] else None
            overdue = due is not None and due < self.today
            due_rank = (0, (due - self.today).days) if due is not None else (1, 0)
            return (0 if overdue else 1, priority_order[task["priority"]], due_rank, task["id"])

        chosen = min(tasks, key=rank)
        due = date.fromisoformat(chosen["due_date"]) if chosen["due_date"] else None
        if due and due < self.today:
            reason = f"Overdue since {due.isoformat()}"
        elif chosen["priority"] == "high":
            reason = "High priority"
        elif due:
            reason = f"Due {due.isoformat()}"
        else:
            reason = "Next available incomplete task"
        return {"task": chosen, "reason": reason}
