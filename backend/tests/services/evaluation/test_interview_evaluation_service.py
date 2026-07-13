import pytest
from unittest.mock import Mock, patch
from app.services.evaluation.evaluation_service import InterviewEvaluationService
from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import SelectedQuestion
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.schemas.ai_evaluation import AIEvaluationResult, CommunicationFeedback, QualitativeRating
from app.shared.enums import AnswerSource, QuestionCategory, DifficultyLevel
from app.ai.llm.prompts.answer_evaluation_prompt import AnswerEvaluationPromptBuilder
from app.ai.llm.prompts.base import Prompt, PromptVersion

@pytest.fixture
def mock_deterministic_engine():
    engine = Mock()
    engine.evaluate.return_value = AnswerEvaluation(
        keyword_coverage=0.8,
        concept_coverage=0.7,
        completeness=0.9,
        vocabulary_statistics={"word_count": 100},
        overall_score=0.8
    )
    return engine

@pytest.fixture
def mock_llm_service():
    service = Mock()
    service.generate_json.return_value = AIEvaluationResult(
        strengths=[],
        weaknesses=[],
        communication=CommunicationFeedback(
            clarity_rating=QualitativeRating.GOOD,
            confidence_rating=QualitativeRating.EXCELLENT,
            tone="Professional",
            feedback="Good"
        ),
        suggestions=[]
    )
    return service

@pytest.fixture
def sample_request():
    return EvaluationRequest(
        submitted_answer=SubmittedAnswer(transcript="This is my answer.", answer_source=AnswerSource.TEXT),
        selected_question=SelectedQuestion(question_id="1", question_text="What is this?", category=QuestionCategory.TECHNICAL, difficulty=DifficultyLevel.EASY, expected_duration_seconds=60, tags=[], ordering=1, objective_name="Test")
    )

def test_evaluate_answer_success(mock_deterministic_engine, mock_llm_service, sample_request):
    service = InterviewEvaluationService(mock_deterministic_engine, mock_llm_service)
    
    with patch.object(AnswerEvaluationPromptBuilder, 'build', wraps=AnswerEvaluationPromptBuilder.build) as mock_build:
        result = service.evaluate_answer(sample_request, interview_context="Senior Role")
        
        # Verify deterministic engine invocation
        mock_deterministic_engine.evaluate.assert_called_once_with(sample_request)
        
        # Verify prompt builder invocation
        mock_build.assert_called_once()
        kwargs = mock_build.call_args.kwargs
        assert kwargs["question_text"] == "What is this?"
        assert kwargs["answer_text"] == "This is my answer."
        assert kwargs["interview_context"] == "Senior Role"
        
        # Verify llm_service.generate_json invocation
        mock_llm_service.generate_json.assert_called_once()
        called_prompt, called_schema = mock_llm_service.generate_json.call_args.args
        assert isinstance(called_prompt, Prompt)
        assert called_schema == AIEvaluationResult
        
        # Verify merge correctness
        assert result.deterministic_metrics.overall_score == 0.8
        assert result.ai_interpretation is not None
        assert result.ai_interpretation.communication.tone == "Professional"

def test_evaluate_answer_graceful_degradation(mock_deterministic_engine, mock_llm_service, sample_request):
    # Make LLM service raise an error
    mock_llm_service.generate_json.side_effect = Exception("LLM connection failed")
    
    service = InterviewEvaluationService(mock_deterministic_engine, mock_llm_service)
    
    # It should not raise an exception
    result = service.evaluate_answer(sample_request)
    
    # Verify deterministic engine invocation still happened
    mock_deterministic_engine.evaluate.assert_called_once_with(sample_request)
    
    # Verify graceful degradation
    assert result.deterministic_metrics.overall_score == 0.8
    assert result.ai_interpretation is None  # AI feedback is absent safely
