from pydantic import BaseModel, ConfigDict
from .selected_question import SelectedQuestion

class QuestionSelection(BaseModel):
    """
    Immutable business aggregate containing the selected questions.
    """
    model_config = ConfigDict(frozen=True)
    
    selected_questions: list[SelectedQuestion]
    total_questions: int
