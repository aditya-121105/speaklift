# backend/app/ai/document_processing/schemas/__init__.py
"""
Document Processing Schemas
============================

Pydantic models for document extraction inputs and outputs.

DocumentContent is the primary output contract: it represents a parsed,
cleaned, and section-detected document ready for NLP processing.

Sprint C.2 — initial schema defined.
Sprint C.3 — DocumentSection added; DocumentContent extended with
             cleaned_text and sections.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SectionType(str, Enum):
    """
    Canonical section names recognised by the SectionDetector.

    Values are lowercase strings so they can be used directly as
    dictionary keys and compared case-insensitively.
    """

    SUMMARY = "summary"
    OBJECTIVE = "objective"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    WORK_EXPERIENCE = "work_experience"
    PROJECTS = "projects"
    SKILLS = "skills"
    CERTIFICATIONS = "certifications"
    ACHIEVEMENTS = "achievements"
    AWARDS = "awards"
    PUBLICATIONS = "publications"
    LANGUAGES = "languages"
    INTERESTS = "interests"
    REFERENCES = "references"
    CONTACT = "contact"
    REQUIREMENTS = "requirements"
    RESPONSIBILITIES = "responsibilities"
    BENEFITS = "benefits"
    COMPANY_OVERVIEW = "company_overview"
    OTHER = "other"


class DocumentSection(BaseModel):
    """
    A single detected section within a resume document.

    Fields
    ------
    section_type  : Canonical section type (from SectionType enum).
    heading       : The raw heading text as it appeared in the document.
    content       : The section body text (everything between this heading
                    and the next one, cleaned and normalised).
    start_char    : Character offset of the heading in cleaned_text.
    end_char      : Character offset of the end of this section.
    """

    model_config = ConfigDict(frozen=True)

    section_type: SectionType
    heading: str
    content: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)


class DocumentContent(BaseModel):
    """
    Structured content extracted from a raw document file.

    This is the primary output of the DocumentProcessingPipeline.
    It carries both the raw extracted text and the post-processing
    artefacts (cleaned text, detected sections).

    Fields
    ------
    raw_text        : Full extracted text, preserving paragraph structure
                      as returned by the extractor. Not cleaned.
    cleaned_text    : Text after applying TextCleaner — normalised unicode,
                      whitespace, bullet characters. Used by NLP pipeline.
    page_count      : Number of pages (None for DOCX / single-page formats).
    word_count      : Word count computed from cleaned_text.
    char_count      : Character count computed from cleaned_text.
    source_filename : Original filename for traceability.
    mime_type       : MIME type of the source file.
    sections        : Ordered dict mapping SectionType → DocumentSection.
                      Empty dict if no sections were detected.
    extraction_metadata : Provider-specific extras. Not for business logic.
    """

    model_config = ConfigDict(frozen=True)

    raw_text: str
    cleaned_text: str = ""
    page_count: int | None = None
    word_count: int = Field(default=0, ge=0)
    char_count: int = Field(default=0, ge=0)
    source_filename: str = ""
    mime_type: str = ""
    sections: dict[str, DocumentSection] = Field(default_factory=dict)
    extraction_metadata: dict = Field(default_factory=dict)
