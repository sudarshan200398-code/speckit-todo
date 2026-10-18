def test_next_task_and_daily_summary_endpoints(client):
    overdue = client.post("/api/tasks", json={"title": "Overdue", "priority": "low", "due_date": "2020-01-01"}).json()
    due = client.post("/api/tasks", json={"title": "Today", "priority": "high"}).json()
    result = client.get("/api/plan/next").json()
    assert result["task"]["id"] == overdue["id"]

    summary = client.get("/api/summary?date=2026-10-19").json()
    assert summary["date"] == "2026-10-19"
    assert [task["title"] for task in summary["overdue"]] == ["Overdue"]
    assert summary["due_today"] == []
    assert due["completed"] is False


def test_no_pending_tasks_response(client):
    result = client.get("/api/plan/next").json()
    assert result["task"] is None
    assert result["reason"]
    assert client.get("/api/summary?date=bad-date").status_code == 422
