from pydantic import BaseModel, ConfigDict, Field
from .interview_objective import InterviewObjective

class InterviewPhase(BaseModel):
    """
    Immutable business object representing one phase of an interview.
    Contains sequence ordering and duration allocation.
    """
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(description="Phase name.")
    description: str = Field(description="Purpose of this phase.")
    ordering: int = Field(ge=1, description="Sequential order of the phase in the plan.")
    allocated_minutes: int = Field(gt=0, description="Planned duration.")
    objectives: list[InterviewObjective] = Field(default_factory=list)
