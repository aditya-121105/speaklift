from pydantic import BaseModel, ConfigDict
from .salary_range import SalaryRange


class JDEmploymentRecord(BaseModel):
    """
    Represents employment details extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    job_title: str | None
    location: str | None
    remote_type: str | None
    salary: SalaryRange | None
    confidence: float
