from pydantic import BaseModel, ConfigDict


class JDResponsibilityRecord(BaseModel):
    """
    Represents a responsibility extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    description: str
    confidence: float
