from pydantic import BaseModel, ConfigDict, Field

class InterviewObjective(BaseModel):
    """
    Immutable business object representing one deterministic planning objective.
    Does not contain question text or runtime state.
    """
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(description="Objective name.")
    description: str = Field(description="What this objective evaluates.")
    priority: int = Field(ge=1, le=10, description="Importance of this objective.")
