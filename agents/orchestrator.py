"""Routes normalized requests to task, planner, and summary agents."""

from __future__ import annotations

from datetime import date
from typing import Any

from agents.llm_provider import OpenAIIntentProvider
from agents.planner_agent import PlannerAgent
import logging

from agents.rule_based import detect_priority, parse_request
from agents.summary_agent import SummaryAgent
from agents.task_agent import TaskAgent
from tools.repository import TaskRepositoryTools

logger = logging.getLogger("uvicorn.error")


class Orchestrator:
    def __init__(
        self,
        tools: TaskRepositoryTools,
        *,
        provider: Any | None = None,
        today: date | None = None,
    ) -> None:
        self.tools = tools
        self.task_agent = TaskAgent(tools)
        self.planner_agent = PlannerAgent(tools, today=today)
        self.summary_agent = SummaryAgent(tools, today=today)
        self.provider = provider if provider is not None else OpenAIIntentProvider()
        self.today = today or date.today()

    def _interpret(self, text: str) -> dict[str, Any]:
        if self.provider.available:
            try:
                result = self.provider.interpret(f"Current local date: {self.today.isoformat()}. Request: {text}")
                self.provider.validate(result)
                return result
            except Exception as error:
                logger.warning("LLM intent extraction failed, using fallback: %s: %s", type(error).__name__, error)
        return parse_request(text, today=self.today)

    def handle(self, text: str) -> dict[str, Any]:
        intent = self._interpret(text)
        action = intent["action"]
        if action == "clarification":
            return {
                "status": "clarification",
                "message": intent.get("message") or "Please clarify the task.",
                "task": None,
                "can_add_as_task": bool(intent.get("unrecognized")),
            }
        if action == "next":
            result = self.planner_agent.suggest_next()
            return {"status": "completed", "message": result["reason"] if result else "There are no pending tasks.", "task": result["task"] if result else None}
        if action == "summary":
            summary = self.summary_agent.summarize(self.today)
            return {"status": "completed", "message": _summary_message(summary), "summary": summary, "task": None}
        title = intent.get("title")
        if not title:
            return {"status": "clarification", "message": "Which task should I act on?", "task": None}
        if action == "create":
            priority = intent.get("priority")
            if priority in (None, "normal") and detect_priority(text):
                priority = "high"
            planned = self.planner_agent.interpret(title, priority, intent.get("due_date"))
            task = self.task_agent.create(**planned)
            return {"status": "completed", "message": f"Added {task['title']}.", "task": task}
        existing = self.task_agent.find_by_title(title)
        if existing is None:
            return {"status": "clarification", "message": f"I couldn't find a task named {title!r}.", "task": None}
        if action == "complete":
            task = self.task_agent.complete(existing["id"])
            message = f"Completed {task['title']}."
        elif action == "reopen":
            task = self.task_agent.reopen(existing["id"])
            message = f"Reopened {task['title']}."
        elif action == "delete":
            self.task_agent.delete(existing["id"])
            task = None
            message = f"Deleted {existing['title']}."
        elif action == "update":
            changes = {}
            if intent.get("priority"):
                changes["priority"] = intent["priority"]
            if intent.get("due_date"):
                changes["due_date"] = intent["due_date"]
            if "title" in intent and intent.get("new_title"):
                changes["title"] = intent["new_title"]
            if not changes:
                return {"status": "clarification", "message": "Tell me what to change for that task.", "task": None}
            task = self.task_agent.update(existing["id"], changes)
            message = f"Updated {task['title']}."
        else:
            return {"status": "clarification", "message": "Please clarify the task action.", "task": None}
        return {"status": "completed", "message": message, "task": task}


def _summary_message(summary: dict[str, Any]) -> str:
    return (
        f"For {summary['date']}: {len(summary['completed_today'])} completed, "
        f"{len(summary['due_today'])} due today, {len(summary['overdue'])} overdue."
    )
