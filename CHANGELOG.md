# Changelog

All notable changes to the SpeakLift project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Sprint F1 – Frontend Architecture Foundation**
- Bootstrapped Next.js App Router project in `/frontend` directory.
- Configured strictly typed TypeScript environment and `tsconfig.json` path aliases (`@/components`, `@/features`, etc.).
- Integrated Tailwind CSS v4 and `shadcn/ui` with semantic design tokens defined in `globals.css` (dark mode first).
- Set up root `layout.tsx` incorporating Next Fonts (`Inter`, `Geist_Mono`), SEO placeholders, and `sonner` Toaster.
- Established `GlobalProviders` composing `ThemeProvider` and `QueryClientProvider` (TanStack Query).
- Configured frontend error handling infrastructure (`error.tsx`, `global-error.tsx`, `not-found.tsx`, `loading.tsx`).
- Created scalable folder structure conforming to architecture specifications (Features, Hooks, Services, etc.).
- Added code quality tooling (`eslint`, `prettier`, `lint-staged`, `husky`) and `cn` class utility.

- **Sprint PE2 – Operational Security & Reliability**
- Added Global Exception Middleware translating unhandled internal errors into sanitized JSON responses using the standard Error Model.
- Added configurable `CORSMiddleware` supporting dynamic origin whitelisting.
- Added `TrustedHostMiddleware` to reject spoofed Host headers.
- Added `SecurityHeadersMiddleware` (CSP, X-Frame-Options, HSTS, etc.).
- Added `RequestSizeLimitMiddleware` rejecting requests >15MB with HTTP 413.
- Added IP-based `RateLimitMiddleware` returning Retry-After headers with HTTP 429.

- **Sprint PE1 – Observability & Runtime Foundation**
- Configured native JSON structured logging (`app/core/logging.py`) with automatic correlation ID injection via context variables.
- Created `CorrelationIdMiddleware` to trace requests (`X-Request-ID` and `X-Process-Time`).
- Added robust Liveness (`/api/v1/health/live`) and Readiness (`/api/v1/health/ready`) probes returning detailed system diagnostics and database connectivity state.
- Implemented `lifespan` hook in `main.py` for failing fast on invalid `Settings` and graceful database shutdown.

- **Sprint M3.2 – Interview Intelligence Engine**
- Created comprehensive reporting schemas representing `InterviewReport`, `ExecutiveSummary`, `CompetencyAssessment`, `HiringRecommendation`, `LearningRoadmap`, and `InterviewStatistics`.
- Implemented `InterviewReportService` to consume persisted evaluation data and generate a full candidate-facing report using an LLM.
- Added a highly optimized prompt builder (`ReportPromptBuilder`) to pass aggregated statistics and per-question reviews instead of large raw transcripts.
- Exposed `GET /api/v1/interviews/{id}/report` endpoint.

- **Sprint M3.1 – Evaluation Persistence Layer**
- Created `AnswerEvaluation` ORM model for persistent storage of granular answer-level NLP metrics and AI feedback.
- Created `AnswerEvaluationRepository` for specialized data access.
- Updated `InterviewExecutionService` to evaluate answers inline and persist them during `submit_answer`.
- Modified `InterviewEvaluationService.evaluate_session` to perform DB aggregation from persisted answer evaluations instead of recalculating metrics at session close.
- Generated Alembic migrations (`add_answer_evaluations`).

- **Sprint M2.2.2 – Execution Queue Refactor**
- Implemented Materialized Path execution queue architecture for adaptive interview paths.
- Added `execution_path` (String) to `InterviewQuestion` for infinite-depth, lexicographical tree sorting (e.g. `01`, `01.01`).
- Renamed `question_order` to `planned_order` to strictly represent the immutable interview plan mapping.

### Changed
- `InterviewExecutionService`: Replaced loop-based collision resolution with constant-time execution path derivation.
- `FollowUpGenerationService`: Updated generate signature and instantiation logic to bind execution paths.
- `InterviewQuestionRepository`: Queries now explicitly sort by `execution_path` rather than integer order.
- Provided a backward-compatible database migration safely translating existing `question_order` integers into zero-padded execution paths.

## [0.9.1] - 2026-07-19

