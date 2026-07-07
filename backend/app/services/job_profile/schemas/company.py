from pydantic import BaseModel, ConfigDict

class CompanyProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str | None
    industry: str | None
    size: str | None
    culture_keywords: list[str]
