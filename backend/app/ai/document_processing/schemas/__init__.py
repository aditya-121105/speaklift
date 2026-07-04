# backend/app/ai/document_processing/schemas/__init__.py
"""
Document Processing Schemas
============================

Pydantic models for document extraction inputs and outputs.

DocumentContent is the primary output contract: it represents a parsed
document as structured text, ready for NLP processing.

Sprint C.2 — schemas defined. No extraction logic.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentContent(BaseModel):
    """
    Structured content extracted from a raw document file.

    This is the output contract of DocumentExtractor and the primary
    input to the NLP pipeline.

    Fields
    ------
    raw_text        : Full extracted text, preserving paragraph structure.
    page_count      : Number of pages (None for DOCX / single-page formats).
    word_count      : Total word count in raw_text.
    char_count      : Total character count in raw_text.
    source_filename : Original filename for traceability.
    mime_type       : MIME type of the source file.
    extraction_metadata : Provider-specific details (e.g. extractor version,
                          font info). Not for business logic.
    """

    model_config = ConfigDict(frozen=True)

    raw_text: str
    page_count: int | None = None
    word_count: int = Field(default=0, ge=0)
    char_count: int = Field(default=0, ge=0)
    source_filename: str = ""
    mime_type: str = ""
    extraction_metadata: dict = Field(default_factory=dict)
