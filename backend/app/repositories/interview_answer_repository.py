from sqlalchemy.orm import Session

from app.models.interview_answer import (
    InterviewAnswer,
)


from app.services.interview_execution.repository import ExecutionAnswerRepository

from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer

class InterviewAnswerRepository(ExecutionAnswerRepository):

    @staticmethod
    def persist_answer(
        db: Session,
        session_id: int,
        question_id: int,
        submitted_answer: SubmittedAnswer,
    ) -> None:

        try:
            answer = InterviewAnswer(
                interview_session_id=session_id,
                interview_question_id=question_id,
                transcript=submitted_answer.transcript,
                answer_source=submitted_answer.answer_source,
                answer_duration_seconds=submitted_answer.answer_duration_seconds,
            )
            db.add(answer)
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_by_id(
        db: Session,
        answer_id: int,
    ) -> InterviewAnswer | None:

        return (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.id == answer_id
            )
            .first()
        )

    @staticmethod
    def get_by_question(
        db: Session,
        question_id: int,
    ) -> list[InterviewAnswer]:

        return (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.interview_question_id
                == question_id
            )
            .all()
        )

    @staticmethod
    def get_by_session(
        db: Session,
        session_id: int,
    ) -> list[InterviewAnswer]:

        return (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.interview_session_id
                == session_id
            )
            .all()
        )