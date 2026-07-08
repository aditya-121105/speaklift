from pydantic import BaseModel, ConfigDict
from app.shared.enums import QuestionCategory, DifficultyLevel

class SelectedQuestion(BaseModel):
    """
    Immutable business object representing a deterministically selected question.
    """
    model_config = ConfigDict(frozen=True)
    
    question_id: int
    question_text: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    ordering: int
    objective_name: str
