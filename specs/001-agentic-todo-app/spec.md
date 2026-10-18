# Feature Specification: Agentic To-Do App

**Feature Branch**: `001-agentic-todo-app`

**Created**: 2026-10-18

**Status**: Draft

**Input**: User description: "Build a to-do app with natural-language task management, planning and daily summaries, plus standard task CRUD."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Tasks (Priority: P1)

A user views a single-page to-do app, creates tasks, edits task details, marks tasks complete, reopens them if needed, and deletes tasks. Tasks remain available after the user leaves and returns.

**Why this priority**: Reliable task capture and management are the essential value of a to-do app and provide the data needed by all other journeys.

**Independent Test**: Create a task, retrieve it in the task list, update its title, complete and reopen it, then delete it; confirm each state change is reflected in the list and remains consistent after reload.

**Acceptance Scenarios**:

1. **Given** a task list, **When** the user creates a task with a title, **Then** the task appears as incomplete.
2. **Given** an existing task, **When** the user changes its details or completion state, **Then** the list shows the updated task.
3. **Given** an existing task, **When** the user deletes it, **Then** it no longer appears in the task list.
4. **Given** a task created before a page reload, **When** the user returns to the app, **Then** the task and its current state are still available.

---

### User Story 2 - Add Tasks in Natural Language (Priority: P2)

A user describes a task in ordinary language, including optional due date and priority, and the app creates a task with the understood details. For example, “add buy milk tomorrow, high priority.” The Orchestrator delegates task creation to the Task Agent and planning interpretation to the Planner Agent. Agents access task data only through TaskRepository tool functions.

**Why this priority**: Natural-language capture reduces friction while preserving task management as a usable foundation if agent assistance is unavailable.

**Independent Test**: Submit natural-language requests with and without dates and priorities; verify the task title and any interpreted attributes, then repeat without an LLM API key and confirm the rule-based fallback provides supported behavior.

**Acceptance Scenarios**:

1. **Given** a request naming a task, **When** the user submits it, **Then** the app creates the task and confirms the interpreted title.
2. **Given** a request containing a recognizable due date or priority, **When** it is processed, **Then** the resulting task reflects those details.
3. **Given** a request whose meaning cannot be confidently interpreted, **When** it is processed, **Then** the app asks the user to clarify rather than silently creating a materially different task.
4. **Given** no LLM API key is configured, **When** the user submits a supported request, **Then** the app handles it with the rule-based fallback and remains usable.

---

### User Story 3 - Plan and Review the Day (Priority: P3)

A user can ask for a suggested next task and a daily summary. The Planner Agent recommends an incomplete task using due date and priority information; the Summary Agent reports the day's task status.

**Why this priority**: Planning and summaries help users decide what to do next, building on a persisted task list and natural-language interaction.

**Independent Test**: Seed tasks spanning incomplete, completed, due-today, and overdue states; request the next task and daily summary, and verify the recommendation and summary reflect the seeded tasks. Repeat without an LLM API key.

**Acceptance Scenarios**:

1. **Given** incomplete tasks with due dates and priorities, **When** the user requests a next-task suggestion, **Then** the app recommends one eligible task and explains the relevant reason.
2. **Given** there are no incomplete tasks, **When** the user requests a next-task suggestion, **Then** the app says there is no pending task to recommend.
3. **Given** tasks with activity or due dates relevant to today, **When** the user requests a daily summary, **Then** the summary distinguishes completed, due, and overdue tasks where applicable.
4. **Given** no LLM API key is configured, **When** the user requests planning or a summary, **Then** supported results are produced by the rule-based fallback.

---

### User Story 4 - Use Task CRUD Integrations (Priority: P2)

A user or client can create, read, update, and delete tasks through plain REST endpoints, receiving a clear response for successful operations and invalid requests.

**Why this priority**: Standard CRUD access supports direct integrations and makes task behavior independently verifiable beyond the page and agent workflows.

**Independent Test**: Exercise each CRUD operation through the REST interface, verify returned task state, and verify invalid identifiers and invalid input receive clear failure responses.

**Acceptance Scenarios**:

1. **Given** a valid task request, **When** a client creates, lists, retrieves, updates, or deletes a task, **Then** the response reflects the requested operation and persisted state.
2. **Given** an unknown task identifier, **When** a client retrieves, updates, or deletes it, **Then** the response clearly indicates that the task does not exist.
3. **Given** invalid task data, **When** a client submits a create or update request, **Then** the app rejects it without changing the stored task.

### Edge Cases

