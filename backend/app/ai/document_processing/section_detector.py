# backend/app/ai/document_processing/section_detector.py
"""
Section Detector
================

Detects resume sections using deterministic heading matching.

No ML, no NLP models, no AI. Pure rule-based pattern matching.

Algorithm
---------
1. Split cleaned_text into lines.
2. For each line, test against a prioritised set of heading patterns.
3. A line is a heading if:
   a. It matches a known heading pattern (case-insensitive), AND
   b. It is "heading-like" in formatting:
      - Very short (≤ MAX_HEADING_CHARS characters of body text), OR
      - All uppercase, OR
      - Followed immediately by a blank line, OR
      - Ends with a colon
4. The text between heading N and heading N+1 becomes section N's content.
5. Text before the first heading is classified as a preamble (CONTACT or OTHER).

Heading patterns
----------------
Patterns are compiled regexes. Each maps to a SectionType.
Patterns are checked in PRIORITY ORDER — more specific patterns first.

Sprint C.3 — implemented (deterministic, no AI).
"""

from __future__ import annotations

import re
from typing import NamedTuple

from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_HEADING_CHARS = 60
"""Maximum character length for a line to be considered a heading candidate."""


# ---------------------------------------------------------------------------
# Heading pattern registry
# ---------------------------------------------------------------------------

class _HeadingPattern(NamedTuple):
    section_type: SectionType
    pattern: re.Pattern[str]


# Each tuple: (SectionType, compiled pattern)
# Patterns are listed in priority order (more specific first).
_HEADING_PATTERNS: tuple[_HeadingPattern, ...] = (
    # -- Contact / Personal ---------------------------------------------------
    _HeadingPattern(
        SectionType.CONTACT,
        re.compile(r"^(contact(\s+information)?|personal(\s+details)?|about\s+me)\s*:?\s*$", re.I),
    ),
    # -- Summary / Objective --------------------------------------------------
    _HeadingPattern(
        SectionType.OBJECTIVE,
        re.compile(r"^(career\s+)?objective\s*:?\s*$", re.I),
    ),
    _HeadingPattern(
        SectionType.SUMMARY,
        re.compile(
            r"^(professional\s+)?(summary|profile|overview|synopsis"
            r"|career\s+summary|executive\s+summary)\s*:?\s*$",
            re.I,
        ),
    ),
    # -- Education ------------------------------------------------------------
    _HeadingPattern(
        SectionType.EDUCATION,
        re.compile(
            r"^(education(al)?\s*(background|qualifications|history)?|"
            r"academic(\s+background)?|qualifications?|degrees?)\s*:?\s*$",
            re.I,
        ),
    ),
    # -- Experience -----------------------------------------------------------
    _HeadingPattern(
        SectionType.WORK_EXPERIENCE,
        re.compile(
            r"^(work(\s+history|\s+experience)?|professional(\s+experience)?|"
            r"employment(\s+history)?|internship(s)?|industry\s+experience)\s*:?\s*$",
            re.I,
        ),
    ),
    _HeadingPattern(
        SectionType.EXPERIENCE,
        re.compile(r"^experience\s*:?\s*$", re.I),
    ),
    # -- Projects -------------------------------------------------------------
    _HeadingPattern(
        SectionType.PROJECTS,
        re.compile(
            r"^(projects?|personal\s+projects?|academic\s+projects?|"
            r"side\s+projects?|key\s+projects?|portfolio)\s*:?\s*$",
            re.I,
        ),
    ),
    # -- Skills ---------------------------------------------------------------
    _HeadingPattern(
        SectionType.SKILLS,
        re.compile(
            r"^(technical\s+)?(skills?|competenc(y|ies)|expertise|"
            r"technologies|tech\s+stack|core\s+competencies|"
            r"areas?\s+of\s+expertise|proficiencies)\s*:?\s*$",
            re.I,
        ),
    ),
    # -- Certifications -------------------------------------------------------
    _HeadingPattern(
        SectionType.CERTIFICATIONS,
        re.compile(
            r"^(certifications?|certificates?|credentials?|"
            r"professional\s+certifications?|licenses?\s+and\s+certifications?)\s*:?\s*$",
            re.I,
        ),
    ),
    # -- Achievements / Awards ------------------------------------------------
    _HeadingPattern(
        SectionType.ACHIEVEMENTS,
        re.compile(
            r"^(achievements?|accomplishments?|key\s+achievements?|"
            r"highlights?)\s*:?\s*$",
            re.I,
        ),
    ),
    _HeadingPattern(
        SectionType.AWARDS,
        re.compile(r"^(awards?(\s+and\s+honors?)?|honors?|distinctions?)\s*:?\s*$", re.I),
    ),
    # -- Publications ---------------------------------------------------------
    _HeadingPattern(
        SectionType.PUBLICATIONS,
        re.compile(r"^(publications?|papers?|research|patents?)\s*:?\s*$", re.I),
    ),
    # -- Languages ------------------------------------------------------------
    _HeadingPattern(
        SectionType.LANGUAGES,
        re.compile(r"^languages?\s*:?\s*$", re.I),
    ),
    # -- Interests ------------------------------------------------------------
    _HeadingPattern(
        SectionType.INTERESTS,
        re.compile(r"^(interests?|hobbies|activities|extracurriculars?)\s*:?\s*$", re.I),
    ),
    # -- References -----------------------------------------------------------
    _HeadingPattern(
        SectionType.REFERENCES,
        re.compile(r"^references?\s*:?\s*$", re.I),
    ),
)


