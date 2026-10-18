---

description: "Executable implementation tasks for the Agentic To-Do App"
---

# Tasks: Agentic To-Do App

**Input**: Design documents from `specs/001-agentic-todo-app/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Required by FR-014 and the project constitution. Each story includes pytest coverage for its acceptance scenarios; tests must not require a live LLM provider.

**Organization**: Tasks are grouped by user story to support incremental implementation and verification.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the requested application and test layout and install the named runtime/test dependencies.

- [X] T001 Create the project package and test directory layout from `specs/001-agentic-todo-app/plan.md` with `main.py`, `agents/__init__.py`, `tools/__init__.py`, `tests/conftest.py`, and `tests/unit/`, `tests/integration/`, and `tests/contract/` directories.
- [X] T002 Add FastAPI, Uvicorn, OpenAI client, pytest, and httpx dependencies to `requirements.txt`; ensure the application can start without `OPENAI_API_KEY`.
- [X] T003 [P] Add setup, no-key launch, and pytest invocation instructions to `README.md`, including the required `uvicorn main:app --host 0.0.0.0 --port $PORT` command.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared SQLite persistence and the exclusive TaskRepository tool boundary before any user story.

**⚠️ CRITICAL**: All user-story work depends on these shared task operations and fixtures.

- [X] T004 Implement task schema initialization and connection lifecycle in `tools/repository.py`: `id` is a stable positive unique identifier; `title` is required and non-empty after trimming; `completed` defaults to `false`; `priority` is restricted to `high|normal|low` and defaults to `normal`; `due_date` is an optional ISO `YYYY-MM-DD` date; `created_at` is immutable ISO-8601 UTC; `completed_at` is an optional ISO-8601 UTC timestamp set on completion and cleared on reopen.
- [X] T005 Implement `TaskRepository` create, get, list, update, and delete operations in `tools/repository.py`, using parameterized SQL, short-lived SQLite connections, transaction rollback on failure, and explicit connection closing; invalid updates must leave records unchanged and missing IDs must have a consistent not-found result.
- [X] T006 Implement explicit agent-facing task tool functions in `tools/repository.py` that delegate to `TaskRepository` and expose task values/results only, never SQLite connections or SQL execution.
- [X] T007 [P] Add temporary file-backed SQLite fixtures and a frozen/injectable date fixture in `tests/conftest.py` for isolated persistence, local-date, and agent tests.
- [X] T008 Add repository pytest coverage in `tests/unit/test_repository.py` for create/get/list/update/delete, required non-empty title, allowed priority enum/default, nullable valid ISO date, completion timestamp set/clear, rejected update rollback, and persistence after closing and reopening a file-backed database.

**Checkpoint**: Shared storage and tool functions exist; agents have no direct database interface.

---

## Phase 3: User Story 1 - Manage Tasks (Priority: P1) 🎯 MVP

**Goal**: Deliver a single-page task list where users can create, view, edit, complete, reopen, and delete persisted tasks.

**Independent Test**: Start the app without an LLM key, load `/`, create a task, edit its title and priority, set a due date, complete and reopen it, delete it, and refresh to confirm persisted state after each operation.

### Tests for User Story 1

- [X] T009 [P] [US1] Add page-serving and task-list/create/edit/complete/reopen/delete acceptance tests in `tests/integration/test_ui.py`, including reload persistence and startup without an LLM key.
- [X] T010 [P] [US1] Add tests for task validation and completion lifecycle responses in `tests/integration/test_task_flows.py`, asserting empty titles and invalid priority/date values do not mutate data.

### Implementation for User Story 1

- [X] T011 [US1] Implement FastAPI app creation, startup schema initialization, configurable SQLite path, `/` HTML response, and user-facing task routes in `main.py` using `tools/repository.py`.
- [X] T012 [P] [US1] Build the single-page HTML task list, create/edit controls, completion/reopen actions, delete action, and clear empty/error states in `index.html`.
- [X] T013 [US1] Connect the interactions in `index.html` to the task routes from `main.py`; render current task title, completion state, priority, and due date and refresh state after every successful change.
- [X] T014 [US1] Add request validation and consistent not-found/error handling for the page's task actions in `main.py`; return errors without applying partial updates.

**Checkpoint**: User Story 1 is independently usable without an LLM key and persists task changes through reloads.

---

## Phase 4: User Story 2 - Add Tasks in Natural Language (Priority: P2)

**Goal**: Accept natural-language task instructions, delegate to Task and Planner agents, and remain functional through rule-based fallback.

**Independent Test**: With an empty database, submit “add buy milk tomorrow, high priority” and verify title, date, and priority; repeat with no key, with a mocked configured provider, and with ambiguous input that must request clarification without a write.

### Tests for User Story 2

- [X] T015 [P] [US2] Add rule-based parsing unit tests for supported create, update, complete, reopen, and delete phrases, relative dates, priorities, and ambiguous requests in `tests/unit/test_fallback.py`.
- [X] T016 [P] [US2] Add Task Agent tool-boundary and action tests for CRUD delegation in `tests/unit/test_task_agent.py`, verifying the agent only receives and invokes repository tool functions.
- [X] T017 [P] [US2] Add mocked-provider tests for valid structured intent, invalid provider output, provider failure, no-key selection, and configured-key selection in `tests/unit/test_llm_provider.py`.
- [X] T018 [P] [US2] Add natural-language create and clarification integration tests for `/api/assistant` in `tests/integration/test_orchestration.py`, verifying clarification never changes task data.

### Implementation for User Story 2

- [X] T019 [P] [US2] Implement the optional OpenAI client adapter, environment-based `OPENAI_API_KEY` selection, bounded provider timeout, and structured output validation in `agents/llm_provider.py`; provider absence or failure must be representable without preventing app startup.
- [X] T020 [P] [US2] Implement deterministic supported-intent and date/priority parsing in `agents/rule_based.py`; use injected local date and return clarification for unsupported or uncertain task meaning.
- [X] T021 [US2] Implement Task Agent create/update/complete/reopen/delete actions in `agents/task_agent.py` using only the agent-facing functions from `tools/repository.py`.
- [X] T022 [US2] Implement Planner Agent interpretation of task title, due date, and priority in `agents/planner_agent.py`; default omitted priority to normal and omitted due date to null, and do not invent uncertain dates.
- [X] T023 [US2] Implement request classification, provider/fallback selection, structured intent validation, and delegation to Task and Planner agents in `agents/orchestrator.py`; unsafe or ambiguous instructions must return clarification without side effects.
- [X] T024 [US2] Add the `/api/assistant` request/response route and normalized completed/clarification results in `main.py` by calling the Orchestrator.

**Checkpoint**: Natural-language task actions are testable via provider stubs and rule-based mode, and all agent data access passes through tools.

---

## Phase 5: User Story 4 - Use Task CRUD Integrations (Priority: P2)

**Goal**: Provide a stable, plain REST CRUD contract for clients independent of the HTML page and agent flows.

**Independent Test**: Use an HTTP client against the REST API to create, list, retrieve, patch, and delete a task; confirm response bodies/statuses match `contracts/openapi.yaml`, unknown IDs return 404, and invalid payloads return 422 without mutation.

### Tests for User Story 4

- [X] T025 [P] [US4] Add REST contract tests for collection and item CRUD, successful status codes, response schemas, and persisted values in `tests/contract/test_task_api.py`.
- [X] T026 [P] [US4] Add REST failure contract tests for unknown task IDs, empty patch, empty title, invalid priority, malformed date, and unchanged stored state in `tests/contract/test_task_api_errors.py`.
- [X] T027 [P] [US4] Add an OpenAPI contract consistency test for required paths, fields, enum/date constraints, and response codes in `tests/contract/test_openapi_contract.py`.

### Implementation for User Story 4

- [X] T028 [US4] Expose `GET /api/tasks`, `POST /api/tasks`, `GET /api/tasks/{task_id}`, `PATCH /api/tasks/{task_id}`, and `DELETE /api/tasks/{task_id}` as plain JSON REST operations in `main.py` using `tools/repository.py`.
- [X] T029 [US4] Define REST request/response validation and map created/read/updated/deleted/missing/invalid outcomes to 201/200/200/204/404/422 in `main.py`, consistent with `specs/001-agentic-todo-app/contracts/openapi.yaml`.
- [X] T030 [US4] Ensure REST task updates preserve omitted fields and atomically reject empty patches, blank titles, invalid priorities, and malformed dates in `tools/repository.py` and `main.py`.

**Checkpoint**: REST CRUD is independently usable by clients, follows its documented contract, and shares the same validated persistence layer as the page and agents.

---

## Phase 6: User Story 3 - Plan and Review the Day (Priority: P3)

**Goal**: Recommend the next incomplete task and provide a date-specific daily task summary.

**Independent Test**: Seed overdue, due-today, future, completed-today, and unscheduled tasks; request the next task and daily summary with a fixed local date; verify rank order, groups, and empty states with and without an LLM key.

### Tests for User Story 3

- [X] T031 [P] [US3] Add Planner Agent unit tests for overdue-first, high/normal/low priority, nearest due date, stable tie-break, and no-incomplete-task behavior in `tests/unit/test_planner_agent.py`.
- [X] T032 [P] [US3] Add Summary Agent unit tests for completed-today, due-today, overdue-incomplete groups, empty summaries, and requested-date handling in `tests/unit/test_summary_agent.py`.
- [X] T033 [P] [US3] Add next-task and daily-summary endpoint integration tests in `tests/integration/test_planning_summary.py`, including fixed-date results and no-key fallback behavior.

### Implementation for User Story 3

- [X] T034 [US3] Implement deterministic next-task ranking over repository tool results in `agents/planner_agent.py`: exclude completed tasks, rank overdue first, then priority high-to-low, then nearest due date, and resolve ties consistently.
- [X] T035 [US3] Implement daily completed-today, due-today, and overdue-incomplete calculations in `agents/summary_agent.py` using repository tool functions and an injected local calendar date.
- [X] T036 [US3] Extend `agents/orchestrator.py` to delegate next-task and summary requests to Planner and Summary agents without bypassing tools or requiring provider credentials.
- [X] T037 [US3] Add `GET /api/plan/next` and `GET /api/summary` routes in `main.py`; validate optional `date=YYYY-MM-DD`, default to local today, and return explicit empty recommendation and summary results.

**Checkpoint**: Planning and summaries work from real persisted task data and use deterministic date logic when no key is configured.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature, document operation, and confirm no-key and configured-provider behavior.

- [X] T038 [P] Add end-to-end tests covering task CRUD, UI serving, assistant delegation, planning, and summaries in `tests/integration/test_end_to_end.py`.
- [X] T039 [P] Document environment configuration, database path override, optional OpenAI credential, fallback scope, and single-user limitations in `README.md`.
- [X] T040 Verify all tests pass with `OPENAI_API_KEY` absent using `pytest` and fix regressions in the owning source/test files under `tests/`.
- [X] T041 Verify configured-provider tests pass with a mocked OpenAI adapter and no live provider call using `pytest tests/unit/test_llm_provider.py tests/integration/test_orchestration.py`.
- [X] T042 Validate all quickstart scenarios and the requested startup command, and document any platform-specific invocation notes in `specs/001-agentic-todo-app/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes package layout and dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories because every task action and agent tool requires shared persistence.
- **User Stories (Phases 3–6)**: Depend on the Foundation. US2 depends on the task operations from US1 for natural-language task actions. US3 depends on persisted tasks and Planner structure introduced in US2. US4 shares repository contracts and can be implemented after Foundation; coordinate `main.py` route ownership with US1.
- **Polish (Phase 7)**: Depends on all selected story phases.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundation; establishes end-user task operations and single-page MVP.
- **US2 (P2)**: Starts after Foundation; natural-language actions require the repository tools and Task operations; integrate sequentially after US1's task operations.
- **US4 (P2)**: Starts after Foundation; REST routes share task validation and repository operations. It can be developed independently of agent stories, but coordinate `main.py` route changes with US1 to avoid file conflicts.
- **US3 (P3)**: Starts after Foundation; planning/summary read task state and extend Planner/orchestrator components from US2, so complete after US2. Recommended single-developer order: US1, US2, US4, US3.

