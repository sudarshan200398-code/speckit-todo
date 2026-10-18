# Research: Agentic To-Do App

**Date**: 2026-10-18

## Decisions

### Runtime and service structure

- **Decision**: Use Python 3.11, FastAPI, synchronous route handlers for synchronous `sqlite3` and provider operations, `main.py` as the application entry point, and one `index.html` served at `/` with `FileResponse` using a path derived from `__file__`.
- **Rationale**: This follows the requested entry point and single-page UI while avoiding blocking synchronous work inside `async def` handlers and avoiding a frontend build system.
- **Alternatives considered**: An ORM, async database driver, separate frontend app, or static asset directory. These add complexity beyond the requested small single-page service.

### SQLite persistence

- **Decision**: Use the standard-library `sqlite3` module with a short-lived connection per repository operation, `sqlite3.Row`, parameterized SQL, and explicit transaction commit/rollback and connection close. Create the schema idempotently during application startup. Keep the database file path configurable and resolve its default relative to the application, creating the parent directory when necessary.
- **Rationale**: Short-lived connections make ownership and test isolation clear and avoid sharing a connection across request threads. Parameter binding prevents values from becoming SQL syntax. Idempotent schema initialization supports first-run startup without a migration framework.
- **Alternatives considered**: ORM, shared global connection, and database server. They are unnecessary for the requested SQLite service. The SQLite connection context manager controls transactions but does not itself close the connection, so closure remains explicit.

### TaskRepository tool boundary

- **Decision**: Keep all SQL and row/domain conversion in `tools/repository.py`. Provide repository operations for create, get, list, update, and delete plus explicit agent-facing tool functions. Agents receive task values and tool results only, never connections or SQL access. REST routes may use the repository for the plain CRUD API; all agent access to task data must go through its tool functions.
- **Rationale**: This enforces the constitution's non-negotiable agent boundary while keeping data operations independently testable.
- **Alternatives considered**: Direct SQLite access from agents or embedding SQL in routes/agents. Both violate the required boundary and duplicate persistence rules.

### Agent orchestration and provider fallback

- **Decision**: The Orchestrator classifies a request and delegates to Task Agent, Planner Agent, or Summary Agent. The presence of `OPENAI_API_KEY` enables the OpenAI-backed interpretation path; absence selects a deterministic rule-based path. Validate model output against a small structured intent/result schema before side effects. Provider errors, invalid output, or unavailable credentials use supported fallback behavior; unsafe or ambiguous requests return a clarification response rather than applying a destructive or uncertain action.
- **Rationale**: Supported behavior remains available without credentials and tests need no external service. Structured validation prevents model output from becoming an unchecked task operation.
- **Alternatives considered**: Requiring an API key, making model calls responsible for persistence, or calling an external provider from every agent. These would compromise local usability, the repository boundary, and deterministic tests.

### Task selection, dates, and daily summary

- **Decision**: Store due dates as ISO `YYYY-MM-DD` date-only values and timestamps as ISO UTC values. Use the host's local calendar date for relative-date interpretation and daily summaries, with the clock/date injected into pure agent logic for tests. Rank incomplete tasks by overdue first, priority high-to-low, then nearest due date, with a stable tie-break. Report completed today, due today, and overdue incomplete tasks separately.
- **Rationale**: Date-only due dates match the task domain, and injected dates make behavior deterministic. The ranking and day-boundary behavior make the spec's outcomes testable.
- **Alternatives considered**: Persisting local timestamps for due dates or guessing an unsupported timezone/date. A named user timezone is outside the current single-user scope; deployment timezone is the documented default.

### REST and assistant API

- **Decision**: Expose REST CRUD at `/api/tasks` and `/api/tasks/{task_id}` with 201 for create, 200 for reads/updates, 204 for successful delete, 404 for unknown IDs, and 422 for invalid bodies. Expose natural-language input at `POST /api/assistant`, next-task selection at `GET /api/plan/next`, and daily summary at `GET /api/summary?date=YYYY-MM-DD` (date optional, defaults to today).
- **Rationale**: Conventional resource endpoints keep plain CRUD usable independently of agents. Separate assistant routes avoid conflating task resources with orchestration results.
- **Alternatives considered**: One endpoint for all operations or exposing each agent as a public endpoint. The latter leaks internal boundaries and complicates the public API. Assistant route shapes are an informed design choice because the feature spec does not prescribe paths.

### Testing and dependencies

- **Decision**: Use pytest, FastAPI `TestClient`, temporary file-backed SQLite databases, focused unit tests for parser/agent behavior, and integration tests for routes and agent delegation. Stub the OpenAI client for configured-key tests and cover no-key fallback; never make a live provider call in the normal suite. Include `fastapi`, `uvicorn`, `openai`, `pytest`, and `httpx` in the dependency plan.
- **Rationale**: File-backed temporary databases exercise real persistence across connections, and mocked provider calls make tests deterministic and credential-free.
- **Alternatives considered**: In-memory SQLite shared across threads or live LLM calls in the test suite; these introduce lifecycle complexity and nondeterminism.

## Assumptions and resolved unknowns

- The user-provided feature description and constitution resolve stack, entry point, UI shape, SQLite module, agent modules, tool path, provider credential name, fallback requirement, and test location.
- `OPENAI_API_KEY` presence selects the OpenAI provider; there is no second provider-selection setting in scope.
- Database location defaults to a file beside `main.py`, with an environment override for tests/deployment.
- The host's local timezone defines “today”; a user-configurable timezone is not in scope.
- FastAPI's request validation is surfaced as HTTP 422. Missing resource IDs return 404.
- API details and deterministic rule support are documented in `contracts/openapi.yaml` and remain implementable without exposing LLM internals.

## Sources

- Python 3.11 `sqlite3`: https://docs.python.org/3.11/library/sqlite3.html
- Python 3.11 `datetime`: https://docs.python.org/3.11/library/datetime.html
- FastAPI static files: https://fastapi.tiangolo.com/tutorial/static-files/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
