import pytest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import QuestionSelection, SelectedQuestion
from app.shared.enums import InterviewStatus, QuestionCategory, QuestionType, AnswerSource, DifficultyLevel
from app.shared.exceptions import InvalidSessionStateError
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
    q_mock.planned_order = 1
    q_mock.execution_path = "01"
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
    next_q_mock.planned_order = 2
    next_q_mock.execution_path = "02"
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

def test_submit_answer_adaptive_follow_up_generated():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    det_engine = MagicMock()
    follow_up_service = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q_mock = MagicMock(spec=InterviewQuestion)
    q_mock.id = 10
    q_mock.interview_session_id = 1
    q_mock.planned_order = 1
    q_mock.execution_path = "01"
    q_mock.parent_question_id = None
    q_mock.question_category = QuestionCategory.TECHNICAL
    q_mock.question_text = "Primary Q"
    question_repo.get_by_id.return_value = q_mock
    question_repo.get_by_session.return_value = [q_mock]
    
    # Mock adaptive engine to return GENERATE_FOLLOW_UP
    
    # Since AdaptiveDecisionEngine is instantiated inside InterviewExecutionService with defaults,
    # we need to patch it or pass thresholds. Wait, we can mock deterministic engine 
    # to return a terrible evaluation and let the real AdaptiveDecisionEngine decide!
    from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
    eval_mock = AnswerEvaluation(
        keyword_coverage=0.1,
        concept_coverage=0.1,
        completeness=0.1,
        overall_score=0.1,
        vocabulary_statistics={}
    )
    det_engine.evaluate.return_value = eval_mock
    
    follow_up_q = MagicMock(spec=InterviewQuestion)
    follow_up_q.id = 11
    follow_up_q.question_text = "Follow up Q"
    follow_up_q.question_type = QuestionType.FOLLOW_UP
    follow_up_q.question_category = QuestionCategory.TECHNICAL
    follow_up_q.planned_order = 1
    follow_up_q.execution_path = "01.01"
    
    follow_up_service.generate.return_value = follow_up_q
    question_repo.create_many.return_value = [follow_up_q]
    
    service = InterviewExecutionService(
        session_repo=session_repo, 
        question_repo=question_repo, 
        answer_repo=answer_repo,
        deterministic_engine=det_engine,
        follow_up_service=follow_up_service
    )
    
    submitted_answer = SubmittedAnswer(
        transcript="Bad answer",
        answer_source=AnswerSource.TEXT,
        answer_duration_seconds=10
    )
    
    state = service.submit_answer(db, 1, 1, 10, submitted_answer)
    
    assert state.is_completed is False
    assert state.current_question is not None
    assert state.current_question.question_id == 11
    follow_up_service.generate.assert_called_once()
    question_repo.create_many.assert_called_once_with(db, [follow_up_q])

