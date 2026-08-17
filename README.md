# TaskBridge API — Notification & Audit Service

## Overview

TaskBridge is a B2B SaaS project collaboration platform for distributed engineering teams. This repository contains the core microservices architecture, including the **Project Service** and the new **Notification & Audit Service**.

## Technology Stack

### Runtime & Language
- **Node.js** 18+ (LTS)
- **TypeScript** 5.0+ (strict mode)

### API & Web
- **Express.js** 4.18+ (HTTP framework)
- **Joi** 17.9+ (request validation)
- **uuid** 9.0+ (identifier generation)

### Database & Persistence
- **PostgreSQL** 14+ (primary data store)
- **TypeORM** 0.3+ (ORM layer)
- **typeorm-cli** (migrations)

### Testing & Quality
- **Jest** 29.5+ (unit & integration tests)
- **Supertest** 6.3+ (HTTP endpoint testing)
- **ts-jest** 29.1+ (TypeScript support for Jest)

### Development & DevOps
- **Nodemon** (development auto-reload)
- **ESLint** 8.40+ (linting)
- **Prettier** 2.8+ (code formatting)
- **dotenv** 16.0+ (environment management)

### Logging & Monitoring
- **Winston** 3.8+ (structured logging)
- **Morgan** 1.10+ (HTTP request logging)

## Architecture

This project follows a **multi-service, layered architecture**:

```
API Requests
    ↓
Controllers/Routes (Express)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database (PostgreSQL)
```

### Services

#### Project Service (`src/projects/`)
Manages project milestones and state. Emits events to the Notification & Audit Service via API integration.

**Key Responsibilities:**
- CRUD operations for projects
- Milestone state management (created, updated, closed)
- Multi-tenant isolation
- Input validation & error handling

#### Notification & Audit Service (`src/notifications/`)
Listens to Project Service state changes and maintains:
- **Audit Log**: Immutable records of all state changes with before/after snapshots
- **Notifications**: Real-time alerts to team members on project changes

**Key Responsibilities:**
- Receive audit events from Project Service
- Persist immutable audit entries
- Create notifications for relevant team members
- Expose audit history queries with filters
- Enforce multi-tenant isolation

## Project Structure

```
taskbridge-api/
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── projects/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── controllers/
│   ├── notifications/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── controllers/
│   ├── middleware/
│   ├── config/
│   ├── types/
│   └── app.ts
├── tests/
├── docs/
├── package.json
└── tsconfig.json
```

## Security Considerations

- **Multi-tenant Isolation**: Every query includes organization filter
- **Input Validation**: All incoming requests validated against Joi schemas
- **Authentication**: JWT tokens required; organization ID extracted from token
- **Immutability Enforcement**: Audit log entries cannot be modified post-creation
- **Error Handling**: No sensitive information leaked in error responses

## Contributing

Read [.github/copilot-instructions.md](.github/copilot-instructions.md) before using AI tools.
