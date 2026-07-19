"""
==============================================================================
Module:
    Readability Feature Extractor

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Computes standard readability metrics from a candidate's answer text.

Metrics
-------
Flesch Reading Ease
    FRE = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)

    Score interpretation:
        90–100   Very Easy
        70– 90   Easy
        60– 70   Standard
        50– 60   Fairly Difficult
        30– 50   Difficult
         0– 30   Very Confusing

Flesch-Kincaid Grade Level
    FKGL = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59

    Approximates US school grade needed to understand the text.

Both formulas require:
    - word count
    - sentence count
    - syllable count (approximated by vowel-group counting)

Responsibilities:
    ✔ Count syllables using a vowel-group heuristic
    ✔ Compute FRE and FKGL
    ✔ Produce a human-readable summary

Does NOT:
    ✘ Use AI models
    ✘ Access the database
    ✘ Evaluate interview quality
==============================================================================
"""

import re

from app.core.nlp import NLPResourceManager
from app.services.evaluation.schemas.readability_evaluation import ReadabilityEvaluation

_VOWEL_RE = re.compile(r"[aeiou]+", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    """Approximate syllable count for a word using vowel-group counting."""
    syllables = len(_VOWEL_RE.findall(word))
    # Silent 'e' at end
    if word.lower().endswith("e") and syllables > 1:
        syllables -= 1
    return max(1, syllables)


class ReadabilityFeatureExtractor:
    """
    Compute Flesch Reading Ease and Flesch-Kincaid Grade Level
    from raw interview text.
    """

    def extract(self, text: str) -> ReadabilityEvaluation:
        if not text.strip():
            return ReadabilityEvaluation(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                average_sentence_length=0.0,
                average_syllables_per_word=0.0,
                summary="Empty answer – no readability analysis performed.",
            )

        nlp = NLPResourceManager.get_spacy_model()
        doc = nlp(text)

        # Collect alphabetic tokens and sentence boundaries
        alpha_tokens = [t for t in doc if t.is_alpha]
        sentences = list(doc.sents)

        word_count = len(alpha_tokens)
        sentence_count = max(len(sentences), 1)
        syllable_count = sum(_count_syllables(t.text) for t in alpha_tokens)

        if word_count == 0:
            return ReadabilityEvaluation(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                average_sentence_length=0.0,
                average_syllables_per_word=0.0,
                summary="Answer contains no words – readability cannot be computed.",
            )

        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count

        fre = (
            206.835
            - 1.015 * avg_sentence_length
            - 84.6 * avg_syllables_per_word
        )
        fkgl = (
            0.39 * avg_sentence_length
            + 11.8 * avg_syllables_per_word
            - 15.59
        )

        # Summarise FRE
        if fre >= 90:
            level = "Very Easy"
        elif fre >= 70:
            level = "Easy"
        elif fre >= 60:
            level = "Standard"
        elif fre >= 50:
            level = "Fairly Difficult"
        elif fre >= 30:
            level = "Difficult"
        else:
            level = "Very Complex"

        summary = (
            f"Readability: {level} "
            f"(FRE {fre:.1f}, Grade Level {fkgl:.1f}, "
            f"Avg sentence length {avg_sentence_length:.1f} words)."
        )

        return ReadabilityEvaluation(
            flesch_reading_ease=round(fre, 4),
            flesch_kincaid_grade=round(fkgl, 4),
            average_sentence_length=round(avg_sentence_length, 4),
            average_syllables_per_word=round(avg_syllables_per_word, 4),
            summary=summary,
        )
