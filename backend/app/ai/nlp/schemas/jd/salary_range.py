from pydantic import BaseModel, ConfigDict
from enum import Enum


class SalaryPeriod(str, Enum):
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"


class SalaryRange(BaseModel):
    """
    Dedicated schema for salary ranges.
    """
    model_config = ConfigDict(frozen=True)

    minimum: float | None
    maximum: float | None
    currency: str | None
    period: SalaryPeriod | None
    confidence: float
