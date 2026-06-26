"""
==============================================================================
Module:
    Statistics Feature Extractor

Purpose:
    Extracts numerical statistical features from processed interview answers.

Responsibilities:
    ✔ Count words
    ✔ Count answers
    ✔ Compute averages
    ✔ Compute lexical diversity

Does NOT:
    ✘ Evaluate candidate quality
    ✘ Apply interview rules
    ✘ Use AI models
==============================================================================
"""

from app.schemas.evaluation.text_document import TextDocument


class StatisticsFeatureExtractor:
    """
    Extract statistical features from interview documents.
    """

    SHORT_ANSWER_THRESHOLD = 10
    LONG_ANSWER_THRESHOLD = 80

    @classmethod
    def extract(
        cls,
        documents: list[TextDocument],
        answer_durations: list[int] | None = None,
    ) -> dict[str, float | int]:

        total_answers = len(documents)

        total_words = sum(
            len(document.tokens)
            for document in documents
        )

        unique_words = len(
            {
                lemma
                for document in documents
                for lemma in document.lemmas
            }
        )

        total_sentences = sum(
            len(document.sentences)
            for document in documents
        )

        average_words_per_answer = (
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

        average_sentence_length = (
            total_words / total_sentences
            if total_sentences
            else 0.0
        )

        vocabulary_richness = (
            unique_words / total_words
            if total_words
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

        average_answer_duration = (
            sum(answer_durations) / len(answer_durations)
            if answer_durations
            else 0.0
        )

        return {
            "total_answers": total_answers,
            "total_words": total_words,
            "unique_words": unique_words,
            "total_sentences": total_sentences,
            "average_words_per_answer": average_words_per_answer,
            "average_word_length": average_word_length,
            "average_sentence_length": average_sentence_length,
            "average_answer_duration": average_answer_duration,
            "vocabulary_richness": vocabulary_richness,
            "empty_answers": empty_answers,
            "short_answers": short_answers,
            "long_answers": long_answers,
        }