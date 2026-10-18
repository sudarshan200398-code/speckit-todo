# Quickstart: Agentic To-Do App

This guide describes end-to-end validation once the implementation tasks are complete.

## Prerequisites

- Python 3.11
- A shell with the project root as the working directory
- No LLM API key is required for fallback validation
- For the configured-provider test, use a mocked provider; do not make a live request in the normal test suite

## Install and run tests

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
pytest
```

On Windows PowerShell, activate the environment with `.\.venv\Scripts\Activate.ps1`.

Expected result: pytest passes, including CRUD, page serving, repository/tool boundary, agent orchestration, date handling, summaries, and no-key fallback cases. Configured-LLM tests use a stubbed OpenAI client and do not need a secret.

## Start the application

Set the optional database path as needed. Without `OPENAI_API_KEY`, the service uses its rule-based fallback.

```sh
export PORT=8000
uvicorn main:app --host 0.0.0.0 --port $PORT
```

For a configured provider, set `OPENAI_API_KEY` in the process environment before startup. Never commit the key. The requested command is POSIX-shell syntax; on Windows PowerShell, set the port with `$env:PORT = "8000"` and start with `uvicorn main:app --host 0.0.0.0 --port $env:PORT`.

Expected result: the service starts without provider credentials and serves the single-page application at `http://localhost:8000/`.

## Validate user flows

1. Open `/`, create a task, edit it, mark it complete, reopen it, and delete it. Refresh between operations to verify persistence.
2. Send `POST /api/assistant` with `{"text":"add buy milk tomorrow, high priority"}`. Confirm the task title, due date, and priority. Repeat without `OPENAI_API_KEY` to exercise fallback.
3. Create incomplete tasks with different priorities and dates. Call `GET /api/plan/next`; verify it returns an incomplete task ordered according to the rules in [data-model.md](data-model.md).
4. Call `GET /api/summary` and `GET /api/summary?date=YYYY-MM-DD`; verify completed-today, due-today, and overdue tasks appear in the correct groups.
5. Exercise `POST`, `GET`, `PATCH`, and `DELETE` on `/api/tasks` and `/api/tasks/{task_id}`. Confirm unknown IDs return 404 and invalid payloads return 422 without mutating stored data.

The request and response shapes are defined in [contracts/openapi.yaml](contracts/openapi.yaml); task states and date rules are defined in [data-model.md](data-model.md).
