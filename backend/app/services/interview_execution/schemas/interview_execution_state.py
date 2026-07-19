from pydantic import BaseModel, ConfigDict
from app.shared.enums import InterviewStatus, QuestionCategory, QuestionType
from datetime import datetime

class CurrentQuestion(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    question_id: int
    question_text: str
    question_type: QuestionType
    question_category: QuestionCategory
    ordering: int
    execution_path: str

class InterviewExecutionState(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    session_id: int
    status: InterviewStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    current_question: CurrentQuestion | None = None
    is_completed: bool
