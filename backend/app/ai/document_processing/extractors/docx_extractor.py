# backend/app/ai/document_processing/extractors/docx_extractor.py
"""
DOCX Extractor — python-docx
==============================

Extracts text from Microsoft Word (.docx) files using python-docx.

Text extraction strategy
------------------------
1. All paragraphs are extracted in document order.
2. Table cell text is extracted row-by-row, cell-by-cell, separated by
   tab characters so that table structure is at least partially preserved.
3. Headers and footers are NOT extracted (they typically contain page
   numbers, document titles, and other noise — not resume content).
4. Paragraphs with no visible text are skipped.

Sprint C.3 — implemented.
"""

from __future__ import annotations

import io
import logging

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.ai.document_processing.extractors import DocumentExtractor
from app.ai.document_processing.schemas import DocumentContent
from app.ai.shared.exceptions import AIValidationError, DocumentExtractionError

logger = logging.getLogger(__name__)

_SUPPORTED_MIME_TYPES = frozenset({
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
})


class DOCXExtractor(DocumentExtractor):
    """
    Extracts text from DOCX files using python-docx.

    The extractor processes document body elements in order (paragraphs
    and tables), preserving the reading sequence as it appears in the
    document. This is important for section detection.

    DOCX files have no concept of "pages" at the XML level — page_count
    is set to None.
    """

    def extract(
        self,
        file_data: bytes,
        filename: str = "",
        mime_type: str = "",
    ) -> DocumentContent:
        """
        Extract text from DOCX bytes.

        Parameters
        ----------
        file_data : Raw bytes of the .docx file.
        filename  : Original filename (used in error messages only).
        mime_type : Expected to be a DOCX MIME type.

        Returns
        -------
        DocumentContent with raw_text populated. page_count is None.

        Raises
        ------
        AIValidationError       — file_data is empty.
        DocumentExtractionError — python-docx cannot parse the file,
                                   or no text could be extracted.
        """
        if not file_data:
            raise AIValidationError(
                f"Cannot extract DOCX '{filename}': file data is empty."
            )

        try:
            document = docx.Document(io.BytesIO(file_data))
        except Exception as exc:
            raise DocumentExtractionError(
                f"python-docx could not open DOCX '{filename}': {exc}"
            ) from exc

        parts: list[str] = []
        paragraph_count = 0
        table_count = 0

        try:
            for element in self._iter_block_elements(document):
                if isinstance(element, Paragraph):
                    text = element.text.strip()
                    if text:
                        parts.append(text)
                        paragraph_count += 1
                elif isinstance(element, Table):
                    table_text = self._extract_table_text(element)
                    if table_text:
                        parts.append(table_text)
                        table_count += 1
        except Exception as exc:
            raise DocumentExtractionError(
                f"Error reading document body of '{filename}': {exc}"
            ) from exc

        raw_text = "\n".join(parts)

        if not raw_text.strip():
            raise DocumentExtractionError(
                f"python-docx extracted no text from '{filename}'. "
                "The DOCX may contain only images or be malformed."
            )

        logger.debug(
            "DOCXExtractor: extracted %d chars (%d paragraphs, %d tables) from '%s'",
            len(raw_text),
            paragraph_count,
            table_count,
            filename,
        )

        return DocumentContent(
            raw_text=raw_text,
            page_count=None,
            source_filename=filename,
            mime_type=mime_type or (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
            extraction_metadata={
                "extractor": "python-docx",
                "paragraph_count": paragraph_count,
                "table_count": table_count,
            },
        )

    def supports(self, mime_type: str) -> bool:
        """Return True for DOCX and legacy DOC MIME types."""
        return mime_type.lower() in _SUPPORTED_MIME_TYPES

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _iter_block_elements(document: docx.Document):
        """
        Yield block-level elements (Paragraph or Table) in document order.

        python-docx exposes paragraphs and tables separately; this
        method interleaves them using the underlying XML element order
        so that the reading sequence is preserved.
        """
        body = document.element.body
        for child in body:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "p":
                yield Paragraph(child, document)
            elif tag == "tbl":
                yield Table(child, document)

    @staticmethod
    def _extract_table_text(table: Table) -> str:
        """
        Extract text from a table, joining cells with tabs and rows with newlines.

        Parameters
        ----------
        table : python-docx Table object.

        Returns
        -------
        str — tab/newline separated cell text, or empty string if all cells
              are empty.
        """
        rows: list[str] = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                rows.append("\t".join(cells))
        return "\n".join(rows)
