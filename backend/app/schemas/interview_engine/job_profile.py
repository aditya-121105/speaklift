"""
==============================================================================
Job Profile

Purpose:
Represents structured information extracted from a Job Description (JD).

This object is created once by the JD Parsing Pipeline and reused
throughout the interview lifecycle.

It is NOT a database model.

Future AI modules should consume this object instead of reading the
raw job description.

==============================================================================
"""

from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    """
    AI-ready representation of a job description.
    """

    role: str = Field(
        description="Target job role."
    )

    required_skills: list[str] = Field(
        default_factory=list,
        description="Mandatory skills."
    )

    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Preferred skills."
    )

    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies mentioned in the JD."
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key responsibilities."
    )

    experience_level: str | None = Field(
        default=None,
        description="Required experience level."
    )