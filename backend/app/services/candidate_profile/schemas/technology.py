from pydantic import BaseModel, ConfigDict


class TechNode(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    years_applied: float
    last_used_year: int | None
    source_count: int


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
