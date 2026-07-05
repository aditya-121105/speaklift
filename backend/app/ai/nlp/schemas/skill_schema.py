from pydantic import BaseModel, ConfigDict


class SkillEntry(BaseModel):
    """A single detected skill or technology."""
    model_config = ConfigDict(frozen=True)

    normalized_name: str
    raw_text: str
    category: str
    confidence: float
    source_section: str


class SkillSet(BaseModel):
    """Collection of all skills extracted from a resume."""
    model_config = ConfigDict(frozen=True)

    skills: list[SkillEntry]
    technologies: list[SkillEntry]
