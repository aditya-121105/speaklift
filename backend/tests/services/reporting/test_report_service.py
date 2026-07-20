import pytest
from unittest.mock import MagicMock, patch
from app.services.reporting.report_service import InterviewReportService
from app.models.interview_session import InterviewSession
from app.models.interview_question import InterviewQuestion
from app.models.interview_answer import InterviewAnswer
from app.models.answer_evaluation import AnswerEvaluation
from app.models.interview_evaluation import InterviewEvaluation
from app.shared.enums import InterviewStatus, QuestionType, QuestionCategory
from app.services.reporting.ai_schemas import (
    AIReportGenerationResult, 
    AIExecutiveSummary, 
    AIHiringRecommendation, 
    AILearningRoadmap,
    AICompetencyAssessment
)
from app.services.reporting.schemas import HiringDecision

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_llm_service():
    mock = MagicMock()
    
    mock_result = AIReportGenerationResult(
        executive_summary=AIExecutiveSummary(
            overall_performance="Good",
            confidence_level="Medium",
            narrative="Candidate did well."
        ),
        competencies=[
            AICompetencyAssessment(
                competency_name="Technical",
                score=85,
                evidence="Solved algorithm well.",
                strengths=["Python"],
                weaknesses=[],
                missing_concepts=[],
                demonstrated_concepts=["Loops"]
            )
        ],
        hiring_recommendation=AIHiringRecommendation(
            decision=HiringDecision.HIRE,
            confidence="High",
            reasoning="Strong tech skills.",
            supporting_evidence=[]
        ),
        learning_roadmap=AILearningRoadmap(
            prioritized_skill_gaps=[],
            learning_sequence=[]
        )
    )
    
    mock.generate_json.return_value = mock_result
    return mock

def test_generate_report_success(mock_db, mock_llm_service):
    session_id = 1
    
    # Mock data
    mock_session = InterviewSession(id=session_id, status=InterviewStatus.COMPLETED)
    mock_question = InterviewQuestion(
        id=1, interview_session_id=session_id, question_type=QuestionType.PRIMARY, 
        planned_order=1, execution_path="01", question_text="What is Python?", 
        question_category=QuestionCategory.TECHNICAL
    )
    mock_answer = InterviewAnswer(id=1, interview_question_id=1, transcript="Python is a PL.", answer_duration_seconds=30)
    mock_eval = AnswerEvaluation(
        id=1, interview_answer_id=1, overall_score=0.85, 
        keyword_coverage=0.8, concept_coverage=0.9, completeness=0.8,
        grammar_score=0.9, readability_score=0.8, confidence_score=0.9, semantic_similarity=0.8,
        vocabulary_statistics={"unique_words": 10}, strengths=["Good"], weaknesses=[]
    )
    mock_session_eval = InterviewEvaluation(interview_session_id=session_id, overall_score=85)
    
    # Setup mock_db query chaining
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == InterviewSession:
            query_mock.filter.return_value.first.return_value = mock_session
        elif model == InterviewQuestion:
            query_mock.filter.return_value.order_by.return_value.all.return_value = [mock_question]
        elif model == InterviewAnswer:
            query_mock.filter.return_value.all.return_value = [mock_answer]
        elif model == AnswerEvaluation:
            query_mock.filter.return_value.all.return_value = [mock_eval]
        elif model == InterviewEvaluation:
            query_mock.filter.return_value.first.return_value = mock_session_eval
        return query_mock

    mock_db.query.side_effect = query_side_effect
    
    service = InterviewReportService(llm_service=mock_llm_service)
    
    report = service.generate_report(mock_db, session_id)
    
    assert report.session_id == session_id
    assert report.executive_summary.completion_status == "COMPLETED"
    assert report.executive_summary.overall_score == 85
    assert len(report.question_reviews) == 1
    assert report.question_reviews[0].execution_path == "01"
    assert report.statistics.total_questions_asked == 1
    assert report.statistics.interview_duration_seconds == 30
    assert report.communication.grammar_score == 90 # 0.9 * 100
    assert report.hiring_recommendation.decision == HiringDecision.HIRE

def test_generate_report_session_not_found(mock_db, mock_llm_service):
    # Setup mock to return None for session
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = None
    mock_db.query.return_value = query_mock
    
    service = InterviewReportService(llm_service=mock_llm_service)
    
    with pytest.raises(ValueError, match="Session 99 not found."):
        service.generate_report(mock_db, 99)