### Added
- **Milestone M2.2 – Adaptive Interview System**
- `AdaptiveDecisionEngine`: Stateless decision engine determining routing branches (Next Question, Follow-up, End Interview) based on real-time evaluation metrics.
- `FollowUpPromptBuilder`: Constructs localized follow-up LLM prompts dynamically targeting specific candidate answer gaps (e.g. `WEAK_KEYWORD_COVERAGE`, `LOW_CONFIDENCE`).
- `FollowUpGenerationService`: Generates and constructs contextual follow-up `InterviewQuestion`s via the `LLMService` with resilient template fallbacks.
- Configurable `AdaptiveThresholds` providing fine-grained bounds for generation triggering (e.g., max follow-ups per primary question, weak metric counts).
- Immutable `AdaptiveDecision` and `AdaptiveDecisionResult` value objects ensuring traceable decision auditing.

### Changed
- `InterviewExecutionService`: Completely refactored `submit_answer` to support dynamic adaptive routing, follow-up injection, and graceful limit enforcement without corrupting linear plan execution.
- Resolved execution package cyclic dependency (via `EvaluationRequest` and `SubmittedAnswer`) by refining DI scoping and `__init__.py` export boundaries.

---

## [0.9.0] - 2026-07-19

### Added
- **Milestone M2.1 – Evaluation Engine Completion**
- `GrammarFeatureExtractor`: Deterministic grammar quality scoring using spaCy dependency-parse heuristics (SV mismatch, fragment detection, double negation).
- `ReadabilityFeatureExtractor`: Flesch Reading Ease and Flesch-Kincaid Grade Level metrics computed from syllable and sentence statistics.
- `ConfidenceFeatureExtractor`: Lexicon-based filler-word and hedging-phrase detection producing a normalised confidence score.
- `SemanticSimilarityFeatureExtractor`: Local BAAI/bge-base-en-v1.5 sentence-embedding cosine similarity between question and answer (no external API calls).
- New immutable Pydantic schemas: `GrammarEvaluation`, `ReadabilityEvaluation`, `ConfidenceEvaluation`, `SemanticEvaluation`.
- Extended `AnswerEvaluation` with optional `grammar`, `readability`, `confidence`, and `semantic_similarity` fields.
- 36 new tests across 5 test files covering all new extractors and the enriched prompt builder.

### Changed
- `DeterministicEvaluationEngine`: Fully refactored to orchestrate all four new feature extractors. Backward-compatible via optional constructor parameters.
- `AnswerEvaluationPromptBuilder` (v1.1): Now injects vocabulary statistics, grammar, readability, confidence, and semantic metrics into the LLM prompt when available.
- `app/dependencies/engine.py`: Updated `get_evaluation_service()` to wire all new extractors into `DeterministicEvaluationEngine`.
- `pyproject.toml`: Registered `slow` pytest mark for embedding-model tests.

---

## [0.8.0] - 2026-07-19


### Added
- **Backend Milestone M1: End-to-End Interview Startup Validation**
- Integrated document reconstruction engine between PDF extraction and Section Detection.
- Introduced `InterviewWorkflowService` to orchestrate end-to-end interview startup.
- Introduced factory methods to gracefully supply complete domain aggregates for candidate and job profiles.

### Changed
- Unified the parallel pipeline architecture: `InterviewWorkflowService` now acts as the central facade for `MatchingEngine`, `InterviewPlanner`, and `QuestionSelector`.
- Updated PostgreSQL JSON querying in `QuestionBankRepository` to use the JSONB `?` operator.
- Resolved dependency injection issues in FastAPI evaluation services.
- Successfully achieved a fully automated pipeline executing from Document Parsing -> AI Extraction -> Domain Model Creation -> Skill Matching -> Interview Planning -> Question Selection.

### Removed
- Deprecated legacy `InterviewQuestionGeneratorService` and old live-flow shims in favor of the full `InterviewWorkflowService` pipeline.

---

### Added

