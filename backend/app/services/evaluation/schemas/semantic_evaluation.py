"""
==============================================================================
Module:
    Semantic Evaluation Schema

Milestone:
    M2.1 – Evaluation Engine Completion

Purpose:
    Immutable result produced by SemanticSimilarityFeatureExtractor.

Consumers:
    - DeterministicEvaluationEngine
    - AnswerEvaluationPromptBuilder
==============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field


class SemanticEvaluation(BaseModel):
    """Embedding-based semantic relevance score between question and answer."""

    model_config = ConfigDict(frozen=True)

    cosine_similarity: float = Field(
        ge=-1.0,
        le=1.0,
        description="Raw cosine similarity between question and answer embeddings.",
    )

    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Normalised relevance 0–1 (cosine similarity clipped to [0, 1]).",
    )

    summary: str = Field(
        description="Human-readable one-line semantic relevance summary.",
    )
