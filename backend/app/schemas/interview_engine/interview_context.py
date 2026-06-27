"""
==============================================================================
Interview Context

Purpose:
Represents the complete context required to conduct an interview.

It combines:

- Candidate Profile
- Job Profile
- Interview Configuration

Every AI component in SpeakLift should consume this object.

Used by:

- Interview Planner
- Question Selector
- Follow-up Selector
- Evaluation Engine
- Report Generator
- Learning Roadmap Generator

==============================================================================
"""

from pydantic import BaseModel, Field

from app.schemas.interview_engine.candidate_profile import (
    CandidateProfile,
)
from app.schemas.interview_engine.job_profile import (
    JobProfile,
)


class InterviewContext(BaseModel):
    """
    Complete interview context.
    """

    candidate_profile: CandidateProfile

    job_profile: JobProfile

    interview_type: str = Field(
        description="Technical, HR, Viva, etc."
    )

    duration_minutes: int = Field(
        gt=0,
        description="Interview duration."
    )

    difficulty: str = Field(
        description="Easy, Medium, Hard, Adaptive."
    )