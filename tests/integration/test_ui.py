def test_page_served_and_task_flow_persists(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Make room for" in response.text

    created = client.post("/api/tasks", json={"title": "Read"})
    assert created.status_code == 201
    task = created.json()
    task_id = task["id"]
    assert client.get("/api/tasks").json()[0]["title"] == "Read"
    assert client.patch(f"/api/tasks/{task_id}", json={"title": "Read a book"}).json()["title"] == "Read a book"
    assert client.patch(f"/api/tasks/{task_id}", json={"completed": True}).json()["completed"] is True
    assert client.patch(f"/api/tasks/{task_id}", json={"completed": False}).json()["completed"] is False
    assert client.get(f"/api/tasks/{task_id}").json()["title"] == "Read a book"
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get("/api/tasks").json() == []


def test_create_page_available_without_llm_key(client):
    assert client.get("/").status_code == 200
    assert client.post("/api/assistant", json={"text": "add buy milk tomorrow, high priority"}).status_code == 200
