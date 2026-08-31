# Notification & Audit Service Specification

## Overview

The Notification & Audit Service sits between the Project Service and client-facing integrations. It reacts to milestone lifecycle changes and persists immutable records for compliance and collaboration workflows in a multi-tenant B2B SaaS context.

## Data Models

### AuditEntry

- id: string
- organisation_id: string
- project_id: string
- entity_type: string
- entity_id: string
- actor_user_id: string
- actor_ip: string
- event_type: enum
- previous_state: object
- new_state: object
- timestamp: datetime
- immutable: boolean = true

### NotificationRecord

- id: string
- organisation_id: string
- recipient_user_id: string
- project_id: string
- event_type: string
- message: string
- read_status: boolean
- created_at: datetime

## API Contracts

### POST /audit

Request:

{
  "organisation_id": "org-123",
  "project_id": "proj-456",
  "actor_user_id": "user-42",
  "actor_ip": "203.0.113.9",
  "event_type": "MILESTONE_UPDATED",
  "entity_type": "project",
  "entity_id": "proj-456",
  "previous_state": {"status": "ACTIVE"},
  "new_state": {"status": "ARCHIVED"}
}

Response: created audit entry object.

### GET /audit/:projectId

Query parameters:

- from: optional ISO datetime
- to: optional ISO datetime
- eventType: optional string

Response: array of audit entries for the project, scoped to org tenancy.

### GET /notifications/:userId

Response: unread notifications for the authenticated user within the same organisation.

### PATCH /notifications/:id/read

Response: updated notification record with `read_status=true`.

## Integration Points

- The Project Service emits lifecycle events when a project milestone is created, updated, or deleted.
- The Notification & Audit Service listens to these events and stores both immutable audit entries and notifications.
- All calls require tenant scoping and identity validation.

## Constraints

- Audit entries are immutable once written and cannot be updated or deleted by API consumers.
- Only the organisation owning the project may access project history or notifications.
- Validation must reject invalid event names, empty project IDs, and malformed timestamps.
- Copilot was used to help draft the initial data model and endpoint structure; final constraints and multi-tenant security choices were validated and adjusted by human judgment.
