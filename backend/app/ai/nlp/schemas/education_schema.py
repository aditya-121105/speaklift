from pydantic import BaseModel, ConfigDict


class EducationRecord(BaseModel):
    """A single education entry."""
    model_config = ConfigDict(frozen=True)

    degree: str | None
    field_of_study: str | None
    institution: str | None
    start_year: int | None = None
    graduation_year: int | None
    cgpa: float | None = None
    percentage: float | None = None
    is_current: bool = False
    confidence: float = 1.0
    raw_text: str
    normalized_name: str | None = None
