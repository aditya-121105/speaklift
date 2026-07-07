from pydantic import BaseModel, ConfigDict
from enum import Enum
from .salary_range import SalaryRange

class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    FREELANCE = "FREELANCE"
    UNKNOWN = "UNKNOWN"

class RemoteType(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"
    UNKNOWN = "UNKNOWN"


class JDEmploymentRecord(BaseModel):
    """
    Represents employment details extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    job_title: str | None
    location: str | None
    remote_type: RemoteType | None
    employment_type: EmploymentType | None
    salary: SalaryRange | None
    confidence: float
