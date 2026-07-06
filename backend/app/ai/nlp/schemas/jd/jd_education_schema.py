from pydantic import BaseModel, ConfigDict


class JDEducationRecord(BaseModel):
    """
    Represents an education requirement extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    min_degree_level: str | None
    field_of_study: str | None
    confidence: float
