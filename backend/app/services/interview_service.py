#backend/app/services/interview_service.py
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.interview_answer import (
    InterviewAnswer,
)
from app.models.interview_question import (
    InterviewQuestion,
)

from app.repositories.interview_answer_repository import (
    InterviewAnswerRepository,
)

from app.shared.enums import (
    AnswerSource,
)

from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)

from app.services.interview_question_generator_service import (
    InterviewQuestionGeneratorService,
)

from app.shared.enums import (
    InterviewStatus,
)
from app.shared.exceptions import (
    InterviewSessionNotFoundError,
    InterviewQuestionNotFoundError,
    InvalidSessionStateError,
)


class InterviewService:

    @staticmethod
    def start_interview(
        db: Session,
        session_id: int,
        user_id: int,
    ) -> InterviewQuestion:

        interview_session = (
            InterviewSessionRepository.get_by_id_and_user(
                db=db,
                interview_session_id=session_id,
                user_id=user_id,
            )
        )

        if not interview_session:

            raise InterviewSessionNotFoundError(
                "Interview session not found."
            )

        questions = (
            InterviewQuestionRepository.get_by_session(
                db=db,
                interview_session_id=session_id,
            )
        )

        if not questions:

            questions = (
                InterviewQuestionGeneratorService
                .generate_questions(
                    db=db,
                    interview_session=interview_session,
                )
            )

        if (
                interview_session.status
                == InterviewStatus.CREATED
        ):
            interview_session.status = (
                InterviewStatus.IN_PROGRESS
            )

            interview_session.started_at = (
                datetime.utcnow()
            )

            InterviewSessionRepository.save(
                db=db,
                interview_session=interview_session,
            )

        first_question = (
            InterviewQuestionRepository
            .get_first_unasked_question(
                db=db,
                interview_session_id=session_id,
            )
        )

        if not first_question:
            raise InvalidSessionStateError(
                "No interview questions available."
            )

        return first_question

    @staticmethod
    def submit_answer(
            db: Session,
            session_id: int,
            user_id: int,
            question_id: int,
            transcript: str,
            answer_source: AnswerSource,
            answer_duration_seconds: int | None = None,
    ) -> InterviewQuestion | None:
        interview_session = (
            InterviewSessionRepository.get_by_id_and_user(
                db=db,
                interview_session_id=session_id,
                user_id=user_id,
            )
        )

        if not interview_session:
            raise InterviewSessionNotFoundError(
                "Interview session not found."
            )
        question = (
            InterviewQuestionRepository.get_by_id(
                db=db,
                question_id=question_id,
            )
        )

        if not question:
            raise InterviewQuestionNotFoundError(
                "Question not found."
            )

        if (
                question.interview_session_id
                != session_id
        ):
            raise InvalidSessionStateError(
                "Question does not belong to session."
            )

        answer = InterviewAnswer(
            interview_session_id=session_id,
            interview_question_id=question_id,
            transcript=transcript,
            answer_source=answer_source,
            answer_duration_seconds=(
                answer_duration_seconds
            ),
        )

        InterviewAnswerRepository.create(
            db=db,
            answer=answer,
        )

        question.is_asked = True

        InterviewQuestionRepository.save(
            db=db,
            question=question,
        )

        next_question = (
            InterviewQuestionRepository
            .get_first_unasked_question(
                db=db,
                interview_session_id=session_id,
            )
        )

        if next_question:
            return next_question

        interview_session = (
            InterviewSessionRepository.get_by_id(
                db=db,
                interview_session_id=session_id,
            )
        )

        if interview_session:
            interview_session.status = (
                InterviewStatus.COMPLETED
            )

            interview_session.completed_at = (
                datetime.utcnow()
            )

            InterviewSessionRepository.save(
                db=db,
                interview_session=interview_session,
            )

        return None

    @staticmethod
    def get_questions(
            db: Session,
            session_id: int,
            user_id: int,
    ) -> list[InterviewQuestion]:
        interview_session = (
            InterviewSessionRepository.get_by_id_and_user(
                db=db,
                interview_session_id=session_id,
                user_id=user_id,
            )
        )

        if not interview_session:
            raise InterviewSessionNotFoundError(
                "Interview session not found."
            )

        return (
            InterviewQuestionRepository
            .get_by_session(
                db=db,
                interview_session_id=session_id,
            )
        )

    @staticmethod
    def get_answers(
            db: Session,
            session_id: int,
            user_id: int,
    ) -> list[InterviewAnswer]:

        interview_session = (
            InterviewSessionRepository.get_by_id_and_user(
                db=db,
                interview_session_id=session_id,
                user_id=user_id,
            )
        )

        if not interview_session:
            raise InterviewSessionNotFoundError(
                "Interview session not found."
            )

        return (
            InterviewAnswerRepository
            .get_by_session(
                db=db,
                session_id=session_id,
            )
        )