def test_submit_answer_adaptive_follow_up_limit_reached():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    det_engine = MagicMock()
    follow_up_service = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q_mock = MagicMock(spec=InterviewQuestion)
    q_mock.id = 10
    q_mock.interview_session_id = 1
    q_mock.planned_order = 1
    q_mock.execution_path = "01"
    q_mock.parent_question_id = None
    q_mock.question_category = QuestionCategory.TECHNICAL
    q_mock.question_text = "Primary Q"
    question_repo.get_by_id.return_value = q_mock
    
    # 2 follow-ups already asked (reaches default cap of 2)
    fu1 = MagicMock(spec=InterviewQuestion)
    fu1.question_type = QuestionType.FOLLOW_UP
    fu1.parent_question_id = 10
    fu1.execution_path = "01.01"
    fu2 = MagicMock(spec=InterviewQuestion)
    fu2.question_type = QuestionType.FOLLOW_UP
    fu2.parent_question_id = 10
    fu2.execution_path = "01.02"
    
    question_repo.get_by_session.return_value = [q_mock, fu1, fu2]
    
    # Bad answer, but limit reached
    from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
    eval_mock = AnswerEvaluation(
        keyword_coverage=0.1,
        concept_coverage=0.1,
        completeness=0.1,
        overall_score=0.1,
        vocabulary_statistics={}
    )
    det_engine.evaluate.return_value = eval_mock
    
    next_planned_q = MagicMock(spec=InterviewQuestion)
    next_planned_q.id = 15
    next_planned_q.question_text = "Next Planned Q"
    next_planned_q.question_type = QuestionType.PRIMARY
    next_planned_q.question_category = QuestionCategory.TECHNICAL
    next_planned_q.planned_order = 5
    next_planned_q.execution_path = "05"
    
    question_repo.get_first_unasked_question.return_value = next_planned_q
    
    service = InterviewExecutionService(
        session_repo=session_repo, 
        question_repo=question_repo, 
        answer_repo=answer_repo,
        deterministic_engine=det_engine,
        follow_up_service=follow_up_service
    )
    
    submitted_answer = SubmittedAnswer(
        transcript="Bad answer again",
        answer_source=AnswerSource.TEXT,
        answer_duration_seconds=10
    )
    
    state = service.submit_answer(db, 1, 1, 10, submitted_answer)
    
    assert state.is_completed is False
    assert state.current_question.question_id == 15
    # Should not generate another follow up
    follow_up_service.generate.assert_not_called()

def test_submit_answer_adaptive_queue_ordering():
    db = MagicMock(spec=Session)
    session_repo = MagicMock()
    question_repo = MagicMock()
    answer_repo = MagicMock()
    det_engine = MagicMock()
    follow_up_service = MagicMock()
    
    session_mock = MagicMock(spec=InterviewSession)
    session_mock.id = 1
    session_mock.status = InterviewStatus.IN_PROGRESS
    session_repo.get_by_id_and_user.return_value = session_mock
    
    q1 = MagicMock(spec=InterviewQuestion)
    q1.id = 10
    q1.interview_session_id = 1
    q1.planned_order = 1
    q1.execution_path = "01"
    q1.question_category = QuestionCategory.TECHNICAL
    q1.question_text = "Q1"
    
    q2 = MagicMock(spec=InterviewQuestion)
    q2.id = 20
    q2.interview_session_id = 1
    q2.planned_order = 2
    q2.execution_path = "02"
    q2.is_asked = False
    
    question_repo.get_by_id.return_value = q1
    question_repo.get_by_session.return_value = [q1, q2]
    
    # Mock bad answer to trigger follow-up
    from app.services.evaluation.schemas.answer_evaluation import AnswerEvaluation
    det_engine.evaluate.return_value = AnswerEvaluation(
        keyword_coverage=0.1, concept_coverage=0.1, completeness=0.1, overall_score=0.1, vocabulary_statistics={}
    )
    
    follow_up_q = MagicMock(spec=InterviewQuestion)
    follow_up_q.id = 11
    follow_up_q.execution_path = "01.01"
    follow_up_q.question_type = QuestionType.FOLLOW_UP
    follow_up_q.question_category = QuestionCategory.TECHNICAL
    follow_up_q.question_text = "F1"
    follow_up_q.planned_order = 1
    
    follow_up_service.generate.return_value = follow_up_q
    question_repo.create_many.return_value = [follow_up_q]
    
    service = InterviewExecutionService(
        session_repo=session_repo, question_repo=question_repo, answer_repo=answer_repo,
        deterministic_engine=det_engine, follow_up_service=follow_up_service
    )
    
    submitted_answer = SubmittedAnswer(transcript="Bad", answer_source=AnswerSource.TEXT, answer_duration_seconds=10)
    state = service.submit_answer(db, 1, 1, 10, submitted_answer)
    
    # Ensure follow up path was passed to generate correctly
    follow_up_service.generate.assert_called_once()
    _, kwargs = follow_up_service.generate.call_args
    assert kwargs["execution_path"] == "01.01"
    
    # Assert state reflects the inserted follow-up
    assert state.current_question.question_id == 11
    assert state.current_question.execution_path == "01.01"

