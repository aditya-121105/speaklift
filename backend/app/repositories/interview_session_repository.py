from sqlalchemy.orm import Session

from app.models.interview_session import (
    InterviewSession,
)


class InterviewSessionRepository:

    @staticmethod
    def create(
        db: Session,
        interview_session: InterviewSession,
    ) -> InterviewSession:

        db.add(interview_session)

        db.commit()

        db.refresh(interview_session)

        return interview_session

    @staticmethod
    def get_by_id(
        db: Session,
        interview_session_id: int,
    ) -> InterviewSession | None:

        return (
            db.query(InterviewSession)
            .filter(
                InterviewSession.id
                == interview_session_id
            )
            .first()
        )

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
    ) -> list[InterviewSession]:

        return (
            db.query(InterviewSession)
            .filter(
                InterviewSession.user_id
                == user_id
            )
            .order_by(
                InterviewSession.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_id_and_user(
        db: Session,
        interview_session_id: int,
        user_id: int,
    ) -> InterviewSession | None:

        return (
            db.query(InterviewSession)
            .filter(
                InterviewSession.id
                == interview_session_id,
                InterviewSession.user_id
                == user_id,
            )
            .first()
        )