- Sprint C9.2 completed (AI Infrastructure) with historical record from C9.2.1 to C9.2.8.2.
- **C9.2.1/C9.2.2**: `Prompt` immutable domain aggregates enforcing type-safe inputs and prompt versioning.
- **C9.2.3**: `GeminiProvider` implementation using the official `google-genai` SDK and Provider abstraction layer hardening.
- **C9.2.4**: `OllamaProvider` for local, cost-free inference.
- **C9.2.5**: `LLMRouter` for configuration-driven routing and failover (`prefer_local`, `prefer_cloud`).
- **C9.2.6/C9.2.7**: `LLMService` centralized AI orchestration and Dependency Injection Factory mapping.
- **C9.2.8**: `AI_PROVIDER_SETUP.md` documentation, `smoke_test_ai.py` toolkit, production stream hardening, and AI test suite rate limit handling.
- **C9.2.9**: AI Infrastructure Documentation freeze.
- Interview Context Builder
- LLM Provider Layer Integration
- Front-End UI

### Architecture

- **Sprint C9.2 completed**: AI Infrastructure
- The AI Infrastructure (Prompt, Provider, Router, Service, DI Factory) is fully hardened, documented, and frozen.

---

## [0.7.0] - 2026-07-08

### Added

- `InterviewContext` immutable business aggregate and `InterviewConfiguration`.
- `InterviewContextBuilder` for strict isolation from persistence.
- `InterviewPlanner` domain implementing deterministic sequence planning.
- `InterviewPlan`, `InterviewPhase`, and `InterviewObjective` immutable schemas.
- `QuestionSelector` domain providing deterministic, state-free extraction.
- `QuestionSelection` and `SelectedQuestion` immutable aggregates.
- `QuestionRepository` domain-level protocol abstraction.

### Changed

- Adopted formal Dependency Injection within `QuestionSelector`.
- Hardened Repository Pattern by isolating business logic from concrete `QuestionBankRepository`.

### Removed

- Obsolete legacy `interview_engine` planner and question selector implementations.

### Architecture

- Hardened Business Layer against ORM leakage.
- Sprint C7 completed: The Interview Context, Planning, and Selection domains are fully operational.

---

## [0.6.0] - 2026-07-07

### Added

- `EducationMatcher` for deterministic minimum degree and specific degree checks.
- `EducationMatchResult` immutable schema.
- `MatchResultBuilder` for stateless aggregation of matching outputs.
- `MatchResult` final unified business aggregate.
- `MatchingEngine` to fully orchestrate the deterministic matching subsystem.

### Changed

- Sprint C6 completed. The deterministic Matching Engine is fully functional.

### Architecture

- `MatchingEngine` utilizes pure dependency injection for all underlying matchers and builders.
- `MatchResultBuilder` aggregates `MatchStatistics` across all matchers purely statelessly.
- Enforced zero `app.ai` imports inside the `matching` package.

---

## [0.5.9] - 2026-07-07

### Added

- ExperienceMatcher
- ExperienceMatchResult
- Business schemas (CareerPosition, AcademicDegree, CandidateCertification, CandidateProject)

### Changed

- CandidateProfile aggregate completely isolated from AI DTO leakage.
- CandidateProfileBuilder strictly translates raw AI extractions to business models.
- Business Layer hardened.

### Architecture

- Removed all imports of `app.ai.*` from the Business Layer.
- Implemented deterministic `ExperienceMatcher` using pure integer-based comparison.

---

## [0.5.8] - 2026-07-07

### Added

- MatchStatistics
- SkillMatchResult
- SkillMatcher
- Skill matching infrastructure
- Deterministic technology comparison
- Shared matching statistics

### Testing

- SkillMatcher unit tests
- MatchStatistics tests
- SkillMatchResult tests
- Regression coverage

### Architecture

- Introduced reusable matching schema layer
- Introduced first Business Matcher
- Reused TechNode
- Preserved RequirementTier semantics
- Maintained AI/Business separation
- Stateless deterministic matcher design

---

## [0.5.7] - 2026-07-07

### Added

- JobProfile business aggregate.
- JobProfileBuilder.
- Business schemas.
- Technology categorization.
- Requirement aggregation.
- Qualification aggregation.
- Employment aggregation.
- Company profile placeholder.
- Metadata aggregation.

### Testing

- Expanded JobProfileBuilder regression suite.
- Empty entity handling.
- Taxonomy fallback.
- Enum mapping verification.

### Architecture

