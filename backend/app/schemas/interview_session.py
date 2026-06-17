from datetime import datetime

from pydantic import BaseModel, Field
from pydantic import ConfigDict
from app.shared.enums import (
    ExperienceLevel,
    InterviewStatus,
)


class CreateInterviewSessionRequest(BaseModel):
    role: str

    experience_level: ExperienceLevel

    duration_minutes: int = Field(
        ge=15,
        le=60,
    )

    resume_id: int | None = None

    job_description: str | None = None


class InterviewSessionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int

    role: str

    experience_level: ExperienceLevel

    duration_minutes: int

    status: InterviewStatus

    created_at: datetime


class InterviewSessionDetailResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    user_id: int

    role: str

    experience_level: ExperienceLevel

    duration_minutes: int

    resume_id: int | None

    job_description: str | None

    status: InterviewStatus

    started_at: datetime | None

    completed_at: datetime | None

    created_at: datetime

    updated_at: datetime