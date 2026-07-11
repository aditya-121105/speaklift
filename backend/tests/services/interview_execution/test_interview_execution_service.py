import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState, CurrentQuestion
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import QuestionSelection, SelectedQuestion
from app.shared.enums import InterviewStatus, QuestionCategory, QuestionType, AnswerSource, DifficultyLevel
from app.shared.exceptions import InterviewSessionNotFoundError, InvalidSessionStateError, InterviewQuestionNotFoundError
from app.models.interview_session import InterviewSession
from app.models.interview_question import InterviewQuestion

def test_start_interview_success():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.CREATED
    session_mock.started_at = None
    session_mock.completed_at = None
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q_mock = MagicMock(spec=InterviewQuestion)
    q_mock.id = 10
    q_mock.question_text = "What is Python?"
    q_mock.question_type = QuestionType.PRIMARY
    q_mock.question_category = QuestionCategory.TECHNICAL
    q_mock.question_order = 1
    question_repo.get_first_unasked_question.return_value = q_mock
    
    selection = QuestionSelection(
        total_questions=1,
        selected_questions=[
            SelectedQuestion(
                question_id=100,
                question_text="What is Python?",
                category=QuestionCategory.TECHNICAL,
                difficulty=DifficultyLevel.MEDIUM,
                ordering=1,
                objective_name="Python Core"
            )
        ]
    )
    
    session_mock_in_progress = MagicMock(spec=InterviewSession)
    session_mock_in_progress.id = 1
    session_mock_in_progress.status = InterviewStatus.IN_PROGRESS
    session_mock_in_progress.started_at = datetime.utcnow()
    session_mock_in_progress.completed_at = None
    session_repo.mark_in_progress.return_value = session_mock_in_progress
    
    service = InterviewExecutionService(session_repo, question_repo, answer_repo)
    state = service.start_interview(db, 1, 1, selection)
    
    assert isinstance(state, InterviewExecutionState)
    assert state.session_id == 1
    assert state.status == InterviewStatus.IN_PROGRESS
    assert state.is_completed is False
    assert state.current_question is not None
    assert state.current_question.question_id == 10
    
    question_repo.create_many.assert_called_once()
    session_repo.mark_in_progress.assert_called_once_with(db, 1)

def test_start_interview_invalid_state():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    service = InterviewExecutionService(session_repo, MagicMock(), MagicMock())
    with pytest.raises(InvalidSessionStateError):
        service.start_interview(db, 1, 1, MagicMock(spec=QuestionSelection))

def test_submit_answer_success():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q_mock = MagicMock(spec=InterviewQuestion)
    q_mock.id = 10
    q_mock.interview_session_id = 1
    question_repo.get_by_id.return_value = q_mock
    
    next_q_mock = MagicMock(spec=InterviewQuestion)
    next_q_mock.id = 11
    next_q_mock.question_text = "Next question"
    next_q_mock.question_type = QuestionType.PRIMARY
    next_q_mock.question_category = QuestionCategory.TECHNICAL
    next_q_mock.question_order = 2
    question_repo.get_first_unasked_question.return_value = next_q_mock
    
    q_mock.is_asked = True
    question_repo.mark_as_asked.return_value = q_mock
    
    service = InterviewExecutionService(session_repo, question_repo, answer_repo)
    
    submitted_answer = SubmittedAnswer(
        transcript="My answer",
        answer_source=AnswerSource.TEXT,
        answer_duration_seconds=30
    )
    
    state = service.submit_answer(db, 1, 1, 10, submitted_answer)
    
    assert isinstance(state, InterviewExecutionState)
    assert state.is_completed is False
    assert state.current_question is not None
    assert state.current_question.question_id == 11
    
    answer_repo.persist_answer.assert_called_once_with(db, 1, 10, submitted_answer)
    question_repo.mark_as_asked.assert_called_once_with(db, 10)

def test_submit_answer_completes_interview():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q_mock = MagicMock(spec=InterviewQuestion)
    q_mock.id = 10
    q_mock.interview_session_id = 1
    question_repo.get_by_id.return_value = q_mock
    
    q_mock.is_asked = True
    question_repo.mark_as_asked.return_value = q_mock
    
    # No more questions
    question_repo.get_first_unasked_question.return_value = None
    
    session_mock_completed = MagicMock(spec=InterviewSession)
    session_mock_completed.id = 1
    session_mock_completed.status = InterviewStatus.COMPLETED
    session_repo.mark_completed.return_value = session_mock_completed
    
    service = InterviewExecutionService(session_repo, question_repo, answer_repo)
    
    submitted_answer = SubmittedAnswer(
        transcript="My answer",
        answer_source=AnswerSource.TEXT,
        answer_duration_seconds=30
    )
    
    state = service.submit_answer(db, 1, 1, 10, submitted_answer)
    
    assert isinstance(state, InterviewExecutionState)
    assert state.is_completed is True
    assert state.current_question is None
    session_repo.mark_completed.assert_called_once_with(db, 1)
