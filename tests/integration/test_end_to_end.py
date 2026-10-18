def test_end_to_end_task_crud_assistant_planning_and_summary(client):
    assert client.get("/").status_code == 200
    created = client.post("/api/tasks", json={"title": "Prepare report", "priority": "high", "due_date": "2026-10-19"})
    assert created.status_code == 201

    assistant = client.post("/api/assistant", json={"text": "add buy milk tomorrow, high priority"}).json()
    assert assistant["status"] == "completed"
    assert assistant["task"]["title"] == "buy milk"

    next_task = client.get("/api/plan/next").json()
    assert next_task["task"] is not None
    summary = client.get("/api/summary?date=2026-10-19").json()
    assert summary["date"] == "2026-10-19"
    assert any(task["title"] == "Prepare report" for task in summary["due_today"])

def test_openapi_contains_documented_routes(client):
    schema = client.get("/openapi.json").json()
    assert {"/", "/api/tasks", "/api/tasks/{task_id}", "/api/assistant", "/api/plan/next", "/api/summary"} <= set(schema["paths"])
