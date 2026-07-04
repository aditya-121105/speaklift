# backend/app/ai/document_processing/cleaners/__init__.py
"""
Document Cleaners
=================

Text cleaning and normalisation pipelines applied after raw text
extraction and before NLP processing.

Responsibilities
----------------
- Whitespace normalisation
- Encoding artefact removal (e.g. ligatures, non-breaking spaces)
- Header/footer stripping
- Noise removal (page numbers, watermarks in extracted text)

Sprint C.2 — package skeleton only. No implementations.
Sprint C.3+ — implement BasicTextCleaner, ResumeTextCleaner.
"""
