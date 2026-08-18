# GitHub Copilot Instructions for TaskBridge API

## Purpose

This document defines the technology stack, architecture conventions, coding standards, and security rules for TaskBridge API. All developers using GitHub Copilot (or other AI tools)  follow these guidelines to ensure consistent, production-ready, and secure code.

---

## 1. Technology Stack (Canonical)

### Core Runtime
- **Node.js**: 18+ (LTS)
- **TypeScript**: 5.0+, strict mode enabled
- **Express.js**: 4.18+ for HTTP routing
- **TypeORM**: 0.3+ for database access (mandatory ORM, no raw SQL drivers)

### Database
- **PostgreSQL**: 14+ only (single source of truth for persistence)
- **TypeORM Migrations**: For all schema changes (no manual SQL)

### Validation & Type Safety
- **Joi**: 17.9+ for request/response schema validation
- **uuid**: 9.0+ for ID generation
- TypeScript interfaces for all API contracts (request/response)

### Testing
- **Jest**: 29.5+ (unit & integration tests)
- **Supertest**: 6.3+ (HTTP endpoint testing)
- **ts-jest**: 29.1+ (TypeScript support)
- **Minimum coverage**: 80% (enforced in CI)

### Logging & Observability
- **Winston**: 3.8+ for structured logging
- **Morgan**: 1.10+ for HTTP request logging
- All logs must include: timestamp, level, service name, correlation ID (if available), and context

### Code Quality
- **ESLint**: 8.40+ with TypeScript support
- **Prettier**: 2.8+ (auto-formatting on commit)
- **.prettierrc** and **.eslintrc.json** are source of truth
- Linting must pass before merge (enforced in CI)

---

## 2. Architecture & Layering

### Mandatory Layered Architecture

Every service follows this strict separation:

```
┌─────────────────────────────────────────┐
│ Controller / Route Handler (Express)    │
│ • Parse HTTP request                    │
│ • Delegate to Service layer             │
│ • Format & send HTTP response           │
│ • Status code mapping                   │
└────────────────┬────────────────────────┘
                 │ (calls)
┌────────────────▼────────────────────────┐
│ Service Layer (Business Logic)          │
│ • Enforce business rules                │
│ • Coordinate across repositories        │
│ • Validate inputs (with Joi schemas)    │
│ • Throw specific, semantic errors       │
│ • Emit events (e.g., to audit service)  │
└────────────────┬────────────────────────┘
                 │ (uses)
┌────────────────▼────────────────────────┐
│ Repository Layer (Data Access)          │
│ • Query via TypeORM entities only       │
│ • No raw SQL; no database drivers       │
│ • Single source of queries per entity   │
│ • Support sorting, pagination, filters  │
└────────────────┬────────────────────────┘
                 │ (uses)
┌────────────────▼────────────────────────┐
│ Database (PostgreSQL)                   │
└─────────────────────────────────────────┘
```

### Naming Conventions

- **Controllers**: `<Entity>Controller.ts` (e.g., `ProjectController.ts`)
- **Services**: `<Entity>Service.ts` (e.g., `ProjectService.ts`)
- **Repositories**: `<Entity>Repository.ts` (e.g., `ProjectRepository.ts`)
- **Models/Entities**: `<Entity>.ts` (e.g., `Project.ts`, `AuditLog.ts`)
- **Type definitions**: `<Feature>.types.ts` or centralized `types/index.ts`

### Directory Structure (Per Service)

```
src/<service-name>/
├── models/
│   └── <Entity>.ts              # TypeORM entity definition
├── repositories/
│   └── <Entity>Repository.ts    # Data access layer
├── services/
│   └── <Entity>Service.ts       # Business logic
├── controllers/
│   └── <Entity>Controller.ts    # HTTP handlers
├── dto/
│   └── <Entity>.dto.ts          # Request/response contracts
└── routes.ts                    # Route definitions
```

---

## 3. Coding Standards

### TypeScript Strict Mode

All files must have:
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Type Definitions

