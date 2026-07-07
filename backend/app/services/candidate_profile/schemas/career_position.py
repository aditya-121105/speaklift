from pydantic import BaseModel, ConfigDict

class CareerPosition(BaseModel):
    """A single work experience entry mapped into the business domain."""
    model_config = ConfigDict(frozen=True)

    job_title: str | None
    company: str | None
    employment_type: str | None
    location: str | None
    start_date: str | None
    end_date: str | None
    is_current: bool
    duration_months: int | None
    description: str | None
    technologies_used: list[str]
