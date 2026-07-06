from enum import Enum
from pydantic import BaseModel, ConfigDict
from app.ai.nlp.schemas.experience_schema import ExperienceRecord


class CareerStage(str, Enum):
    STUDENT = "STUDENT"
    ENTRY = "ENTRY"
    ASSOCIATE = "ASSOCIATE"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    PRINCIPAL = "PRINCIPAL"


class CareerProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    career_stage: CareerStage
    current_role: str | None = None
    most_recent_employer: str | None = None
    total_months_experience: int
    internship_months: int
    positions: list[ExperienceRecord]