✅ **DO THIS:**
```typescript
interface CreateProjectRequest {
  name: string;
  description: string;
  orgId: string;
}

interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
}

async createProject(req: CreateProjectRequest): Promise<ProjectResponse>
```

❌ **DO NOT DO THIS:**
```typescript
async createProject(req: any): Promise<any>
async createProject(req: { [key: string]: any }): Promise<{ [key: string]: any }>
```

### Input Validation with Joi

✅ **REQUIRED:** All incoming requests must be validated.

```typescript
import Joi from 'joi';

const createProjectSchema = Joi.object({
  name: Joi.string().required().min(1).max(255),
  description: Joi.string().optional().max(1000),
  orgId: Joi.string().uuid().required(),
});

app.post('/projects', async (req, res) => {
  const { error, value } = createProjectSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.details[0].message });
  }
  // Use `value` (sanitized input)
  const result = await projectService.create(value);
  res.json(result);
});
```

### Error Handling

✅ **REQUIRED:** Use specific, semantic error classes.

```typescript
export class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public errorCode: string
  ) {
    super(message);
  }
}

export class NotFoundError extends AppError {
  constructor(entity: string, id: string) {
    super(404, `${entity} with ID ${id} not found`, 'NOT_FOUND');
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(401, message, 'UNAUTHORIZED');
  }
}

// In controller:
try {
  const project = await projectService.getById(projectId);
  res.json(project);
} catch (error) {
  if (error instanceof AppError) {
    res.status(error.statusCode).json({ 
      error: error.message, 
      code: error.errorCode 
    });
  } else {
    res.status(500).json({ error: 'Internal server error', code: 'INTERNAL' });
  }
}
```

### Structured Logging

✅ **REQUIRED:** Use Winston for all logging.

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
  ],
});

// Usage:
logger.info('Project created', {
  projectId: project.id,
  orgId: project.orgId,
  action: 'CREATE_PROJECT',
  userId: req.user.id,
});

logger.error('Failed to update project', {
  projectId: projectId,
  error: error.message,
  stack: error.stack,
});
```

### Documentation

✅ **REQUIRED:** JSDoc on all public methods and exported functions.

```typescript
/**
 * Creates a new project for an organization.
 * 
 * @param createProjectInput - Request payload with project details
 * @param orgId - The organization ID (from JWT token)
 * @returns Created project with full details
 * @throws {ValidationError} If input validation fails
 * @throws {UnauthorizedError} If user lacks permission
 */
export async createProject(
  createProjectInput: CreateProjectRequest,
  orgId: string
): Promise<ProjectResponse> {
  // implementation
}
```

---

## 4. Multi-Tenant B2B SaaS Security

### 4.1 Authentication & Authorization

#### JWT Token Structure (Required)

All endpoints except `/health` require a valid JWT in the `Authorization: Bearer <token>` header.

Token payload must include:
```typescript
{
  sub: string;           // User ID
  orgId: string;         // Organization ID (CRITICAL: used for all isolation)
  email: string;
  iat: number;           // Issued at
  exp: number;           // Expiration (max 24 hours)
}
```

#### Authorization Middleware (Required)

```typescript
// middleware/auth.ts
export async function authenticateJWT(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Missing token', code: 'MISSING_TOKEN' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    // Attach to request for downstream use
    req.user = { userId: decoded.sub, orgId: decoded.orgId };
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token', code: 'INVALID_TOKEN' });
  }
}

app.use(authenticateJWT);
```

### 4.2 Multi-Tenant Data Isolation (Critical)

❌ **NEVER allow users to access data outside their organization.**

✅ **EVERY query must filter by organization:**

```typescript
// ✅ Correct: Repository method includes orgId filter
async getProjectsByOrg(orgId: string, filters?: GetProjectsFilters) {
  return this.projectRepository.find({
    where: {
      orgId, // MANDATORY filter
      ...filters,
    },
  });
}

// ❌ WRONG: No orgId filter
async getAllProjects() {
  return this.projectRepository.find();
}

// ✅ Service layer enforces orgId (from JWT)
async getProjectsByOrg(orgId: string) {
  if (!orgId) throw new UnauthorizedError('Organization ID missing');
  return this.projectRepository.getProjectsByOrg(orgId);
}

