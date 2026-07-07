# Changelog

All notable changes to the SpeakLift project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- ExperienceMatcher
- EducationMatcher
- MatchResultBuilder
- MatchingEngine
- Matching Integration
- Interview Context Builder
- Interview Planner
- Question Selection
- Answer Evaluation

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


  