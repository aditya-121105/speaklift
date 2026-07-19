"""
==============================================================================
Module:
    Confidence Evaluation Schema

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Immutable result produced by ConfidenceFeatureExtractor.

Consumers:
    - DeterministicEvaluationEngine
    - AnswerEvaluationPromptBuilder
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field


class ConfidenceEvaluation(BaseModel):
    """Deterministic confidence indicators extracted from a candidate's answer."""

    model_config = ConfigDict(frozen=True)

    filler_word_count: int = Field(
        ge=0,
        description="Total filler words detected (e.g., um, uh, like, you know).",
    )

    hedging_phrase_count: int = Field(
        ge=0,
        description=(
            "Total hedging phrases detected "
            "(e.g., 'I think', 'maybe', 'kind of', 'sort of')."
        ),
    )

    filler_word_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Filler words as a fraction of total words.",
    )

    detected_fillers: list[str] = Field(
        default_factory=list,
        description="Distinct filler tokens or phrases that were found.",
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Deterministic confidence score 0–1 (1 = maximally confident).",
    )

    summary: str = Field(
        description="Human-readable one-line confidence summary.",
    )
