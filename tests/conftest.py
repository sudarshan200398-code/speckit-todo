from datetime import date

import pytest
from fastapi.testclient import TestClient

from main import create_app
from tools.repository import TaskRepository


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "tasks.sqlite3"


@pytest.fixture
def repository(db_path):
    repo = TaskRepository(db_path)
    repo.initialize()
    return repo


@pytest.fixture
def today():
    return date(2026, 10, 19)


@pytest.fixture
def client(db_path, monkeypatch):
    monkeypatch.setenv("TODO_DATABASE", str(db_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
