from datetime import date

import pytest

from agents.rule_based import parse_request


def test_parse_natural_language_create_with_date_and_priority():
    intent = parse_request("add buy milk tomorrow, high priority", date(2026, 10, 19))
    assert intent == {
        "action": "create",
        "title": "buy milk",
        "priority": "high",
        "due_date": "2026-10-20",
    }


@pytest.mark.parametrize(
    ("text", "action", "title"),
    [
        ("complete call mom", "complete", "call mom"),
        ("reopen call mom", "reopen", "call mom"),
        ("delete call mom", "delete", "call mom"),
        ("update call mom high priority", "update", "call mom"),
    ],
)
def test_parse_task_actions(text, action, title):
    parsed = parse_request(text, date(2026, 10, 19))
    assert parsed["action"] == action
    assert parsed["title"] == title


def test_parse_planner_and_summary_requests():
    assert parse_request("what should I do next")['action'] == "next"
    assert parse_request("daily summary")['action'] == "summary"


def test_unknown_or_blank_requests_ask_for_clarification():
    assert parse_request("", date(2026, 10, 19))["action"] == "clarification"
    assert parse_request("do something", date(2026, 10, 19))["action"] == "clarification"
