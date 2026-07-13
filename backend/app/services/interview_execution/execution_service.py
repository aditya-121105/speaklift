from sqlalchemy.orm import Session
from app.shared.enums import InterviewStatus, QuestionType, AnswerSource
from app.shared.exceptions import (
    InterviewSessionNotFoundError,
    InterviewQuestionNotFoundError,
    InvalidSessionStateError,
)
from datetime import datetime
from app.services.question_selection.schemas.question_selection import QuestionSelection
from app.models.interview_question import InterviewQuestion
from app.models.interview_answer import InterviewAnswer
from app.models.interview_session import InterviewSession
from app.services.interview_execution.repository import (
    ExecutionSessionRepository,
    ExecutionQuestionRepository,
    ExecutionAnswerRepository
)
from app.services.interview_execution.schemas.interview_execution_state import (
    InterviewExecutionState,
    CurrentQuestion
)
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import SelectedQuestion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.evaluation.evaluation_service import InterviewEvaluationService

class InterviewExecutionService:
    def __init__(
        self,
        session_repo: ExecutionSessionRepository,
        question_repo: ExecutionQuestionRepository,
        answer_repo: ExecutionAnswerRepository,
        evaluation_service: 'InterviewEvaluationService | None' = None
    ):
        self._session_repo = session_repo
        self._question_repo = question_repo
        self._answer_repo = answer_repo
        self._evaluation_service = evaluation_service
        
    def start_interview(
        self, 
        db: Session, 
        session_id: int, 
        user_id: int, 
        selection: QuestionSelection
    ) -> InterviewExecutionState:
        session = self._session_repo.get_by_id_and_user(db, session_id, user_id)
        if not session:
            raise InterviewSessionNotFoundError("Interview session not found.")
            
        if session.status != InterviewStatus.CREATED:
            raise InvalidSessionStateError("Session is already started or completed.")
            
        # Bootstrap questions
        questions = []
        for sq in selection.selected_questions:
            questions.append(
                InterviewQuestion(
                    interview_session_id=session_id,
                    question_text=sq.question_text,
                    question_type=QuestionType.PRIMARY,
                    question_category=sq.category,
                    question_order=sq.ordering,
                    is_asked=False
                )
            )
            
        self._question_repo.create_many(db, questions)
        
        session = self._session_repo.mark_in_progress(db, session_id)
        if not session:
            raise InvalidSessionStateError("Failed to update session state.")
        
        first_q = self._question_repo.get_first_unasked_question(db, session_id)
        if not first_q:
            raise InvalidSessionStateError("No questions bootstrapped.")
            
        return self._build_state(session, first_q)
        
    def submit_answer(
        self,
        db: Session,
        session_id: int,
        user_id: int,
        question_id: int,
        submitted_answer: SubmittedAnswer
    ) -> InterviewExecutionState:
        session = self._session_repo.get_by_id_and_user(db, session_id, user_id)
        if not session:
            raise InterviewSessionNotFoundError("Interview session not found.")
            
        question = self._question_repo.get_by_id(db, question_id)
        if not question:
            raise InterviewQuestionNotFoundError("Question not found.")
            
        if question.interview_session_id != session_id:
            raise InvalidSessionStateError("Question does not belong to session.")
            
        self._answer_repo.persist_answer(db, session_id, question_id, submitted_answer)
        
        question = self._question_repo.mark_as_asked(db, question_id)
        
        next_q = self._question_repo.get_first_unasked_question(db, session_id)
        
        if not next_q:
            session = self._session_repo.mark_completed(db, session_id)
            
            # Trigger evaluation if service is configured
            if self._evaluation_service:
                self._trigger_evaluation(db, session_id)
                
        return self._build_state(session, next_q)

    def _trigger_evaluation(self, db: Session, session_id: int) -> None:
        questions = self._question_repo.get_by_session(db, session_id)
        answers = self._answer_repo.get_by_session(db, session_id)
        
        self._evaluation_service.evaluate_session(db, session_id, questions, answers)
        
    def _build_state(self, session: InterviewSession, question: InterviewQuestion | None) -> InterviewExecutionState:
        cq = None
        if question:
            cq = CurrentQuestion(
                question_id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                question_category=question.question_category,
                ordering=question.question_order
            )
            
        return InterviewExecutionState(
            session_id=session.id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            current_question=cq,
            is_completed=(session.status == InterviewStatus.COMPLETED)
        )
