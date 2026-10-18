def test_assistant_creates_task_using_rule_fallback(client):
    response = client.post("/api/assistant", json={"text": "add buy milk tomorrow, high priority"})
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "completed"
    assert result["task"]["title"] == "buy milk"
    assert result["task"]["priority"] == "high"
    assert result["task"]["due_date"] is not None


def test_ambiguous_request_does_not_write(client):
    before = client.get("/api/tasks").json()
    result = client.post("/api/assistant", json={"text": "please do this thing"}).json()
    assert result["status"] == "clarification"
    assert client.get("/api/tasks").json() == before


def test_assistant_uses_task_agent_for_complete_action(client):
    task = client.post("/api/tasks", json={"title": "call mom"}).json()
    result = client.post("/api/assistant", json={"text": "complete call mom"}).json()
    assert result["task"]["id"] == task["id"]
    assert result["task"]["completed"] is True
