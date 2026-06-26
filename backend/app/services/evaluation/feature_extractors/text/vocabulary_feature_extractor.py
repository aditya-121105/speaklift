"""
==============================================================================
Module:
    Vocabulary Feature Extractor

Sprint:
    Sprint 4 - Evaluation Engine

Purpose:
    Extract lexical and vocabulary-related features from processed interview
    answers.

Responsibilities:
    ✔ Measure vocabulary richness
    ✔ Measure lexical density
    ✔ Count content words
    ✔ Count stop words

Does NOT:
    ✘ Evaluate interview quality
    ✘ Apply scoring rules
    ✘ Use AI models

==============================================================================
Interview Notes

Q. What is lexical density?

Answer:
Lexical density is the percentage of meaningful (content) words
compared to the total number of words.

Higher lexical density generally indicates richer communication.

Formula:

Lexical Density =
Content Words / Total Words

------------------------------------------------------------------------------
"""

from app.schemas.evaluation.text_document import TextDocument


class VocabularyFeatureExtractor:
    """
    Extract vocabulary-related features from interview answers.
    """

    @classmethod
    def extract(
        cls,
        documents: list[TextDocument],
    ) -> dict[str, float | int]:
        """
        Extract vocabulary features.

        Parameters
        ----------
        documents:
            List of processed interview answers.

        Returns
        -------
        Dictionary containing vocabulary features.
        """

        total_lemmas = sum(
            len(document.lemmas)
            for document in documents
        )

        unique_lemmas = len(
            {
                lemma
                for document in documents
                for lemma in document.lemmas
            }
        )

        total_stop_words = sum(
            len(document.stop_words)
            for document in documents
        )

        total_content_words = sum(
            len(document.content_words)
            for document in documents
        )

        average_lemma_length = (
            sum(
                len(lemma)
                for document in documents
                for lemma in document.lemmas
            )
            / total_lemmas
            if total_lemmas
            else 0.0
        )

        vocabulary_richness = (
            unique_lemmas / total_lemmas
            if total_lemmas
            else 0.0
        )

        lexical_density = (
            total_content_words / total_lemmas
            if total_lemmas
            else 0.0
        )

        stop_word_ratio = (
            total_stop_words / total_lemmas
            if total_lemmas
            else 0.0
        )

        return {
            "unique_lemmas": unique_lemmas,
            "vocabulary_richness": vocabulary_richness,
            "average_lemma_length": average_lemma_length,
            "content_word_count": total_content_words,
            "stop_word_count": total_stop_words,
            "lexical_density": lexical_density,
            "stop_word_ratio": stop_word_ratio,
        }