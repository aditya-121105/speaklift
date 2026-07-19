# backend/app/ai/document_processing/extractors/pdf_extractor.py
"""
PDF Extractor — pdfplumber (Primary)
=====================================

Extracts text from PDF files using pdfplumber.

pdfplumber is the primary PDF extractor because it:
- Preserves reading order more reliably than raw pdfminer
- Handles multi-column layouts better than PyMuPDF for text-heavy PDFs
- Provides word-level bounding boxes for future layout analysis
- Is pure-Python with no native binary dependency

Fallback
--------
If pdfplumber fails (corrupted PDF, no text layer, unexpected error),
DocumentExtractionServiceImpl will retry with PyMuPDFExtractor.

Sprint C.3 — implemented.
"""

from __future__ import annotations

import io
import logging

import pdfplumber

from app.ai.document_processing.extractors import DocumentExtractor
from app.ai.document_processing.schemas import DocumentContent
from app.ai.shared.exceptions import AIValidationError, DocumentExtractionError
from app.ai.document_processing.layout_reconstructor import DocumentReconstructionEngine

logger = logging.getLogger(__name__)

_SUPPORTED_MIME_TYPES = frozenset({"application/pdf"})


class PDFPlumberExtractor(DocumentExtractor):
    """
    Extracts text from PDF files using pdfplumber.

    Text is extracted page by page. Pages are joined with a newline
    separator so that the caller can identify page boundaries in
    the raw_text if needed.

    Empty pages (no extractable text) are skipped silently. If the
    entire document yields no text, DocumentExtractionError is raised
    to signal that the fallback extractor should be tried.
    """

    def extract(
        self,
        file_data: bytes,
        filename: str = "",
        mime_type: str = "",
    ) -> DocumentContent:
        """
        Extract text from PDF bytes using pdfplumber.

        Parameters
        ----------
        file_data : Raw PDF bytes.
        filename  : Original filename (used in error messages only).
        mime_type : Expected to be 'application/pdf'.

        Returns
        -------
        DocumentContent with raw_text populated.

        Raises
        ------
        AIValidationError       — file_data is empty.
        DocumentExtractionError — pdfplumber cannot parse the file,
                                   or no text could be extracted.
        """
        if not file_data:
            raise AIValidationError(
                f"Cannot extract PDF '{filename}': file data is empty."
            )

        try:
            pdf_file = io.BytesIO(file_data)
            page_texts: list[str] = []

            with pdfplumber.open(pdf_file, laparams={"all_texts": True}) as pdf:
                page_count = len(pdf.pages)
                reconstructor = DocumentReconstructionEngine()

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = reconstructor.reconstruct(page)
                        if text and text.strip():
                            page_texts.append(text)
                    except Exception as exc:
                        # Log and skip the problematic page rather than failing.
                        logger.warning(
                            "pdfplumber failed to extract page %d of '%s': %s",
                            page_num,
                            filename,
                            exc,
                        )

        except Exception as exc:
            raise DocumentExtractionError(
                f"pdfplumber could not open PDF '{filename}': {exc}"
            ) from exc

        raw_text = "\n\n".join(page_texts)

        if not raw_text.strip():
            raise DocumentExtractionError(
                f"pdfplumber extracted no text from '{filename}'. "
                "The PDF may be image-only (scanned) or encrypted. "
                "Retry with PyMuPDF or an OCR extractor."
            )

        logger.debug(
            "PDFPlumberExtractor: extracted %d chars from %d pages of '%s'",
            len(raw_text),
            page_count,
            filename,
        )

        return DocumentContent(
            raw_text=raw_text,
            page_count=page_count,
            source_filename=filename,
            mime_type=mime_type or "application/pdf",
            extraction_metadata={
                "extractor": "pdfplumber",
                "page_count": page_count,
                "pages_with_text": len(page_texts),
            },
        )

    def supports(self, mime_type: str) -> bool:
        """Return True for application/pdf."""
        return mime_type.lower() in _SUPPORTED_MIME_TYPES
