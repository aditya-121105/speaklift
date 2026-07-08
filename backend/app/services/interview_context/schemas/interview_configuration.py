from pydantic import BaseModel, ConfigDict
from app.shared.enums import ExperienceLevel

class InterviewConfiguration(BaseModel):
    """
    Immutable business schema representing the configuration of an interview.
    """
    model_config = ConfigDict(frozen=True)
    
    role: str
    experience_level: ExperienceLevel
    duration_minutes: int
