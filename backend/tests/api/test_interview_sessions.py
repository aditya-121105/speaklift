from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.engine import get_interview_workflow_service, get_execution_service
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState, CurrentQuestion
from app.schemas.interview_evaluation import InterviewEvaluationResponse
from app.shared.enums import InterviewStatus, QuestionType, QuestionCategory, EvaluationSource
from datetime import datetime, timezone

client = TestClient(app)

def override_get_current_user():
    user = MagicMock(spec=User)
    user.id = 1
    return user

app.dependency_overrides[get_current_user] = override_get_current_user

def build_sample_state():
    return InterviewExecutionState(
        session_id=42,
        status=InterviewStatus.IN_PROGRESS,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        is_completed=False,
        current_question=CurrentQuestion(
            question_id=1,
            question_text="Sample",
            question_type=QuestionType.PRIMARY,
            question_category=QuestionCategory.TECHNICAL,
            ordering=1,
            execution_path="01"
        )
    )

def build_sample_evaluation():
    return InterviewEvaluationResponse(
        id=1,
        interview_session_id=42,
        technical_score=80,
        communication_score=85,
        behavioral_score=90,
        confidence_score=75,
        overall_score=82,
        strengths=["Good"],
        weaknesses=[],
        recommendations=[],
        evaluation_source=EvaluationSource.RULE_BASED,
        created_at=datetime.now(timezone.utc)
    )

@patch("app.api.v1.endpoints.interview_sessions.InterviewSessionService")
def test_start_interview_session(mock_session_service):
    mock_workflow = MagicMock()
    mock_workflow.start_workflow.return_value = build_sample_state()
    
    app.dependency_overrides[get_interview_workflow_service] = lambda: mock_workflow
    
    response = client.post("/api/v1/interviews/42/start")
    assert response.status_code == 200
    assert response.json()["session_id"] == 42
    
    app.dependency_overrides.pop(get_interview_workflow_service, None)

@patch("app.api.v1.endpoints.interview_sessions.InterviewSessionService")
def test_submit_interview_answer(mock_session_service):
    mock_execution = MagicMock()
    mock_execution.get_state.return_value = build_sample_state()
    mock_execution.submit_answer.return_value = build_sample_state()
    
    app.dependency_overrides[get_execution_service] = lambda: mock_execution
    
    response = client.post(
        "/api/v1/interviews/42/answers", 
        json={"transcript": "test answer", "answer_source": "TEXT"}
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == 42
    
    app.dependency_overrides.pop(get_execution_service, None)

@patch("app.api.v1.endpoints.interview_sessions.InterviewSessionService")
def test_get_interview_state(mock_session_service):
    mock_execution = MagicMock()
    mock_execution.get_state.return_value = build_sample_state()
    
    app.dependency_overrides[get_execution_service] = lambda: mock_execution
    
    response = client.get("/api/v1/interviews/42/state")
    assert response.status_code == 200
    assert response.json()["session_id"] == 42
    
    app.dependency_overrides.pop(get_execution_service, None)

@patch("app.api.v1.endpoints.interview_sessions.InterviewSessionService")
@patch("app.api.v1.endpoints.interview_sessions.InterviewEvaluationRepository")
def test_get_interview_evaluation(mock_repo, mock_session_service):
    mock_repo.get_by_session.return_value = build_sample_evaluation()
    
    response = client.get("/api/v1/interviews/42/evaluation")
    assert response.status_code == 200
    assert response.json()["interview_session_id"] == 42

@patch("app.api.v1.endpoints.interview_sessions.InterviewSessionService")
@patch("app.api.v1.endpoints.interview_sessions.InterviewEvaluationRepository")
def test_get_interview_evaluation_not_found(mock_repo, mock_session_service):
    mock_repo.get_by_session.return_value = None
    
    response = client.get("/api/v1/interviews/42/evaluation")
    assert response.status_code == 404

def test_unauthorized_access():
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get("/api/v1/interviews/42/state")
    assert response.status_code == 401
    
    # Restore override for other tests if any
    app.dependency_overrides[get_current_user] = override_get_current_user
