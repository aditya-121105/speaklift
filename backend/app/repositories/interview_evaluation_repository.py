from sqlalchemy.orm import Session

from app.models.interview_evaluation import (
    InterviewEvaluation,
)


class InterviewEvaluationRepository:

    @staticmethod
    def create(
        db: Session,
        evaluation: InterviewEvaluation,
    ) -> InterviewEvaluation:

        db.add(evaluation)

        db.commit()

        db.refresh(evaluation)

        return evaluation

    @staticmethod
    def get_by_session(
        db: Session,
        interview_session_id: int,
    ) -> InterviewEvaluation | None:

        return (
            db.query(InterviewEvaluation)
            .filter(
                InterviewEvaluation.interview_session_id
                == interview_session_id
            )
            .first()
        )

    @staticmethod
    def save(
        db: Session,
        evaluation: InterviewEvaluation,
    ) -> InterviewEvaluation:

        db.commit()

        db.refresh(evaluation)

        return evaluation