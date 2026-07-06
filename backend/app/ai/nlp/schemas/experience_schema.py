from pydantic import BaseModel, ConfigDict


class ExperienceRecord(BaseModel):
    """A single work experience entry."""
    model_config = ConfigDict(frozen=True)

    job_title: str | None
    company: str | None
    employment_type: str | None = None
    location: str | None = None
    start_date: str | None
    end_date: str | None
    is_current: bool = False
    duration_months: int | None = None
    description: str | None = None
    technologies_used: list[str] = []  # populated with normalized_names
    confidence: float = 1.0
    raw_text: str
    normalized_name: str | None = None
