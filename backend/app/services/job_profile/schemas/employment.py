from pydantic import BaseModel, ConfigDict
from enum import Enum

class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    FREELANCE = "FREELANCE"
    UNKNOWN = "UNKNOWN"

class SalaryPeriod(str, Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"

class SalaryProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    minimum: float | None
    maximum: float | None
    currency: str | None
    period: SalaryPeriod | None

class EmploymentProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    employment_type: EmploymentType | None
    salary: SalaryProfile | None
