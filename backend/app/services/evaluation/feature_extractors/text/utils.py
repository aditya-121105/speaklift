"""
==============================================================================
Module:
    Text Feature Utilities

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Provides reusable helper functions for text preprocessing and
    feature extraction.

Architecture:

Interview Answers
        │
        ▼
Text Utilities
        │
        ▼
Statistics Feature Extractor
Vocabulary Feature Extractor
Keyword Feature Extractor
Readability Feature Extractor
Grammar Feature Extractor
NLP Feature Extractor

Responsibilities:
    ✔ Normalize text
    ✔ Tokenize text
    ✔ Count words
    ✔ Count unique words
    ✔ Split sentences

Does NOT:
    ✘ Calculate interview scores
    ✘ Access database
    ✘ Call AI APIs
    ✘ Perform evaluation

==============================================================================
Interview Notes

Q. Why separate utility functions?

Answer:

These operations are common across multiple extractors.

Keeping them in one module:

- avoids duplicate code
- improves maintainability
- follows DRY principle
- simplifies testing

==============================================================================
"""

import re


class TextUtils:
    """
    Utility class containing reusable text processing methods.
    """

    WORD_PATTERN = re.compile(r"\b[\w']+\b")

    SENTENCE_PATTERN = re.compile(r"[.!?]+")

    @staticmethod
    def normalize_text(
        text: str,
    ) -> str:
        """
        Normalize whitespace and convert text to lowercase.
        """

        return " ".join(
            text.lower().split()
        )

    @staticmethod
    def tokenize_words(
        text: str,
    ) -> list[str]:
        """
        Split text into normalized words.
        """

        normalized = (
            TextUtils.normalize_text(text)
        )

        return (
            TextUtils.WORD_PATTERN.findall(
                normalized
            )
        )

    @staticmethod
    def split_sentences(
        text: str,
    ) -> list[str]:
        """
        Split text into sentences.

        Empty sentences are ignored.
        """

        sentences = (
            TextUtils.SENTENCE_PATTERN.split(
                text.strip()
            )
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def word_count(
        text: str,
    ) -> int:
        """
        Count words in text.
        """

        return len(
            TextUtils.tokenize_words(text)
        )

    @staticmethod
    def unique_word_count(
        text: str,
    ) -> int:
        """
        Count unique words.
        """

        return len(
            set(
                TextUtils.tokenize_words(
                    text
                )
            )
        )

    @staticmethod
    def average_word_length(
        text: str,
    ) -> float:
        """
        Calculate average word length.
        """

        words = (
            TextUtils.tokenize_words(text)
        )

        if not words:
            return 0.0

        total_characters = sum(
            len(word)
            for word in words
        )

        return (
            total_characters
            / len(words)
        )

    @staticmethod
    def average_sentence_length(
        text: str,
    ) -> float:
        """
        Calculate average sentence length
        measured in words.
        """

        sentences = (
            TextUtils.split_sentences(
                text
            )
        )

        if not sentences:
            return 0.0

        total_words = sum(
            TextUtils.word_count(
                sentence
            )
            for sentence in sentences
        )

        return (
            total_words
            / len(sentences)
        )