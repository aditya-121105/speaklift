"""
==============================================================================
Module:
    Adaptive Decision Thresholds

Milestone:
    M2.2 – Adaptive Interview System

Purpose:
    Configurable thresholds that control when a follow-up question is
    generated versus when the interview progresses to the next planned
    primary question.

Design
------
All thresholds are declared here as a single immutable value object.
Callers construct AdaptiveThresholds with explicit values or accept the
production defaults.  The engine consumes them without any global state.

Default values are conservative: a follow-up is only generated when
multiple metrics simultaneously indicate a weak answer.
==============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveThresholds:
    """
    Configurable gate values for the AdaptiveDecisionEngine.

    Attributes
    ----------
    min_keyword_coverage      : Minimum fraction of question keywords present
                                in the answer. Below this → candidate for follow-up.
    min_concept_coverage      : Minimum named-entity coverage fraction.
    min_semantic_similarity   : Minimum cosine relevance (0–1).
    min_confidence_score      : Minimum deterministic confidence score (0–1).
    min_completeness          : Minimum token-length completeness (0–1).
    max_follow_ups_per_primary: Hard cap on follow-up questions per primary.
    max_total_questions       : Hard cap on total questions in a session.
    weak_metric_threshold     : Number of metrics simultaneously below
                                threshold required to trigger a follow-up.
    """

    min_keyword_coverage: float = 0.40
    min_concept_coverage: float = 0.40
    min_semantic_similarity: float = 0.50
    min_confidence_score: float = 0.50
    min_completeness: float = 0.30
    max_follow_ups_per_primary: int = 2
    max_total_questions: int = 20
    weak_metric_threshold: int = 2  # ≥ N weak metrics → generate follow-up

    def __post_init__(self) -> None:
        for name in (
            "min_keyword_coverage",
            "min_concept_coverage",
            "min_semantic_similarity",
            "min_confidence_score",
            "min_completeness",
        ):
            val = getattr(self, name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {val}")
        if self.max_follow_ups_per_primary < 0:
            raise ValueError("max_follow_ups_per_primary must be >= 0")
        if self.max_total_questions < 1:
            raise ValueError("max_total_questions must be >= 1")
        if self.weak_metric_threshold < 1:
            raise ValueError("weak_metric_threshold must be >= 1")
