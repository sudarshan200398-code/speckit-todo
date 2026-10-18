"""Daily task summaries derived from repository tool results."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

from tools.repository import TaskRepositoryTools


class SummaryAgent:
    def __init__(self, tools: TaskRepositoryTools, today: date | None = None) -> None:
        self.tools = tools
        self.today = today or date.today()

    def summarize(self, for_date: date | None = None) -> dict[str, Any]:
        target = for_date or self.today
        completed_today = []
        due_today = []
        overdue = []
        for task in self.tools.list_tasks():
            if task["completed"]:
                if task["completed_at"]:
                    completed_at = datetime.fromisoformat(task["completed_at"])
                    if completed_at.tzinfo is None:
                        completed_at = completed_at.replace(tzinfo=timezone.utc)
                    local_day = completed_at.astimezone().date()
                    if local_day == target:
                        completed_today.append(task)
                continue
            if not task["due_date"]:
                continue
            due = date.fromisoformat(task["due_date"])
            if due == target:
                due_today.append(task)
            elif due < target:
                overdue.append(task)
        return {
            "date": target.isoformat(),
            "completed_today": completed_today,
            "due_today": due_today,
            "overdue": overdue,
        }
