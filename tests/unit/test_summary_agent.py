from datetime import date

from agents.summary_agent import SummaryAgent
from tools.repository import TaskRepositoryTools


def test_summary_reports_completed_due_and_overdue(repository):
    today = date.today()
    due = repository.create("Due", due_date=today.isoformat())
    overdue = repository.create("Overdue", due_date="2020-01-01")
    completed = repository.create("Completed")
    repository.update(completed["id"], {"completed": True})

    summary = SummaryAgent(TaskRepositoryTools(repository), today=today).summarize(today)

    assert [task["id"] for task in summary["due_today"]] == [due["id"]]
    assert [task["id"] for task in summary["overdue"]] == [overdue["id"]]
    assert [task["id"] for task in summary["completed_today"]] == [completed["id"]]


def test_summary_empty_result(repository):
    summary = SummaryAgent(TaskRepositoryTools(repository), today=date(2026, 10, 19)).summarize()
    assert summary == {"date": "2026-10-19", "completed_today": [], "due_today": [], "overdue": []}