// ✅ Controller passes orgId from token
app.get('/projects', authenticateJWT, async (req, res) => {
  const projects = await projectService.getProjectsByOrg(req.user.orgId);
  res.json(projects);
});
```

### 4.3 Input Validation (Defense Against Injection)

✅ **MANDATORY:** Validate all user input before database queries.

```typescript
// Use Joi schemas for all request bodies
const createProjectSchema = Joi.object({
  name: Joi.string().required().min(1).max(255),
  description: Joi.string().optional().max(1000),
  // Reject unknown properties
}).unknown(false);

// Validate before processing
const { error, value } = createProjectSchema.validate(req.body);
if (error) return res.status(400).json({ error: error.message });
```

### 4.4 Data Exposure Prevention

❌ **NEVER return sensitive fields:**
- `password` hashes
- API keys or secrets
- PII (except for the authenticated user's own data)
- Database internal IDs (use UUID instead)

✅ **Use DTOs to control response shape:**

```typescript
// models/Project.ts (TypeORM entity — all fields)
@Entity()
export class Project {
  @PrimaryColumn('uuid')
  id: string;

  @Column()
  orgId: string;

  @Column()
  name: string;

  @Column({ select: false }) // Exclude by default
  internalNotes: string;
}

// dto/Project.dto.ts (API response — safe subset)
export interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
}

// service: map entity to DTO
function toProjectResponse(project: Project): ProjectResponse {
  return {
    id: project.id,
    name: project.name,
    description: project.description,
    createdAt: project.createdAt,
  };
}
```

### 4.5 Immutable Audit Log (Compliance & Security)

✅ **REQUIRED:** Audit entries are write-once, never updated or deleted.

```typescript
// models/AuditLog.ts
@Entity()
export class AuditLog {
  @PrimaryColumn('uuid')
  id: string;

  @Column({ update: false }) // TypeORM: prevent updates
  eventType: string;

  @Column({ update: false })
  entityType: string;

  @Column({ update: false })
  entityId: string;

  @Column('jsonb', { update: false })
  beforeSnapshot: Record<string, any>;

  @Column('jsonb', { update: false })
  afterSnapshot: Record<string, any>;

  @Column({ update: false })
  actorUserId: string;

  @Column({ update: false })
  actorOrgId: string;

  @Column('timestamp', { update: false })
  createdAt: Date;
}

// service: enforce immutability
export class AuditLogService {
  async createAuditEntry(input: CreateAuditInput): Promise<AuditLog> {
    const entry = new AuditLog();
    entry.id = uuid();
    entry.eventType = input.eventType;
    entry.entityType = input.entityType;
    // ... populate all fields
    return this.auditLogRepository.save(entry);
  }

