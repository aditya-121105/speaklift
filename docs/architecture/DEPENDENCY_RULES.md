# SpeakLift Backend: Dependency Rules

## Allowed Imports
- `app.api` MAY import `app.services`, `app.dependencies`, `app.schemas`, `app.core`.
- `app.services` MAY import `app.repositories`, `app.shared`, `app.core`, `app.ai`.
- `app.repositories` MAY import `app.models`, `app.db`, `app.schemas`.
- `app.ai` MAY import generic utilities, abstract AI interfaces, and internal `app.ai.schemas`.

## Forbidden Imports
- `app.models` MUST NEVER import from `app.services` or `app.repositories`.
- `app.schemas` MUST NEVER import from `app.services`.
- `app.repositories` MUST NEVER import from `app.services`.
- `app.db` MUST NEVER import from `app.models` (preventing initialization cycles). Instead, Alembic uses `app.models.__init__.py` for discovery.

## Circular Dependency Policy
Circular dependencies are explicitly forbidden. 

If Service A requires Service B, and Service B requires Service A, it indicates a domain modeling flaw. The solution is:
1. **Extraction**: Move the shared logic into a new Service C that both A and B can depend on.
2. **Dependency Inversion**: Service A defines an abstract Protocol, which Service B implements, breaking the direct import chain.

Python's `if TYPE_CHECKING:` block may be used *only* for type hints when objects refer to each other logically, but never for runtime execution flows. Moving imports inside method bodies to resolve circular dependencies is considered **technical debt** and should be refactored via structural extraction.

## Dependency Injection (DI) Rules
1. All complex service instantiation MUST occur via FastAPI's `Depends()` or the factory definitions located in `app/dependencies/engine.py`.
2. Hard-coding constructor arguments (`service = InterviewService(repo=MySqlRepo())`) inside API controllers is prohibited.
3. Repositories should be passed into Services as Python `typing.Protocol` interfaces, not concrete implementations, allowing for unit testing via Mocks.

## Singleton Rules
- **Stateful Connections**: Resources like the database connection pool (`engine`), HTTP clients (`httpx.AsyncClient`), and NLP language models (`spacy.load()`) MUST be singletons. 
- **Business Services**: Services (`InterviewReportService`, `MatchingEngine`) are inherently stateless and therefore safe to be instantiated transiently (per-request) or identically mapped as Singletons. Currently, they are transiently injected per API request via `Depends`.

## Service Lifetime
- **Request Lifetime (Scoped)**: `SessionLocal` (the database transaction). It opens at the start of the HTTP request and is closed upon resolution.
- **Transient Lifetime**: Business services and repositories are created fresh on every HTTP request by `get_execution_service()`, holding the current Request's DB Session.
- **Singleton Lifetime (Application)**: AI Embedding models, configurations (`settings`), and database connection pools (`engine`).
