"""Optional OpenAI intent adapter with no import-time credential requirement."""

from __future__ import annotations

import json
import os
from typing import Any, Callable


class OpenAIIntentProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None, client: Any = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = client

    @property
    def available(self) -> bool:
        return bool(self.api_key or self._client)

    def interpret(self, text: str) -> dict[str, Any]:
        if not self.available:
            raise RuntimeError("OpenAI provider is not configured")
        client = self._client
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, timeout=10.0, max_retries=0)
            self._client = client
        response = client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Convert a to-do instruction to JSON only. Keys: action (create, update, complete, "
                        "reopen, delete, next, summary, clarification), title (string or null), priority "
                        "(high, normal, low, or null), due_date (YYYY-MM-DD or null), message (string or null). "
                        "Never claim an action was performed. Use clarification when uncertain. Relative dates "
                        "use the current local date provided in the user message."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("provider returned empty output")
        result = json.loads(content)
        self.validate(result)
        return result

    @staticmethod
    def validate(result: Any) -> None:
        if not isinstance(result, dict):
            raise ValueError("provider output must be a JSON object")
        actions = {"create", "update", "complete", "reopen", "delete", "next", "summary", "clarification"}
        if result.get("action") not in actions:
            raise ValueError("provider returned an unsupported action")
        title = result.get("title")
        if title is not None and (not isinstance(title, str) or not title.strip()):
            raise ValueError("provider returned an invalid title")
        priority = result.get("priority")
        if priority is not None and priority not in {"high", "normal", "low"}:
            raise ValueError("provider returned an invalid priority")
        due_date = result.get("due_date")
        if due_date is not None:
            from datetime import date

            if not isinstance(due_date, str) or date.fromisoformat(due_date).isoformat() != due_date:
                raise ValueError("provider returned an invalid due date")
        if result["action"] in {"create", "update", "complete", "reopen", "delete"} and not title:
            raise ValueError("provider must identify a task title")


def provider_from_env(factory: Callable[..., Any] = OpenAIIntentProvider) -> Any | None:
    key = os.getenv("OPENAI_API_KEY")
    return factory(api_key=key) if key else None
