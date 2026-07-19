from pydantic import BaseModel, ConfigDict, Field


class JDCompanyRecord(BaseModel):
    """
    Represents company details extracted from a Job Description.
    Extraction is deferred to a future LLM sprint, so all fields are nullable.
    """
    model_config = ConfigDict(frozen=True)

    company_name: str | None
    industry: str | None
    company_size: str | None
    culture_keywords: list[str] = Field(default_factory=list)
    website: str | None
    confidence: float
