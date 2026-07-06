from pydantic import BaseModel, ConfigDict
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
    skills: list[JDSkillRecord]
    experience: list[JDExperienceRecord]
    education: list[JDEducationRecord]
    responsibilities: list[JDResponsibilityRecord]
    company: JDCompanyRecord
    
    source_filename: str
    pipeline_version: str
    processing_time_ms: int
    document_language: str
    model_version: str
