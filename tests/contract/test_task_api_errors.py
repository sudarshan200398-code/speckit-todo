def test_invalid_update_is_atomic(client):
    task = client.post("/api/tasks", json={"title": "Keep"}).json()
    task_id = task["id"]

    assert client.patch(f"/api/tasks/{task_id}", json={}).status_code == 422
    assert client.patch(f"/api/tasks/{task_id}", json={"title": "  "}).status_code == 422
    assert client.patch(f"/api/tasks/{task_id}", json={"priority": "urgent"}).status_code == 422
    assert client.patch(f"/api/tasks/{task_id}", json={"due_date": "not-a-date"}).status_code == 422
    assert client.get(f"/api/tasks/{task_id}").json() == task


def test_unknown_item_errors(client):
    assert client.get("/api/tasks/1111").status_code == 404
    assert client.patch("/api/tasks/1111", json={"title": "No task"}).status_code == 404
    assert client.delete("/api/tasks/1111").status_code == 404
