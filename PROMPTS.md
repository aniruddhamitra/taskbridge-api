# Prompt Engineering Documentation

## Prompt Chain

### 1. Project generation prompt
- Exact prompt: "Generate a Project model and a Project service with create, update status, get by team, and delete functions. Use a database."
- Copilot feature: Chat / code generation
- Technique: role-based + constraint
- Rationale: This created the unreviewed contractor code required by the assessment.

### 2. Standards setup prompt
- Exact prompt: "Create a standards file for a Python FastAPI multi-service project with security, tenant isolation, testing, and architecture rules."
- Copilot feature: Chat
- Technique: specificity + decomposition
- Rationale: It produced a reusable instruction file that would guide subsequent generation.

### 3. Spec drafting prompt
- Exact prompt: "Draft a 1-2 page technical specification for a Notification & Audit Service in a SaaS project tool. Include data models, API contracts, integration points, and constraints."
- Copilot feature: Chat + inline code generation
- Technique: few-shot + constraints
- Rationale: It gave a solid baseline, which I then corrected for multi-tenant and immutability requirements.

## Post-Generation Corrections

- Copilot initially generated a simplistic shared-memory project model without enough tenant guarding.
- I corrected this by explicitly requiring organisation-scoped data access and validation in the service layer.
- Copilot also defaulted to generic audit semantics; I added immutability enforcement and explicit actor IP handling.
