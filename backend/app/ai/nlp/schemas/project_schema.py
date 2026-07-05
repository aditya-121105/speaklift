from pydantic import BaseModel, ConfigDict


class ProjectRecord(BaseModel):
    """A single project entry."""
    model_config = ConfigDict(frozen=True)

    name: str | None
    description: str | None
    technologies: list[str]  # populated with normalized_names
    skills: list[str]
    raw_text: str
    normalized_name: str | None = None
