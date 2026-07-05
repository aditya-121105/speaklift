from pydantic import BaseModel, ConfigDict


class ExperienceRecord(BaseModel):
    """A single work experience entry."""
    model_config = ConfigDict(frozen=True)

    job_title: str | None
    company: str | None
    start_date: str | None
    end_date: str | None
    is_current: bool
    duration_months: int | None
    technologies_used: list[str]  # populated with normalized_names
    raw_text: str
    normalized_name: str | None = None
