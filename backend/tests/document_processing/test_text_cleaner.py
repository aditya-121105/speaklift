# backend/tests/document_processing/test_text_cleaner.py
"""
Unit tests for TextCleaner.

These tests are fully self-contained — no fixtures, no external files,
no databases. The cleaner is deterministic; given the same input it
always produces the same output.
"""

from __future__ import annotations

import pytest

from app.ai.document_processing.cleaners.text_cleaner import TextCleaner


@pytest.fixture()
def cleaner() -> TextCleaner:
    return TextCleaner()


# ---------------------------------------------------------------------------
# Empty / trivial inputs
# ---------------------------------------------------------------------------

class TestEmptyInputs:
    def test_empty_string_returns_empty(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("") == ""

    def test_only_whitespace_returns_empty(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("   \n\t\n   ") == ""


# ---------------------------------------------------------------------------
# Unicode normalisation
# ---------------------------------------------------------------------------

class TestUnicodeNormalisation:
    def test_nfc_normalisation(self, cleaner: TextCleaner) -> None:
        # é as decomposed (NFD: e + combining acute accent) → composed NFC
        nfd_text = "re\u0301sume\u0301"  # ré-su-mé in NFD
        result = cleaner.clean(nfd_text)
        assert result == "résumé"

    def test_ligature_fi_expanded(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("pro\ufb01le") == "profile"

    def test_ligature_fl_expanded(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("\ufb02uent") == "fluent"

    def test_ligature_ff_expanded(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("o\ufb00ice") == "office"

    def test_ligature_ffi_expanded(self, cleaner: TextCleaner) -> None:
        assert cleaner.clean("o\ufb03cial") == "official"

    def test_non_breaking_space_normalised(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Python\u00a0Developer")
        assert "\u00a0" not in result
        assert "Python Developer" in result

    def test_zero_width_space_removed(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Py\u200bthon")
        assert "\u200b" not in result
        assert "Python" in result

    def test_bom_removed(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("\ufeffHello")
        assert result == "Hello"


# ---------------------------------------------------------------------------
# Whitespace normalisation
# ---------------------------------------------------------------------------

class TestWhitespaceNormalisation:
    def test_crnl_converted_to_nl(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("line1\r\nline2")
        assert "\r" not in result
        assert "line1\nline2" in result

    def test_carriage_return_only_converted(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("line1\rline2")
        assert "\r" not in result

    def test_tab_converted_to_space(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Python\tDeveloper")
        assert "\t" not in result
        assert "Python Developer" in result

    def test_multiple_spaces_collapsed(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Python    Developer")
        assert "Python Developer" in result

    def test_trailing_spaces_stripped_from_lines(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Hello   \nWorld   ")
        lines = result.split("\n")
        for line in lines:
            assert line == line.rstrip()


# ---------------------------------------------------------------------------
# Blank line collapsing
# ---------------------------------------------------------------------------

class TestBlankLineCollapsing:
    def test_single_blank_line_preserved(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Section A\n\nSection B")
        assert "Section A\n\nSection B" in result

    def test_three_blank_lines_collapsed_to_one(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("Section A\n\n\n\nSection B")
        assert "\n\n\n" not in result
        assert "Section A" in result
        assert "Section B" in result

    def test_five_blank_lines_collapsed(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("A\n\n\n\n\n\nB")
        assert "\n\n\n" not in result


# ---------------------------------------------------------------------------
# Bullet normalisation
# ---------------------------------------------------------------------------

class TestBulletNormalisation:
    def test_unicode_bullet_normalised(self, cleaner: TextCleaner) -> None:
        # U+2022 BULLET
        result = cleaner.clean("\u2022 Python experience")
        assert "\u2022" not in result
        assert "- Python experience" in result

    def test_right_triangle_bullet_normalised(self, cleaner: TextCleaner) -> None:
        # U+25B6 BLACK RIGHT-POINTING TRIANGLE
        result = cleaner.clean("\u25b6 Led a team")
        assert "- Led a team" in result

    def test_regular_hyphen_not_affected(self, cleaner: TextCleaner) -> None:
        result = cleaner.clean("- Python experience")
        assert "- Python experience" in result

    def test_multiline_bullets_preserved(self, cleaner: TextCleaner) -> None:
        text = "\u2022 Skill one\n\u2022 Skill two\n\u2022 Skill three"
        result = cleaner.clean(text)
        assert result.count("- Skill") == 3


# ---------------------------------------------------------------------------
# Real-world-like inputs
# ---------------------------------------------------------------------------

class TestRealWorldInputs:
    def test_resume_block_cleaned(self, cleaner: TextCleaner) -> None:
        raw = (
            "John\u00a0Doe\r\n"
            "john@example.com\r\n"
            "\r\n"
            "SKILLS\r\n"
            "\u2022 Python\r\n"
            "\u2022 FastAPI\r\n"
            "\r\n"
            "EXPERIENCE\r\n"
            "Senior\u00a0Developer\t2022\u20132024\r\n"
        )
        result = cleaner.clean(raw)
        assert "\r" not in result
        assert "\u00a0" not in result
        assert "\u2022" not in result
        assert "- Python" in result
        assert "- FastAPI" in result
        assert "John Doe" in result
