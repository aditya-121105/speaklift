# backend/app/ai/document_processing/cleaners/text_cleaner.py
"""
Text Cleaner
============

Deterministic text cleaning and normalisation for extracted document text.

Pipeline applied by TextCleaner.clean()
-----------------------------------------
1. Decode/normalise Unicode (NFC form, ligature expansion)
2. Normalise whitespace (tabs → spaces, \r\n → \n)
3. Expand common ligatures (ﬁ → fi, ﬂ → fl, etc.)
4. Normalise bullet characters to ASCII hyphen
5. Remove zero-width and invisible characters
6. Collapse runs of blank lines (max 1 consecutive blank line)
7. Strip leading/trailing whitespace per line
8. Strip leading/trailing whitespace for the whole document

Design rules
------------
- Pure functions only. No state, no I/O.
- Input and output are both str.
- Never loses section structure (headings, bullets, blank-line separators).
- Does NOT remove content — only normalises presentation.

Sprint C.3 — implemented.
"""

from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Ligature expansion table
# ---------------------------------------------------------------------------

_LIGATURES: dict[str, str] = {
    "\ufb00": "ff",   # ﬀ
    "\ufb01": "fi",   # ﬁ
    "\ufb02": "fl",   # ﬂ
    "\ufb03": "ffi",  # ﬃ
    "\ufb04": "ffl",  # ﬄ
    "\ufb05": "st",   # ﬅ
    "\ufb06": "st",   # ﬆ
}

_LIGATURE_TABLE = str.maketrans(_LIGATURES)


# ---------------------------------------------------------------------------
# Bullet normalisation
# ---------------------------------------------------------------------------

# Unicode bullet and dash characters to normalise to ASCII hyphen-space.
_BULLET_PATTERN = re.compile(
    r"^[\u2022\u2023\u2024\u2025\u2043\u204c\u204d\u2219"
    r"\u25aa\u25ab\u25b6\u25cf\u25e6\u29bf\u2014\u2013\u2012"
    r"\uf0b7\u00b7\u00bb]\s*",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Zero-width / invisible character removal
# ---------------------------------------------------------------------------

_INVISIBLE_PATTERN = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060\u2061"
    r"\u2062\u2063\u2064\ufeff]"
)


# ---------------------------------------------------------------------------
# Non-breaking space and special whitespace normalisation
# ---------------------------------------------------------------------------

_SPECIAL_SPACE_PATTERN = re.compile(
    r"[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]"
)


# ---------------------------------------------------------------------------
# Multiple blank lines collapse
# ---------------------------------------------------------------------------

_MULTI_BLANK_LINE_PATTERN = re.compile(r"\n{3,}")


class TextCleaner:
    """
    Applies the full text normalisation pipeline to extracted document text.

    Usage
    -----
    cleaner = TextCleaner()
    cleaned = cleaner.clean(raw_text)

    The cleaner is stateless — a single instance may be shared across
    all extraction calls (thread-safe).
    """

    def clean(self, text: str) -> str:
        """
        Apply the full cleaning pipeline to raw extracted text.

        Parameters
        ----------
        text : Raw text as returned by a document extractor.

        Returns
        -------
        str — cleaned, normalised text. Empty string if input is empty.
        """
        if not text:
            return ""

        text = self._normalise_unicode(text)
        text = self._expand_ligatures(text)
        text = self._remove_invisible_chars(text)
        text = self._normalise_whitespace(text)
        text = self._normalise_bullets(text)
        text = self._collapse_blank_lines(text)
        text = self._strip_lines(text)
        return text.strip()

    # ------------------------------------------------------------------
    # Private pipeline steps
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_unicode(text: str) -> str:
        """Apply NFC normalisation to resolve composed/decomposed forms."""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _expand_ligatures(text: str) -> str:
        """Replace typographic ligatures with their ASCII equivalents."""
        return text.translate(_LIGATURE_TABLE)

    @staticmethod
    def _remove_invisible_chars(text: str) -> str:
        """Strip zero-width and invisible Unicode control characters."""
        return _INVISIBLE_PATTERN.sub("", text)

    @staticmethod
    def _normalise_whitespace(text: str) -> str:
        """
        Normalise whitespace characters.

        - \r\n and \r → \n
        - Non-breaking and special spaces → regular space
        - Tabs → single space
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = _SPECIAL_SPACE_PATTERN.sub(" ", text)
        text = text.replace("\t", " ")
        # Collapse multiple spaces within a line (not newlines)
        text = re.sub(r"[^\S\n]+", " ", text)
        return text

    @staticmethod
    def _normalise_bullets(text: str) -> str:
        """Replace Unicode bullet characters with '- ' (ASCII hyphen-space)."""
        return _BULLET_PATTERN.sub("- ", text)

    @staticmethod
    def _collapse_blank_lines(text: str) -> str:
        """Collapse 3+ consecutive newlines to exactly 2 (one blank line)."""
        return _MULTI_BLANK_LINE_PATTERN.sub("\n\n", text)

    @staticmethod
    def _strip_lines(text: str) -> str:
        """Strip trailing whitespace from each line."""
        return "\n".join(line.rstrip() for line in text.split("\n"))