- Reused TechNode.
- Preserved UNKNOWN requirement tier.
- Deferred Seniority computation.
- Business metadata separated from AI telemetry.

---

## [0.5.6] - 2026-07-07

### Added

- SalaryRangeValidator
- ExperienceRangeValidator
- Generic Validator[T]
- JD validator integration tests

### Changed

- EntityValidator now supports generic immutable entity validation.
- DuplicateValidator extended to JD entities.

### Fixed

- Removed DTO duplication from JD validation.
- Validation now discards invalid entities instead of correcting them.

---

## [0.5.5] - 2026-07-07

### Added

- JDResponsibilityExtractor
- JDEducationExtractor
- Responsibility noun phrase extraction
- Canonical degree normalization
- Field-of-study extraction
- Responsibility tests
- Education tests

### Changed

- JD ExtractorRegistry now includes all core JD extractors.

### Fixed

- Prevented competency inference from responsibilities.
- Prevented academic ranking during education extraction.

---

## [0.5.4] - 2026-07-07

### Added

- JDEmploymentExtractor
- JDExperienceExtractor
- Salary normalization
- EmploymentType extraction
- RemoteType extraction
- Experience range extraction
- JD employment tests
- JD experience tests

### Changed

- JD registry now includes Employment and Experience extractors.
- Salary DTO refined with SalaryPeriod.

### Fixed

- SalaryPeriod is never inferred.
- Experience is never inferred from job titles.

---

## [0.5.3] - 2026-07-06

### Added

- Deterministic JDSkillExtractor
- RequirementTier enum support
- UNKNOWN requirement tier
- Section-aware JD skill extraction
- Confidence filtering during extraction
- JD Skill extractor tests

### Changed

- JD ExtractorRegistry now includes JDSkillExtractor.
- JD NLP pipeline now performs deterministic skill extraction.

### Fixed

- Prevented ambiguous requirements from being incorrectly promoted to REQUIRED.

---

## [0.5.2] - 2026-07-06

### Added

- JD NLP schema package
- SalaryRange schema
- RequirementTier enum
- ExtractedJDEntities DTO
- JD extractor registry package
- JD NLP infrastructure tests

### Changed

- ExtractorRegistry now supports configurable output schemas.
- NLPPipeline now supports polymorphic schema orchestration while remaining backward compatible.

### Fixed

- Eliminated the need for duplicate NLP pipelines for Resume and Job Description.

---

## [0.5.1] - 2026-07-06

### Added

- Job Description upload infrastructure
- JobDescription ORM model
- Repository layer
- Service layer
- REST API endpoints
- Dependency injection
- TXT Job Description support
- Shared document processing reuse
- Job Description orchestration tests

### Changed

- SectionDetector now supports both Resume and Job Description headings while remaining reusable.
- Shared document processing infrastructure now serves multiple document types.

### Fixed

- Eliminated infrastructure duplication between Resume and Job Description pipelines.

---

## [0.4.8] - 2026-07-06

### Added

- AI dependency injection module
- End-to-end resume orchestration
- ResumeService integration with AI pipeline
- CandidateProfile integration
- Resume orchestration tests

### Changed

- Resume upload now executes the complete deterministic AI processing pipeline.

### Fixed

- Resume parsing state transitions are now fully deterministic.
- Failure handling guarantees consistent parsing states.

---

## [0.4.7] - 2026-07-06

### Added

- CandidateProfile business layer
- CandidateProfileBuilder
- Immutable CandidateProfile schemas
- IdentityProfile
- CareerProfile
- EducationProfile
- TechnologyProfile
- ProfileMetadata
- CandidateProfile unit tests

### Changed

- NLP pipeline now hands off to the business layer through CandidateProfileBuilder.

### Fixed

- Removed regex parsing from CandidateProfileBuilder to preserve business-layer boundaries.

---

## [0.4.6] - 2026-07-06

### Added

- Validator base class
- EntityValidator
- DuplicateValidator
- ChronologyValidator
- ConfidenceValidator
- URLValidator
- Validator unit tests

### Changed

- NLP pipeline now includes deterministic validation stage.

### Fixed

- Duplicate entity handling.
- Invalid chronology handling.
- Confidence normalization.
- URL validation.

---

## [0.4.5] - 2026-07-06

