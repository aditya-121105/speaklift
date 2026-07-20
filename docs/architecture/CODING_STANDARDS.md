# SpeakLift Backend: Coding Standards

## 1. Naming Conventions
- **Files/Modules**: `snake_case` (e.g., `execution_service.py`).
- **Classes**: `PascalCase` (e.g., `InterviewExecutionService`).
- **Methods/Functions**: `snake_case` (e.g., `submit_answer()`).
- **Variables**: `snake_case` (e.g., `candidate_profile`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `START_TIME`).
- **Interfaces (Protocols)**: Usually named with the role (e.g., `ExecutionAnswerRepository`).

## 2. Folders and Structure
- **Domain Segmentation**: Group files by domain boundary rather than technical type where applicable (e.g., `app/services/interview_execution/` holds the service, its schemas, and its specific repository protocols).
- **Core**: Cross-cutting application lifecycle components go in `app/core/` (config, logging).

## 3. Repositories
- **Abstract via Protocol**: Expose capabilities via `typing.Protocol` (e.g., `InterviewSessionRepository`) in the service layer, while implementing them concretely in `app/repositories/`.
- **Method Names**: Use domain-driven intent names (`get_first_unasked_question`, `persist_answer`) rather than generic CRUD wrappers (`update_row`).

## 4. Services
- **Stateless**: All instance variables must be immutable dependencies injected at construction. Do not store request-specific state in `self`.
- **Dependency Injection**: Use constructor injection: `def __init__(self, repo: MyRepoProtocol):`.

## 5. Schemas
- **Pydantic First**: Use Pydantic V2 `BaseModel`.
- **Validation**: Rely on Pydantic `@field_validator` and `@model_validator` instead of custom procedural checks.
- **Strict Typing**: Always enforce explicit types `name: str`. Use `| None` or `Optional[...]` when a field is genuinely optional.

## 6. Enums
- Extend `str, Enum` to ensure JSON serialization natively functions in FastAPI (e.g., `class QuestionType(str, Enum):`).

## 7. Logging
- **Structured**: Use `import logging` configured by `app.core.logging`.
- **No Prints**: Never use `print()`.
- **Contextualize**: Pass variables into the log string `logger.info("Found %d items for user %s", count, user_id)` rather than using f-strings for the base logger invocation to preserve structured attributes.

## 8. Exceptions
- **Domain Exceptions**: Inherit from `SpeakLiftException` defined in `app/shared/exceptions.py`.
- **Status Mapping**: Global exception handlers in `app/core/exception_handlers.py` map these to appropriate HTTP responses (`404 Not Found`, `400 Bad Request`).
- **Do not leak stack traces**: End users should receive standard JSON error messages. Stack traces go to logs.

## 9. Testing
- **Framework**: `pytest`.
- **Mocking**: Use `unittest.mock.MagicMock` for isolating services.
- **Fixtures**: Define complex objects in `conftest.py` or local `@pytest.fixture` blocks.
- **Naming**: `test_<component>_<behavior>()` (e.g., `test_generate_report_session_not_found`).

## 10. Documentation
- **Docstrings**: Use Google-style or standard descriptive docstrings on public methods, classes, and modules.
- **ADRs**: Major structural decisions go into Architecture Decision Records.
- **Tracking**: Update `CHANGELOG.md` when delivering a feature. Update `docs/project_status.md` when introducing new subsystems.
