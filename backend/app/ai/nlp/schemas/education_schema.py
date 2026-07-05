from pydantic import BaseModel, ConfigDict


class EducationRecord(BaseModel):
    """A single education entry."""
    model_config = ConfigDict(frozen=True)

    degree: str | None
    field_of_study: str | None
    institution: str | None
    graduation_year: int | None
    raw_text: str
    normalized_name: str | None = None
