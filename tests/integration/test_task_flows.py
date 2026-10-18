def test_invalid_task_requests_do_not_mutate(client):
    created = client.post("/api/tasks", json={"title": "Keep me"})
    task_id = created.json()["id"]

    assert client.post("/api/tasks", json={"title": "   "}).status_code == 422
    assert client.patch(f"/api/tasks/{task_id}", json={"priority": "urgent"}).status_code == 422
    assert client.patch(f"/api/tasks/{task_id}", json={"due_date": "2026-02-30"}).status_code == 422
    assert client.get(f"/api/tasks/{task_id}").json()["title"] == "Keep me"


def test_unknown_task_returns_not_found(client):
    assert client.get("/api/tasks/999").status_code == 404
    assert client.patch("/api/tasks/999", json={"title": "Nope"}).status_code == 404
    assert client.delete("/api/tasks/999").status_code == 404
