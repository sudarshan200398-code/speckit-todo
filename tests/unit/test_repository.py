import sqlite3

import pytest

from tools.repository import TaskRepository


def test_create_defaults_and_list(repository):
    task = repository.create("  Buy milk  ")

    assert task["title"] == "Buy milk"
    assert task["completed"] is False
    assert task["priority"] == "normal"
    assert task["due_date"] is None
    assert task["completed_at"] is None
    assert repository.get(task["id"]) == task
    assert repository.list() == [task]


def test_create_with_priority_and_due_date(repository):
    task = repository.create("Buy milk", priority="high", due_date="2026-10-20")

    assert task["priority"] == "high"
    assert task["due_date"] == "2026-10-20"


@pytest.mark.parametrize("title", ["", "  ", "\t"])
def test_rejects_empty_title(repository, title):
    with pytest.raises(ValueError):
        repository.create(title)


@pytest.mark.parametrize("priority", ["urgent", "HIGH", ""])
def test_rejects_invalid_priority(repository, priority):
    with pytest.raises(ValueError):
        repository.create("Task", priority=priority)


@pytest.mark.parametrize("due_date", ["tomorrow", "2026-02-30", "2026/10/20"])
def test_rejects_invalid_due_date(repository, due_date):
    with pytest.raises(ValueError):
        repository.create("Task", due_date=due_date)


def test_completion_and_reopen_update_timestamp(repository):
    task = repository.create("Task")

    completed = repository.update(task["id"], {"completed": True})
    reopened = repository.update(task["id"], {"completed": False})

    assert completed["completed"] is True
    assert completed["completed_at"] is not None
    assert reopened["completed"] is False
    assert reopened["completed_at"] is None


def test_update_preserves_omitted_fields(repository):
    task = repository.create("Task", priority="high", due_date="2026-10-20")
    updated = repository.update(task["id"], {"title": "Changed"})

    assert updated["title"] == "Changed"
    assert updated["priority"] == "high"
    assert updated["due_date"] == "2026-10-20"
    assert updated["created_at"] == task["created_at"]


def test_invalid_update_rolls_back(repository):
    task = repository.create("Task")

    with pytest.raises(ValueError):
        repository.update(task["id"], {"title": "Changed", "priority": "urgent"})

    assert repository.get(task["id"]) == task


def test_file_database_persists_between_repository_instances(db_path):
    first = TaskRepository(db_path)
    first.initialize()
    task = first.create("Persist me")

    second = TaskRepository(db_path)
    assert second.get(task["id"])["title"] == "Persist me"


def test_missing_task_and_delete(repository):
    with pytest.raises(LookupError):
        repository.get(404)

    task = repository.create("Delete me")
    repository.delete(task["id"])

    with pytest.raises(LookupError):
        repository.get(task["id"])


def test_schema_enforces_priority_enum(db_path):
    repo = TaskRepository(db_path)
    repo.initialize()
    with pytest.raises(sqlite3.IntegrityError):
        with repo._connect() as connection:
            connection.execute(
                "INSERT INTO tasks (title, completed, priority, created_at) VALUES (?, 0, ?, ?)",
                ("Bad priority", "urgent", "2026-10-19T00:00:00+00:00"),
            )
