"""
==============================================================================
Module:
    Grammar Evaluation Schema

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Immutable result produced by GrammarFeatureExtractor.

Consumers:
    - DeterministicEvaluationEngine
    - AnswerEvaluationPromptBuilder
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field


class GrammarEvaluation(BaseModel):
    """Deterministic grammar quality metrics for a candidate's answer."""

    model_config = ConfigDict(frozen=True)

    grammar_error_count: int = Field(
        ge=0,
        description="Number of grammatical errors detected by dependency analysis.",
    )

    grammar_quality_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalised score 0–1 (1 = no errors).",
    )

    error_rate_per_sentence: float = Field(
        ge=0.0,
        description="Average grammar errors per sentence.",
    )

    summary: str = Field(
        description="Human-readable one-line grammar summary.",
    )
