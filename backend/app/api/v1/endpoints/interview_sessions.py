from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import (
    get_current_user,
)
from app.dependencies.database import (
    get_db,
)
from app.models.user import User
from app.schemas.interview_session import (
    CreateInterviewSessionRequest,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
)
from app.services.interview_session_service import (
    InterviewSessionService,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interview Sessions"],
)

@router.post(
    "",
    response_model=InterviewSessionResponse,
)
def create_interview_session(
    payload: CreateInterviewSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    interview_session = (
        InterviewSessionService.create_interview_session(
            db,
            current_user,
            payload,
        )
    )

    return interview_session

@router.get(
    "",
    response_model=list[
        InterviewSessionResponse
    ],
)
def get_user_interview_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return (
        InterviewSessionService
        .get_user_interview_sessions(
            db,
            current_user.id,
        )
    )

@router.get(
    "/{interview_session_id}",
    response_model=InterviewSessionDetailResponse,
)
def get_interview_session(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return InterviewSessionService.get_interview_session(
        db,
        interview_session_id,
        current_user.id,
    )
