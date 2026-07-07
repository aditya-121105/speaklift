"""
JD specific NLP schemas.
All schemas are immutable and contain no business logic.
"""
from .salary_range import SalaryRange, SalaryPeriod
from .jd_skill_schema import JDSkillRecord, RequirementTier
from .jd_experience_schema import JDExperienceRecord
from .jd_education_schema import JDEducationRecord
from .jd_employment_schema import JDEmploymentRecord, EmploymentType, RemoteType
from .jd_responsibility_schema import JDResponsibilityRecord
from .jd_company_schema import JDCompanyRecord
from .jd_extracted_entities import ExtractedJDEntities

__all__ = [
    "SalaryRange",
    "SalaryPeriod",
    "JDSkillRecord",
    "RequirementTier",
    "JDExperienceRecord",
    "JDEducationRecord",
    "JDEmploymentRecord",
    "EmploymentType",
    "RemoteType",
    "JDResponsibilityRecord",
    "JDCompanyRecord",
    "ExtractedJDEntities",
]
