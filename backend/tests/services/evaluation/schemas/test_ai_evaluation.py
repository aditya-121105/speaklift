import pytest
from pydantic import ValidationError
from app.services.evaluation.schemas.ai_evaluation import (
    ImprovementSuggestion,
    CommunicationFeedback,
    AIEvaluationResult,
    EnhancedAnswerEvaluation,
    QualitativeRating,
    EvaluationObservation,
)
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation

def test_improvement_suggestion_serialization():
    s = ImprovementSuggestion(category="Tone", description="Be more positive.")
    d = s.model_dump()
    assert d["category"] == "Tone"
    assert d["description"] == "Be more positive."
    assert d["example"] is None

def test_improvement_suggestion_optional_field():
    s = ImprovementSuggestion(category="Tone", description="Be more positive.", example="Instead of saying NO, say maybe.")
    assert s.example == "Instead of saying NO, say maybe."

def test_communication_feedback_validation():
    with pytest.raises(ValidationError):
        CommunicationFeedback(clarity_rating="NOT_AN_ENUM", confidence_rating="GOOD", tone="Good", feedback="Great")
    
    cf = CommunicationFeedback(clarity_rating=QualitativeRating.GOOD, confidence_rating=QualitativeRating.EXCELLENT, tone="Professional", feedback="Well articulated.")
    assert cf.clarity_rating == QualitativeRating.GOOD

def test_evaluation_observation_serialization():
    obs = EvaluationObservation(category="Technical", observation="Good mention of asyncio", evidence="I used async/await")
    d = obs.model_dump()
    assert d["category"] == "Technical"
    assert d["evidence"] == "I used async/await"

def test_ai_evaluation_result_composition():
    cf = CommunicationFeedback(clarity_rating=QualitativeRating.GOOD, confidence_rating=QualitativeRating.EXCELLENT, tone="Professional", feedback="Well articulated.")
    s = ImprovementSuggestion(category="Tone", description="Be more positive.")
    obs1 = EvaluationObservation(category="Technical", observation="Good mention of asyncio")
    obs2 = EvaluationObservation(category="Clarity", observation="Too fast")
    
    res = AIEvaluationResult(
        strengths=[obs1],
        weaknesses=[obs2],
        communication=cf,
        suggestions=[s]
    )
    assert len(res.strengths) == 1
    assert res.communication.clarity_rating == QualitativeRating.GOOD
    assert len(res.suggestions) == 1

def test_enhanced_answer_evaluation_composition():
    ans = AnswerEvaluation(
        keyword_coverage=0.8,
        concept_coverage=0.7,
        completeness=0.9,
        vocabulary_statistics={"word_count": 100},
        overall_score=0.8
    )
    cf = CommunicationFeedback(clarity_rating=QualitativeRating.GOOD, confidence_rating=QualitativeRating.EXCELLENT, tone="Professional", feedback="Well articulated.")
    ai_res = AIEvaluationResult(
        strengths=[],
        weaknesses=[],
        communication=cf,
        suggestions=[]
    )
    
    enhanced = EnhancedAnswerEvaluation(
        deterministic_metrics=ans,
        ai_interpretation=ai_res
    )
    
    assert enhanced.deterministic_metrics.overall_score == 0.8
    assert enhanced.ai_interpretation.communication.confidence_rating == QualitativeRating.EXCELLENT

def test_immutability():
    s = ImprovementSuggestion(category="Tone", description="Be more positive.")
    with pytest.raises(ValidationError):
        s.category = "New"

def test_equality():
    s1 = ImprovementSuggestion(category="Tone", description="Be more positive.")
    s2 = ImprovementSuggestion(category="Tone", description="Be more positive.")
    assert s1 == s2
