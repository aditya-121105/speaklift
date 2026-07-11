from pydantic import BaseModel, ConfigDict
from app.shared.enums import AnswerSource

class SubmittedAnswer(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    transcript: str
    answer_source: AnswerSource
    answer_duration_seconds: int | None = None
