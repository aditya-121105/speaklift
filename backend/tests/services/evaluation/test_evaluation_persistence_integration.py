import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.evaluation.evaluation_service import InterviewEvaluationService
from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
from app.services.evaluation.schemas.ai_evaluation import AIEvaluationResult, CommunicationFeedback, QualitativeRating
from app.shared.enums import AnswerSource, QuestionCategory, EvaluationSource, QuestionType
from app.models.interview_evaluation import InterviewEvaluation
from app.models.interview_question import InterviewQuestion
from app.models.interview_answer import InterviewAnswer

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
def db_session():
    return Mock(spec=Session)

@pytest.fixture
def sample_questions():
    return [
        InterviewQuestion(id=1, interview_session_id=42, question_text="Q1", question_category=QuestionCategory.TECHNICAL, planned_order=1, execution_path="01", question_type=QuestionType.PRIMARY),
        InterviewQuestion(id=2, interview_session_id=42, question_text="Q2", question_category=QuestionCategory.TECHNICAL, planned_order=2, execution_path="02", question_type=QuestionType.PRIMARY)
    ]

@pytest.fixture
def sample_answers():
    return [
        InterviewAnswer(id=1, interview_session_id=42, interview_question_id=1, transcript="Answer 1", answer_source=AnswerSource.TEXT),
        InterviewAnswer(id=2, interview_session_id=42, interview_question_id=2, transcript="Answer 2", answer_source=AnswerSource.TEXT)
    ]

@patch("app.services.evaluation.evaluation_service.InterviewEvaluationRepository")
def test_evaluate_session_persistence(mock_repo, mock_deterministic_engine, mock_llm_service, db_session, sample_questions, sample_answers):
    mock_repo.create.side_effect = lambda db, eval_model: eval_model
    
    service = InterviewEvaluationService(mock_deterministic_engine, mock_llm_service)
    
    result = service.evaluate_session(db_session, session_id=42, questions=sample_questions, answers=sample_answers)
    
    # Verify evaluate was invoked per answer
    assert mock_deterministic_engine.evaluate.call_count == 2
    assert mock_llm_service.generate_json.call_count == 2
    
    # Verify repository persistence
    mock_repo.create.assert_called_once()
    saved_model = mock_repo.create.call_args.args[1]
    
    assert isinstance(saved_model, InterviewEvaluation)
    assert saved_model.interview_session_id == 42
    assert saved_model.evaluation_source == EvaluationSource.HYBRID
    
    # 80% deterministic metric mapped properly
    assert saved_model.technical_score == 80
    assert saved_model.overall_score == 80
    
    # AI ratings mapped properly (GOOD = 75, EXCELLENT = 100)
    assert saved_model.communication_score == 75
    assert saved_model.confidence_score == 100

@patch("app.services.evaluation.evaluation_service.InterviewEvaluationRepository")
def test_evaluate_session_persistence_fallback(mock_repo, mock_deterministic_engine, mock_llm_service, db_session, sample_questions, sample_answers):
    # Simulate LLM Failure
    mock_llm_service.generate_json.side_effect = Exception("LLM Down")
    mock_repo.create.side_effect = lambda db, eval_model: eval_model
    
    service = InterviewEvaluationService(mock_deterministic_engine, mock_llm_service)
    
    result = service.evaluate_session(db_session, session_id=42, questions=sample_questions, answers=sample_answers)
    
    # Verify repository persistence
    mock_repo.create.assert_called_once()
    saved_model = mock_repo.create.call_args.args[1]
    
    # Since AI failed, source should be RULE_BASED
    assert saved_model.evaluation_source == EvaluationSource.RULE_BASED
    
    # Deterministic facts should still be saved
    assert saved_model.technical_score == 80
    assert saved_model.overall_score == 80
    
    # Default fallback scores for communication and confidence when AI fails is 50
    assert saved_model.communication_score == 50
    assert saved_model.confidence_score == 50
