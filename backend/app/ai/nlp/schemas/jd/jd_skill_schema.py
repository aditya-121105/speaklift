from enum import Enum
from pydantic import BaseModel, ConfigDict


class RequirementTier(str, Enum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    OPTIONAL = "OPTIONAL"
    UNKNOWN = "UNKNOWN"


class JDSkillRecord(BaseModel):
    """
    Represents a single skill requirement extracted from a Job Description.
    """
    model_config = ConfigDict(frozen=True)

    name: str
    requirement_tier: RequirementTier
    confidence: float
