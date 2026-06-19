from sqlalchemy.orm import Session

from app.models.interview_answer import (
    InterviewAnswer,
)


class InterviewAnswerRepository:

    @staticmethod
    def create(
        db: Session,
        answer: InterviewAnswer,
    ) -> InterviewAnswer:

        try:
            db.add(answer)

            db.commit()

            db.refresh(answer)

            return answer

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