- A natural-language request omits priority or due date; the task is created with a normal priority and no due date unless the user later sets them.
- A date phrase cannot be interpreted reliably; the app asks for clarification and does not invent a date.
- The requested task has already been deleted or does not exist; the app reports that it cannot perform the requested operation.
- The user requests a daily summary when there are no tasks; the app returns a concise empty-state summary.
- All tasks are complete; the planner does not recommend a completed task.
- The LLM provider is unavailable, misconfigured, or returns unusable output; the app falls back to supported rule-based behavior and reports when it cannot safely interpret the request.
- A client submits an invalid priority or malformed date; the task is not changed and the client receives a validation error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create, view, update, complete, reopen, and delete tasks from the single-page app.
- **FR-002**: The app MUST persist tasks and their current state so they remain available after a page reload or service restart.
- **FR-003**: Users MUST be able to submit natural-language task requests and receive a confirmation of the interpreted task details.
- **FR-004**: The app MUST identify a task title and recognize supported due-date and priority expressions in natural-language requests.
- **FR-005**: The app MUST ask for clarification when a request cannot be safely interpreted, rather than silently applying an uncertain date or task action.
- **FR-006**: The Orchestrator MUST delegate task creation, updates, completion, reopening, and deletion to the Task Agent; due-date and priority interpretation and next-task suggestions to the Planner Agent; and daily summaries to the Summary Agent.
- **FR-007**: Agents MUST access, create, update, complete, and delete task data only through TaskRepository tool functions; they MUST NOT access the task store directly.
- **FR-008**: The Planner Agent MUST set a task's priority and due date when these can be determined from the user's request, and MUST suggest an incomplete next task when asked.
- **FR-009**: The Summary Agent MUST provide a daily summary that distinguishes completed, due, and overdue tasks where applicable.
- **FR-010**: The app MUST remain usable without an LLM API key by providing supported natural-language, planning, and summary behavior through a rule-based fallback.
- **FR-011**: The app MUST allow the LLM provider to be selected through an environment variable and MUST not require provider credentials to start or use supported fallback behavior.
- **FR-012**: The app MUST provide plain REST endpoints for task create, list, retrieve, update, and delete operations.
- **FR-013**: The app MUST return clear validation and not-found responses for invalid task requests without applying unintended changes.
- **FR-014**: The delivered feature MUST include pytest tests for page task flows, REST CRUD, agent-to-tool data access, planning and summaries, and operation with and without an LLM API key.
- **FR-015**: The deliverable MUST include a requirements.txt dependency manifest and support the requested startup command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.

### Key Entities *(include if feature involves data)*

- **Task**: A user action to complete, with a title, completion state, priority, optional due date, and creation or completion timing as needed to support summaries.
- **Natural-Language Request**: A user's task-management, planning, or summary instruction and the app's resulting action or clarification.
- **Task Recommendation**: A suggested incomplete task with a concise reason based on its urgency and priority.
- **Daily Summary**: A date-specific overview of completed, due, and overdue tasks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, users can create, edit, complete, reopen, and delete a task through the page, with each result visible immediately and retained after reload.
- **SC-002**: At least 9 of 10 supported natural-language task requests produce the intended action and task details.
- **SC-003**: All five task actions—create, retrieve, update, complete, and delete—succeed in acceptance testing, while invalid or missing-task requests are rejected without unintended changes.
- **SC-004**: In every seeded daily-task scenario, the summary accounts for completed-today, due-today, and overdue tasks, and the next-task suggestion is incomplete or the app correctly reports none is available.
- **SC-005**: For requests that require clarification, at least 9 of 10 do not create or change a task in a way the user did not intend.
- **SC-006**: Users can open the task page and complete a basic task-creation journey without installing separate client software.

## Assumptions

- The app is a single-user local or small-deployment task manager; multi-user accounts, authentication, and sharing are out of scope unless added later.
- Priority uses the levels high, normal, and low. If omitted, it defaults to normal; omitted due dates remain unset.
- Relative dates such as “tomorrow” are interpreted using the service's local calendar date. Ambiguous or unsupported dates require clarification.
- A next-task suggestion considers incomplete tasks, preferring overdue tasks first, then higher priority, then nearer due date; ties are resolved consistently.
- A daily summary covers the current local calendar day and reports completed today, due today, and overdue incomplete tasks.
- The delivery constraints supplied by the user are binding for planning: Python 3.11, FastAPI, SQLite, a single HTML page served by the service, an environment-selected LLM provider, a TaskRepository tool layer for all agent data access, pytest coverage, requirements.txt, and the specified Uvicorn startup command.
- The rule-based fallback is expected to handle common, explicitly supported task commands and summary/planning behavior; it is not expected to understand arbitrary language as broadly as an LLM.
