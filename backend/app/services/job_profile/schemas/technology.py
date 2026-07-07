from pydantic import BaseModel, ConfigDict
from app.services.candidate_profile.schemas.technology import TechNode

class TechnologyProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    languages: list[TechNode]
    frameworks: list[TechNode]
    libraries: list[TechNode]
    databases: list[TechNode]
    cloud: list[TechNode]
    devops: list[TechNode]
    ai_ml: list[TechNode]
    testing: list[TechNode]
    operating_systems: list[TechNode]
    tools: list[TechNode]
