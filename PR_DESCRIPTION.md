# Pull Request Description

## Summary

This change introduces the TaskBridge Notification & Audit Service alongside a remediated Project Service. The design preserves project lifecycle integrity while supporting compliance-oriented audit history and user notifications for milestone events.

## AI Tool Disclosure

Used Copilot features included Chat, inline code generation, and repository-aware suggestions. AI output was accepted for initial scaffolding and documentation drafts, but human review corrected security, validation, and immutability concerns. Estimated code mix: 60% AI-assisted scaffolding, 40% hand-written and corrected logic.

## Integration

The Project Service emits milestone lifecycle events; the Notification & Audit Service listens to these events and writes immutable audit records while distributing notifications to team members. The integration contract is a simple event payload: project ID, organisation ID, actor user, actor IP, previous state, new state, and event type.

## Testing Coverage

- team fan-out notifications
- audit creation on milestone update
- immutability enforcement
- history filtering by date range
- history filtering by event type
- tenant isolation for audit access

Known gaps: no external database or real JWT/auth integration was implemented in this local assessment version.

## Risk and Trade-off

The biggest trade-off is storing actor IPs for audit compliance versus the privacy risk of retaining operational metadata longer than necessary. The design chooses explicit retention controls and least-privilege access to reduce exposure.

## Self-Review Checklist

- architecture boundaries clear
- tenant scoping enforced
- audit immutability preserved
- tests cover critical flows
- documentation includes impact and prompt trace

## Peer Review Simulation

### Comment 1
- Location: `src/notifications/service.py`, `create_audit_entry`
- Action: validate `actor_ip` against allowed formats and reject unset values before writing
- Why: audit logs with missing or malformed IPs weaken compliance and incident response

### Comment 2
- Location: `src/projects/service.py`, `update_status`
- Action: centralise status-transition validation in a single policy object and add explicit transition tests
- Why: status logic is currently duplicated and easy to drift across service methods

### Comment 3
- Location: `SPEC.md`, API contract section
- Action: document a retention policy for audit and notification data and call out access controls by role
- Why: AI-generated specs often miss privacy and data lifecycle requirements that matter in production SaaS systems
