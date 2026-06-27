"""
==============================================================================
Interview Context Builder

Purpose:
Build the runtime InterviewContext used by the Interview Engine.

Responsibilities

✔ Build CandidateProfile
✔ Build JobProfile
✔ Build InterviewContext

This class is the entry point for all future AI pipelines.

Future Versions

Resume
    ↓
Resume Parser (LLM + NLP)
    ↓
CandidateProfile

Job Description
    ↓
JD Parser (LLM + NLP)
    ↓
JobProfile

InterviewContextBuilder simply orchestrates these components.
==============================================================================
"""

from app.models.interview_session import InterviewSession

from app.schemas.interview_engine.candidate_profile import (
    CandidateProfile,
)

from app.schemas.interview_engine.job_profile import (
    JobProfile,
)

from app.schemas.interview_engine.interview_context import (
    InterviewContext,
)


class InterviewContextBuilder:
    """
    Build the runtime InterviewContext.
    """

    @classmethod
    def build(
        cls,
        interview_session: InterviewSession,
    ) -> InterviewContext:

        candidate_profile = cls._build_candidate_profile(
            interview_session
        )

        job_profile = cls._build_job_profile(
            interview_session
        )

        return InterviewContext(
            candidate_profile=candidate_profile,
            job_profile=job_profile,
            interview_type="Technical",
            duration_minutes=interview_session.duration_minutes,
            difficulty="Medium",
        )

    @staticmethod
    def _build_candidate_profile(
        interview_session: InterviewSession,
    ) -> CandidateProfile:
        """
        Temporary implementation.

        Resume Parsing Pipeline will populate this
        object in a later sprint.
        """

        return CandidateProfile()

    @staticmethod
    def _build_job_profile(
        interview_session: InterviewSession,
    ) -> JobProfile:
        """
        Temporary implementation.

        JD Parsing Pipeline will populate this
        object in a later sprint.
        """

        return JobProfile(
            role=interview_session.role,
            experience_level=(
                interview_session.experience_level.value
            ),
        )