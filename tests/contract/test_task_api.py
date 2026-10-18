def test_task_rest_crud_contract(client):
    created = client.post("/api/tasks", json={"title": "Read", "priority": "high", "due_date": "2026-10-20"})
    assert created.status_code == 201
    task = created.json()
    assert task["priority"] == "high"
    task_id = task["id"]

    assert client.get("/api/tasks").json() == [task]
    assert client.get(f"/api/tasks/{task_id}").json() == task
    updated = client.patch(f"/api/tasks/{task_id}", json={"title": "Read today"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Read today"
    assert updated.json()["priority"] == "high"
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_invalid_create_and_extra_field_are_rejected(client):
    assert client.post("/api/tasks", json={"title": ""}).status_code == 422
    assert client.post("/api/tasks", json={"title": "Task", "unexpected": True}).status_code == 422
