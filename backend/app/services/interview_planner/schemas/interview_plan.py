from pydantic import BaseModel, ConfigDict, Field
from .interview_phase import InterviewPhase
from app.shared.enums import ExperienceLevel

class InterviewPlan(BaseModel):
    """
    Immutable business aggregate representing the complete deterministic interview strategy.
    """
    model_config = ConfigDict(frozen=True)
    
    phases: list[InterviewPhase] = Field(default_factory=list)
    total_duration_minutes: int = Field(gt=0, description="Total planned duration.")
    role: str = Field(description="Target role for the interview.")
    experience_level: ExperienceLevel = Field(description="Target experience level.")
