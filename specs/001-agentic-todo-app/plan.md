# Implementation Plan: Agentic To-Do App

**Branch**: `001-agentic-todo-app` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification and implementation constraints supplied by the user.

## Summary

Build a single-user to-do service with a single-page HTML interface, REST task CRUD, and natural-language task operations. A FastAPI application in `main.py` serves the page and endpoints; SQLite persistence is isolated in `tools/repository.py`, whose agent-facing tool functions are the only route by which agents access task data. The Orchestrator delegates to Task, Planner, and Summary agents. Presence of `OPENAI_API_KEY` enables OpenAI-backed interpretation; deterministic rule-based behavior keeps supported flows available without a key. See [research.md](research.md), [data-model.md](data-model.md), and [contracts/openapi.yaml](contracts/openapi.yaml).

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: FastAPI, Uvicorn, OpenAI Python client (optional at runtime; credential selected by `OPENAI_API_KEY`), pytest, httpx for `TestClient`

**Storage**: SQLite via Python standard-library `sqlite3`; file path configurable, default beside `main.py`

**Testing**: pytest, FastAPI `TestClient`, temporary file-backed databases; stubbed provider tests

**Target Platform**: Cross-platform Python service; deployment shell must provide `PORT`

**Project Type**: Single-project web service with a server-served HTML page

**Performance Goals**: Local/small-deployment task workflow; no throughput or latency SLO specified. Keep SQLite operations bounded and provider calls time-limited.

**Constraints**: Single user; no authentication or sharing. Agents must use only repository tool functions for task data. Core supported flows must operate without an LLM API key. Due dates are calendar dates; host local date is used for relative dates and summaries. The required `uvicorn main:app --host 0.0.0.0 --port $PORT` command is POSIX-shell syntax.

**Scale/Scope**: One application process and one SQLite database for a single user's tasks; CRUD, natural-language add/update/complete/delete, next-task suggestion, daily summary, and one HTML page.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution requirement | Gate result | Design evidence |
|---|---|---|
| Python 3.11, FastAPI, SQLite | PASS | Technical Context and selected single-service structure use exactly this stack. |
| Agents access application data only through tool functions | PASS | `agents/` depend on tool functions in `tools/repository.py`; only repository code owns SQL and connections. |
| Every feature has pytest coverage | PASS | Tests are organized by unit, integration, and contract concerns under `tests/`; validation is defined in [quickstart.md](quickstart.md). |
| Works without LLM credentials using deterministic fallback | PASS | `OPENAI_API_KEY` is optional; rule-based behavior is the no-key route and provider failures are handled safely. |
| Explicit, testable boundaries and readable code | PASS | Separate route, agent, tool, and provider modules; contracts and data model define boundary behavior. |

No constitution deviations are required. Recheck after design: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-todo-app/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
main.py
agents/
├── __init__.py
├── orchestrator.py
├── task_agent.py
├── planner_agent.py
├── summary_agent.py
├── rule_based.py
└── llm_provider.py
tools/
├── __init__.py
└── repository.py
index.html
tests/
├── conftest.py
├── unit/
│   ├── test_repository.py
│   ├── test_task_agent.py
│   ├── test_llm_provider.py
│   ├── test_planner_agent.py
│   ├── test_summary_agent.py
│   └── test_fallback.py
├── integration/
│   ├── test_ui.py
│   ├── test_task_flows.py
│   ├── test_orchestration.py
│   ├── test_planning_summary.py
│   └── test_end_to_end.py
└── contract/
    ├── test_task_api.py
    ├── test_task_api_errors.py
    └── test_openapi_contract.py
requirements.txt
```

**Structure Decision**: Use the requested single-project layout with `main.py`, `agents/`, `tools/`, and `tests/` at the repository root. Keep the single page in `index.html`; no separate frontend build is needed. The API and UI call agent workflows through the orchestrator, while plain CRUD routes use the repository directly. Agents themselves receive only tool functions and never a database connection.

## Complexity Tracking

No constitution violations or unjustified complexity. The repository/tool boundary is explicitly required by the constitution and user request.
