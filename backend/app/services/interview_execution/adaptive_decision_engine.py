"""
==============================================================================
Module:
    Adaptive Decision Engine

Milestone:
    M2.2 – Adaptive Interview System

Purpose:
    Pure, stateless evaluator that decides whether the interview should
    proceed to the next planned question, generate a follow-up, or end.

Architecture
------------
The engine receives the already-computed AnswerEvaluation (from
DeterministicEvaluationEngine) and the session context.  It does NOT
re-evaluate the answer – it only classifies the existing metrics.

Decision Priority
-----------------
1. END_INTERVIEW if max_total_questions reached (absolute cap).
2. NEXT_QUESTION if follow-up limit for this primary question is hit.
3. GENERATE_FOLLOW_UP if ≥ weak_metric_threshold metrics are weak.
4. NEXT_QUESTION (strong answer).

Responsibilities:
    ✔ Classify evaluation metrics against configurable thresholds
    ✔ Enforce follow-up and session-length limits
    ✔ Return an immutable AdaptiveDecisionResult
    ✔ Remain fully testable with no side effects

Does NOT:
    ✘ Generate follow-up question text
    ✘ Access the database
    ✘ Call any LLM or AI service
==============================================================================
"""

from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.interview_execution.adaptive_thresholds import AdaptiveThresholds
from app.services.interview_execution.schemas.adaptive_decision import (
    AdaptiveDecision,
    AdaptiveDecisionResult,
    DecisionReason,
)


class AdaptiveDecisionEngine:
    """
    Stateless classifier that maps evaluation metrics → routing decision.

    Parameters
    ----------
    thresholds : AdaptiveThresholds
        Gate values controlling when follow-ups are generated.
    """

    def __init__(self, thresholds: AdaptiveThresholds | None = None) -> None:
        self._thresholds = thresholds or AdaptiveThresholds()

    def decide(
        self,
        evaluation: AnswerEvaluation,
        *,
        total_questions_so_far: int,
        follow_up_count_for_primary: int,
    ) -> AdaptiveDecisionResult:
        """
        Evaluate metrics and return a routing decision.

        Parameters
        ----------
        evaluation                  : The deterministic evaluation of the submitted answer.
        total_questions_so_far      : Number of questions already asked in this session.
        follow_up_count_for_primary : Follow-ups already generated for this primary question.

        Returns
        -------
        AdaptiveDecisionResult
        """
        t = self._thresholds

        # --- Absolute session cap ---
        if total_questions_so_far >= t.max_total_questions:
            return AdaptiveDecisionResult(
                decision=AdaptiveDecision.END_INTERVIEW,
                reason=DecisionReason.MAX_QUESTIONS_REACHED,
                trigger_metrics=self._metrics_snapshot(evaluation),
                follow_up_count=follow_up_count_for_primary,
            )

        # --- Follow-up limit: already at cap, skip further follow-ups ---
        if follow_up_count_for_primary >= t.max_follow_ups_per_primary:
            return AdaptiveDecisionResult(
                decision=AdaptiveDecision.NEXT_QUESTION,
                reason=DecisionReason.FOLLOW_UP_LIMIT_REACHED,
                trigger_metrics=self._metrics_snapshot(evaluation),
                follow_up_count=follow_up_count_for_primary,
            )

        # --- Identify weak signals ---
        weak_reasons: list[DecisionReason] = []

        if evaluation.keyword_coverage < t.min_keyword_coverage:
            weak_reasons.append(DecisionReason.WEAK_KEYWORD_COVERAGE)

        if evaluation.concept_coverage < t.min_concept_coverage:
            weak_reasons.append(DecisionReason.WEAK_CONCEPT_COVERAGE)

        if (
            evaluation.semantic_similarity is not None
            and evaluation.semantic_similarity.relevance_score < t.min_semantic_similarity
        ):
            weak_reasons.append(DecisionReason.WEAK_SEMANTIC_SIMILARITY)

        if (
            evaluation.confidence is not None
            and evaluation.confidence.confidence_score < t.min_confidence_score
        ):
            weak_reasons.append(DecisionReason.LOW_CONFIDENCE)

        if evaluation.completeness < t.min_completeness:
            weak_reasons.append(DecisionReason.INCOMPLETE_ANSWER)

        # --- Routing ---
        if len(weak_reasons) >= t.weak_metric_threshold:
            # Use the first (highest priority) weak reason as the primary driver
            return AdaptiveDecisionResult(
                decision=AdaptiveDecision.GENERATE_FOLLOW_UP,
                reason=weak_reasons[0],
                trigger_metrics=self._metrics_snapshot(evaluation),
                follow_up_count=follow_up_count_for_primary,
            )

        return AdaptiveDecisionResult(
            decision=AdaptiveDecision.NEXT_QUESTION,
            reason=DecisionReason.STRONG_ANSWER,
            trigger_metrics=self._metrics_snapshot(evaluation),
            follow_up_count=follow_up_count_for_primary,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _metrics_snapshot(evaluation: AnswerEvaluation) -> dict[str, float]:
        """Extract a compact numeric snapshot of the core metrics for audit."""
        snapshot: dict[str, float] = {
            "keyword_coverage": evaluation.keyword_coverage,
            "concept_coverage": evaluation.concept_coverage,
            "completeness": evaluation.completeness,
            "overall_score": evaluation.overall_score,
        }
        if evaluation.confidence is not None:
            snapshot["confidence_score"] = evaluation.confidence.confidence_score
        if evaluation.semantic_similarity is not None:
            snapshot["semantic_similarity"] = (
                evaluation.semantic_similarity.relevance_score
            )
        if evaluation.grammar is not None:
            snapshot["grammar_quality_score"] = (
                evaluation.grammar.grammar_quality_score
            )
        return snapshot
