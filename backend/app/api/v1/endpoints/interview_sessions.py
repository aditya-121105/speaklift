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
from app.services.interview_workflow_service import InterviewWorkflowService
from app.services.interview_execution.execution_service import InterviewExecutionService
from app.services.evaluation.evaluation_service import InterviewEvaluationService
from app.dependencies.engine import (
    get_interview_workflow_service,
    get_execution_service,
    get_evaluation_service
)
from app.services.interview_execution.schemas.interview_execution_state import InterviewExecutionState
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.schemas.interview_evaluation import InterviewEvaluationResponse
from app.repositories.interview_evaluation_repository import InterviewEvaluationRepository
from fastapi import HTTPException


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

@router.post(
    "/{interview_session_id}/start",
    response_model=InterviewExecutionState,
)
def start_interview_session(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workflow_service: InterviewWorkflowService = Depends(get_interview_workflow_service)
):
    try:
        return workflow_service.start_workflow(db, interview_session_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/{interview_session_id}/answers",
    response_model=InterviewExecutionState,
)
def submit_interview_answer(
    interview_session_id: int,
    payload: SubmittedAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    execution_service: InterviewExecutionService = Depends(get_execution_service)
):
    # Security check: ensures user owns session
    session = InterviewSessionService.get_interview_session(db, interview_session_id, current_user.id)
    state = execution_service.get_state(db, interview_session_id)
    
    if not state.current_question:
        raise HTTPException(status_code=400, detail="No active question to answer.")
        
    try:
        return execution_service.submit_answer(db, interview_session_id, state.current_question.question_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/{interview_session_id}/state",
    response_model=InterviewExecutionState,
)
def get_interview_state(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    execution_service: InterviewExecutionService = Depends(get_execution_service)
):
    # Security check
    session = InterviewSessionService.get_interview_session(db, interview_session_id, current_user.id)
    try:
        return execution_service.get_state(db, interview_session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/{interview_session_id}/evaluation",
    response_model=InterviewEvaluationResponse,
)
def get_interview_evaluation(
    interview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Security check
    session = InterviewSessionService.get_interview_session(db, interview_session_id, current_user.id)
    
    eval_record = InterviewEvaluationRepository.get_by_session(db, interview_session_id)
    if not eval_record:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
        
    return eval_record