### Added

- ProjectExtractor
- CertificationExtractor
- Project schema enhancements
- Certification schema enhancements
- Project extraction tests
- Certification extraction tests

### Changed

- Extended ProjectRecord schema
- Extended CertificationRecord schema

---

## [0.4.3] - 2026-07-06

### Completed
- **Sprint C4.3: Contact & Skill Extraction**

### Added
- `ContactExtractor` implementation for parsing:
  - Candidate Full Name (spaCy `PERSON` with multiline filtering).
  - Phone numbers, Email addresses.
  - Social profile URLs (LinkedIn, GitHub, Kaggle, LeetCode, HackerRank, Portfolio) with false-positive domain/email-domain validation checks.
- `SkillExtractor` implementation supporting:
  - Candidate generation from spaCy `tokens`, `lemmas`, `noun_chunks`, and `named_entities`.
  - Dynamic synonyms and taxonomy matching via lookahead/lookbehind patterns.
  - Deterministic skill categorisation and technology mapping.
  - Section-based confidence scoring.
  - Exact match raw text preservation.
- Comprehensive unit tests covering regex word boundaries for special languages (e.g. `C++`, `C#`, `.NET`) and synonym mappings (`NodeJS` -> `Node.js`, `ReactJS` -> `React`, `Tensor Flow` -> `TensorFlow`, `Postgres` -> `PostgreSQL`).

---

## [0.4.2] - 2026-07-04

### Completed
- **Sprint C4.2: Extractor Infrastructure**

### Added
- `EntityExtractor` abstract base class to enforce clean extractor design.
- Thread-safe `ExtractorRegistry` supporting runtime extractor registration, type-safe iteration, and domain duplicate/unknown safety validation.
- `NLPPipeline` pipeline driver matching processed contexts against registered plugins.
- Explicit registry and pipeline orchestration unit tests.

---

## [0.4.1] - 2026-07-04

### Completed
- **Sprint C4.1: NLP Infrastructure**

### Added
- Immutable `ProcessingContext` and `ProcessedDocument` schemas to isolate extraction operations.
- Thread-safe `SpacyResourceManager` singleton class-level loading cache.
- `SpacyProcessor` implementation mapping spaCy's raw doc outputs into clean schemas.
- `Normalizer` resource loader resolving taxonomic synonyms without hardcoding.
- Backward compatibility adapter/shim for the legacy `NLPResourceManager.get_spacy_model()` function.

---

## [0.3.0] - 2026-07-02

### Completed
- **Sprint C3: Resume Parsing (Document Processing)**

### Added
- Integrated document parsers:
  - `PDFPlumberExtractor` (primary PDF extractor).
  - `PyMuPDFExtractor` (fallback PDF extractor).
  - `DOCXExtractor` for Word document processing.
- `TextCleaner` pipeline to normalize whitespace, remove control chars, and clean text.
- `SectionDetector` utilizing rules to segment resume texts into standard categories.
- Orchestrating `DocumentExtractionService` to clean, parse, and structure uploaded resume assets.

---

## [0.2.0] - 2026-06-28

### Completed
- **Sprint C2: AI Core Infrastructure**
- **Sprint C1: Resume Storage**

### Added
- Complete `app/ai/` core folder layout separating shared types, document processing, NLP, ML, embeddings, and LLM integrations.
- Resume model, repository, service, and local file storage subsystem.
- Endpoints supporting resume uploading, listing, details checking, and asset downloading.

---

## [0.1.0] - 2026-06-25

### Completed
- **Sprint B: Modular Question Bank Foundation**
- **Sprint A: Foundation Hardening**

### Added
- Standardized API response wrappers and structured logging setup.
- Database cleanups replacing deprecated UTC functions.
- Multi-role question bank seeding infrastructure, splitting candidate queries into role-specific files (`python_developer`, `backend_developer`, etc.) complete with metadata arrays.
- Global exception mapping from domain errors to HTTP.


## Unreleased

### Changed

- Refined EducationRecord schema with academic metadata:
  - CGPA
  - Percentage
  - Start year
  - Current education flag
  - Confidence

- Refined ExperienceRecord schema with:
  - Employment type
  - Location
  - Description
  - Confidence


  