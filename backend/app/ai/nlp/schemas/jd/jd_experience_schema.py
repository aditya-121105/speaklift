from pydantic import BaseModel, ConfigDict


class JDExperienceRecord(BaseModel):
    """
    Represents an experience requirement extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    min_years: int | None
    max_years: int | None
    domain: str | None
    confidence: float
