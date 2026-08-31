# Tool Strategy Reflection

## Feature Usage Log

1. Chat (baseline generation) — used to create the initial Project model and service scaffolding.
2. Inline code generation — used to draft the project service and validation structure quickly.
3. Multi-file editing — used to produce the service and documentation bundle coherently.
4. Test generation — used to write the six core validation and audit scenarios.
5. Review assistance — used to inspect inherited code for architectural and security issues.
6. Documentation generation — used to create the specification, PR description, and impact analysis.

## Scenario Responses

### Understanding a complex 600-line legacy service in an unfamiliar codebase before wiring a new service to it
Use Copilot Chat with codebase-aware summarisation. It can quickly identify large service boundaries, dependency graphs, and risky patterns before a developer commits to a new integration contract.

### Generating consistent, standards-compliant request-validation middleware across 10 existing route handlers
Use code generation with a reusable validation pattern and a strict prompt for shared DTO rules. This ensures one standardised validation approach across handlers instead of drift.

### Quickly verifying whether a JWT verification implementation correctly handles token expiry and signature tampering
Use Copilot Chat with a security-focused review prompt against the actual verification logic. The result gives a fast first-pass check, but final validation still needs code inspection and tests.

### Enforcing that all commits to main pass linting and test coverage thresholds automatically, with no human intervention
Use GitHub Actions or a CI workflow with enforced checks, not Copilot alone. Copilot can help generate the workflow, but the enforcement must be in the repository automation.

### Reviewing a contractor's AI-generated service module for security vulnerabilities before it reaches staging
Use a structured code review prompt in Copilot Chat that asks for attack-surface analysis, auth issues, and tenant isolation checks. This helps quickly highlight likely bad patterns.

### Ensuring Copilot follows multi-tenant data isolation rules consistently across all developers and sessions
Use a repository-level Copilot instruction file in `.github/copilot-instructions.md`. This is the most reliable way to keep the rules present in every session and generation request.

## Limitations Encountered

### 1. Missing tenant guard in generated code
Prompt: "Generate a Project model and a Project service with create, update status, get by team, and delete functions. Use a database."
What went wrong: the default result did not clearly enforce organisation-scoped access.
How detected: manual review and domain-specific tests.
How fixed: added explicit org validation and access guard logic.
What to do differently: prompt for multi-tenant security constraints explicitly and insist on repository/service isolation.

### 2. Audit immutability not enforced in initial design
Prompt: "Design audit and notification service with history and read status."
What went wrong: the first pass treated audit records as mutable.
How detected: review of API usage and test design for delete/overwrite attempts.
How fixed: added enforcement in the service layer and documented immutability constraints.
What to do differently: ask for compliance guardrails and no-update/no-delete rules in the first draft.

### 3. Event contracts were under-specified
Prompt: "Draft API contract for notifications and audit." 
What went wrong: the draft lacked required IP capture and retention concerns.
How detected: spec review and impact analysis on the new change request.
How fixed: revised the data contract and documented the privacy/security trade-offs.
What to do differently: explicitly ask for change-risk analysis and security review before accepting the contract.
