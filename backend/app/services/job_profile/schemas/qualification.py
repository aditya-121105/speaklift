from pydantic import BaseModel, ConfigDict

class ExperienceRequirements(BaseModel):
    model_config = ConfigDict(frozen=True)
    min_years: int | None
    max_years: int | None

class EducationRequirements(BaseModel):
    model_config = ConfigDict(frozen=True)
    minimum_degree: str | None
    degrees: list[str]

class QualificationProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    experience: ExperienceRequirements
    education: EducationRequirements
