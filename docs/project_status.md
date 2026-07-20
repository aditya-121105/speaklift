# SpeakLift — Project Status Document

> **Living Document** | Last Updated: July 19, 2026 | Backend Milestone M2.2 Completed: Adaptive Interview System
>
> This document is the single source of truth for the SpeakLift project. It reflects the current state of the codebase as of the audit date and should be updated at the end of every sprint.

---

# 1. Project Overview

## What is SpeakLift?

SpeakLift is an AI-powered Interview and Viva Simulation Platform. Its stated mission is to help students, freshers, and job seekers transform their existing knowledge into communication confidence by simulating realistic interview experiences and providing actionable, AI-driven feedback.

The platform currently exists as a backend API only. No frontend, no voice pipeline, no real-time features. The core interview session loop — create a session, receive questions, submit answers — is functionally complete. The evaluation engine is partially built at the infrastructure level but does not yet produce evaluations from real interviews.

## Architecture

SpeakLift uses a **Modular Monolith** architecture. All backend logic lives in a single deployable FastAPI application, organised into clear, bounded domain modules. Module boundaries are maintained through the layered folder structure:

```
API Endpoints → Services → Repositories → SQLAlchemy Models → PostgreSQL
```

AI components (NLP, embeddings) are isolated behind singleton resource managers and domain-specific service sub-packages. This means they can be replaced or extracted into microservices without touching business logic.

The architecture was deliberately designed so that future services (Speech, Vision, Evaluation) can be split out without requiring schema or interface redesign. This is documented in ADR-004.

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10 |
| API Framework | FastAPI | >=0.137.1 |
| ORM | SQLAlchemy | >=2.0.51 |
| Migrations | Alembic | >=1.18.4 |
| Database | PostgreSQL | 16 |
| Validation | Pydantic / pydantic-settings | v2 |
| Auth | python-jose (JWT) + passlib (bcrypt) | Latest |
| NLP | spaCy | >=3.8.14 (en_core_web_sm model) |
| Embeddings | sentence-transformers | >=5.6.0 (BAAI/bge-base-en-v1.5) |
| Grammar Check | language-tool-python | >=3.4.0 |
| Text Stats | textstat | >=0.7.13 |
| Tokenisation | NLTK | >=3.9.4 |
| ASGI Server | Uvicorn | >=0.49.0 |
| DB Driver | psycopg (v3, binary) | >=3.3.4 |
| Containerisation | Docker / Docker Compose | postgres:16 image |
| Test Runner | pytest | >=9.1.1 |
| Package Manager | uv | Latest |

## Design Philosophy

1. **Layered architecture**: Strict separation between API, Service, Repository, and Model layers. No business logic in endpoints, no database queries in services.
2. **Repository pattern**: All database access is encapsulated in repository classes. Services never import SQLAlchemy queries directly.
3. **Singleton resource managers**: Expensive NLP models (spaCy, SentenceTransformer) are loaded once at runtime and shared via class-level caching.
4. **Domain schemas over ORM exposure**: Runtime domain objects (InterviewContext, InterviewPlan, CandidateProfile) are Pydantic models, not ORM models. This decouples AI logic from the persistence layer entirely.
5. **Provider abstraction readiness**: ADR-003 defines an LLM provider abstraction layer. The `LLMProvider` ABC is now implemented in `app/ai/llm/providers/`. Concrete provider implementations (Ollama, Gemini) are planned for Sprint C.5.
6. **Progressive enhancement**: The question bank currently uses metadata matching (skills/technologies arrays). The architecture documents that future versions will upgrade to vector similarity search without changing the public interface.

---

# 2. Folder Structure

## Root

```
/
├── backend/          Core backend application
├── docs/             Architecture docs, ADRs, requirements
├── frontend/         Empty — not started
├── infrastructure/   Docker Compose + AWS/nginx placeholders
├── pyproject.toml    Project metadata and dependencies
├── alembic.ini       Alembic configuration (script_location points to backend/alembic)
├── .env              Root-level environment file (used by alembic.ini)
└── uv.lock           uv lockfile for reproducible installs
```

## backend/

```
backend/
├── app/              Main application package
├── alembic/          Database migrations
├── scripts/          Developer utility scripts
├── tests/            Test suite
├── .env              Backend-specific environment variables
├── .env.example      Environment variable template
└── .python-version   Pins Python 3.10
```

## backend/app/

The primary application package. Contains all business logic.

```
app/
├── ai/               AI core infrastructure (Sprint C.2+)
├── api/              HTTP layer (routers and endpoints)
├── core/             Infrastructure concerns (config, security, NLP, DB)
├── db/               SQLAlchemy base and session factory
├── dependencies/     FastAPI dependency injection providers
├── models/           SQLAlchemy ORM models (database schema)
├── repositories/     Data access objects
├── schemas/          Pydantic models (request/response + domain objects)
├── services/         Business logic
├── shared/           Cross-cutting enums, exceptions, utilities
└── main.py           FastAPI application entry point
```

### backend/app/api/v1/endpoints/
**Purpose**: HTTP request handlers. Thin layer — validate input, call service, return response.
**Current files**: `auth.py`, `health.py`, `interview_sessions.py`, `resumes.py`
**Dependencies**: Services, dependencies (auth, database, storage), schemas

### backend/app/core/
**Purpose**: Application-wide infrastructure concerns.
**Current files**:
- `config.py` — Pydantic Settings reading from `.env` (now includes `STORAGE_BACKEND`, `STORAGE_LOCAL_ROOT`, `MAX_RESUME_SIZE_MB`)
- `security.py` — bcrypt hashing, JWT creation and decoding
- `nlp.py` — Singleton loader for spaCy `en_core_web_sm`
- `storage.py` — `StorageBackend` (abstract), `LocalStorageBackend` (concrete)
- `logging.py` — **Empty file** (placeholder)
- `database.py` — Re-exports `engine` and `SessionLocal` (thin wrapper over `db/session.py`)
- `exception_handlers.py` — Global FastAPI exception handlers (SpeakLiftException → HTTP)

### backend/app/db/
**Purpose**: SQLAlchemy engine, session factory, and base class.
**Current files**:
- `base.py` — `Base` (DeclarativeBase) + `TimestampMixin` (created_at, updated_at)
- `session.py` — Creates `engine` from `settings.DATABASE_URL`, creates `SessionLocal`

### backend/app/dependencies/
**Purpose**: FastAPI dependency providers for injection into endpoints.
**Current files**:
- `auth.py` — `get_current_user` — extracts JWT from Bearer header, verifies, returns User
- `database.py` — `get_db` — yields a `SessionLocal` instance, closes on exit

### backend/app/models/
**Purpose**: SQLAlchemy ORM models. Define the database schema.
**Current files**: `user.py`, `profile.py`, `interview_session.py`, `interview_question.py`, `interview_answer.py`, `interview_evaluation.py`, `answer_evaluation.py`, `question_bank.py`, `resume.py`
**Dependencies**: `app.db.base`, `app.shared.enums`

### backend/app/repositories/
**Purpose**: All database access. Services never query the DB directly.
**Current files**: `user_repository.py`, `interview_session_repository.py`, `interview_question_repository.py`, `interview_answer_repository.py`, `interview_evaluation_repository.py`, `answer_evaluation_repository.py`, `question_bank_repository.py`, `resume_repository.py`
**Dependencies**: SQLAlchemy Session, ORM models

### backend/app/schemas/
**Purpose**: Pydantic models for API request/response validation and runtime domain objects.
**Sub-packages**:
- `evaluation/` — `TextDocument`, `TextFeatureVector`
- `interview_engine/` — `CandidateProfile`, `JobProfile`, `InterviewContext`, `InterviewPhase`, `InterviewObjective`, `InterviewPlan`
**Current files**: `auth.py`, `interview_session.py`, `interview_question.py`, `interview_answer.py`, `interview_evaluation.py`

### backend/app/ai/  *(Sprint C.2 — new)*
**Purpose**: Exclusive home for all AI and ML logic. Business services in `services/` may call into this package, but no AI implementation lives inside `services/`.
**Architecture rule**: AI logic MUST live in `app/ai/`. This boundary prevents AI concerns from leaking into the business service layer.
**Sub-packages**:
- `shared/` — `types.py` (`EmbeddingVector`, `AIResult`, `AIRequest`), `exceptions.py` (full AI exception hierarchy), `constants.py` (thresholds, dims, LLM defaults)
- `document_processing/` — `DocumentExtractor` ABC, `DocumentExtractionService` ABC/impl, `DocumentContent`+`DocumentSection` schemas, `TextCleaner`, `SectionDetector`, `PDFPlumberExtractor`, `PyMuPDFExtractor`, `DOCXExtractor`
- `nlp/` — Processors, extractors, schemas, resource managers (skeletons)
- `ml/` — Models, inference, training, preprocessing (skeletons)
- `embeddings/` — `EmbeddingProvider` ABC, vectorizers, service skeleton
- `llm/` — `LLMProvider` ABC (with `LLMResponse`), prompts, routers, service (COMPLETED & FROZEN - Sprint C9.2). Includes:
  - **Prompt Infrastructure**: Versioned, immutable prompt aggregates.
  - **Providers**: `GeminiProvider` (Cloud), `OllamaProvider` (Local).
  - **LLMRouter**: Configuration-driven multi-provider routing and resilient stream locking.
  - **LLMService**: Centralized AI orchestration (JSON generation parsing, etc.).
  - **Dependency Injection Factory**: Wiring orchestration in `factory.py`.
  - **Configuration System**: Environment-driven fallback logic and quota strategies.
  - **Smoke Test & Integration Tests**: Verified via `smoke_test_ai.py` and robust pytest suite with rate-limit evasion.
  - **Production Hardening**: Deterministic API quotas, failover mechanisms, and empty-payload handling.

**Final AI Architecture Flow**:
```text
Business
↓
LLMService
↓
LLMRouter
↓
Gemini / Ollama
```
- `evaluation/` — Skeleton (Sprint C.5)
- `recommendations/` — Skeleton (Sprint C.6)
- `ranking/` — Skeleton (Sprint C.4)
- `utils/` — Skeleton (Sprint C.3+)

### backend/app/services/
**Purpose**: All business logic. Services orchestrate repositories, AI modules, and domain logic.
**Top-level files**: `auth_service.py`, `interview_session_service.py`, `interview_service.py`, `interview_answer_service.py`, `interview_question_generator_service.py`, `question_bank_service.py`
**Sub-packages**:
- `interview_engine/` — `InterviewContextBuilder`, `InterviewPlanner`, `QuestionSelector`
- `evaluation/` — Feature extractors, embedding manager, constants, keywords, utils
- `reporting/` — `InterviewReportService`, `schemas.py`, `ai_schemas.py`, `prompt_builder.py`

