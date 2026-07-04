# backend/app/ai/document_processing/extractors/__init__.py
"""
Document Extractors
===================

Abstract interface for all document extractor implementations.

Design contract
---------------
Every concrete extractor (PDF, DOCX, OCR) must:
  1. Inherit from DocumentExtractor.
  2. Implement the extract() method.
  3. Return a DocumentContent instance.
  4. Raise DocumentExtractionError on failure (never propagate raw IO errors).
  5. Be stateless — no instance state beyond configuration.

Adding a new extractor
----------------------
1. Create a file in this package (e.g. pdf_extractor.py).
2. Implement DocumentExtractor.
3. Register it in DocumentExtractionService (document_processing/services/).

Sprint C.2 — abstract interface only. No concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.document_processing.schemas import DocumentContent


class DocumentExtractor(ABC):
    """
    Abstract base class for all document extractor implementations.

    A DocumentExtractor converts raw file bytes into a DocumentContent
    object. It is responsible for extracting text only — no NLP, no AI,
    no scoring.

    Concrete implementations
    ------------------------
    PDFDocumentExtractor  (Sprint C.3) — uses PyMuPDF / pdfplumber
    DOCXDocumentExtractor (Sprint C.3) — uses python-docx
    OCRDocumentExtractor  (Sprint C.4) — uses Tesseract for scanned PDFs

    Usage
    -----
    Extractors are selected by DocumentExtractionService based on the
    file MIME type. Do NOT instantiate extractors directly in services.
    """

    @abstractmethod
    def extract(
        self,
        file_data: bytes,
        filename: str = "",
        mime_type: str = "",
    ) -> DocumentContent:
        """
        Extract text content from raw file bytes.

        Parameters
        ----------
        file_data : Raw bytes of the uploaded file.
        filename  : Original filename for tracing (not used for logic).
        mime_type : MIME type of the file (e.g. 'application/pdf').

        Returns
        -------
        DocumentContent — structured text representation of the document.

        Raises
        ------
        DocumentExtractionError — if the file cannot be parsed.
        AIValidationError       — if file_data is empty or unsupported.
        """

    @abstractmethod
    def supports(self, mime_type: str) -> bool:
        """
        Return True if this extractor can handle the given MIME type.

        Used by DocumentExtractionService to select the appropriate extractor.

        Parameters
        ----------
        mime_type : MIME type string (e.g. 'application/pdf').

        Returns
        -------
        bool — True if this extractor handles the MIME type.
        """
