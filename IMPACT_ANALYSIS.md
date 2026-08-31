# Scope Change Impact Analysis

## Change Request

Add a new milestone event type `MILESTONE_REOPENED`. This should trigger audit logging and notifications. Audit entries must also capture the actor's IP address.

## Files and Modules Affected

- `src/notifications/service.py` — audit and notification generation logic
- `src/notifications/model.py` — audit entry schema includes actor IP
- `src/notifications/controller.py` — request shape and response contracts
- `tests/test_notifications_service.py` — new tests for reopened milestone and IP capture
- `SPEC.md` — contract update for the new event type and field

## Change Nature

- Additive: new event type and notification handling are added without removing legacy states.
- Breaking: existing audit entry records may not include `actor_ip` unless migrated or default values are stored.
- Migration required: any persisted audit data created before this change should either default to `actor_ip` = null or be backfilled with a best-effort value.

## Security and Compliance Risks

- IP addresses are PII-like operational metadata and must be protected from unnecessary exposure.
- Retention period should be controlled to avoid indefinite storage.
- Access control must limit who can read or export audit entries containing IPs.

## Recommended Implementation Approach

1. Extend the audit schema to include `actor_ip` as a required field when the event is created.
2. Add event type validation to accept `MILESTONE_REOPENED` alongside existing lifecycle events.
3. Ensure notification logic triggers for reopened milestones by using the same project member fan-out logic.
4. Review retention and access controls before deployment.

## How Copilot Assisted This Analysis

- I prompted Copilot to enumerate likely code touchpoints for the new event type and identify migration risks.
- It produced a useful impact list for service, model, and tests.
- I validated the output by checking the real event flow and tightening the security and retention concerns manually.
