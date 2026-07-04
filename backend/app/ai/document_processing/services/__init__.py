# backend/app/ai/document_processing/services/__init__.py
"""
Document Extraction Service
============================

Orchestrates the full document processing pipeline:

  Raw bytes
      │
      ▼
  DocumentExtractor.extract()   ← selected by MIME type
      │
      ▼
  DocumentCleaner.clean()       ← normalises extracted text
      │
      ▼
  DocumentContent               ← ready for NLP pipeline

Design contract
---------------
DocumentExtractionService is an abstract interface.
Concrete implementations receive a list of DocumentExtractor instances
via dependency injection. The service selects the correct extractor
based on the file's MIME type and delegates to it.

This design means:
- Adding a new file format requires only a new DocumentExtractor.
- The service interface never changes when new formats are added.
- Business services in app/services/ call this service; they never
  instantiate extractors directly.

Sprint C.2 — abstract service interface only.
Sprint C.3+ — implement DocumentExtractionServiceImpl.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.document_processing.schemas import DocumentContent


class DocumentExtractionService(ABC):
    """
    Abstract interface for the document extraction orchestration service.

    Concrete implementations should:
    1. Accept a registry of DocumentExtractor instances.
    2. Select the correct extractor based on the file's MIME type.
    3. Apply cleaning after extraction.
    4. Return a DocumentContent object.

    Raised exceptions are translated to HTTP responses by the global
    exception handler. The service itself raises only AI exceptions.
    """

    @abstractmethod
    def extract(
        self,
        file_data: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentContent:
        """
        Extract and clean text from a document file.

        Parameters
        ----------
        file_data : Raw file bytes.
        filename  : Original filename (for tracing only).
        mime_type : MIME type used to select the correct extractor.

        Returns
        -------
        DocumentContent — structured, cleaned text ready for NLP.

        Raises
        ------
        DocumentExtractionError — if no extractor supports the MIME type
                                   or extraction fails.
        AIValidationError       — if file_data is empty.
        """
