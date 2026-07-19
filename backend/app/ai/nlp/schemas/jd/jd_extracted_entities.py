from pydantic import BaseModel, ConfigDict, Field
from .jd_skill_schema import JDSkillRecord
from .jd_experience_schema import JDExperienceRecord
from .jd_education_schema import JDEducationRecord
from .jd_employment_schema import JDEmploymentRecord
from .jd_responsibility_schema import JDResponsibilityRecord
from .jd_company_schema import JDCompanyRecord


class ExtractedJDEntities(BaseModel):
    """
    The complete output of the JD NLP pipeline.
    This is the primary contract consumed by business services and ML.
    """
    model_config = ConfigDict(frozen=True)

    employment: JDEmploymentRecord
    skills: list[JDSkillRecord] = Field(default_factory=list)
    experience: list[JDExperienceRecord] = Field(default_factory=list)
    education: list[JDEducationRecord] = Field(default_factory=list)
    responsibilities: list[JDResponsibilityRecord] = Field(default_factory=list)
    company: JDCompanyRecord
    
    source_filename: str
    pipeline_version: str
    processing_time_ms: int
    document_language: str
    model_version: str