### backend/app/shared/
**Purpose**: Cross-cutting concerns shared across all modules.
**Current files**:
- `enums.py` — All domain enums
- `exceptions.py` — `UserAlreadyExistsError`, `InvalidCredentialsError`
- `responses.py` — **Empty file** (placeholder for standardised API response wrappers)

### backend/alembic/
**Purpose**: Database migration scripts managed by Alembic.
**versions/**: 4 migration files tracking the full schema history.

### backend/scripts/
**Purpose**: Developer utility scripts (not part of the application itself).
**Current files**: `seed_question_bank.py` (orchestration-only seed entry point), `test_question_generation.py` (debug script for question generation pipeline)

### backend/scripts/question_bank/
**Purpose**: Modular question bank seed package. Each file owns exactly one role's question collection and exposes a `QUESTIONS: list[QuestionBank]` variable.
**Design rule**: `seed_question_bank.py` imports and combines all `QUESTIONS` lists — it never contains question data itself.
**Current files**:
- `__init__.py` — package marker and documentation
- `common.py` — shared `create_question()` factory, constants, and path bootstrap
- `backend_developer.py` — Backend Developer questions
- `python_developer.py` — Python Developer questions
- `ai_ml_engineer.py` — AI/ML Engineer questions
- `data_scientist.py` — Data Scientist questions
- `cloud_engineer.py` — Cloud Engineer questions
- `devops_engineer.py` — DevOps Engineer questions

**Adding a new role**: Create one new file in this folder and import its `QUESTIONS` in `seed_question_bank.py`. Nothing else changes.

### backend/tests/
**Purpose**: Automated test suite.
**Current structure**: Only `tests/evaluation/` has tests. Two test files covering `StatisticsFeatureExtractor` and `VocabularyFeatureExtractor`.

### docs/
**Purpose**: Project documentation and architectural decisions.
**Current files**:
- `architecture/architecture-v1.md` — High-level architecture overview
- `architecture/sprint-roadmap.md` — 12-sprint development plan
- `architecture/api-contract-v1.md` — API contract specification
- `architecture/database-design-v1.md` — Original database design (partially diverged from implementation)
- `decisions/ADR-001 through ADR-004` — Framework, database, LLM abstraction, modular monolith decisions
- `requirements/project-vision.md` — Product vision and target users

### infrastructure/
**Purpose**: Deployment configuration.
**Current files**: `docker/docker-compose.yml` (PostgreSQL container only), `docker/backend.Dockerfile` (empty), `aws/` (empty), `nginx/` (empty)

### frontend/
**Purpose**: Frontend application. **Completely empty.**

---

# 3. Module Inventory

## app/main.py
**Purpose**: FastAPI application entry point.
**Status**: Complete (minimal and correct).
**Implementation**: Creates the `FastAPI` app instance with title/description, mounts the API router. No middleware, no startup/shutdown events, no CORS, no exception handlers.
**Missing**: CORS middleware, global exception handler, startup events (e.g. model warm-up), request logging middleware.

---

## app/core/config.py
**Purpose**: Centralised configuration loading from environment variables.
**Status**: Complete.
**Implementation**: Pydantic `BaseSettings` class reading `APP_NAME`, `APP_VERSION`, `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` from `.env`.
**Missing**: No `CORS_ORIGINS`, no `DEBUG` flag, no environment-specific profiles, no secrets rotation.

---

## app/core/security.py
**Purpose**: Password hashing and JWT operations.
**Status**: Complete for current needs.
**Implementation**: bcrypt via passlib, JWT creation and decoding via python-jose. Tokens contain `sub` (user_id as string), `exp`, and `type: "access"`.
**Missing**: Refresh token support, token revocation/blacklist, `is_active` check during decode.

---

## app/core/nlp.py
**Purpose**: Singleton loader for spaCy NLP model.
**Status**: Complete.
**Implementation**: `NLPResourceManager` with class-level `_spacy_model` cache. Loads `en_core_web_sm` on first call.
**Missing**: Error handling if model is not installed, async-safe loading for concurrent startup requests.

---

## app/core/logging.py
**Purpose**: Centralised logging configuration.
**Status**: Empty placeholder. No implementation.
**Missing**: Everything — structured logging setup, request ID injection, log level from config.

---

## app/db/base.py
**Purpose**: SQLAlchemy declarative base and timestamp mixin.
**Status**: Complete.
**Implementation**: `Base(DeclarativeBase)` + `TimestampMixin` providing `created_at`/`updated_at` with timezone-aware timestamps and `server_default=func.now()`.
**Note**: `updated_at` uses `onupdate=func.now()` which works correctly.

---

## app/db/session.py
**Purpose**: SQLAlchemy engine and session factory.
**Status**: Complete.
**Implementation**: `create_engine` with `echo=True` (logs all SQL — this should be disabled or made configurable for production). `SessionLocal` with `autocommit=False`, `autoflush=False`.
**Issue**: `echo=True` is hardcoded. In production this will flood logs.

---

## app/models/user.py
**Purpose**: User authentication model.
**Status**: Complete.
**Fields**: `id`, `email` (unique, indexed), `password_hash`, `is_active`, `is_verified`.
**Missing**: No `last_login_at`, no relationships defined (Profile, Sessions), no `is_superuser`.

---

## app/models/profile.py
**Purpose**: User profile / resume metadata.
**Status**: Minimal. Structural skeleton only.
**Fields**: `id`, `user_id` (FK, unique), `full_name`, `experience_level`.
**Missing**: `education`, `target_role`, `phone`, `linkedin_url`, `resume_url`. The database design document specifies significantly more fields. No relationship back to `User`.

---

## app/models/interview_session.py
**Purpose**: Represents one interview practice session.
**Status**: Complete for current scope.
**Fields**: `id`, `user_id`, `role`, `experience_level`, `duration_minutes`, `resume_id` (nullable int — no FK), `job_description`, `status`, `started_at`, `completed_at`.
**Missing**: `resume_id` has no foreign key constraint (Resume table doesn't exist yet). No SQLAlchemy relationships defined.

---

## app/models/interview_question.py
**Purpose**: Individual question within a session.
**Status**: Complete.
**Fields**: `id`, `interview_session_id`, `parent_question_id` (self-referential FK for follow-ups), `question_text`, `question_type` (PRIMARY/FOLLOW_UP), `question_category`, `planned_order`, `execution_path`, `is_asked`.
**Missing**: No `asked_at` timestamp, no relationships.

---

## app/models/interview_answer.py
**Purpose**: Candidate's answer to a question.
**Status**: Complete.
**Fields**: `id`, `interview_session_id`, `interview_question_id`, `transcript`, `answer_source` (TEXT/VOICE), `answer_duration_seconds`.
**Missing**: No `audio_url` for voice answers, no relationship to `InterviewQuestion`.

---

## app/models/interview_evaluation.py
**Purpose**: AI-generated evaluation scores for a completed session.
**Status**: Schema complete, pipeline not connected.
**Fields**: `id`, `interview_session_id` (unique FK with CASCADE), `technical_score`, `communication_score`, `behavioral_score`, `confidence_score`, `overall_score`, `strengths` (JSONB), `weaknesses` (JSONB), `recommendations` (JSONB), `evaluation_source`.
**Missing**: No relationship to `InterviewSession`. Score validation (no min/max constraints in the model).

---

## app/models/answer_evaluation.py
**Purpose**: Granular, per-answer evaluation scores including deterministic NLP metrics and AI feedback.
**Status**: Complete.
**Fields**: `id`, `interview_answer_id`, `overall_score`, `keyword_coverage`, `concept_coverage`, `completeness`, `grammar_score`, `readability_score`, `confidence_score`, `semantic_similarity`, `vocabulary_statistics`, `grammar_details`, `readability_details`, `confidence_details`, `semantic_details`, `strengths`, `weaknesses`, `recommendations`, `communication_clarity`, `communication_confidence`, `communication_tone`, `communication_feedback`, `engine_version`.

---

## app/models/question_bank.py
**Purpose**: Central repository of reusable interview questions with AI metadata.
**Status**: Complete and well-designed.
**Fields**: `id`, `role`, `experience_level`, `category`, `difficulty`, `question_text`, `skills` (JSON), `technologies` (JSON), `expected_concepts` (JSON), `has_follow_up`, `source`, `usage_count`, `is_active`.
**Notes**: The AI metadata fields (`skills`, `technologies`, `expected_concepts`) enable both metadata-based and future semantic retrieval. `usage_count` enables usage-weighted randomised selection. Well thought out.

---

## app/repositories/user_repository.py
**Purpose**: User database access.
**Status**: Complete for current scope.
**Methods**: `get_by_email`, `create`, `get_by_id`.
**Missing**: `update`, `delete`, `get_all` (admin use).

---

## app/repositories/interview_session_repository.py
**Purpose**: Interview session database access.
**Status**: Complete.
**Methods**: `create`, `get_by_id`, `get_by_user`, `get_by_id_and_user`, `save`.
**Notes**: `get_by_id_and_user` correctly enforces ownership — users cannot access other users' sessions.

---

## app/repositories/interview_question_repository.py
**Purpose**: Interview question database access.
**Status**: Complete.
**Methods**: `create`, `create_many`, `get_by_id`, `get_by_session`, `get_first_unasked_question`, `save`.
**Notes**: `get_first_unasked_question` is critical for the interview flow and correctly filters `is_asked=False` ordered by `execution_path` (Materialized Path architecture).

---

## app/repositories/interview_answer_repository.py
**Purpose**: Answer database access.
**Status**: Complete.
**Methods**: `create`, `get_by_id`, `get_by_question`, `get_by_session`.

---

## app/repositories/interview_evaluation_repository.py
**Purpose**: Evaluation database access.
**Status**: Complete.
**Methods**: `create`, `get_by_session`, `save`.

---

## app/repositories/answer_evaluation_repository.py
**Purpose**: Answer evaluation database access.
**Status**: Complete.
**Methods**: `create`, `get_by_id`, `get_by_answer_id`.

---

## app/repositories/question_bank_repository.py
**Purpose**: Question bank database access with intelligent retrieval logic.
**Status**: Complete and well-implemented.
**Methods**: `create`, `get_by_id`, `get_questions`, `find_best_questions`, `increment_usage_count`.
**Notes**: `find_best_questions` uses PostgreSQL array containment operators (`@>`) via SQLAlchemy to match questions against objectives. This is the most sophisticated repository in the codebase. `get_questions` orders by `usage_count ASC, random()` — ensuring least-used questions get priority.

---

## app/services/auth_service.py
**Purpose**: User registration and login business logic.
**Status**: Complete.
**Implementation**: `register_user` checks for duplicate email, creates `User` + `Profile` atomically in a single transaction with `db.flush()` before commit. `login_user` verifies password and returns JWT token.
**Missing**: Email verification flow, password reset, audit logging.

---

## app/services/interview_session_service.py
**Purpose**: Interview session lifecycle management.
**Status**: Complete for current scope.
**Methods**: `create_interview_session`, `get_interview_session`, `get_user_interview_sessions`.

---

## app/services/interview_service.py
**Purpose**: Core interview orchestration — the main interview loop.
**Status**: Functionally complete.
**Methods**: `start_interview` (generates questions on first call, sets status to IN_PROGRESS), `submit_answer` (saves answer, marks question asked, returns next question or completes session), `get_questions`, `get_answers`.
**Issues**: Uses `datetime.utcnow()` (deprecated in Python 3.12+). `get_answers` passes `session_id` as keyword arg `session_id` but `InterviewAnswerRepository.get_by_session` expects `session_id` positional — works but inconsistent.

---

## app/services/interview_answer_service.py
**Purpose**: Alternative answer submission service.
**Status**: Partially redundant with `interview_service.py`.
**Issue**: This service partially duplicates the answer submission logic in `InterviewService.submit_answer`. `InterviewAnswerService.submit_answer` does NOT mark the question as `is_asked=True` and does NOT advance to the next question. These are separate services implementing overlapping concerns. **Technical debt.**

---

## app/services/interview_question_generator_service.py
**Purpose**: Generate a set of interview questions from the question bank based on interview duration.
**Status**: Complete.
**Implementation**: `get_question_distribution` maps interview duration to per-category counts (3 tiers: ≤15 min, ≤30 min, 30+ min). Fetches questions from bank per category, creates `InterviewQuestion` records.
**Issues**: Uses `print()` for debug output — should use logger. Does not use the `InterviewPlanner` or `InterviewContextBuilder` — these are parallel implementations with overlapping responsibility.

---

## app/services/question_bank_service.py
**Purpose**: Question creation and retrieval from the question bank.
**Status**: Complete for current scope.
**Methods**: `create_question`, `get_questions`.
**Missing**: Update, deactivate, bulk import, admin management endpoints.

---

## app/services/interview_engine/interview_context_builder.py
**Purpose**: Build the `InterviewContext` runtime domain object.
**Status**: Functional placeholder implementation.
**Implementation**: `_build_candidate_profile` returns an empty `CandidateProfile()`. `_build_job_profile` returns only `role` and `experience_level`. Everything else is empty.
**Notes**: Marked in comments as "Temporary implementation. Resume Parsing Pipeline will populate this in a later sprint." The architecture is correct — the builder is the right pattern — but it currently produces empty context.

---

## app/services/interview_engine/interview_planner.py
**Purpose**: Generate a structured `InterviewPlan` from an `InterviewContext`.
**Status**: Complete as a deterministic rule-based planner.
**Implementation**: Creates 5 phases (Introduction, Projects, Technical, Behavioral, Closing) with time allocation weights (10%, 25%, 45%, 15%, 5%). Each phase gets `InterviewObjective` objects. Time is distributed proportionally with the last phase absorbing remainder.
**Notes**: The planner is not currently used in the actual interview flow. `InterviewService` calls `InterviewQuestionGeneratorService` directly, bypassing the planner entirely. **Architecture inconsistency.**

---

## app/services/interview_engine/question_selector.py
**Purpose**: Select questions from the question bank that satisfy an `InterviewPlan`.
**Status**: Implemented but bypassed.
**Issue**: `QuestionSelector` is not called anywhere in the live interview flow. `InterviewService` calls `InterviewQuestionGeneratorService` instead. This is a second parallel implementation. **Significant architectural inconsistency.**

---

## app/services/evaluation/embeddings/embedding_manager.py
**Purpose**: Singleton loader for sentence-transformer embedding model.
**Status**: Complete as infrastructure.
**Implementation**: `EmbeddingManager` class with `_embedding_model` cache. Loads `BAAI/bge-base-en-v1.5` on first call.
**Missing**: Not called from any service. The embedding model is loaded but never used in any pipeline.

---

## app/services/evaluation/feature_extractors/text/text_processor.py
**Purpose**: Convert raw interview text into a structured `TextDocument` using spaCy.
**Status**: Complete and well-implemented.
**Implementation**: Extracts tokens, lemmas, sentences, named entities, stop words, and content words (NOUN, PROPN, VERB, ADJ, ADV). Returns a `TextDocument` Pydantic model.

---

## app/services/evaluation/feature_extractors/text/statistics_feature_extractor.py
**Purpose**: Extract numerical statistical features from processed interview answers.
**Status**: Complete.
**Implementation**: Computes total_answers, total_words, unique_words, averages, vocabulary richness, empty/short/long answer counts, average duration.

---

## app/services/evaluation/feature_extractors/text/vocabulary_feature_extractor.py
**Purpose**: Extract vocabulary and lexical density features.
**Status**: Complete.
**Implementation**: Computes unique_lemmas, vocabulary_richness, average_lemma_length, content_word_count, stop_word_count, lexical_density, stop_word_ratio.

---

## app/services/evaluation/feature_extractors/text/utils.py
**Purpose**: Shared text utility functions.
**Status**: Complete.
**Implementation**: `TextUtils` class with normalize_text, tokenize_words, split_sentences, word_count, unique_word_count, average_word_length, average_sentence_length.
**Note**: This duplicates some functionality in `TextProcessor`. `TextProcessor` uses spaCy; `TextUtils` uses regex. The relationship between the two is unclear.

---

## app/services/evaluation/constants.py
## app/services/evaluation/keywords.py
## app/services/evaluation/utils.py
## app/services/evaluation/knowledge_base/__init__.py
**Status**: All **completely empty** placeholder files.

---

## app/shared/enums.py
**Purpose**: All domain enumerations.
**Status**: Complete.
**Enums**: `InterviewStatus`, `ExperienceLevel`, `QuestionType`, `QuestionCategory`, `DifficultyLevel`, `QuestionSource`, `AnswerSource`, `EvaluationSource`.

---

## app/shared/exceptions.py
**Purpose**: Custom domain exceptions.
**Status**: Minimal — only 2 exceptions defined.
**Missing**: `SessionNotFoundError`, `QuestionNotFoundError`, `EvaluationError`, `InvalidSessionStateError`. Currently most services raise generic `ValueError`.

---

## app/shared/responses.py
**Status**: **Empty placeholder.**
**Missing**: Standardised API response wrapper (`{ "success": true, "data": {}, "message": "" }`) as specified in `api-contract-v1.md`.

---

# 4. Database Status

## Migrations Chain

```
f0f592e2c169 (initial)
    → 02e119cac187 (interview_answers)
        → bd4b041b5ffe (interview_evaluations)
            → 0144ba5aca6b (question_bank metadata)
```

All 4 migrations are linear with no branches. Migration chain is clean.

## Table Status

| Table | Purpose | Relationships | Completion | Missing Fields | Notes |
|---|---|---|---|---|---|
| `users` | Authentication | → profiles, → interview_sessions | ✅ Complete | `last_login_at`, `is_superuser` | `echo=True` on engine will log all queries |
| `profiles` | User profile metadata | users.id (unique FK) | ⚠️ Skeleton | `education`, `target_role`, `phone`, `linkedin_url`, `resume_url` | Far fewer fields than database design doc specifies |
| `interview_sessions` | Session lifecycle | users.id (FK), → interview_questions | ✅ Complete | None critical | `resume_id` is an int with no FK — Resume table not yet created |
| `interview_questions` | Per-session questions | interview_sessions.id (FK), self-referential parent_question_id | ✅ Complete | `asked_at` timestamp | Uses `execution_path` for infinite depth adaptive queue injection |
| `interview_answers` | Candidate transcripts | interview_sessions.id (FK), interview_questions.id (FK) | ✅ Complete | `audio_url` | `answer_source` enum supports VOICE but no audio storage yet |
| `interview_evaluations` | AI evaluation results | interview_sessions.id (CASCADE FK, unique) | ✅ Schema complete | Score min/max constraints | Unique constraint ensures one evaluation per session |
| `question_bank` | Reusable question library | None | ✅ Complete | None | Most advanced table — JSON metadata supports future vector search |
| `resumes` | Resume file metadata | users.id (FK CASCADE) | ✅ Complete (Sprint C.1) | None | Stores file identity + storage metadata only. No AI/extracted content. |

## Key Design Observations

- **Primary keys are INTEGER**, not UUID. The database design document specified UUID. This is a divergence from the original design. Integer PKs are fine for this scale but may require a migration if global uniqueness is needed later.
- `interview_evaluations.interview_session_id` has `ondelete=CASCADE` — correct.
- `profiles.user_id` has a `UNIQUE` constraint — one profile per user enforced at DB level.
- `question_bank.skills` and `question_bank.technologies` are stored as `JSON` (not `JSONB`). This means they cannot be indexed efficiently. For future vector search, these should move to `JSONB` or a dedicated vector column.
- No indexes beyond the primary key and the unique email index on `users`. As data grows, `interview_sessions.user_id`, `interview_questions.interview_session_id`, and `interview_answers.interview_session_id` will need indexes.

## Future Tables (Not Yet Created)

| Table | Required By |
|---|---|
| `viva_sessions` | Viva mode |
| `user_progress` | Analytics dashboard |
| `session_analytics` | Progress tracking |
| `recommendations` | Personalised improvement plan |

---

# 5. API Status

## Base URL: `/api/v1`

### Health Endpoints

| Route | Method | Purpose | Status | Notes |
|---|---|---|---|---|
| `/` | GET | Welcome message | ✅ Complete | Returns static JSON |
| `/health` | GET | App health check | ✅ Complete | No actual health assertions |
| `/db-health` | GET | Database connectivity check | ✅ Complete | Executes `SELECT 1` |

### Auth Endpoints (`/auth`)

| Route | Method | Purpose | Status | Notes |
|---|---|---|---|---|
| `/auth/register` | POST | User registration | ✅ Complete | Creates User + Profile atomically |
| `/auth/login` | POST | Login + JWT | ✅ Complete | Returns `access_token` |
| `/auth/me` | GET | Get current user | ✅ Complete | Requires Bearer token |

**Missing from auth**: POST `/auth/refresh`, POST `/auth/logout`, POST `/auth/forgot-password`, GET `/auth/verify-email/{token}`

### Interview Session Endpoints (`/interviews`)

| Route | Method | Purpose | Status | Notes |
|---|---|---|---|---|
| `POST /interviews` | POST | Create session | ✅ Complete | Validates duration 15-60 min |
| `GET /interviews` | GET | List user sessions | ✅ Complete | Ordered by created_at DESC |
| `GET /interviews/{id}` | GET | Session detail | ✅ Complete | Returns full detail response |
| `POST /interviews/{id}/start` | POST | Start interview, get first question | ✅ Complete | Generates questions on first call |
| `POST /interviews/{id}/answer` | POST | Submit answer, get next question | ✅ Complete | Returns `interview_completed` flag |
| `GET /interviews/{id}/questions` | GET | Get all questions | ✅ Complete | Returns ordered list |
| `GET /interviews/{id}/answers` | GET | Get all answers | ✅ Complete | Returns answer list |

**Missing**: POST `/interviews/{id}/abandon`, GET `/interviews/{id}/evaluation`, POST `/interviews/{id}/evaluate`

### Ownership Enforcement
All interview endpoints correctly validate that the session belongs to the authenticated user via `get_by_id_and_user`. Returning 404 (not 403) for unauthorised access is a common security pattern to avoid information disclosure.

### Error Handling
All services raise `ValueError` for business logic errors. Endpoints catch `ValueError` and return `HTTP 404`. This is incorrect in some cases — e.g. a question not belonging to a session should be `HTTP 400` or `HTTP 403`, not `404`. There is no global exception handler in `main.py`.

### API Contract Divergence
The `api-contract-v1.md` specifies a standardised envelope `{ "success": true, "data": {}, "message": "" }`. The actual API returns raw Pydantic models without this envelope. `shared/responses.py` was intended to implement this but is empty.

---

# 6. Services Status

## AuthService
**Responsibilities**: User registration (with atomic User+Profile creation), password hashing, JWT generation and validation.
**Dependencies**: `UserRepository`, `security.py`, `Profile` model.
**Implementation**: ~95%
**Current Limitations**: No email verification, no refresh tokens, no password reset. Profile is created with only `full_name` — no skills or target role captured at registration.

---

## InterviewSessionService
**Responsibilities**: Create, retrieve, and list interview sessions.
**Dependencies**: `InterviewSessionRepository`, `InterviewSession` model.
**Implementation**: ~80%
**Current Limitations**: No session abandonment logic, no ability to update session metadata after creation.

---

## InterviewService
**Responsibilities**: Core interview loop orchestration. Start interview, advance through questions, submit answers, detect completion.
**Dependencies**: `InterviewSessionRepository`, `InterviewQuestionRepository`, `InterviewAnswerRepository`, `InterviewQuestionGeneratorService`.
**Implementation**: ~75%
**Current Limitations**:
- Uses deprecated `datetime.utcnow()`.
- Bypasses the `InterviewPlanner` and `QuestionSelector` that were built for this purpose.
- No follow-up question generation.
- No evaluation triggered on completion.
- `get_answers` has a parameter naming inconsistency.

---

## InterviewAnswerService
**Responsibilities**: Submit answers to questions.
**Dependencies**: `InterviewAnswerRepository`, `InterviewQuestionRepository`, `InterviewSessionRepository`.
**Implementation**: ~60%
**Current Limitations**: Does NOT mark questions as `is_asked=True`. Does NOT advance to next question. Partially duplicates `InterviewService.submit_answer`. Should be merged or clearly differentiated. **This service is not currently used by any endpoint.**

---

## InterviewQuestionGeneratorService
**Responsibilities**: Generate a set of interview questions from the question bank based on duration.
**Dependencies**: `QuestionBankRepository`, `InterviewQuestionRepository`.
**Implementation**: ~80%
**Current Limitations**:
- Does not use `InterviewPlanner` or `InterviewContext`.
- Does not use `QuestionSelector`.
- Uses `print()` instead of a logger.
- Does not increment `usage_count` atomically — increments in memory then relies on session commit.

---

## QuestionBankService
**Responsibilities**: Create and retrieve questions from the question bank.
**Dependencies**: `QuestionBankRepository`.
**Implementation**: ~50%
**Current Limitations**: No management API endpoints. No bulk import. No question deactivation endpoint. No admin-facing features.

---

## InterviewContextBuilder (interview_engine/)
**Responsibilities**: Build the `InterviewContext` runtime domain object from session data and (future) resume + JD parsing.
**Dependencies**: `InterviewSession`, `CandidateProfile`, `JobProfile`, `InterviewContext` schemas.
**Implementation**: ~20%
**Current Limitations**: Returns empty `CandidateProfile`. `JobProfile` has only `role` and `experience_level`. The builder exists and has the right interface, but produces no useful context. Not called from any endpoint.

---

## InterviewPlanner (interview_engine/)
**Responsibilities**: Generate a structured `InterviewPlan` from an `InterviewContext`.
**Dependencies**: `InterviewContext`, `InterviewPhase`, `InterviewObjective`, `InterviewPlan` schemas.
**Implementation**: ~85%
**Current Limitations**: None. It is fully integrated into the live `InterviewWorkflowService` orchestration flow.

---

## QuestionSelector (interview_engine/)
**Responsibilities**: Select questions from the question bank that satisfy an `InterviewPlan`.
**Dependencies**: `QuestionBankRepository`, `InterviewPlan`, `InterviewSession`.
**Implementation**: ~60%
**Current Limitations**: None. It is fully integrated into `InterviewWorkflowService`, successfully translates objectives to PostgreSQL JSON queries, and correctly fetches the best questions.

---

## TextProcessor (evaluation/feature_extractors/text/)
**Responsibilities**: Convert raw text into a structured `TextDocument` via spaCy.
**Dependencies**: `NLPResourceManager`, `TextDocument` schema.
**Implementation**: ~100%
**Notes**: Well-implemented and fully functional. Has unit tests.

---

## StatisticsFeatureExtractor (evaluation/feature_extractors/text/)
**Responsibilities**: Extract numerical text statistics from a list of `TextDocument` objects.
**Dependencies**: `TextDocument`.
**Implementation**: ~100%
**Notes**: Well-implemented and has unit tests passing.

---

## VocabularyFeatureExtractor (evaluation/feature_extractors/text/)
**Responsibilities**: Extract vocabulary and lexical density features.
**Dependencies**: `TextDocument`.
**Implementation**: ~100%
**Notes**: Well-implemented. The "test" in `test_vocabulary_feature_extractor.py` is a script (no assertions), not a proper test.

---

## EmbeddingManager (evaluation/embeddings/)
**Responsibilities**: Singleton loader for `BAAI/bge-base-en-v1.5` sentence transformer.
**Dependencies**: `sentence_transformers`.
**Implementation**: ~100% as infrastructure.
**Notes**: Model loading works correctly. However, this manager is **not called from anywhere in the application**. The evaluation pipeline that would use it has not been implemented.

---

## Evaluation Pipeline (evaluation/ — constants, keywords, utils, knowledge_base/)
**Status**: All files are **empty**. No implementation exists beyond the feature extractors.
**Missing**: Keyword matching logic, scoring rules, evaluation orchestrator, LLM integration, report generator.

---

# 7. AI Pipeline Status

## spaCy

**Model**: `en_core_web_sm`
**Loader**: `NLPResourceManager.get_spacy_model()` (singleton)
**Status**: Infrastructure complete. Model loads correctly.
**Used in**: `TextProcessor` → called from unit tests only. Not called from any interview answer flow.
**Capabilities enabled**: Tokenisation, lemmatisation, POS tagging, sentence segmentation, named entity recognition, stop word detection.
**Missing**: No pipeline hook for on-startup warm-up. First request that triggers NLP will have latency.

---

## Sentence Transformers

**Model**: `BAAI/bge-base-en-v1.5`
**Loader**: `EmbeddingManager.get_model()` (singleton)
**Status**: Infrastructure complete. Loads correctly.
**Used in**: Nowhere. The `EmbeddingManager` is defined but never called.
**Intended Use**: Semantic similarity scoring between candidate answers and expected concepts.
**Missing**: The entire semantic evaluation pipeline. The embedding model is a dependency that has no consumer yet.

---

## Evaluation Engine

**Status**: Partial infrastructure, no active pipeline.

What exists:
- `TextProcessor` — converts text → `TextDocument`
- `StatisticsFeatureExtractor` — extracts stats features
- `VocabularyFeatureExtractor` — extracts vocab features
- `TextFeatureVector` schema — rich feature vector definition with 20+ fields
- `InterviewEvaluation` model — schema ready to store scores
- `EmbeddingManager` — ready to produce embeddings

What is missing:
- `KeywordFeatureExtractor` — `keywords.py` is empty
- `ReadabilityFeatureExtractor` — not started (textstat is installed but not used)
- `GrammarFeatureExtractor` — not started (language-tool-python is installed but not used)
- `SemanticFeatureExtractor` — not started (would use `EmbeddingManager`)
- Feature fusion service — combines all feature vectors into `TextFeatureVector`
- Scoring rules engine — maps `TextFeatureVector` to domain scores
- Evaluation orchestrator — drives the full pipeline end-to-end
- Evaluation API endpoint — `POST /interviews/{id}/evaluate` not implemented
- LLM integration — for feedback generation (strengths, weaknesses, recommendations)

The `TextFeatureVector` schema already declares fields for `sentiment_score`, `readability_score`, `semantic_similarity_score`, `grammar_error_count`, `spelling_error_count` — all reserved as `None` for future use. The architecture is planned but the pipeline is not built.

---

## Interview Engine

**Status**: Fully integrated and validated end-to-end.

What exists:
- `InterviewContextBuilder` — integrated, builds context placeholders securely.
- `InterviewPlanner` — complete, generates a 5-phase plan with time allocation
- `QuestionSelector` — complete, selects questions per objective
- All runtime domain schemas — `InterviewContext`, `InterviewPlan`, `InterviewPhase`, `InterviewObjective`, `CandidateProfile`, `JobProfile`

What is connected:
- The live interview flow (`InterviewWorkflowService`) natively calls `MatchingEngine`, `InterviewPlanner`, and `QuestionSelector` to produce an `InterviewExecutionState`.

---

## Question Generation

**Status**: Rule-based only. Functional.

`InterviewQuestionGeneratorService` generates questions by pulling from the question bank based on category distribution and interview duration. This is a deterministic algorithm, not AI generation.

True AI question generation (via LLM, as specified in Sprint 3 of the roadmap) has not been started. `QuestionSource.AI` is defined in enums but no AI-generated questions exist.

---

## Question Bank

**Status**: Modular seed architecture implemented. 6 roles scaffolded with placeholder questions (18 total). All questions carry fully populated `skills`, `technologies`, and `expected_concepts` metadata.

**Seeded roles**:
- Backend Developer (FRESHER) — **30 production-quality questions** (reference implementation)
- Python Developer (FRESHER) — 3 placeholder questions
- AI/ML Engineer (FRESHER) — 3 placeholder questions
- Data Scientist (FRESHER) — 3 placeholder questions
- Cloud Engineer (FRESHER) — 3 placeholder questions
- DevOps Engineer (FRESHER) — 3 placeholder questions

**Backend Developer topic coverage**: Python · OOP · FastAPI · REST APIs · SQL · PostgreSQL · SQLAlchemy · Authentication · JWT · Docker · Git · HTTP · API Design · Error Handling · Performance · Caching · Async Programming · Testing · System Design

**Category distribution (Backend Developer)**: INTRODUCTION ×4 · PROJECT ×5 · TECHNICAL ×13 · ROLE_SPECIFIC ×5 · BEHAVIORAL ×3

**Difficulty distribution (Backend Developer)**: EASY ×10 · MEDIUM ×14 · HARD ×6

**Metadata status**: All seeded questions have non-empty `skills`, `technologies`, and `expected_concepts` arrays. `QuestionBankRepository.find_best_questions()` will now return results for objectives that match these arrays.

**Seed architecture**: The seed script is now an orchestration-only file. Role question data lives in `backend/scripts/question_bank/<role>.py`. The shared `create_question()` factory in `common.py` enforces consistent field population across all roles. Future semantic retrieval (embeddings, pgvector) can consume these metadata fields without schema changes.

---

## Resume/JD Parsing

**Status**: Resume Storage Foundation complete (Sprint C.1). Parsing not started.
**Architecture**: Designed. `CandidateProfile` and `JobProfile` domain schemas exist. `InterviewContextBuilder` provides graceful fallbacks for both.
**Resume Storage**: `Resume` ORM model, `ResumeRepository`, `ResumeService`, `LocalStorageBackend` all implemented and tested.
**Endpoints**: `POST /api/v1/resumes/upload`, `GET /api/v1/resumes`, `GET /api/v1/resumes/{id}`, `DELETE /api/v1/resumes/{id}`, `GET /api/v1/resumes/{id}/download`
**Missing**: Resume parsing pipeline (Sprint C.2), spaCy/NLP extraction, Candidate Profile enrichment.

---

## LLM Provider Layer

**Status**: Not started.
**Architecture**: Defined in ADR-003. Provider abstraction interface described.
**Missing**: `LLMProvider` abstract interface, Ollama adapter, OpenAI adapter, Gemini adapter, prompt templates, integration with question generation and evaluation services.

---

## Voice / Speech

**Status**: Not started.
**Architecture**: Whisper integration mentioned in architecture doc (Sprint 5 of roadmap).
**Missing**: Audio upload endpoint, Whisper integration, transcript storage, streaming support.

---

## Vision Analysis

**Status**: Not started. (Sprint 11 in roadmap)

---

# 8. Feature Progress

```
Authentication             ████████████████████  90%
  ├─ Register/Login        ████████████████████ 100%
  ├─ JWT Auth              ████████████████████ 100%
  ├─ Email Verification    ░░░░░░░░░░░░░░░░░░░░   0%
  └─ Refresh Tokens        ░░░░░░░░░░░░░░░░░░░░   0%

Interview Sessions         ████████████████░░░░  80%
  ├─ Create Session        ████████████████████ 100%
  ├─ List Sessions         ████████████████████ 100%
  ├─ Session Detail        ████████████████████ 100%
  ├─ Start Interview       ████████████████████ 100%
  ├─ Submit Answer         ████████████████████ 100%
  ├─ Session Abandonment   ░░░░░░░░░░░░░░░░░░░░   0%
  └─ Interview Completion  ██████████████░░░░░░  70%

Question Bank              ████████████████░░░░  75%
  ├─ Schema & Model        ████████████████████ 100%
  ├─ Repository Logic      ████████████████████ 100%
  ├─ Seed Architecture     ████████████████████ 100%  ← modular, 6 roles scaffolded
  ├─ Seed Data (full)      ████░░░░░░░░░░░░░░░░  20%  ← placeholder questions only
  ├─ AI Metadata Populated ████████████████████ 100%  ← all questions have metadata
  └─ Admin API             ░░░░░░░░░░░░░░░░░░░░   0%

Interview Engine            ████████████████████ 100%
  ├─ Context Builder       ████████████████████ 100%
  ├─ Interview Planner     ████████████████████ 100%
  ├─ Question Selector     ████████████████████ 100%
  └─ Live Flow Integration ████████████████████ 100%

Evaluation Engine          ████░░░░░░░░░░░░░░░░  25%
  ├─ Text Processor        ████████████████████ 100%
  ├─ Statistics Extractor  ████████████████████ 100%
  ├─ Vocabulary Extractor  ████████████████████ 100%
  ├─ Keyword Extractor     ░░░░░░░░░░░░░░░░░░░░   0%
  ├─ Readability Extractor ░░░░░░░░░░░░░░░░░░░░   0%
  ├─ Grammar Extractor     ░░░░░░░░░░░░░░░░░░░░   0%
  ├─ Semantic Extractor    ░░░░░░░░░░░░░░░░░░░░   0%
  ├─ Feature Fusion        ░░░░░░░░░░░░░░░░░░░░   0%
  ├─ Scoring Engine        ░░░░░░░░░░░░░░░░░░░░   0%
  └─ Evaluation API        ░░░░░░░░░░░░░░░░░░░░   0%

AI Core Infrastructure     ████████████████████ 100%  ← Sprint C.2 complete
  ├─ shared/ (types, exceptions, constants) ████████████████████ 100%
  ├─ document_processing/ (ABCs + schemas) ████████████████████ 100%
  ├─ nlp/         (skeletons)  ████████████████████ 100%
  ├─ ml/          (skeletons)  ████████████████████ 100%
  ├─ embeddings/  (EmbeddingProvider ABC)  ████████████████████ 100%
  ├─ llm/         (LLMProvider ABC)        ████████████████████ 100%
  └─ evaluation/recommendations/ranking/utils (skeletons) ████████████████████ 100%

LLM Provider Layer         ████░░░░░░░░░░░░░░░░  20%  ← interface only
  ├─ Provider Interface    ████████████████████ 100%  ← Sprint C.2
  ├─ Ollama Adapter        ░░░░░░░░░░░░░░░░░░░░   0%  ← Sprint C.5
  └─ Gemini Adapter        ░░░░░░░░░░░░░░░░░░░░   0%  ← Sprint C.5

Resume Storage             ████████████████████ 100%  ← Sprint C.1 complete
  ├─ ORM Model             ████████████████████ 100%
  ├─ Repository            ████████████████████ 100%
  ├─ Service               ████████████████████ 100%
  ├─ StorageBackend        ████████████████████ 100%
  ├─ Endpoints             ████████████████████ 100%
  └─ Tests (29 passing)    ████████████████████ 100%

Resume Parsing             ████████████████████ 100%  ← Sprint C.3 complete
  ├─ PDF Extractor (pdfplumber)   ████████████████████ 100%
  ├─ PDF Fallback (PyMuPDF)       ████████████████████ 100%
  ├─ DOCX Extractor               ████████████████████ 100%
  ├─ TextCleaner pipeline         ████████████████████ 100%
  ├─ SectionDetector              ████████████████████ 100%
  ├─ DocumentExtractionService    ████████████████████ 100%
  └─ Tests (47 passing)           ████████████████████ 100%

Resume NLP Pipeline        ████████████████████ 100%  ← Sprint C4.6 complete
  ├─ NLP Infrastructure (C4.1)    ████████████████████ 100%
  ├─ Extractor Infrastructure (C4.2) ████████████████████ 100%
  ├─ Contact Extraction (C4.3)    ████████████████████ 100%
  ├─ Skill Extraction (C4.3)      ████████████████████ 100%
  ├─ Education Extraction (C4.4)  ████████████████████ 100%
  ├─ Experience Extraction (C4.4) ████████████████████ 100%
  ├─ Project Extraction (C4.5)    ████████████████████ 100%
  ├─ Certification Extraction (C4.5) ████████████████████ 100%
  └─ Entity Validation (C4.6)     ████████████████████ 100%

Voice / Speech (Whisper)   ░░░░░░░░░░░░░░░░░░░░   0%

Analytics / Dashboard      ░░░░░░░░░░░░░░░░░░░░   0%

Frontend                   ░░░░░░░░░░░░░░░░░░░░   0%

Infrastructure / Docker    ████░░░░░░░░░░░░░░░░  20%
  ├─ Docker Compose (DB)   ████████████████████ 100%
  ├─ Backend Dockerfile    ░░░░░░░░░░░░░░░░░░░░   0%
  └─ AWS / Nginx           ░░░░░░░░░░░░░░░░░░░░   0%

Testing                    ████████████░░░░░░░░  60%
  ├─ Statistics Tests      ████████████████████ 100%
  ├─ Vocabulary Tests      ██████████░░░░░░░░░░  50% (no assertions)
  ├─ Resume Service Tests  ████████████████████ 100%  ← 21 tests, Sprint C.1
  ├─ Storage Backend Tests ████████████████████ 100%  ← 8 tests, Sprint C.1
  ├─ Resume Parsing Tests  ████████████████████ 100%  ← 47 tests, Sprint C.3
  └─ NLP & Extractor Tests ████████████████████ 100%  ← 12 tests, Sprint C4.3

Overall Project             ██████████░░░░░░░░░░  50%
```

---

# 9. Technical Debt

## Critical Issues

**2. Question bank seed data is placeholder-only** *(partially resolved)*
The seed architecture is now modular and all seeded questions carry full AI metadata. `QuestionBankRepository.find_best_questions()` will return results for matching objectives. However, each role currently has only 3 placeholder questions. Full population (20–30 questions per role, multiple experience levels) is a separate task.

**3. `InterviewAnswerService` duplicates and conflicts with `InterviewService`**
`InterviewAnswerService.submit_answer` saves an answer but does NOT mark the question as asked and does NOT advance the interview. `InterviewService.submit_answer` does both. The two services implement overlapping but inconsistent semantics. `InterviewAnswerService` is not wired to any endpoint.

**4. No evaluation endpoint exists**
`InterviewEvaluation` model, schema, repository, and migration are all complete. The feature extractor infrastructure exists. But there is no service, no endpoint, and no pipeline to actually produce an evaluation. The evaluation feature has its schema but no working implementation.

**5. Empty placeholder modules create false impression of completeness**
`core/logging.py`, `services/evaluation/constants.py`, `services/evaluation/keywords.py`, `services/evaluation/utils.py`, `services/evaluation/knowledge_base/__init__.py`, and `shared/responses.py` are all empty files. They represent future work but may mislead.

---

## Architecture Inconsistencies

**6. API response format does not match the documented contract**
`api-contract-v1.md` specifies `{ "success": true, "data": {}, "message": "" }`. The actual API returns raw Pydantic model serialisations. `shared/responses.py` was meant to implement this but is empty.

**7. `datetime.utcnow()` deprecated**
`InterviewService` uses `datetime.utcnow()`. This is deprecated since Python 3.12. Should use `datetime.now(timezone.utc)`.

**8. `echo=True` hardcoded in database engine**
`db/session.py` has `echo=True`, which will log every SQL statement to stdout. This is appropriate for development but will pollute logs and degrade performance in production.

**9. `resume_id` has no foreign key constraint**
`InterviewSession.resume_id` is a nullable integer with no FK relationship. It will accept any integer value without constraint. When the Resume table is eventually created, a migration will be needed to add the FK.

**10. Database design document specifies UUID primary keys; implementation uses integers**
`database-design-v1.md` specifies UUID PKs throughout. The implementation uses auto-increment integers. This is not necessarily wrong but is a divergence from the documented design.

**11. `QuestionSelector` increments `usage_count` in memory without committing**
`QuestionSelector.select_questions` does `bank_question.usage_count += 1` but there is no subsequent `db.commit()`. Usage counts will not be persisted.

**12. `InterviewQuestionGeneratorService` also increments usage count without atomic commit**
Same pattern — usage count is mutated before the question list is fully built, relying on the final commit to persist all changes. If an exception occurs mid-loop, partial usage count increments will be lost.

---

## Missing Infrastructure

**13. No CORS middleware**
The `FastAPI` app has no CORS configuration. When a frontend is built, it will be blocked by the browser.

**14. No global exception handler**
`main.py` has no exception handlers. Unhandled exceptions will leak Python tracebacks to API consumers. All `ValueError` exceptions in services are mapped to `404` even when `400` or `403` would be more appropriate.

**15. No request/response logging middleware**

**16. No startup event for NLP model warm-up**
The spaCy and sentence-transformer models are loaded lazily on first use. The first request that triggers them will be slow. A startup event should pre-warm the models.

**17. Backend Dockerfile is empty**
`infrastructure/docker/backend.Dockerfile` is empty. The backend cannot be containerised.

**18. No CI/CD configuration**
`.github/workflows/` folder exists but is empty.

**19. No production secrets management**
`JWT_SECRET_KEY` is set to `"change-me-in-production"` in `.env.example` with no enforcement mechanism.

---

## Missing Tests

**20. No API integration tests**
No tests for any endpoint. No tests for auth flow, session creation, interview loop.

**21. `test_vocabulary_feature_extractor.py` has no assertions**
It runs the extractor and prints output but asserts nothing. It's a script, not a test.

**22. No tests for services, repositories, or the interview engine components**

---

## Minor Issues

**23. `print()` used for debug output in `InterviewQuestionGeneratorService`**
Should use Python `logging` module.

**24. `TextUtils` partially duplicates `TextProcessor`**
`TextUtils` uses regex-based tokenisation. `TextProcessor` uses spaCy. The relationship and intended use of each is unclear. `TextUtils` appears unused by any other module.

**25. `database.py` in `core/` is a thin re-export wrapper over `db/session.py`**
`core/database.py` doesn't appear to exist as a file but `db/session.py` fills this role directly. The separation between `core/` and `db/` is slightly inconsistent.

**26. Seed data is placeholder-only across 6 roles**
The modular seed architecture scaffolds 6 roles but each has only 3 questions. Full population (20–30 questions per role, multiple experience levels) is needed before demo quality is reached.

---

# 10. Recommended Sprint Plan

Based on the current state of the repository, the following sprints are recommended. Each sprint builds on the previous. Sprints assume a solo or 2-person team working part-time.

---

## Sprint A — Foundation Hardening
**Goal**: Fix the critical technical debt that blocks all future progress.
**Effort**: 2-3 days

**Deliverables**:
- Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` throughout
- Set `echo=True` to be config-driven (`DEBUG` flag in Settings)
- Implement `shared/responses.py` — standardised API response envelope
- Implement `core/logging.py` — structured logging with request IDs
- Add CORS middleware to `main.py`
- Add global exception handler to `main.py`
- Replace `ValueError` raises in services with proper custom exceptions from `shared/exceptions.py`
- Add proper `POST /interviews/{id}/abandon` endpoint
- Add FastAPI startup event to pre-warm spaCy and embedding models

**Dependencies**: None. These are all independent fixes.
**Risk**: Low.

---

## Sprint B — Unify the Interview Engine (COMPLETED)
**Goal**: Replace the parallel pipeline architecture with a single unified interview flow.
**Status**: Completed as part of Backend Milestone M1.

**Deliverables**:
- Wire `InterviewContextBuilder` → `InterviewPlanner` → `QuestionSelector` into `InterviewService.start_interview`
- Deprecate `InterviewQuestionGeneratorService` or reduce it to a fallback
- Populate AI metadata (`skills`, `technologies`, `expected_concepts`) — **done via modular seed architecture**
- Expand seed data to 20–30 questions per role across FRESHER and MID experience levels (placeholder structure is in place)
- Fix `QuestionSelector` to commit usage count increments atomically
- Verify the full interview loop works end-to-end with the unified pipeline

**Dependencies**: Sprint A (exception handling, logging).
**Risk**: Medium — requires careful testing of the interview flow.

---

## Sprint C — Evaluation Engine MVP
**Goal**: Produce a real evaluation score for a completed interview session.
**Effort**: 4-5 days

**Deliverables**:
- Implement `services/evaluation/keywords.py` — technical and behavioural keyword dictionaries
- Implement `services/evaluation/constants.py` — scoring thresholds and weights
- Implement `KeywordFeatureExtractor` and `ReadabilityFeatureExtractor` (using `textstat`)
- Implement feature fusion service — combines all extractors into `TextFeatureVector`
- Implement rule-based scoring engine — maps `TextFeatureVector` to `technical_score`, `communication_score`, `behavioral_score`, `confidence_score`, `overall_score`
- Implement `POST /interviews/{id}/evaluate` endpoint
- Implement `GET /interviews/{id}/evaluation` endpoint
- Wire evaluation trigger on interview completion (or on-demand via endpoint)
- Add integration test for the evaluation pipeline

**Dependencies**: Sprint A, Sprint B.
**Risk**: Medium. Scoring rules will be arbitrary at this stage — they can be refined later.

---

## Sprint D — Backend Dockerfile and CI
**Goal**: Make the backend fully deployable and add basic CI.
**Effort**: 2 days

**Deliverables**:
- Complete `infrastructure/docker/backend.Dockerfile`
- Add backend service to `docker-compose.yml`
- Create `.github/workflows/ci.yml` with: lint (ruff), type check (mypy), run pytest
- Add pytest configuration to `pyproject.toml`
- Expand test coverage to auth endpoints and interview session flow

**Dependencies**: Sprint A.
**Risk**: Low.

---

## Sprint E — LLM Provider Layer
**Goal**: Implement AI-powered question generation and feedback.
**Effort**: 5-7 days

**Deliverables**:
- Design and implement `LLMProvider` abstract interface (`generate_question`, `evaluate_answer`, `generate_feedback`)
- Implement Gemini adapter (free tier, no cost for demo)
- Integrate LLM-generated feedback into `InterviewEvaluation.strengths`, `weaknesses`, `recommendations`
- Add LLM-based follow-up question generation after each primary answer
- Add `QuestionSource.AI` questions to the question bank via LLM seeding script
- Abstract provider selection via `settings.LLM_PROVIDER`

**Dependencies**: Sprint C.
**Risk**: Medium-High. LLM latency and cost management needed.

---

## Sprint F — Frontend MVP
**Goal**: Build a minimal working web UI for recruiter demos.
**Effort**: 7-10 days

**Deliverables**:
- React + TypeScript + TailwindCSS setup
- Auth pages (Register, Login)
- Dashboard (list interview sessions, start new session)
- Interview room (question display, text answer input, next question flow)
- Results page (evaluation scores, strengths, recommendations)

**Dependencies**: Sprints A-D (stable API). Sprint C (evaluation data to display).
**Risk**: High if solo — significant scope.

---

## Sprint G — AWS Deployment
**Goal**: Deploy to AWS and make the project publicly accessible.
**Effort**: 3-4 days

**Deliverables**:
- Deploy backend to EC2
- Deploy PostgreSQL to RDS
- Configure environment variables via AWS Parameter Store
- Configure HTTPS via ALB or nginx
- Set up S3 for future file storage (resume uploads)
- Configure CloudWatch for logs
- Update CI/CD to deploy on merge to main

**Dependencies**: Sprint D (Dockerfile), Sprint F (Frontend) if deploying full-stack.
**Risk**: Medium. AWS cost management required.

---

# 11. Production Readiness

| Dimension | Score | Notes |
|---|---|---|
| Architecture Quality | 72/100 | Clean layered architecture, good separation of concerns. Significant inconsistency between the interview engine sub-package and the live code path. |
| Maintainability | 65/100 | Code is well-structured and documented. Empty placeholder files, duplicate services, and bypassed modules reduce confidence. |
| Scalability | 55/100 | Modular monolith is appropriate for current scale. Missing database indexes on foreign key columns. NLP model loading is lazy. No caching layer. |
| Security | 60/100 | JWT auth is correctly implemented. bcrypt hashing is correct. No CORS, no rate limiting, no input sanitisation beyond Pydantic, no refresh tokens, no token revocation. |
| AI Readiness | 45/100 | Infrastructure is thoughtful — singleton managers, domain schemas, feature vectors. But the pipeline is ~25% complete. LLM layer is 0%. Embedding model loads but has no consumer. |
| Deployment Readiness | 15/100 | Dockerfile is empty. No CI/CD. Docker Compose only runs the database. No production secrets management. |
| Testing Readiness | 15/100 | 2 unit tests exist (one without assertions). No API tests, no service tests, no integration tests. No test configuration. |

**Overall Production Readiness: 47/100**

The codebase demonstrates strong architectural thinking and clean implementation in the areas that are built. The gap is completion — many systems exist as skeletons and the deployment layer is essentially absent.

---

# 12. Recruiter Demo Readiness

**Current answer: No. Not demo-ready.**

A recruiter or hiring manager cannot currently experience SpeakLift as a product. There is no frontend, no UI, no voice interaction, and no evaluation output to show.

However, the backend API is functional and can be demoed via Swagger UI (`/docs`) or Postman, which demonstrates architectural sophistication to a technical interviewer.

## Minimum Requirements Before Resume-Worthy

The following are the minimum features needed before this project can be meaningfully shown on a CV or in an interview:

1. **Working evaluation output** — A completed interview must produce an evaluation with scores and feedback. Without this, the "AI" aspect of the platform cannot be demonstrated.

2. **Deployed, public URL** — The backend must be deployed somewhere accessible. A running EC2 instance or a Railway/Render deployment is sufficient. "It runs locally" is not demo-worthy.

3. **Basic frontend OR polished API documentation** — Either a minimal React UI that shows the interview flow, or a thoroughly documented Postman collection / OpenAPI spec that a recruiter can follow.

4. **At least one more role seeded** — The question bank only covers `Backend Developer/FRESHER`. A demo covering 2-3 roles demonstrates the platform's generalisability.

5. **Dockerfile working** — The project must be containerisable to claim "production-grade" architecture.

## What is already impressive (for technical reviewers)

- The layered architecture (API → Service → Repository → Model) is clean and correct
- Alembic migrations are properly managed with a 4-step history
- The domain schema design (InterviewContext, InterviewPlan, CandidateProfile) is sophisticated
- The evaluation feature vector schema is well-designed and ML-ready
- The question bank AI metadata design anticipates vector search
- Pydantic v2 schemas are correctly used throughout
- JWT auth is properly implemented with bcrypt
- Repository pattern with ownership enforcement is production-correct

With Sprint A through Sprint C completed and deployed, this project would be strong enough for placement interviews at a mid-to-senior backend role level.

---

# 13. Sprint C4 Completion Details (Sprint C4.1 - C4.4)

## Completed Milestones

### Sprint C4.1 — NLP Infrastructure (Completed)
- **Immutable ProcessingContext**: Created context object for safe state flow.
- **SpacyResourceManager Singleton**: Implemented thread-safe loader for spaCy.
- **SpacyProcessor**: Decoupled features extractor schema from raw spaCy objects.
- **Normalizer**: Applied dynamic taxonomic synonym mappings.
- **NLP Schemas**: Created unified Pydantic schemas for entities.
- **Structured Taxonomy JSON Resources**: Set up file-based domain lists.
- **Compatibility Shim**: Preserved legacy `NLPResourceManager` get_spacy_model function.
- **Unit Tests**: Full test suite passing.
- **Architecture Audit**: Passed and verified.
- **Manual Verification**: Completed successfully.

### Sprint C4.2 — Extractor Infrastructure (Completed)
- **EntityExtractor ABC**: Clean interface design.
- **ExtractorRegistry**: Plugin system with registry validation.
- **Domain Validation**: Explicit type checks for domains.
- **Duplicate Domain Protection**: Rejects overlapping registrations.
- **Explicit Routing Validation**: Strict schema matching.
- **NLPPipeline Skeleton**: Orchestrates processors, normalizers, and plugins.
- **Registry Unit Tests**: Verified safety controls.
- **Pipeline Unit Tests**: Evaluated pipeline behaviors.
- **Architecture Audit**: Passed.
- **Manual Verification**: Completed.

### Sprint C4.3 — Contact & Skill Extraction (Completed)

#### ContactExtractor
- **Full name** (Persona NER with newline trimming)
- **Email** (standard regex)
- **Phone** (10-digit standard regex matching)
- **Location** (GPE NER extraction)
- **LinkedIn** (handle matching)
- **GitHub** (handle matching)
- **Portfolio** (general domain matching with email exclusion)
- **Kaggle** (platform matching)
- **LeetCode** (platform matching)
- **HackerRank** (platform matching)

#### SkillExtractor
- **spaCy candidate generation**: Harvesting from tokens, lemmas, noun chunks, and named entities.
- **Taxonomy matching**: Checking candidates against file-based lists.
- **Synonym normalization**: Resolving raw variants.
- **Category assignment**: Deterministic categorization based on JSON file names.
- **Confidence scoring**: Dynamic scoring based on section weights.
- **Duplicate removal**: Unique list mapping.
- **Raw text preservation**: Tracks exact resume substring.
- **normalized_name generation**: Returns standard name.

#### Normalization Examples
- `NodeJS` → `Node.js`
- `ReactJS` → `React`
- `Tensor Flow` → `TensorFlow`
- `Postgres` → `PostgreSQL`

#### Engineering Decisions
- **spaCy-first extraction**: Driven by linguistic properties.
- **Regex only where appropriate**: Minimizes greediness.
- **Rule-based confidence scoring**: Section-based weights.
- **Efficient cached taxonomy loading**: Cached mapping dictionary.
- **No business logic inside extractors**: Decoupled domain extraction.

#### Testing
- **Unit tests passed**: 12/12 tests green.
- **Independent architecture audit passed**: 20/20 checks passed.
- **Swagger regression testing completed successfully**: Verified all endpoints.
- **Existing Authentication, Resume and Interview APIs verified**: Fully operational.
- **No regressions detected**.

### Sprint C4.4 — Education & Experience Extraction (Completed)

#### EducationExtractor
- **Institution**: Extracts universities, colleges, and institutes.
- **Degree**: Parses exact degree variations (e.g., B.S., Ph.D., B.Tech).
- **Field of Study**: Extracted using structural heuristics.
- **CGPA & Percentage**: Precise float and percentage mapping.
- **Dates**: Resolves start and graduation years, and handles 'Present' for ongoing studies.

#### ExperienceExtractor
- **Job Title**: Accurate title extraction ignoring non-essential prefixes.
- **Company**: Robust company boundary detection including entity matching and regex.
- **Location**: Extracts locations and remote work indicators.
- **Duration & Dates**: Resolves start dates, end dates, and calculates employment duration in months.
- **Technologies Used**: Integrates tightly with `TaxonomyResourceManager` to capture exact role-specific technologies without duplication of taxonomy loads.

#### Engineering Decisions
- **TaxonomyResourceManager Singleton**: Abstracted dictionary loads into a thread-safe singleton, entirely eliminating extractor-to-extractor coupling.
- **Pydantic Immutability**: Adapted test suites and code to support strict `frozen=True` schemas for pipeline safety.
- **Rule-based Confidence**: Deterministic scoring based on matching density.

#### Testing
- **Unit tests passed**: 20/20 tests green across the NLP pipeline.
- **Independent architecture audit passed**: 22/22 checks passed.
- **Architecture Integrity Maintained**: The plugin structure remains strictly decoupled.

---

## Current NLP Pipeline Status

```
Resume Upload
     ↓
Resume Upload
     ↓
ResumeService
     ↓
DocumentExtractionService
     ↓
DocumentContent
     ↓
NLPPipeline
     ↓
ExtractedEntities
     ↓
EntityValidator
     ↓
ValidatedExtractedEntities
     ↓
CandidateProfileBuilder
     ↓
CandidateProfile
     ↓
Parsing Completed
```

### Not Yet Implemented
*   Resume ↔ Job Description Matching
*   Interview Context Builder

---

## Project Progress

*   **Backend Foundation**: 100%
*   **Authentication**: 100%
*   **Interview Module**: 100% (Current MVP)
*   **Resume Storage**: 100%
*   **Document Processing**: 100%
*   **NLP Infrastructure**: 100%
*   **Extractor Framework**: 100%
*   **Contact Extraction**: 100%
*   **Skill Extraction**: 100%
*   **Education Extraction**: 100%
*   **Experience Extraction**: 100%
*   **Project Extraction**: 100%
*   **Certification Extraction**: 100%
*   **Candidate Profile Builder**: 100%
*   **Resume Parsing Integration**: 100%
*   **Interview Context Builder**: 0%
*   **LLM Integration**: 0%
*   **Embeddings**: 0%
*   **ML Models**: 0%

---

## Verification
*   **Unit tests passed**: 12 tests verified and passing for NLP modules.
*   **Architecture audit passed**: Full 20/20 verification completed.
*   **Swagger regression testing passed**: Verified endpoints.
*   **Authentication verified**: Sign-up, sign-in, tokens working correctly.
*   **Resume APIs verified**: File uploading and checking operational.
*   **Interview APIs verified**: Session setup and answering validated.
*   **No regression detected**: General platform stability maintained.

---

## Sprint C4.6 — Entity Validation

### Objectives
*   Introduce deterministic validation layer.
*   Validate extracted entities.
*   Preserve immutable pipeline.

### Completed
*   Validator abstract base class.
*   DuplicateValidator.
*   ChronologyValidator.
*   ConfidenceValidator.
*   URLValidator.
*   EntityValidator orchestrator.
*   Comprehensive unit tests.

### Architecture Decisions
*   Validators are stateless.
*   Validators operate only on ExtractedEntities.
*   Validators never parse raw resume text.
*   EntityValidator only orchestrates.
*   Validation remains deterministic.
*   Pydantic model_copy() preserves immutability.

### Testing
*   Duplicate validation.
*   Chronology validation.
*   Confidence validation.
*   URL validation.
*   Integration validation.
*   Architecture audit passed.

## Sprint C4.7 — CandidateProfile Business Layer

### Objectives
*   Introduce the CandidateProfile business aggregate.
*   Bridge the deterministic NLP pipeline with the business layer.
*   Keep AI extraction completely separated from business representation.

### Completed
*   CandidateProfile immutable schemas
*   CandidateProfileBuilder
*   IdentityProfile
*   CareerProfile
*   EducationProfile
*   TechnologyProfile
*   ProfileMetadata
*   CareerStage enum
*   Comprehensive unit tests
*   Architecture audit passed

### Architecture Decisions
*   CandidateProfile lives inside app/services/candidate_profile.
*   CandidateProfileBuilder is the only component allowed to construct CandidateProfile.
*   CandidateProfile is immutable and represents a snapshot.
*   Builder performs deterministic aggregation only.
*   No NLP logic exists inside the business layer.
*   AI and Business layers remain completely separated.

### Testing
*   Identity mapping
*   Career aggregation
*   Qualification ranking
*   Technology grouping
*   Metadata generation
*   Architecture audit passed with no remaining issues.

---

## Sprint C4.8 — Resume Parsing Integration

### Objectives
*   Integrate all previously implemented AI pipeline components.
*   Complete the deterministic resume processing workflow.
*   Keep ResumeService as a pure orchestrator.

### Completed
*   AI dependency injection layer
*   ResumeService orchestration
*   DocumentExtractionService integration
*   NLPPipeline integration
*   EntityValidator integration
*   CandidateProfileBuilder integration
*   Parsing status transitions
*   End-to-end orchestration tests
*   Architecture audit passed

### Architecture Decisions
*   ResumeService remains an orchestrator only.
*   AI components are injected through dependency factories.
*   CandidateProfile is built but not persisted.
*   No NLP logic exists inside ResumeService.
*   Dependency Injection remains the single construction mechanism.

### Testing
*   Happy path orchestration
*   Extraction failure
*   NLP failure
*   Validation failure
*   Builder failure
*   Parsing status transitions
*   Dependency injection tests
*   Full orchestration tests
*   Architecture audit passed

---

## Sprint C5.1A — Job Description Architecture
*   ✓ Completed (Architecture Frozen)

## Sprint C5.1B — Job Description Infrastructure

### Objectives
*   Introduce Job Description upload capability.
*   Reuse the Resume document processing infrastructure.
*   Stop processing at DocumentContent generation.
*   Prepare the foundation for the JD NLP Pipeline.

### Completed
*   JobDescription model
*   JobDescription repository
*   JobDescription schemas
*   JobDescriptionService
*   Upload API endpoints
*   Dependency Injection integration
*   Storage integration
*   Shared DocumentExtractionService reuse
*   Shared TextCleaner reuse
*   Shared SectionDetector reuse
*   TXT document support
*   Service orchestration tests
*   Architecture audit passed

### Architecture Decisions
*   Maximum infrastructure reuse.
*   No duplicate document processing pipeline.
*   JobDescriptionService remains an orchestrator.
*   Processing stops after DocumentContent.
*   No NLP executed.
*   No JobProfile generation.
*   No business reasoning introduced.

### Testing
*   Upload success
*   Invalid MIME
*   Storage failure
*   Extraction failure
*   Dependency injection
*   Repository tests
*   Service orchestration
*   Architecture audit passed

---

## Sprint C5.2.1 — JD NLP Infrastructure

### Objectives
*   Establish the JD NLP schema layer.
*   Introduce the JD ExtractorRegistry.
*   Extend the shared NLPPipeline to support multiple extraction domains.
*   Preserve complete backward compatibility with the Resume pipeline.

### Completed
*   JD schema package
*   SalaryRange schema
*   RequirementTier enum
*   ExtractedJDEntities DTO
*   JD extractor package
*   Registry factory
*   Polymorphic ExtractorRegistry
*   Polymorphic NLPPipeline
*   Infrastructure tests
*   Architecture audit passed

### Architecture Decisions
*   Shared NLPPipeline now supports multiple schema targets.
*   Shared ExtractorRegistry now accepts schema_cls.
*   Resume pipeline remains unchanged.
*   JD infrastructure contains no extraction logic.
*   Confidence remains extractor-owned.
*   RequirementTier includes UNKNOWN.

### Testing
*   Schema immutability
*   Registry wiring
*   Pipeline compatibility
*   Empty registry behaviour
*   Package exports
*   Resume backward compatibility
*   Architecture audit passed

---

## Sprint C5.2.2 — JD Skill Extraction

### Objectives
*   Implement deterministic Job Description skill extraction.
*   Reuse existing NLP infrastructure.
*   Support requirement tier classification.
*   Preserve Resume/JD extractor independence.

### Completed
*   JDSkillExtractor
*   RequirementTier support
*   UNKNOWN tier
*   Section-aware extraction
*   Linguistic cue detection
*   Taxonomy normalization
*   Synonym normalization
*   Duplicate consolidation
*   Confidence filtering inside extractor
*   Registry integration
*   Unit tests
*   Architecture audit passed

### Architecture Decisions
*   Resume and JD extractors remain completely independent.
*   Confidence filtering is extractor-owned.
*   Requirement tiers never guessed.
*   UNKNOWN introduced for ambiguous requirements.
*   TaxonomyResourceManager reused.
*   No business logic introduced.

### Testing
*   Tier detection
*   Taxonomy normalization
*   Synonym resolution
*   Duplicate resolution
*   Section awareness
*   Empty document handling
*   Confidence filtering
*   Architecture audit passed

---

## Sprint C5.2.3 — JD Employment & Experience Extraction

### Objectives
*   Implement deterministic JDEmploymentExtractor.
*   Implement deterministic JDExperienceExtractor.
*   Normalize salary structures.
*   Normalize experience ranges.
*   Preserve AI/business separation.

### Completed
*   JDEmploymentExtractor
*   JDExperienceExtractor
*   SalaryRange normalization
*   EmploymentType extraction
*   RemoteType extraction
*   SalaryPeriod handling
*   Experience range extraction
*   Domain association
*   Registry integration
*   Unit tests
*   Architecture audit passed

### Engineering Decisions
*   SalaryPeriod is never guessed.
*   Missing currency remains None.
*   Missing salary period remains None.
*   Job titles extracted only from deterministic locations.
*   Experience never inferred from titles.
*   Resume extractor independence maintained.
*   Shared infrastructure reused.

### Testing
*   Salary normalization
*   Currency normalization
*   Period handling
*   Employment types
*   Remote types
*   Experience ranges
*   Freshers handling
*   Domain mapping
*   Empty documents
*   Audit passed

---

## Sprint C5.2.4 — JD Responsibilities & Education Extraction

### Objectives
*   Implement deterministic JDResponsibilityExtractor.
*   Implement deterministic JDEducationExtractor.
*   Complete the JD extraction layer.
*   Preserve strict AI/business separation.

### Completed
*   JDResponsibilityExtractor
*   JDEducationExtractor
*   Responsibility noun phrase support
*   Action-verb responsibility extraction
*   Canonical degree normalization
*   Field-of-study extraction
*   Registry integration
*   Unit tests
*   Architecture audit passed

### Engineering Decisions
*   Responsibilities preserve employer wording.
*   Responsibilities support both action verbs and responsibility noun phrases.
*   Responsibilities never infer competencies.
*   Degree normalization is canonical only.
*   No academic ranking.
*   Equivalent practical experience produces no education record.
*   Resume/JD extractor independence preserved.
*   Shared infrastructure reused.

### Testing
*   Action-verb responsibilities
*   Responsibility noun phrases
*   Deduplication
*   Mixed responsibility/requirement sections
*   Bachelor's normalization
*   Master's normalization
*   PhD normalization
*   Indian degree support
*   Field-of-study extraction
*   Equivalent practical experience
*   Audit passed

---

## Sprint C5.2.5 — JD Validation Layer

### Objectives
*   Complete deterministic validation for JD entities.
*   Reuse the existing validator framework.
*   Preserve immutable DTO architecture.
*   Finalize the JD AI validation pipeline.

### Completed
*   SalaryRangeValidator
*   ExperienceRangeValidator
*   Generic Validator[T]
*   Generic EntityValidator orchestration
*   JD duplicate validation
*   Immutable validation flow
*   Architecture audit passed

### Engineering Decisions
*   Validators operate as filters only.
*   Invalid entities are discarded rather than corrected.
*   No ValidatedJDEntities DTO introduced.
*   Resume/JD validation symmetry preserved.
*   Generic Validator[T] adopted.
*   Existing EntityValidator reused.
*   No business reasoning introduced.

### Testing
*   Salary validation
*   Experience validation
*   Duplicate validation
*   Generic validator behaviour
*   Immutable object creation
*   End-to-end validator chain
*   Architecture audit passed

---

## Sprint C5.3 — JobProfile Builder

### Objectives
*   Implement JobProfileBuilder.
*   Introduce immutable JobProfile business aggregate.
*   Build the translation boundary separating the AI Layer from the Business Layer.

### Completed
*   JobProfileBuilder implementation completed.
*   Immutable JobProfile business aggregate introduced.
*   Complete JobProfile schema hierarchy:
    *   JobIdentity
    *   RequirementsProfile
    *   TechnologyProfile
    *   QualificationProfile
    *   EmploymentProfile
    *   CompanyProfile
    *   ProfileMetadata

### Architectural Decisions
*   AI Layer officially ends at ExtractedJDEntities.
*   Business Layer officially begins at JobProfileBuilder.
*   TechNode schema successfully reused from CandidateProfile to guarantee O(1) matching.
*   Four requirement buckets explicitly preserved (required, preferred, optional, unknown).
*   UNKNOWN tiers are strictly preserved and never heuristically promoted.
*   SeniorityLevel intentionally deferred to the future Matching Engine (Business logic vs AI fact).
*   AI telemetry (processing time, pipeline version) explicitly excluded from ProfileMetadata.
*   Builder designed to be fully deterministic, immutable, and stateless.

### Testing
*   Expanded JobProfileBuilder regression suite with edge-case handling.
*   Confirmed empty entity fallbacks and defaults.
*   Confirmed taxonomy missing-skill fallback (`tools`).
*   Confirmed enum mapping behavior.
*   Entire backend regression suite passes perfectly (179 tests passing).

---

## Sprint C6.2 — Skill Matcher

### Objectives
*   Implement the first deterministic business matcher (`SkillMatcher`).
*   Establish the baseline for comparing Candidate and Job technology aggregates.
*   Guarantee strict separation from NLP extraction logics.

### Completed
*   MatchStatistics implemented as a reusable factual schema.
*   SkillMatchResult implemented.
*   SkillMatcher implemented.
*   Deterministic comparison algorithms applied for `REQUIRED`, `PREFERRED`, `OPTIONAL`, and `UNKNOWN` tiers.
*   Deterministic score generation and metrics extraction.

### Architectural Decisions
*   The `SkillMatcher` belongs completely to the Business Layer and never invokes AI/NLP services.
*   Reused the existing `TechNode` business model to ensure `O(1)` match determinism.
*   Stateless architecture ensuring perfectly predictable results for identical inputs.
*   UNKNOWN requirement tiers are rigorously preserved without heuristic promotion.
*   Immutable outputs. Facts are computed before business interpretations.

### Testing
*   7 new tests added targeting exact matches, missing fields, requirement boundaries, and graceful empty inputs.
*   Entire backend regression suite passes perfectly (186 tests passing).

---

## Sprint C6.3 — Experience Matcher

### Completed
*   ExperienceMatcher implemented.
*   ExperienceMatchResult implemented.
*   Deterministic deficit, surplus, and boundary checks (minimum/maximum experience) applied.

## Sprint C6.4 — Education Matcher

### Completed
*   EducationMatcher implemented.
*   EducationMatchResult implemented.
*   Deterministic hierarchy evaluation for qualifications (e.g. Master > Bachelor).

## Sprint C6.5 & C6.6 — MatchResultBuilder & MatchingEngine

### Completed
*   MatchResultBuilder implemented for stateless aggregation of matcher statistics and outputs.
*   MatchResult immutable schema introduced as final output.
*   MatchingEngine orchestrator implemented using dependency injection.
*   Sprint C6 officially concluded.

### Architectural Decisions
*   The MatchingEngine acts purely as an orchestrator. It executes zero business logic.
*   The MatchResultBuilder cleanly aggregates `MatchStatistics` across all matchers without deduplicating code.
*   Total AI isolation confirmed. No `app.ai` imports exist in the Matching package.
*   All tests (210) passing successfully.

---

## Sprint C7 — Interview Context, Planner, and Selection

### Completed
✓ Interview Context
✓ Interview Planner
✓ Question Selection
✓ Repository abstraction hardening

---


# 14. Backend Milestone M1 — End-to-End Interview Startup Validation

### Completed
✓ PDF layout reconstruction
✓ Resume extraction improvements
✓ CandidateProfile and JobProfile enhancements
✓ Matching Engine validation
✓ Dependency Injection and PostgreSQL repository fixes
✓ **End-to-End Interview Startup Validation**

### Objective
Achieved end-to-end execution of the interview startup workflow using valid, non-placeholder data from the production Resume and Job Description. The complete chain—from Document Parsing, AI Extraction, Domain Model Creation, Skill Matching, Interview Planning, to Question Selection and final Interview Session state transition—successfully processes real candidate and job profiles without triggering runtime exceptions or domain validation failures.

### Current Backend Maturity
The Interview Engine backend orchestration is now fully functional and stable end-to-end for the setup phase. It acts as a flawless bridge between raw document ingestion and session commencement. The system is ready to accept user answers and pipe them through to the Evaluation Engine.


## Next Sprint

### Sprint C8 — Interview Execution
*   (Not Started)

---

*End of SpeakLift Project Status Document — July 8, 2026*
