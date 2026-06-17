from sqlalchemy.orm import Session

from app.models.interview_session import (
    InterviewSession,
)
from app.models.user import User
from app.repositories.interview_session_repository import (
    InterviewSessionRepository,
)
from app.schemas.interview_session import (
    CreateInterviewSessionRequest,
)
from app.shared.enums import (
    InterviewStatus,
)


class InterviewSessionService:

    @staticmethod
    def create_interview_session(
        db: Session,
        current_user: User,
        payload: CreateInterviewSessionRequest,
    ) -> InterviewSession:

        interview_session = InterviewSession(
            user_id=current_user.id,
            role=payload.role,
            experience_level=payload.experience_level,
            duration_minutes=payload.duration_minutes,
            resume_id=payload.resume_id,
            job_description=payload.job_description,
            status=InterviewStatus.CREATED,
        )

        return (
            InterviewSessionRepository.create(
                db,
                interview_session,
            )
        )

    @staticmethod
    def get_interview_session(
        db: Session,
        interview_session_id: int,
        user_id: int,
    ) -> InterviewSession | None:

        return (
            InterviewSessionRepository.get_by_id_and_user(
                db,
                interview_session_id,
                user_id,
            )
        )

    @staticmethod
    def get_user_interview_sessions(
        db: Session,
        user_id: int,
    ) -> list[InterviewSession]:

        return (
            InterviewSessionRepository.get_by_user(
                db,
                user_id,
            )
        )