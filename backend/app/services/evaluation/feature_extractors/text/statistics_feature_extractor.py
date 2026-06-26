"""
==============================================================================
Module:
    Statistics Feature Extractor

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Extract statistical features from an interview corpus.

Responsibilities:
    ✔ Count answers
    ✔ Count words
    ✔ Compute averages
    ✔ Compute vocabulary richness

Does NOT:
    ✘ Evaluate interview quality
    ✘ Call AI models
    ✘ Access database

==============================================================================
"""

from app.schemas.evaluation.text_document import (
    TextDocument,
)


class StatisticsFeatureExtractor:
    """
    Extract statistical features from interview text.
    """

    SHORT_ANSWER_THRESHOLD = 10

    LONG_ANSWER_THRESHOLD = 80

    @classmethod
    def extract(
        cls,
        documents: list[TextDocument],
        durations: list[int] | None = None,
    ) -> dict:
        """
        Extract statistical features.

        Parameters
        ----------
        documents:
            List of processed interview answers.

        durations:
            Duration (seconds) of each answer.

        Returns
        -------
        Dictionary containing statistical features.
        """

        total_answers = len(documents)

        total_words = sum(
            len(document.tokens)
            for document in documents
        )

        unique_words = len(
            {
                token
                for document in documents
                for token in document.lemmas
            }
        )

        average_words = (
            total_words / total_answers
            if total_answers
            else 0.0
        )

        average_word_length = (
            sum(
                len(token)
                for document in documents
                for token in document.tokens
            )
            / total_words
            if total_words
            else 0.0
        )

        total_sentences = sum(
            len(document.sentences)
            for document in documents
        )

        average_sentence_length = (
            total_words / total_sentences
            if total_sentences
            else 0.0
        )

        empty_answers = sum(
            len(document.tokens) == 0
            for document in documents
        )

        short_answers = sum(
            len(document.tokens)
            < cls.SHORT_ANSWER_THRESHOLD
            for document in documents
        )

        long_answers = sum(
            len(document.tokens)
            > cls.LONG_ANSWER_THRESHOLD
            for document in documents
        )

        vocabulary_richness = (
            unique_words / total_words
            if total_words
            else 0.0
        )

        average_duration = (
            sum(durations) / len(durations)
            if durations
            else 0.0
        )

        return {
            "total_answers": total_answers,
            "total_words": total_words,
            "unique_words": unique_words,
            "average_words_per_answer": average_words,
            "average_word_length": average_word_length,
            "average_sentence_length": average_sentence_length,
            "empty_answers": empty_answers,
            "short_answers": short_answers,
            "long_answers": long_answers,
            "average_answer_duration": average_duration,
            "vocabulary_richness": vocabulary_richness,
        }