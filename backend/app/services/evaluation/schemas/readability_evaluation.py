"""
==============================================================================
Module:
    Readability Evaluation Schema

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Immutable result produced by ReadabilityFeatureExtractor.

Consumers:
    - DeterministicEvaluationEngine
    - AnswerEvaluationPromptBuilder
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field


class ReadabilityEvaluation(BaseModel):
    """Standard readability metrics for a candidate's answer."""

    model_config = ConfigDict(frozen=True)

    flesch_reading_ease: float = Field(
        description=(
            "Flesch Reading Ease score. "
            "Higher is easier to read. "
            "90–100: Very Easy, 60–70: Standard, 0–30: Very Difficult."
        )
    )

    flesch_kincaid_grade: float = Field(
        description=(
            "Flesch-Kincaid Grade Level. "
            "Approximates the US school grade required to understand the text. "
            "May be negative for very short or simple texts."
        ),
    )

    average_sentence_length: float = Field(
        ge=0.0,
        description="Average number of words per sentence.",
    )

    average_syllables_per_word: float = Field(
        ge=0.0,
        description="Average syllable count per word.",
    )

    summary: str = Field(
        description="Human-readable one-line readability summary.",
    )
