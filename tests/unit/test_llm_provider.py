import json
from types import SimpleNamespace

import pytest

from agents.llm_provider import OpenAIIntentProvider, provider_from_env
from agents.orchestrator import Orchestrator
from tools.repository import TaskRepositoryTools


class FakeCompletions:
    def __init__(self, content):
        self.content = content

    def create(self, **kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


class FakeClient:
    def __init__(self, content):
        self.chat = SimpleNamespace(completions=FakeCompletions(content))


def test_provider_parses_valid_structured_output():
    provider = OpenAIIntentProvider(client=FakeClient(json.dumps({"action": "create", "title": "Buy milk", "priority": "high", "due_date": "2026-10-20"})))
    result = provider.interpret("add buy milk")
    assert result["action"] == "create"
    assert result["title"] == "Buy milk"


def test_provider_rejects_invalid_output():
    provider = OpenAIIntentProvider(client=FakeClient('{"action":"wipe_database"}'))
    with pytest.raises(ValueError):
        provider.interpret("do something")


def test_provider_fallback_when_configured_provider_fails(repository):
    class BrokenProvider:
        available = True

        @staticmethod
        def interpret(_text):
            raise RuntimeError("offline")

        @staticmethod
        def validate(_result):
            return None

    result = Orchestrator(TaskRepositoryTools(repository), provider=BrokenProvider()).handle(
        "add buy milk tomorrow, high priority"
    )
    assert result["status"] == "completed"
    assert result["task"]["title"] == "buy milk"
    assert result["task"]["priority"] == "high"


def test_provider_selected_only_with_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert provider_from_env() is None
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    assert provider_from_env().available is True