### Parallel Opportunities

- Setup: T003 can proceed alongside T001/T002 once the paths are established; keep dependency manifest ownership in T002.
- Foundation: T007 can proceed alongside repository implementation; repository tests (T008) require T004/T005 behavior to exist.
- US1: T009 and T010 can be written in parallel; T012 can be developed in parallel with backend route work if API response shape remains aligned.
- US2: T015–T018 are separate test files and can be prepared in parallel; T019 and T020 are independent modules; Task/Planner/Orchestrator integration follows their interfaces.
- US4: T025–T027 are separate contract test files; route tests and implementation must agree on the published contract.
- US3: T031–T033 are separate test files and can be prepared in parallel; Planner ranking and Summary calculations are separate agent modules, then wire through orchestrator/routes.
- Different story phases may be assigned to separate contributors only after Foundation, with explicit coordination for shared `main.py`, `agents/orchestrator.py`, and `agents/planner_agent.py` files.

### Parallel Execution Examples

```text
US1 tests: T009 + T010
US2 independent modules/tests: T015 + T016 + T017 + T018; T019 + T020
US4 contracts: T025 + T026 + T027
US3 tests: T031 + T032 + T033
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundation (T001–T008).
2. Complete US1 (T009–T014) to deliver the persisted single-page task manager.
3. Run US1 acceptance tests without `OPENAI_API_KEY`; validate refresh persistence and full CRUD lifecycle.
4. Stop for review/demo. US1 is the minimal useful app; natural-language, planning, and public REST contract coverage are subsequent increments.

### Incremental Delivery

1. Setup + Foundation → verified SQLite/task-tool boundary.
2. US1 → independently usable single-page task manager.
3. US2 → natural-language operations with provider and fallback paths.
4. US4 → documented REST CRUD integration surface.
5. US3 → next-task planning and daily summaries.
6. Polish → full pytest, quickstart, and both provider configurations validated.

### Definition of Done per Story

- Story acceptance tests pass with isolated temporary SQLite data.
- Agent workflows access tasks only through functions in `tools/repository.py`.
- Supported user flows pass without `OPENAI_API_KEY`; configured-provider tests use mocks.
- Each task in this file follows `- [ ] Tnnn [P?] [USn?] Description with file path` format.
