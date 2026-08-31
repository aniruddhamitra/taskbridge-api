The Project Service and Notification & Audit Service are separate domain boundaries. The Project Service owns project lifecycle state and emits milestone events, while the Notification & Audit Service consumes those events and writes immutable audit history and user notifications.

Requests enter through a service/controller layer, which validates tenant ownership and payload shape before calling the repository or event-handling logic. Each layer keeps domain responsibilities explicit instead of mixing persistence and API logic.

From an inbound API request, the flow is: controller -> service -> repository for project state -> event emission -> audit record creation -> notification fan-out -> persistence in the relevant service domain store.

This architecture suits a multi-tenant B2B SaaS application because it makes organisation ownership explicit, isolates failure domains, and keeps audit records immutable for compliance needs.

Key design decisions include tenant-scoped access checks, strong payload validation, and a clear separation between mutable project state and immutable audit logs. The main trade-off is added operational complexity versus higher trust and auditability for downstream services.
