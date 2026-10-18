<!--
Sync Impact Report
Version change: unresolved scaffold → 1.0.0 (initial adoption)
Modified principles: none; five project principles established
Added sections: Architecture and Technology Constraints; Development Workflow
Removed sections: none; scaffold section placeholders replaced
Follow-up TODO: Confirm the original ratification date.
-->
# SpecKit Todo Constitution

## Core Principles

### I. Tool-Mediated Agent Data Access
Agents MUST access application data only through explicitly defined tool functions. Agents MUST NOT
read from or write to SQLite directly, bypassing those tools. Tool functions MUST enforce the
application's validation and persistence rules. This boundary makes data access auditable and
keeps agent behavior separate from storage concerns.

### II. Tests for Every Feature
Every feature MUST include automated pytest coverage for its expected behavior and relevant failure
cases. Changes to API, tool, or persistence contracts MUST include tests at those boundaries. The
pytest suite MUST pass before a change is considered complete. This keeps behavior verifiable as
features evolve.

### III. Simple, Readable Python
The service MUST use Python 3.11, FastAPI, and SQLite. Code MUST favor clear, direct implementations
and standard project patterns over unnecessary abstraction or dependencies. Complexity MUST be
justified by a concrete requirement. This keeps the service approachable and maintainable.

### IV. LLM-Independent Operation
The application MUST function both when an LLM API key is configured and when no key is available.
When an LLM is unavailable or unconfigured, the application MUST use a deterministic rule-based
fallback for supported behavior. Tests MUST verify both configured-LLM and fallback paths without
requiring a live provider. This ensures core usability and reliable local testing.

### V. Explicit, Testable Boundaries
FastAPI endpoints, agent tool functions, LLM integration, and SQLite persistence MUST communicate
through explicit interfaces. Each feature MUST define and test its observable inputs, outputs, and
failure behavior at the relevant boundaries. This makes components replaceable and behavior
diagnosable without weakening the tool-mediated data-access rule.

## Architecture and Technology Constraints

The application MUST be implemented with Python 3.11, FastAPI, and SQLite. Agentic components MUST
invoke tool functions for all application-data access. LLM-provider credentials MUST be optional
for startup and core supported operation; secrets MUST NOT be required by tests or committed to the
repository. The rule-based fallback MUST cover the behavior needed to keep the application usable
without an LLM API key.

## Development Workflow

Every feature change MUST add or update pytest tests. Before a change is complete, run the relevant
pytest suite and resolve failures caused by the change. Reviewers and authors MUST verify that agent
data access remains tool-mediated and that supported behavior works with and without an LLM API
key. Tests MUST use controlled or stubbed provider behavior rather than relying on external service
availability.

## Governance

This constitution is the governing standard for project design and delivery. Amendments MUST update
this document, explain their rationale, and include any necessary migration or compatibility notes.
Changes MUST be reviewed for compliance with these principles and constraints; deviations MUST be
explicitly justified and documented with the affected change.

Constitution versions MUST follow semantic versioning: MAJOR for incompatible governance changes,
MINOR for added principles or materially expanded requirements, and PATCH for clarifications and
non-semantic refinements. Compliance MUST be checked during feature and code review, with pytest
results used to verify test requirements.

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
