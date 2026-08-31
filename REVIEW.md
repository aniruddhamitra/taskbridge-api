# Project Service Review

## Summary

The inherited Project Service was generated quickly and did not meet the production standards required for multi-tenant SaaS use. It lacked proper repository/service separation, validation, and tenant isolation. The biggest risks were cross-tenant data access and unreviewed persistence logic.

## Findings

### 1. Missing tenant guard in data access
- Issue: `get_by_id` and update paths did not enforce organisation-level isolation in a robust, centralised manner.
- Where: `src/projects/repository.py`, `src/projects/service.py`
- Severity: Critical
- Impact: A user from one organisation could query or modify another organisation's project if the ID were guessed.
- Detection: Manual review of repository logic and security test design.
- Fix: Require organisation-scoped access in repository and service layer and reject mismatched org/project combinations.

### 2. No typed validation contract
- Issue: Request payloads were not validated consistently, and invalid statuses could pass through.
- Where: `src/projects/service.py`
- Severity: High
- Impact: Invalid state transitions could create inconsistent project lifecycle data.
- Detection: inspection of service methods and test review.
- Fix: Validate required fields, enum values, and list structure upfront.

### 3. Mixed responsibilities in service layer
- Issue: Repository, validation, and response shaping were intertwined.
- Where: `src/projects/service.py`
- Severity: Medium
- Impact: Harder to test and reason about, and introduces brittle coupling.
- Detection: architecture review against layered design expectations.
- Fix: Separate repository and controller logic and keep service orchestration explicit.

### 4. No structured error handling
- Issue: Service methods raised raw exceptions or failed silently in some cases.
- Where: `src/projects/service.py`
- Severity: High
- Impact: Invariant violations and access errors were not clearly surfaced or audited.
- Detection: manual review of error flows.
- Fix: Raise specific `ValueError` and `PermissionError` cases with clear semantics.

## Review Process

- Copilot was used to generate the initial Project model and service scaffolding.
- Human review identified that the generated code was structurally valid but failed the multi-tenant and production reliability requirements.
- Key areas that required human judgment were tenant isolation, explicit validation, and layer boundaries.

## Architectural & Security Issues Copilot Introduced That Required Human Judgment

- Copilot generated code quickly but did not recognise cross-tenant access hazards without a security-oriented prompt.
- The generated service assumed a single shared database context and did not centralise org ownership checks.
- This matters because downstream services such as the Notification & Audit Service depend on project records being trustworthy and isolated by tenant.
