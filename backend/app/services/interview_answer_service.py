from sqlalchemy.orm import Session

from app.models.interview_answer import (
    InterviewAnswer,
)
from app.models.user import User

from app.repositories.interview_answer_repository import (
    InterviewAnswerRepository,
)
from app.repositories.interview_question_repository import (
    InterviewQuestionRepository,
)
from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)

from app.schemas.interview_answer import (
    SubmitAnswerRequest,
)
from app.shared.exceptions import (
    InterviewSessionNotFoundError,
    InterviewQuestionNotFoundError,
    InvalidSessionStateError,
)


class InterviewAnswerService:

    @staticmethod
    def submit_answer(
        db: Session,
        current_user: User,
        interview_session_id: int,
        payload: SubmitAnswerRequest,
    ) -> InterviewAnswer:

        session = (
            InterviewSessionRepository.get_by_id_and_user(
                db,
                interview_session_id,
                current_user.id,
            )
        )

        if not session:
            raise InterviewSessionNotFoundError(
                "Interview session not found"
            )

        question = (
            InterviewQuestionRepository.get_by_id(
                db,
                payload.question_id,
            )
        )

        if not question:
            raise InterviewQuestionNotFoundError(
                "Question not found"
            )

        if (
            question.interview_session_id
            != interview_session_id
        ):
            raise InvalidSessionStateError(
                "Question does not belong to interview session"
            )

        answer = InterviewAnswer(
            interview_session_id=interview_session_id,
            interview_question_id=payload.question_id,
            transcript=payload.transcript,
            answer_source=payload.answer_source,
            answer_duration_seconds=payload.answer_duration_seconds,
        )

        return (
            InterviewAnswerRepository.create(
                db,
                answer,
            )
        )

    @staticmethod
    def get_session_answers(
        db: Session,
        current_user: User,
        interview_session_id: int,
    ) -> list[InterviewAnswer]:

        session = (
            InterviewSessionRepository.get_by_id_and_user(
                db,
                interview_session_id,
                current_user.id,
            )
        )

        if not session:
            raise InterviewSessionNotFoundError(
                "Interview session not found"
            )

        return (
            InterviewAnswerRepository.get_by_session(
                db,
                interview_session_id,
            )
        )