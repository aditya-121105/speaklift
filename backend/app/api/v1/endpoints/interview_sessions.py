from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
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
from app.schemas.interview_question import (
    InterviewQuestionResponse,
)

from app.services.interview_service import (
    InterviewService,
)
from app.schemas.interview_answer import (
    SubmitAnswerRequest,
)

from app.schemas.interview_question import (
    SubmitAnswerResponse,
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

    interview_session = (
        InterviewSessionService
        .get_interview_session(
            db,
            interview_session_id,
            current_user.id,
        )
    )

    if not interview_session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    return interview_session

@router.post(
    "/{interview_session_id}/start",
    response_model=InterviewQuestionResponse,
)
def start_interview(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        question = (
            InterviewService.start_interview(
                db=db,
                session_id=(
                    interview_session_id
                ),
                user_id=current_user.id,
            )
        )

        return question

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

@router.post(
    "/{interview_session_id}/answer",
    response_model=SubmitAnswerResponse,
)
def submit_answer(
    interview_session_id: int,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    next_question = (
        InterviewService.submit_answer(
            db=db,
            session_id=(
                interview_session_id
            ),
            question_id=payload.question_id,
            transcript=payload.transcript,
            answer_source=(
                payload.answer_source
            ),
            answer_duration_seconds=(
                payload
                .answer_duration_seconds
            ),
        )
    )

    if next_question:

        return {
            "interview_completed": False,
            "next_question": next_question,
        }

    return {
        "interview_completed": True,
        "next_question": None,
    }

@router.get(
    "/{interview_session_id}/questions",
    response_model=list[
        InterviewQuestionResponse
    ],
)
def get_questions(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return (
        InterviewService.get_questions(
            db=db,
            session_id=interview_session_id,
        )
    )