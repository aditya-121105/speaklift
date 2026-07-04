# backend/tests/document_processing/test_section_detector.py
"""
Unit tests for SectionDetector.
"""

from __future__ import annotations

import pytest

from app.ai.document_processing.schemas import DocumentContent, SectionType
from app.ai.document_processing.section_detector import SectionDetector


@pytest.fixture()
def detector() -> SectionDetector:
    return SectionDetector()


def _doc(text: str) -> DocumentContent:
    return DocumentContent(raw_text=text, cleaned_text=text)


class TestNoSections:
    def test_empty_text(self, detector: SectionDetector) -> None:
        assert detector.detect(_doc("")).sections == {}

    def test_plain_lines_no_headings(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("John Doe\njohn@example.com"))
        assert isinstance(doc.sections, dict)


class TestStandardHeadings:
    def test_skills(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("SKILLS\n- Python\n- FastAPI"))
        assert SectionType.SKILLS.value in doc.sections
        assert "Python" in doc.sections[SectionType.SKILLS.value].content

    def test_education(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("EDUCATION\nB.Sc. CS — MIT, 2020"))
        assert SectionType.EDUCATION.value in doc.sections

    def test_experience(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("EXPERIENCE\nSoftware Engineer, 2022–2024"))
        assert SectionType.EXPERIENCE.value in doc.sections

    def test_projects(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("PROJECTS\nBuilt an AI chatbot"))
        assert SectionType.PROJECTS.value in doc.sections

    def test_certifications(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("CERTIFICATIONS\nAWS Solutions Architect"))
        assert SectionType.CERTIFICATIONS.value in doc.sections

    def test_summary(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("SUMMARY\nExperienced backend developer."))
        assert SectionType.SUMMARY.value in doc.sections

    def test_achievements(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("ACHIEVEMENTS\nEmployee of the Year 2023"))
        assert SectionType.ACHIEVEMENTS.value in doc.sections


class TestHeadingVariants:
    @pytest.mark.parametrize("heading", [
        "Skills", "SKILLS", "Technical Skills", "Core Competencies", "Tech Stack",
    ])
    def test_skills_variants(self, detector: SectionDetector, heading: str) -> None:
        doc = detector.detect(_doc(f"{heading}\n- Python"))
        assert SectionType.SKILLS.value in doc.sections

    @pytest.mark.parametrize("heading", [
        "Work Experience", "WORK EXPERIENCE", "Professional Experience",
        "Employment History",
    ])
    def test_experience_variants(self, detector: SectionDetector, heading: str) -> None:
        doc = detector.detect(_doc(f"{heading}\nSoftware Engineer"))
        found = any(
            k in (SectionType.WORK_EXPERIENCE.value, SectionType.EXPERIENCE.value)
            for k in doc.sections
        )
        assert found

    def test_heading_with_colon(self, detector: SectionDetector) -> None:
        doc = detector.detect(_doc("Skills:\n- Python\n- Go"))
        assert SectionType.SKILLS.value in doc.sections


class TestMultiSection:
    def test_full_resume_all_sections(self, detector: SectionDetector) -> None:
        text = (
            "Jane Smith\njane@example.com\n\n"
            "SUMMARY\nAI engineer.\n\n"
            "EDUCATION\nStanford 2019\n\n"
            "EXPERIENCE\nML Engineer at OpenAI\n\n"
            "SKILLS\n- Python\n- PyTorch\n\n"
            "PROJECTS\nLanguage model from scratch.\n\n"
            "CERTIFICATIONS\nAWS SA\n"
        )
        doc = detector.detect(_doc(text))
        for st in [
            SectionType.SUMMARY, SectionType.EDUCATION, SectionType.EXPERIENCE,
            SectionType.SKILLS, SectionType.PROJECTS, SectionType.CERTIFICATIONS,
        ]:
            assert st.value in doc.sections

    def test_skills_content_does_not_include_education(self, detector: SectionDetector) -> None:
        text = "SKILLS\n- Python\n\nEDUCATION\nMIT 2020\n"
        doc = detector.detect(_doc(text))
        assert "MIT" not in doc.sections[SectionType.SKILLS.value].content

    def test_preamble_classified_as_contact(self, detector: SectionDetector) -> None:
        text = "John Doe\njohn@example.com\n\nSKILLS\n- Python"
        doc = detector.detect(_doc(text))
        assert SectionType.CONTACT.value in doc.sections
        assert "John Doe" in doc.sections[SectionType.CONTACT.value].content


class TestEdgeCases:
    def test_long_line_not_treated_as_heading(self, detector: SectionDetector) -> None:
        long_line = "This is a very long sentence mentioning skills and experience " * 3
        doc = detector.detect(_doc(long_line))
        assert SectionType.SKILLS.value not in doc.sections

    def test_duplicate_section_type_handled(self, detector: SectionDetector) -> None:
        text = "EXPERIENCE\nJob A\n\nEXPERIENCE\nJob B\n"
        doc = detector.detect(_doc(text))
        assert any("experience" in k for k in doc.sections)
