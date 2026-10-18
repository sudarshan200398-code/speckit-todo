# Data Model: Agentic To-Do App

## Task

A persisted user action with lifecycle state and optional planning metadata.

| Field | Type / representation | Required | Rules |
|---|---|---:|---|
| `id` | Integer identifier | Yes (generated) | Stable, unique, positive. |
| `title` | Text | Yes | Trim surrounding whitespace; reject empty values. |
| `completed` | Boolean | Yes | Defaults to `false`. |
| `priority` | Enum: `high`, `normal`, `low` | Yes | Defaults to `normal`; reject values outside the enum. |
| `due_date` | ISO date `YYYY-MM-DD` or null | No | Null means unscheduled; invalid calendar dates are rejected. |
| `created_at` | ISO-8601 UTC timestamp | Yes (generated) | Immutable after creation. |
| `completed_at` | ISO-8601 UTC timestamp or null | No | Set when completing; cleared when reopening; null while incomplete. |

### State transitions

- Create → incomplete, with a normal priority unless specified.
- Incomplete → completed: set `completed=true` and record `completed_at`.
- Completed → incomplete (reopen): set `completed=false` and clear `completed_at`.
- Update: change supplied editable fields only; preserve omitted fields. Invalid changes leave the record unchanged.
- Delete: remove the task; subsequent lookups report not found.

### Relationships and ownership

Tasks are single-user records in this feature; no user or sharing relation is modeled. `TaskRecommendation` and `DailySummary` are derived response values, not persisted entities.

## Natural-Language Request

An incoming instruction and normalized interpretation used for one orchestration operation.

| Field | Type / representation | Required | Rules |
|---|---|---:|---|
| `text` | String | Yes | Non-empty user-provided instruction. |
| `intent` | Enum-like value | Derived | Task CRUD, next-task planning, daily summary, or clarification. |
| `task_title` | String or null | Conditional | Required for task creation; must be non-empty. |
| `priority` | `high`, `normal`, `low`, or null | No | Only set when present or confidently parsed; default normal when creating a task. |
| `due_date` | ISO date or null | No | Only set when present or confidently parsed. |
| `clarification` | String or null | No | Present when a safe action cannot be determined; no side effect occurs. |

## Task Recommendation

A derived suggestion containing the selected incomplete task and a user-facing reason. Selection excludes completed tasks and orders overdue first, then priority (`high`, `normal`, `low`), then nearest due date; unscheduled tasks follow scheduled tasks after equal urgency, with a stable identifier tie-break. If no incomplete task exists, return an explicit no-recommendation result.

## Daily Summary

A derived result for one calendar date with three non-overlapping task groups/counts:

- **Completed today**: tasks whose completion timestamp falls within the requested local calendar day.
- **Due today**: incomplete tasks whose due date equals the requested day.
- **Overdue**: incomplete tasks whose due date precedes the requested day.

Empty groups are valid. The date defaults to the host's local calendar date; tests inject a fixed date.
