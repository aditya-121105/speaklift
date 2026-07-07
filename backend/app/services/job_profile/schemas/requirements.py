from pydantic import BaseModel, ConfigDict

class SkillRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str

class ResponsibilityRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str

class RequirementsProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    required_skills: list[SkillRequirement]
    preferred_skills: list[SkillRequirement]
    optional_skills: list[SkillRequirement]
    unknown_skills: list[SkillRequirement]
    responsibilities: list[ResponsibilityRequirement]
