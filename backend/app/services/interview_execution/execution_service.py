"""
==============================================================================
Module:
    Interview Execution Service

Milestone:
    M2.2 – Adaptive Interview System  (refactored from M1 baseline)

Responsibilities:
    ✔ Bootstrap questions on interview start
    ✔ Accept and persist candidate answers
    ✔ Invoke DeterministicEvaluationEngine on each answer
    ✔ Route next step via AdaptiveDecisionEngine
    ✔ Generate and enqueue follow-up questions when needed
    ✔ Enforce follow-up and session-length caps
    ✔ Trigger post-session InterviewEvaluationService when session ends

Architecture change from M1
-----------------------------
submit_answer() previously called get_first_unasked_question and moved on.
It now:
  1. Evaluates the submitted answer deterministically.
  2. Calls AdaptiveDecisionEngine.decide().
  3. On GENERATE_FOLLOW_UP: creates a follow-up via FollowUpGenerationService,
     persists it, then fetches that follow-up as the next question.
  4. On END_INTERVIEW / no more questions: marks session completed.

Backward compatibility
----------------------
The method signatures are unchanged.
The API layer (interview_sessions.py) requires NO modifications.
==============================================================================
"""

import logging
from sqlalchemy.orm import Session

from app.shared.enums import InterviewStatus, QuestionType
from app.shared.exceptions import (
    InterviewSessionNotFoundError,
    InterviewQuestionNotFoundError,
    InvalidSessionStateError,
)
from app.services.question_selection.schemas.question_selection import QuestionSelection
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import InterviewSession
from app.services.interview_execution.repository import (
    ExecutionSessionRepository,
    ExecutionQuestionRepository,
    ExecutionAnswerRepository,
)
from app.services.interview_execution.schemas.interview_execution_state import (
    InterviewExecutionState,
    CurrentQuestion,
)
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.interview_execution.schemas.adaptive_decision import AdaptiveDecision
from app.services.interview_execution.adaptive_thresholds import AdaptiveThresholds
from app.services.interview_execution.adaptive_decision_engine import AdaptiveDecisionEngine
from app.services.interview_execution.follow_up_generation_service import FollowUpGenerationService
from app.models.answer_evaluation import AnswerEvaluation
from app.services.evaluation.engine import DeterministicEvaluationEngine
from app.services.evaluation.schemas.evaluation_request import EvaluationRequest
from app.services.question_selection.schemas.question_selection import SelectedQuestion
from app.shared.enums import DifficultyLevel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.evaluation.evaluation_service import InterviewEvaluationService

logger = logging.getLogger(__name__)


