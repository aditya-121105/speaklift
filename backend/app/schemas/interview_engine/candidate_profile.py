"""
==============================================================================
Candidate Profile

Purpose:
Represents structured information extracted from a candidate's resume.

This object is created once by the Resume Parsing Pipeline and reused
throughout the interview lifecycle.

It is NOT a database model.

Future AI modules should consume this object instead of reading the
resume directly.

==============================================================================
"""

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """
    AI-ready representation of a candidate.
    """

    skills: list[str] = Field(
        default_factory=list,
        description="Technical and soft skills."
    )

    projects: list[str] = Field(
        default_factory=list,
        description="Candidate projects."
    )

    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies used by the candidate."
    )

    certifications: list[str] = Field(
        default_factory=list,
        description="Professional certifications."
    )

    education: list[str] = Field(
        default_factory=list,
        description="Educational background."
    )

    achievements: list[str] = Field(
        default_factory=list,
        description="Achievements and awards."
    )