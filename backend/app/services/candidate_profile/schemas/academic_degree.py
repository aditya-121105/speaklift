from pydantic import BaseModel, ConfigDict

class AcademicDegree(BaseModel):
    """A single education entry mapped into the business domain."""
    model_config = ConfigDict(frozen=True)

    degree: str | None
    field_of_study: str | None
    institution: str | None
    start_year: int | None = None
    graduation_year: int | None
    cgpa: float | None = None
    percentage: float | None = None
    is_current: bool = False