  // ❌ No update or delete methods exist
}
```

### 4.6 Secure Defaults

- **Environment Variables**: All secrets (database URL, JWT_SECRET, API keys) in `.env`, never committed
- **HTTPS Only**: All production APIs must use HTTPS (enforced at load balancer)
- **CORS**: Restrict to known origins only
- **Rate Limiting**: Implement on public endpoints (future enhancement)
- **SQL Injection Prevention**: Use TypeORM parameterized queries only; never string concatenation

---

## 5. Testing Expectations

### Minimum Coverage: 80%

```bash
npm test -- --coverage
```

### Test Categories

#### Unit Tests
- Service layer business logic
- Validation logic
- Error handling
- Data transformation (DTOs)

#### Integration Tests
- Controller → Service → Repository → Database flow
- Multi-tenant isolation (verify orgId filtering)
- Audit log immutability
- Error response formats

#### Test Template

```typescript
describe('ProjectService', () => {
  let service: ProjectService;
  let repository: MockProjectRepository;

  beforeEach(() => {
    repository = new MockProjectRepository();
    service = new ProjectService(repository);
  });

  describe('createProject', () => {
    it('should create a project and return it with ID', async () => {
      const input = { name: 'Test Project', orgId: 'org-123' };
      const result = await service.createProject(input);
      
      expect(result).toBeDefined();
      expect(result.id).toBeDefined();
      expect(result.name).toBe('Test Project');
    });

    it('should throw ValidationError if name is missing', async () => {
      const input = { orgId: 'org-123' }; // missing name
      
      await expect(service.createProject(input))
        .rejects
        .toThrow('Name is required');
    });

    it('should enforce multi-tenant isolation', async () => {
      const org1Project = await service.createProject({
        name: 'Org 1 Project',
        orgId: 'org-1',
      });
      
      // Attempt to retrieve with different orgId should fail
      await expect(
        service.getProjectById(org1Project.id, 'org-2')
      ).rejects.toThrow('Unauthorized');
    });
  });
});
```

---

## 6. Copilot Usage Guidelines

### ✅ When to Use Copilot

1. **Boilerplate code**: Express route handlers, TypeORM repository methods, test setup
2. **Type definitions**: Interface generation from data models
3. **Documentation**: JSDoc comments, README sections, architecture diagrams
4. **Refactoring suggestions**: Ask to simplify or optimize existing code
5. **Learning**: Understanding library APIs (e.g., TypeORM query builders)

### ❌ When NOT to Use Copilot (Always Review)

1. **Security logic**: JWT verification, authorization checks, encryption
2. **Database queries affecting multiple tenants**: Always verify orgId filtering
3. **Audit log operations**: Never allow deletes/updates; verify immutability
4. **Error handling**: Ensure errors don't leak sensitive data
5. **Validation schemas**: Define manually; review generated schemas carefully

### Review Checklist for AI-Generated Code

Before committing AI-generated code, manually verify:

- [ ] **Multi-tenant isolation**: All queries filter by `orgId`
- [ ] **Type safety**: No `any` types; strict mode compliant
- [ ] **Error handling**: Specific error types; no stack traces in production
- [ ] **Input validation**: Joi schema present; unknown properties rejected
- [ ] **Documentation**: JSDoc comments present and accurate
- [ ] **No secrets**: No API keys, passwords, or internal URLs hardcoded
- [ ] **Security**: No SQL injection risks; no data exposure in responses
- [ ] **Testing**: Test cases cover happy path, errors, and edge cases

### Prompt Best Practices

✅ **DO:**
- Provide context: "In a multi-tenant B2B SaaS app, generate..."
- Reference standards: "Follow the patterns in `/src/projects/services/ProjectService.ts`"
- Specify constraints: "Include Joi validation; enforce orgId filtering; add JSDoc"
- Ask for review: "Generate this code, then explain the security implications"

❌ **DON'T:**
- Use vague prompts: "Generate a service"
- Omit constraints: "Write a controller" (how will it handle errors?)
- Accept first output: Always review and test before committing
- Mix concerns: Keep prompts focused on one task

---

## 7. Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no feature change)
- `test`: Test additions/changes
- `docs`: Documentation
- `chore`: Build, dependencies, tooling

### Examples

```
feat(projects): add project milestone status update

- Add PUT /projects/:id/status endpoint
- Implement project state transition validation
- Emit audit event to notification service

Closes #42
```

```
fix(auth): fix JWT expiration check for token validation

- Token expiry was checked incorrectly (used > instead of <=)
- Add test case for expired token rejection

Fixes #51
```

---

## 8. Code Review Checklist (For Human Reviewers)

When reviewing PRs, check:

- [ ] Follows layered architecture (controller → service → repository)
- [ ] All queries include orgId filter (multi-tenant isolation)
- [ ] Input validation present (Joi schema)
- [ ] Error handling is specific (not generic HTTP 500)
- [ ] No data exposure in responses (use DTOs)
- [ ] Tests cover normal flow, errors, and edge cases
- [ ] JSDoc present on public methods
- [ ] Linting passes (`npm run lint`)
- [ ] No hardcoded secrets or internal details
- [ ] Audit log entries are immutable (no update/delete)

---

**Last Updated**: August 2026  
**Version**: 1.0  
**Maintained By**: Tech Lead, TaskBridge
