from sqlalchemy.orm import Session

from app.models.interview_session import (
    InterviewSession,
)


from app.services.interview_execution.repository import ExecutionSessionRepository

class InterviewSessionRepository(ExecutionSessionRepository):

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

    @staticmethod
    def save(
            db: Session,
            interview_session: InterviewSession,
    ) -> InterviewSession:
        db.commit()
        db.refresh(interview_session)
        return interview_session

    @staticmethod
    def mark_in_progress(
        db: Session,
        session_id: int,
    ) -> InterviewSession | None:
        from datetime import datetime, timezone
        from app.shared.enums import InterviewStatus
        
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if session:
            session.status = InterviewStatus.IN_PROGRESS
            session.started_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def mark_completed(
        db: Session,
        session_id: int,
    ) -> InterviewSession | None:
        from datetime import datetime, timezone
        from app.shared.enums import InterviewStatus
        
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if session:
            session.status = InterviewStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
        return session