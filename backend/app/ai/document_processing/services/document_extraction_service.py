# backend/app/ai/document_processing/services/document_extraction_service.py
"""
Document Extraction Service — Concrete Implementation
======================================================

Implements DocumentExtractionService (the abstract interface from
document_processing/services/__init__.py).

Full pipeline
-------------
Raw bytes
    │
    ▼
Extractor selection (by MIME type)
    │  → PDFPlumberExtractor   (primary for PDF)
    │  → PyMuPDFExtractor      (fallback for PDF)
    │  → DOCXExtractor         (for DOCX/DOC)
    ▼
DocumentContent (raw_text populated)
    │
    ▼
TextCleaner.clean()
    │
    ▼
DocumentContent (cleaned_text populated)
    │
    ▼
SectionDetector.detect()
    │
    ▼
DocumentContent (sections populated, word_count / char_count computed)
    │
    ▼
Return to caller

Design
------
- Extractors are injected at construction time (no hard-coded imports).
- PDF fallback logic is encapsulated in _extract_pdf().
- All AI exceptions propagate to the caller — no swallowing.

Sprint C.3 — implemented.
"""

from __future__ import annotations

import logging

from app.ai.document_processing.cleaners.text_cleaner import TextCleaner
from app.ai.document_processing.extractors import DocumentExtractor
from app.ai.document_processing.extractors.docx_extractor import DOCXExtractor
from app.ai.document_processing.extractors.pdf_extractor import PDFPlumberExtractor
from app.ai.document_processing.extractors.pymupdf_extractor import PyMuPDFExtractor
from app.ai.document_processing.schemas import DocumentContent
from app.ai.document_processing.section_detector import SectionDetector
from app.ai.document_processing.services import DocumentExtractionService
from app.ai.shared.exceptions import (
    AIValidationError,
    DocumentExtractionError,
)

logger = logging.getLogger(__name__)

# Supported MIME types → extractor chain
_PDF_MIME = "application/pdf"
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_DOC_MIME = "application/msword"

_SUPPORTED_MIME_TYPES = frozenset({_PDF_MIME, _DOCX_MIME, _DOC_MIME})


def build_default_extraction_service() -> "DocumentExtractionServiceImpl":
    """
    Factory function that creates a DocumentExtractionServiceImpl
    wired with the default extractor set.

    Use this in FastAPI dependency providers. Do not instantiate
    DocumentExtractionServiceImpl directly in endpoints.
    """
    return DocumentExtractionServiceImpl(
        pdf_extractor=PDFPlumberExtractor(),
        pdf_fallback_extractor=PyMuPDFExtractor(),
        docx_extractor=DOCXExtractor(),
        cleaner=TextCleaner(),
        section_detector=SectionDetector(),
    )


class DocumentExtractionServiceImpl(DocumentExtractionService):
    """
    Concrete document extraction pipeline.

    Wires together extractor → cleaner → section detector to produce
    a fully structured DocumentContent from raw file bytes.

    Parameters
    ----------
    pdf_extractor          : Primary PDF extractor (pdfplumber).
    pdf_fallback_extractor : Fallback PDF extractor (PyMuPDF).
    docx_extractor         : DOCX extractor (python-docx).
    cleaner                : Text normalisation pipeline.
    section_detector       : Heading-based section classifier.
    """

    def __init__(
        self,
        pdf_extractor: DocumentExtractor,
        pdf_fallback_extractor: DocumentExtractor,
        docx_extractor: DocumentExtractor,
        cleaner: TextCleaner,
        section_detector: SectionDetector,
    ) -> None:
        self._pdf_extractor = pdf_extractor
        self._pdf_fallback = pdf_fallback_extractor
        self._docx_extractor = docx_extractor
        self._cleaner = cleaner
        self._section_detector = section_detector

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract(
        self,
        file_data: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentContent:
        """
        Run the full extraction pipeline on a document file.

        Parameters
        ----------
        file_data : Raw file bytes.
        filename  : Original filename (for tracing and error messages).
        mime_type : MIME type used to select the extractor.

        Returns
        -------
        DocumentContent — raw_text, cleaned_text, sections, word_count,
                          and char_count all populated.

        Raises
        ------
        AIValidationError       — file_data is empty or MIME type is
                                   not supported.
        DocumentExtractionError — all applicable extractors failed.
        """
        if not file_data:
            raise AIValidationError(
                f"Cannot process '{filename}': file data is empty."
            )

        normalised_mime = mime_type.lower().strip()

        if normalised_mime not in _SUPPORTED_MIME_TYPES:
            raise AIValidationError(
                f"Unsupported MIME type '{mime_type}' for file '{filename}'. "
                f"Supported types: {', '.join(sorted(_SUPPORTED_MIME_TYPES))}."
            )

        # Step 1: Extract raw text
        raw_document = self._extract_raw(file_data, filename, normalised_mime)

        # Step 2: Clean text
        cleaned_text = self._cleaner.clean(raw_document.raw_text)

        # Step 3: Compute counts from cleaned text
        word_count = len(cleaned_text.split()) if cleaned_text else 0
        char_count = len(cleaned_text)

        # Step 4: Build intermediate DocumentContent with cleaned text
        intermediate = raw_document.model_copy(update={
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "char_count": char_count,
        })

        # Step 5: Detect sections
        final_document = self._section_detector.detect(intermediate)

        logger.info(
            "Extracted '%s': %d words, %d sections, extractor=%s",
            filename,
            word_count,
            len(final_document.sections),
            final_document.extraction_metadata.get("extractor", "unknown"),
        )

        return final_document

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_raw(
        self,
        file_data: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentContent:
        """
        Select the appropriate extractor and extract raw text.

        For PDF files, tries the primary extractor first and falls back
        to PyMuPDF if pdfplumber fails. This handles corrupted PDFs
        and PDFs produced by non-standard generators.
        """
        if mime_type == _PDF_MIME:
            return self._extract_pdf(file_data, filename, mime_type)

        if mime_type in (_DOCX_MIME, _DOC_MIME):
            return self._docx_extractor.extract(file_data, filename, mime_type)

        # Unreachable because of MIME validation above, but satisfies type checker.
        raise DocumentExtractionError(
            f"No extractor registered for MIME type '{mime_type}'."
        )

    def _extract_pdf(
        self,
        file_data: bytes,
        filename: str,
        mime_type: str,
    ) -> DocumentContent:
        """
        Extract PDF text with pdfplumber, falling back to PyMuPDF on failure.

        If both extractors fail, re-raises the last DocumentExtractionError.
        """
        try:
            result = self._pdf_extractor.extract(file_data, filename, mime_type)
            logger.debug("PDF '%s': primary extractor (pdfplumber) succeeded.", filename)
            return result
        except DocumentExtractionError as primary_error:
            logger.warning(
                "PDF '%s': pdfplumber failed (%s). Retrying with PyMuPDF.",
                filename,
                primary_error.message,
            )

        try:
            result = self._pdf_fallback.extract(file_data, filename, mime_type)
            logger.debug("PDF '%s': fallback extractor (PyMuPDF) succeeded.", filename)
            return result
        except DocumentExtractionError as fallback_error:
            raise DocumentExtractionError(
                f"All PDF extractors failed for '{filename}'. "
                f"Primary: {primary_error.message}. "
                f"Fallback: {fallback_error.message}."
            ) from fallback_error
