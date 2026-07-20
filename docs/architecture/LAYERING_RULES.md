# SpeakLift Backend: Layering Rules

The SpeakLift backend utilizes a strict N-Tier (Layered) architecture combined with Modular Monolithic domain boundaries. 

## Layer Responsibilities

### 1. API Layer (`app/api/`)
**Responsibility**: HTTP protocol handling, routing, deserialization, request validation, and response serialization.
- Maps external HTTP requests to internal Pydantic domain models.
- Invokes the appropriate Service using Dependency Injection.
- Catches known domain exceptions and formats them as standard HTTP errors (e.g., `404 Not Found`, `422 Unprocessable Entity`).

### 2. Business Services Layer (`app/services/`)
**Responsibility**: Implementation of all application business logic, orchestrating workflows, and maintaining domain state.
- Executes the core product features (e.g., matching algorithms, evaluation pipelines).
- Validates business rules.
- Interacts strictly with Repository protocols for data access.

### 3. Repository Layer (`app/repositories/`)
**Responsibility**: Database abstraction and persistence mechanisms.
- Performs all CRUD operations.
- Translates simple parameters into complex SQLAlchemy Query constructs.
- Prevents database implementation details from leaking into the Business Service layer.

### 4. Domain & ORM Models (`app/schemas/` and `app/models/`)
**Responsibility**: Defining the shape of data.
- **ORM Models**: Reflect the PostgreSQL schema via SQLAlchemy.
- **Domain Schemas**: Pydantic classes reflecting the immutable state of business aggregates.

---

## Allowed Interactions

- **API -> Service**: An API controller may instantiate (via DI) and invoke public methods on any business service.
- **Service -> Repository**: A service may interact with multiple repositories to load data and save aggregate states.
- **Service -> Service**: A service may call another service provided it does not create a circular dependency. Cross-domain interactions should be carefully managed.
- **Repository -> ORM**: Repositories query and construct ORM objects using SQLAlchemy sessions.

---

## Forbidden Interactions

- **API -> Repository**: API controllers MUST NEVER directly query or write to a repository. All operations must route through a Business Service.
- **Service -> Database (SQL)**: Services MUST NEVER emit raw SQL, import `SQLAlchemy` directly for querying, or directly mutate ORM states without repository intervention.
- **Repository -> Service**: Repositories MUST NEVER depend on business service logic. If a repository needs to trigger logic, the service must perform that trigger after the repository completes its data task.
- **ORM -> Anything**: ORM models (`app.models`) are passive data structures. They MUST NEVER contain external dependencies, side-effects, or complex calculated fields that require external resources.

---

## Anti-Patterns

- **"Fat" Controllers**: Placing logic like `if user.score > 80: return "Hire"` inside `app/api/v1/endpoints/`.
- **"God" Services**: A single service (e.g., `InterviewService`) performing HTTP requests, running NLP pipelines, building reports, and writing to the database directly.
- **ORM Leakage**: Returning `db.query(User).first()` directly to FastAPI which serializes it to JSON, exposing internal database column names to external consumers.
