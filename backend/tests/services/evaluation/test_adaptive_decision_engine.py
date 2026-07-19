"""
Tests for AdaptiveDecisionEngine – M2.2 Adaptive Interview System

Validates all routing branches:
    - Strong answer → NEXT_QUESTION
    - Weak answer   → GENERATE_FOLLOW_UP
    - Follow-up limit reached → NEXT_QUESTION
    - Max questions reached   → END_INTERVIEW
"""

import pytest
from app.services.interview_execution.adaptive_decision_engine import AdaptiveDecisionEngine
from app.services.interview_execution.adaptive_thresholds import AdaptiveThresholds
from app.services.interview_execution.schemas.adaptive_decision import (
    AdaptiveDecision,
    DecisionReason,
)
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.schemas.confidence_evaluation import ConfidenceEvaluation
from app.services.evaluation.schemas.semantic_evaluation import SemanticEvaluation


# ------------------------------------------------------------------ helpers --

def _make_evaluation(
    keyword_coverage: float = 0.8,
    concept_coverage: float = 0.8,
    completeness: float = 0.8,
    overall_score: float = 0.8,
    confidence_score: float | None = None,
    semantic_similarity: float | None = None,
) -> AnswerEvaluation:
    confidence = None
    if confidence_score is not None:
        confidence = ConfidenceEvaluation(
            filler_word_count=0,
            hedging_phrase_count=0,
            filler_word_ratio=0.0,
            detected_fillers=[],
            confidence_score=confidence_score,
            summary="test",
        )
    semantic = None
    if semantic_similarity is not None:
        semantic = SemanticEvaluation(
            cosine_similarity=semantic_similarity,
            relevance_score=semantic_similarity,
            summary="test",
        )
    return AnswerEvaluation(
        keyword_coverage=keyword_coverage,
        concept_coverage=concept_coverage,
        completeness=completeness,
        overall_score=overall_score,
        vocabulary_statistics={},
        confidence=confidence,
        semantic_similarity=semantic,
    )


@pytest.fixture
def engine() -> AdaptiveDecisionEngine:
    return AdaptiveDecisionEngine(AdaptiveThresholds())


# ------------------------------------------------------------------ tests ---

class TestStrongAnswer:
    def test_strong_answer_routes_to_next_question(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.9,
            concept_coverage=0.9,
            completeness=0.9,
        )
        result = engine.decide(eval_, total_questions_so_far=3, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.NEXT_QUESTION
        assert result.reason == DecisionReason.STRONG_ANSWER

    def test_strong_answer_with_confidence_above_threshold(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.85,
            concept_coverage=0.85,
            completeness=0.85,
            confidence_score=0.9,
            semantic_similarity=0.8,
        )
        result = engine.decide(eval_, total_questions_so_far=2, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.NEXT_QUESTION


class TestWeakAnswer:
    def test_low_keyword_and_concept_triggers_follow_up(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.1,
            concept_coverage=0.1,
            completeness=0.8,
        )
        result = engine.decide(eval_, total_questions_so_far=2, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.GENERATE_FOLLOW_UP
        assert result.reason in {
            DecisionReason.WEAK_KEYWORD_COVERAGE,
            DecisionReason.WEAK_CONCEPT_COVERAGE,
        }

    def test_low_completeness_and_semantic_triggers_follow_up(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.8,
            concept_coverage=0.8,
            completeness=0.1,
            semantic_similarity=0.1,
        )
        result = engine.decide(eval_, total_questions_so_far=2, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.GENERATE_FOLLOW_UP

    def test_single_weak_metric_does_not_trigger_follow_up(self, engine):
        """Only one metric below threshold → not enough to trigger follow-up (threshold=2)."""
        eval_ = _make_evaluation(
            keyword_coverage=0.1,  # only this one is weak
            concept_coverage=0.9,
            completeness=0.9,
        )
        result = engine.decide(eval_, total_questions_so_far=2, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.NEXT_QUESTION

    def test_low_confidence_counts_as_weak_metric(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.1,    # weak
            concept_coverage=0.9,
            completeness=0.9,
            confidence_score=0.1,    # also weak
        )
        result = engine.decide(eval_, total_questions_so_far=2, follow_up_count_for_primary=0)
        assert result.decision == AdaptiveDecision.GENERATE_FOLLOW_UP


class TestFollowUpLimit:
    def test_follow_up_limit_reached_routes_to_next_question(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.1,
            concept_coverage=0.1,
        )
        result = engine.decide(
            eval_,
            total_questions_so_far=3,
            follow_up_count_for_primary=2,  # at the default cap of 2
        )
        assert result.decision == AdaptiveDecision.NEXT_QUESTION
        assert result.reason == DecisionReason.FOLLOW_UP_LIMIT_REACHED

    def test_custom_higher_follow_up_limit(self):
        engine = AdaptiveDecisionEngine(AdaptiveThresholds(max_follow_ups_per_primary=5))
        eval_ = _make_evaluation(keyword_coverage=0.1, concept_coverage=0.1)
        result = engine.decide(eval_, total_questions_so_far=3, follow_up_count_for_primary=3)
        # 3 < 5, so follow-up should still be generated
        assert result.decision == AdaptiveDecision.GENERATE_FOLLOW_UP


class TestSessionCap:
    def test_max_questions_reached_ends_interview(self, engine):
        eval_ = _make_evaluation(
            keyword_coverage=0.9,
            concept_coverage=0.9,
        )
        result = engine.decide(
            eval_,
            total_questions_so_far=20,  # at default cap of 20
            follow_up_count_for_primary=0,
        )
        assert result.decision == AdaptiveDecision.END_INTERVIEW
        assert result.reason == DecisionReason.MAX_QUESTIONS_REACHED

    def test_max_questions_cap_has_priority_over_follow_up(self, engine):
        """Even with a weak answer, if session cap is hit, end the interview."""
        eval_ = _make_evaluation(keyword_coverage=0.0, concept_coverage=0.0)
        result = engine.decide(
            eval_,
            total_questions_so_far=25,
            follow_up_count_for_primary=0,
        )
        assert result.decision == AdaptiveDecision.END_INTERVIEW


class TestTriggerMetrics:
    def test_trigger_metrics_populated(self, engine):
        eval_ = _make_evaluation(keyword_coverage=0.5, concept_coverage=0.5)
        result = engine.decide(eval_, total_questions_so_far=0, follow_up_count_for_primary=0)
        assert "keyword_coverage" in result.trigger_metrics
        assert "concept_coverage" in result.trigger_metrics
        assert "overall_score" in result.trigger_metrics

    def test_result_is_immutable(self, engine):
        eval_ = _make_evaluation()
        result = engine.decide(eval_, total_questions_so_far=0, follow_up_count_for_primary=0)
        with pytest.raises(Exception):
            result.decision = AdaptiveDecision.END_INTERVIEW  # type: ignore[misc]
