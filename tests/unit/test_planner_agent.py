from datetime import date

from agents.planner_agent import PlannerAgent
from tools.repository import TaskRepositoryTools


def test_planner_prefers_overdue_then_priority_and_nearest_due(repository):
    tools = TaskRepositoryTools(repository)
    repository.create("Future high", priority="high", due_date="2026-10-22")
    repository.create("Overdue low", priority="low", due_date="2026-10-18")
    expected = repository.create("Overdue high", priority="high", due_date="2026-10-18")

    result = PlannerAgent(tools, today=date(2026, 10, 19)).suggest_next()

    assert result["task"]["id"] == expected["id"]
    assert result["reason"] == "Overdue since 2026-10-18"


def test_planner_excludes_completed_and_handles_no_tasks(repository):
    tools = TaskRepositoryTools(repository)
    assert PlannerAgent(tools, today=date(2026, 10, 19)).suggest_next() is None
    task = repository.create("Done")
    repository.update(task["id"], {"completed": True})
    assert PlannerAgent(tools, today=date(2026, 10, 19)).suggest_next() is None