# ---------------------------------------------------------------------------
# Internal helper types
# ---------------------------------------------------------------------------

class _RawHeading(NamedTuple):
    line_index: int
    char_offset: int
    section_type: SectionType
    raw_text: str


# ---------------------------------------------------------------------------
# SectionDetector
# ---------------------------------------------------------------------------

class SectionDetector:
    """
    Detects resume sections using deterministic heading pattern matching.

    The detector is stateless and has no external dependencies.
    A single instance can be reused across many documents.

    Usage
    -----
    detector = SectionDetector()
    content = detector.detect(document_content_with_cleaned_text)
    # content.sections is now populated
    """

    def detect(self, document: DocumentContent) -> DocumentContent:
        """
        Detect sections in the document's cleaned_text and return an
        updated DocumentContent with sections populated.

        If cleaned_text is empty, the original document is returned unchanged.

        Parameters
        ----------
        document : DocumentContent with cleaned_text already populated.

        Returns
        -------
        DocumentContent — a new (frozen) instance with sections filled in.
        """
        text = document.cleaned_text or document.raw_text
        if not text.strip():
            return document

        headings = self._find_headings(text)
        sections = self._build_sections(text, headings)

        return document.model_copy(update={"sections": sections})

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _find_headings(self, text: str) -> list[_RawHeading]:
        """
        Scan text line by line and identify heading lines.

        Returns a list of _RawHeading, ordered by appearance.
        """
        lines = text.split("\n")
        headings: list[_RawHeading] = []
        char_offset = 0

        for line_index, line in enumerate(lines):
            stripped = line.strip()

            if stripped and self._is_heading(stripped, line_index, lines):
                section_type = self._classify_heading(stripped)
                headings.append(_RawHeading(
                    line_index=line_index,
                    char_offset=char_offset,
                    section_type=section_type,
                    raw_text=stripped,
                ))

            char_offset += len(line) + 1  # +1 for the \n

        return headings

    @staticmethod
    def _is_heading(line: str, line_index: int, all_lines: list[str]) -> bool:
        """
        Return True if this line looks structurally like a heading.

        A line qualifies if it:
        - Is short enough (≤ MAX_HEADING_CHARS), AND meets at least one of:
          - Ends with a colon
          - Is all uppercase (and at least 3 chars)
          - Is followed by a blank line
          - Matches a known heading pattern (checked by caller)
        """
        if len(line) > MAX_HEADING_CHARS:
            return False

        # Ends with colon
        if line.endswith(":"):
            return True

        # All uppercase (and not just initials/acronyms)
        if line.isupper() and len(line) >= 3:
            return True

        # Followed immediately by a blank line
        next_index = line_index + 1
        if next_index < len(all_lines) and all_lines[next_index].strip() == "":
            return True

        # Check against known heading patterns even without formatting cues
        # (handles "Skills" alone on a line with no colon/caps/blank-after)
        return _classify_line(line) is not None

    @staticmethod
    def _classify_heading(line: str) -> SectionType:
        """Return the SectionType for a heading line, defaulting to OTHER."""
        result = _classify_line(line)
        return result if result is not None else SectionType.OTHER

    def _build_sections(
        self,
        text: str,
        headings: list[_RawHeading],
    ) -> dict[str, DocumentSection]:
        """
        Build DocumentSection objects from detected headings.

        Text between heading[i] and heading[i+1] is the content of
        section[i]. Text after the last heading is the last section's content.
        Text before the first heading is preamble (CONTACT or OTHER).
        """
        if not headings:
            return {}

        sections: dict[str, DocumentSection] = {}
        text_length = len(text)

        # Preamble (before first heading)
        first_heading = headings[0]
        if first_heading.char_offset > 0:
            preamble = text[: first_heading.char_offset].strip()
            if preamble:
                sections[SectionType.CONTACT.value] = DocumentSection(
                    section_type=SectionType.CONTACT,
                    heading="",
                    content=preamble,
                    start_char=0,
                    end_char=first_heading.char_offset,
                )

        # Each heading → next heading
        for i, heading in enumerate(headings):
            next_start = headings[i + 1].char_offset if i + 1 < len(headings) else text_length

            # Content starts after the heading line itself
            heading_end = heading.char_offset + len(heading.raw_text)
            content_raw = text[heading_end:next_start].strip()

            key = heading.section_type.value
            # If the same section type appears twice, append with a suffix
            if key in sections:
                key = f"{key}_{i}"

            sections[key] = DocumentSection(
                section_type=heading.section_type,
                heading=heading.raw_text,
                content=content_raw,
                start_char=heading.char_offset,
                end_char=next_start,
            )

        return sections


# ---------------------------------------------------------------------------
# Module-level helper (used by both _is_heading and _classify_heading)
# ---------------------------------------------------------------------------

def _classify_line(line: str) -> SectionType | None:
    """
    Match a line against all known heading patterns.

    Returns the first matching SectionType, or None if no match.
    """
    for heading_pattern in _HEADING_PATTERNS:
        if heading_pattern.pattern.match(line.strip()):
            return heading_pattern.section_type
    return None
