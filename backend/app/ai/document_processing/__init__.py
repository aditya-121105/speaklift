# backend/app/ai/document_processing/__init__.py
"""
Document Processing
===================

Responsible for converting raw uploaded files (PDF, DOCX) into structured
text content that downstream NLP and ML components can consume.

Sub-packages
------------
extractors/  — Abstract and concrete document extractor implementations.
               Sprint C.2: abstract interface only.
               Sprint C.3+: PDF extractor (PyMuPDF), DOCX extractor (python-docx).
cleaners/    — Text cleaning and normalisation pipelines.
schemas/     — Pydantic models for extraction input/output (DocumentContent).
services/    — Orchestration service that drives extraction + cleaning.

Public interface (stable)
-------------------------
DocumentExtractor         — abstract base class for all extractors
DocumentExtractionService — abstract service driving the pipeline
DocumentContent           — Pydantic output schema

Future implementations (not in this sprint)
-------------------------------------------
- PDFDocumentExtractor     (PyMuPDF / pdfplumber)
- DOCXDocumentExtractor    (python-docx)
- OCRDocumentExtractor     (Tesseract — for scanned PDFs)
"""
