# backend/app/ai/document_processing/extractors/pymupdf_extractor.py
"""
PDF Extractor — PyMuPDF (Fallback)
====================================

Extracts text from PDF files using PyMuPDF (fitz).

PyMuPDF is used as the fallback extractor when pdfplumber fails.
It handles a wider range of corrupted or unusual PDFs because it is
backed by the highly robust MuPDF C library.

When to use
-----------
DocumentExtractionServiceImpl tries PDFPlumberExtractor first.
If it raises DocumentExtractionError, the service retries with this class.

Sprint C.3 — implemented.
"""

from __future__ import annotations

import logging

import fitz  # PyMuPDF

from app.ai.document_processing.extractors import DocumentExtractor
from app.ai.document_processing.schemas import DocumentContent
from app.ai.shared.exceptions import AIValidationError, DocumentExtractionError

logger = logging.getLogger(__name__)

_SUPPORTED_MIME_TYPES = frozenset({"application/pdf"})


class PyMuPDFExtractor(DocumentExtractor):
    """
    Extracts text from PDF files using PyMuPDF (fitz).

    Text is extracted using fitz.Page.get_text("text") which preserves
    reading order and handles right-to-left text and unusual encodings
    better than pdfminer-based extractors.

    This extractor is intentionally conservative: it will succeed on
    files that pdfplumber cannot open. However, layout preservation
    may be slightly worse for complex multi-column documents.
    """

    def extract(
        self,
        file_data: bytes,
        filename: str = "",
        mime_type: str = "",
    ) -> DocumentContent:
        """
        Extract text from PDF bytes using PyMuPDF.

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
        DocumentExtractionError — PyMuPDF cannot parse the file,
                                   or no text could be extracted.
        """
        if not file_data:
            raise AIValidationError(
                f"Cannot extract PDF '{filename}': file data is empty."
            )

        try:
            doc = fitz.open(stream=file_data, filetype="pdf")
        except Exception as exc:
            raise DocumentExtractionError(
                f"PyMuPDF could not open PDF '{filename}': {exc}"
            ) from exc

        page_count = doc.page_count
        page_texts: list[str] = []

        try:
            for page_num in range(page_count):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text("text")
                    if text and text.strip():
                        page_texts.append(text)
                except Exception as exc:
                    logger.warning(
                        "PyMuPDF failed to extract page %d of '%s': %s",
                        page_num + 1,
                        filename,
                        exc,
                    )
        finally:
            doc.close()

        raw_text = "\n\n".join(page_texts)

        if not raw_text.strip():
            raise DocumentExtractionError(
                f"PyMuPDF extracted no text from '{filename}'. "
                "The PDF may be image-only (scanned). Use an OCR extractor."
            )

        logger.debug(
            "PyMuPDFExtractor: extracted %d chars from %d pages of '%s'",
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
                "extractor": "pymupdf",
                "page_count": page_count,
                "pages_with_text": len(page_texts),
            },
        )

    def supports(self, mime_type: str) -> bool:
        """Return True for application/pdf."""
        return mime_type.lower() in _SUPPORTED_MIME_TYPES
