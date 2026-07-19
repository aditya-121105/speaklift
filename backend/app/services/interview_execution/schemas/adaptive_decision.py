"""
==============================================================================
Module:
    Adaptive Decision Engine Schemas

Milestone:
    M2.2 – Adaptive Interview System

Purpose:
    Immutable value objects produced by AdaptiveDecisionEngine.

Consumers:
    - InterviewExecutionService (decision routing)
    - FollowUpGenerationService (follow-up input)
    - Persistence layer (audit trail)
==============================================================================
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class AdaptiveDecision(str, Enum):
    """The three possible outcomes of an adaptive evaluation decision."""
    NEXT_QUESTION = "NEXT_QUESTION"      # Proceed to next planned question
    GENERATE_FOLLOW_UP = "GENERATE_FOLLOW_UP"  # Insert contextual follow-up
    END_INTERVIEW = "END_INTERVIEW"      # Completion condition met


class DecisionReason(str, Enum):
    """Why the AdaptiveDecisionEngine reached its decision."""
    STRONG_ANSWER = "STRONG_ANSWER"                 # All metrics above threshold
    WEAK_KEYWORD_COVERAGE = "WEAK_KEYWORD_COVERAGE"
    WEAK_CONCEPT_COVERAGE = "WEAK_CONCEPT_COVERAGE"
    WEAK_SEMANTIC_SIMILARITY = "WEAK_SEMANTIC_SIMILARITY"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    INCOMPLETE_ANSWER = "INCOMPLETE_ANSWER"
    FOLLOW_UP_LIMIT_REACHED = "FOLLOW_UP_LIMIT_REACHED"  # Cap hit → next primary
    MAX_QUESTIONS_REACHED = "MAX_QUESTIONS_REACHED"
    NO_MORE_QUESTIONS = "NO_MORE_QUESTIONS"


class AdaptiveDecisionResult(BaseModel):
    """
    Immutable result of one adaptive decision cycle.

    Fields
    ------
    decision       : Routing directive for the execution service.
    reason         : Primary driver of the decision.
    trigger_metrics: Metric snapshot that triggered the decision (for audit).
    follow_up_count: Number of follow-ups already asked for this primary question.
    """

    model_config = ConfigDict(frozen=True)

    decision: AdaptiveDecision
    reason: DecisionReason
    trigger_metrics: dict[str, float] = Field(default_factory=dict)
    follow_up_count: int = Field(ge=0, default=0)
