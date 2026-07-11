from pydantic import BaseModel, ConfigDict
from app.services.interview_execution.schemas.submitted_answer import SubmittedAnswer
from app.services.question_selection.schemas.question_selection import SelectedQuestion

class EvaluationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    submitted_answer: SubmittedAnswer
    selected_question: SelectedQuestion
