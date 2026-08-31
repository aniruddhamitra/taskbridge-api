# Copilot Instructions for TaskBridge

## Stack and Architecture

- Use Python 3.12+ with FastAPI, SQLAlchemy ORM, Pydantic, and pytest.
- Maintain a multi-service layout: `src/projects/` for project domain logic, `src/notifications/` for notification and audit events.
- Keep service boundaries explicit: model -> repository -> service -> route/controller.
- Prefer typed DTOs, validation, structured logging, and explicit error handling.

## Security Rules

- Enforce multi-tenant isolation by organisation ID on every query and mutation.
- Do not expose raw tenant identifiers outside the owning org boundary.
- Validate all user inputs and reject invalid enum values or malformed IDs.
- Treat every audit record as immutable; no update/delete operations in service code.

## Testing Expectations

- Add pytest coverage for validation, tenant isolation, and audit immutability.
- Include both happy-path and failure-path tests.
- Keep tests deterministic and free from hidden global state.