class InterviewExecutionService:
    """
    Orchestrates a single interview session from start to completion.

    Parameters
    ----------
    session_repo           : CRUD for InterviewSession records.
    question_repo          : CRUD for InterviewQuestion records.
    answer_repo            : CRUD for InterviewAnswer records.
    evaluation_service     : End-of-session aggregate evaluator (optional).
    deterministic_engine   : Per-answer metric extractor (optional).
    follow_up_service      : Follow-up text generator (optional).
    thresholds             : Configurable adaptive gate values.
    """

    def __init__(
        self,
        session_repo: ExecutionSessionRepository,
        question_repo: ExecutionQuestionRepository,
        answer_repo: ExecutionAnswerRepository,
        evaluation_service: "InterviewEvaluationService | None" = None,
        deterministic_engine: DeterministicEvaluationEngine | None = None,
        follow_up_service: FollowUpGenerationService | None = None,
        thresholds: AdaptiveThresholds | None = None,
    ) -> None:
        self._session_repo = session_repo
        self._question_repo = question_repo
        self._answer_repo = answer_repo
        self._evaluation_service = evaluation_service
        self._deterministic_engine = deterministic_engine
        self._follow_up_service = follow_up_service
        self._adaptive_engine = AdaptiveDecisionEngine(thresholds)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_interview(
        self,
        db: Session,
        session_id: int,
        user_id: int,
        selection: QuestionSelection,
    ) -> InterviewExecutionState:
        session = self._session_repo.get_by_id_and_user(db, session_id, user_id)
        if not session:
            raise InterviewSessionNotFoundError("Interview session not found.")

        if session.status != InterviewStatus.CREATED:
            raise InvalidSessionStateError("Session is already started or completed.")

        # Bootstrap primary questions
        questions = [
            InterviewQuestion(
                interview_session_id=session_id,
                question_text=sq.question_text,
                question_type=QuestionType.PRIMARY,
                question_category=sq.category,
                planned_order=sq.ordering,
                execution_path=f"{sq.ordering:02d}",
                is_asked=False,
            )
            for sq in selection.selected_questions
        ]

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
        submitted_answer: SubmittedAnswer,
    ) -> InterviewExecutionState:
        session = self._session_repo.get_by_id_and_user(db, session_id, user_id)
        if not session:
            raise InterviewSessionNotFoundError("Interview session not found.")

        question = self._question_repo.get_by_id(db, question_id)
        if not question:
            raise InterviewQuestionNotFoundError("Question not found.")

        if question.interview_session_id != session_id:
            raise InvalidSessionStateError("Question does not belong to session.")

        # Persist answer
        saved_answer = self._answer_repo.persist_answer(db, session_id, question_id, submitted_answer)
        self._question_repo.mark_as_asked(db, question_id)

        # Build EvaluationRequest for answer
        sel_q = SelectedQuestion(
            question_id=str(question.id),
            question_text=question.question_text,
            category=question.question_category,
            difficulty=DifficultyLevel.MEDIUM,
            expected_duration_seconds=60,
            tags=[],
            ordering=question.planned_order,
            objective_name="Adaptive Evaluation",
        )
        eval_request = EvaluationRequest(
            submitted_answer=submitted_answer,
            selected_question=sel_q,
        )

        evaluation = None
        if self._evaluation_service:
            enhanced_eval = self._evaluation_service.evaluate_answer(eval_request)
            self._evaluation_service.persist_answer_evaluation(db, saved_answer.id, enhanced_eval)
            evaluation = enhanced_eval.deterministic_metrics
        elif self._deterministic_engine:
            evaluation = self._deterministic_engine.evaluate(eval_request)

        # --- Adaptive routing ---
        next_q = self._route_adaptively(db, session_id, question, submitted_answer, evaluation)

        if next_q is None:
            # No more questions – complete the session
            session = self._session_repo.mark_completed(db, session_id)
            if self._evaluation_service:
                self._trigger_evaluation(db, session_id)

        return self._build_state(session, next_q)

    def get_state(
        self,
        db: Session,
        session_id: int,
    ) -> InterviewExecutionState:
        """Return the current execution state without mutating anything."""
        session = self._session_repo.get_by_id_and_user(db, session_id, user_id=None)  # type: ignore[call-arg]
        if session is None:
            # Fallback: try without user guard (state read is non-destructive)
            from app.models.interview_session import InterviewSession
            session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            raise InterviewSessionNotFoundError("Interview session not found.")
        next_q = self._question_repo.get_first_unasked_question(db, session_id)
        return self._build_state(session, next_q)

    # ------------------------------------------------------------------
    # Adaptive routing
    # ------------------------------------------------------------------

    def _route_adaptively(
        self,
        db: Session,
        session_id: int,
        current_question: InterviewQuestion,
        submitted_answer: SubmittedAnswer,
        evaluation: "AnswerEvaluation | None",
    ) -> InterviewQuestion | None:
        """
        Evaluate the answer and decide whether to:
          a) Return next planned question,
          b) Generate + enqueue a follow-up, or
          c) Return None (end session).
        """

        # If no deterministic engine is wired up or evaluation failed, fall through to linear
        if not evaluation or self._follow_up_service is None:
            return self._question_repo.get_first_unasked_question(db, session_id)

        # Count existing follow-ups for this primary question
        follow_up_count = self._count_follow_ups(db, current_question)

        # Count total questions asked so far (already-asked ones)
        all_questions = self._question_repo.get_by_session(db, session_id)
        asked_count = sum(1 for q in all_questions if q.is_asked)

        decision_result = self._adaptive_engine.decide(
            evaluation,
            total_questions_so_far=asked_count,
            follow_up_count_for_primary=follow_up_count,
        )

        logger.info(
            "Adaptive decision for session=%s question=%s: %s (%s)",
            session_id,
            current_question.id,
            decision_result.decision.value,
            decision_result.reason.value,
        )

        if decision_result.decision == AdaptiveDecision.END_INTERVIEW:
            return None

        if decision_result.decision == AdaptiveDecision.GENERATE_FOLLOW_UP:
            # Determine the execution path for the follow-up
            all_questions = self._question_repo.get_by_session(db, session_id)
            
            parent_path = current_question.execution_path
            prefix = f"{parent_path}."
            children = [
                q for q in all_questions 
                if q.execution_path.startswith(prefix) and len(q.execution_path) == len(prefix) + 2
            ]
            
            next_suffix = len(children) + 1
            follow_up_path = f"{parent_path}.{next_suffix:02d}"

            follow_up_q = self._follow_up_service.generate(
                session_id=session_id,
                parent_question=current_question,
                candidate_answer=submitted_answer.transcript,
                weak_reason=decision_result.reason,
                objective_name="Interview Follow-up",
                planned_order=current_question.planned_order,
                execution_path=follow_up_path,
            )

            try:
                [created_follow_up] = self._question_repo.create_many(db, [follow_up_q])
                return created_follow_up
            except Exception:
                logger.warning("Failed to persist follow-up; falling through to next planned question.")

        # NEXT_QUESTION or fallback
        return self._question_repo.get_first_unasked_question(db, session_id)

    def _count_follow_ups(
        self,
        db: Session,
        question: InterviewQuestion,
    ) -> int:
        """
        Count follow-ups already generated for this specific primary question.
        Also handles the case where 'question' is itself a follow-up (chain prevention).
        """
        # Resolve to the true primary question
        primary_id = question.parent_question_id or question.id
        all_q = self._question_repo.get_by_session(db, question.interview_session_id)
        return sum(
            1 for q in all_q
            if q.question_type == QuestionType.FOLLOW_UP
            and q.parent_question_id == primary_id
        )

    # ------------------------------------------------------------------
    # Post-session evaluation trigger
    # ------------------------------------------------------------------

    def _trigger_evaluation(self, db: Session, session_id: int) -> None:
        questions = self._question_repo.get_by_session(db, session_id)
        answers = self._answer_repo.get_by_session(db, session_id)
        try:
            self._evaluation_service.evaluate_session(db, session_id, questions, answers)  # type: ignore[union-attr]
        except Exception as exc:
            logger.warning("Post-session evaluation failed for session=%s: %s", session_id, exc)

    # ------------------------------------------------------------------
    # State builder
    # ------------------------------------------------------------------

    def _build_state(
        self,
        session: InterviewSession,
        question: InterviewQuestion | None,
    ) -> InterviewExecutionState:
        cq = None
        if question:
            cq = CurrentQuestion(
                question_id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                question_category=question.question_category,
                ordering=question.planned_order,
                execution_path=question.execution_path,
            )

        return InterviewExecutionState(
            session_id=session.id,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            current_question=cq,
            is_completed=(session.status == InterviewStatus.COMPLETED),
        )
