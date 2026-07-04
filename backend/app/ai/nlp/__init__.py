# backend/app/ai/nlp/__init__.py
"""
NLP — Natural Language Processing
===================================

Responsible for linguistic analysis of extracted document text.

This sub-package sits downstream of document_processing/ and upstream
of ml/ and embeddings/.

Pipeline position
-----------------
DocumentContent (from document_processing/)
    │
    ▼
NLP Processors + Extractors   ← this sub-package
    │
    ▼
Structured extraction results (entities, skills, education, etc.)

Sub-packages
------------
processors/  — Core NLP processors (spaCy, NLTK tokenisers).
               Entry point for running a document through the NLP pipeline.

extractors/  — Domain-specific entity extractors.
               Each extractor targets a specific information type:
               SkillExtractor, TechnologyExtractor, EducationExtractor,
               ExperienceExtractor, ProjectExtractor.

schemas/     — Pydantic models for NLP outputs (ExtractedEntities,
               SkillSet, EducationRecord, ExperienceRecord, etc.).

resources/   — Model loaders and resource managers (spaCy model singleton,
               NLTK data downloader, custom pattern files).

Architecture rule
-----------------
NLP extractors produce STRUCTURED DATA only.
They must NOT make decisions (no scoring, ranking, or recommendations).
That belongs in ml/ or services/.

Sprint C.2 — folder structure and __init__.py files only.
Sprint C.3+ — implement spaCy processor and resume entity extractors.
"""
