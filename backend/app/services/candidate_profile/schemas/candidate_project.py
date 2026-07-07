from pydantic import BaseModel, ConfigDict

class CandidateProject(BaseModel):
    """A single project entry mapped into the business domain."""
    model_config = ConfigDict(frozen=True)

    name: str | None
    description: str | None
    technologies: list[str]
    skills: list[str]
    start_date: str | None = None
    end_date: str | None = None
