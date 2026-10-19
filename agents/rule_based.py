"""Small deterministic natural-language command parser used as a fallback."""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any


_PRIORITY_PATTERNS = (
    ("high", re.compile(r"\b(?:high|urgent|important)\s+priority\b|\bpriority\s+(?:high|urgent)\b|\b(?:it'?s\s+)?(?:urgent|asap|critical)\b", re.I)),
    ("low", re.compile(r"\blow\s+priority\b|\bpriority\s+low\b", re.I)),
    ("normal", re.compile(r"\bnormal\s+priority\b|\bpriority\s+normal\b", re.I)),
)
_DATE_PATTERNS = [
    (re.compile(r"\btomorrow\b", re.I), lambda today: today + timedelta(days=1)),
    (re.compile(r"\btoday\b", re.I), lambda today: today),
    (re.compile(r"\bnext week\b", re.I), lambda today: today + timedelta(days=7)),
]


def _metadata(text: str, today: date) -> tuple[str, str | None, str | None]:
    remaining = text
    priority = None
    for value, pattern in _PRIORITY_PATTERNS:
        if pattern.search(remaining):
            priority = value
            remaining = pattern.sub(" ", remaining)
            break
    due_date = None
    for pattern, resolve in _DATE_PATTERNS:
        if pattern.search(remaining):
            due_date = resolve(today).isoformat()
            remaining = pattern.sub(" ", remaining)
            break
    remaining = re.sub(r"\b(?:please|task|priority)\b", " ", remaining, flags=re.I)
    remaining = re.sub(r"\s+", " ", remaining).strip(" \t,.;:-")
    return remaining, priority, due_date


def parse_request(text: str, today: date | None = None) -> dict[str, Any]:
    """Return a normalized intent or a clarification without side effects."""
    current = today or date.today()
    value = text.strip()
    if not value:
        return {"action": "clarification", "message": "Please describe the task or action."}

    if re.search(r"\b(summary|summarize|what did i do today)\b", value, re.I):
        return {"action": "summary"}
    if re.search(r"\b(what should i do next|next task|suggest a task|plan my day)\b", value, re.I):
        return {"action": "next"}

    patterns = [
        ("create", r"^(?:please\s+)?(?:add|create|remind me to|new task:?|make a task to)\s+"),
        ("complete", r"^(?:please\s+)?(?:complete|finish|mark complete)\s+"),
        ("reopen", r"^(?:please\s+)?(?:reopen|uncomplete)\s+"),
        ("delete", r"^(?:please\s+)?(?:delete|remove)\s+"),
        ("update", r"^(?:please\s+)?(?:update|rename|change)\s+"),
    ]
    action = None
    payload = value
    for candidate, pattern in patterns:
        match = re.match(pattern, value, flags=re.I)
        if match:
            action = candidate
            payload = value[match.end():]
            break
    if action is None:
        return {
            "action": "clarification",
            "message": "I didn't recognise a command. Start with add, complete, update, reopen, delete, next task or summary, or add your text as a new task.",
            "unrecognized": True,
        }

    title, priority, due_date = _metadata(payload, current)
    title = re.sub(r"^(?:a task to|task to|to)\s+", "", title, flags=re.I).strip()
    title = re.sub(r"^(?:add|create)\s+", "", title, flags=re.I).strip()
    if not title:
        return {"action": "clarification", "message": "Which task should I act on?"}
    if action == "create":
        return {"action": action, "title": title, "priority": priority or "normal", "due_date": due_date}
    return {"action": action, "title": title, "priority": priority, "due_date": due_date}


URGENT_WORDS = re.compile(r"\b(?:urgent|urgently|asap|critical|important|high priority)\b", re.I)


def detect_priority(text: str) -> str | None:
    """Return 'high' when the request clearly signals urgency."""
    return "high" if URGENT_WORDS.search(text) else None
