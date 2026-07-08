from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_result import MatchResult
from app.models.interview_session import InterviewSession
from app.services.interview_context.schemas.interview_context import InterviewContext
from app.services.interview_context.schemas.interview_configuration import InterviewConfiguration

class InterviewContextBuilder:
    """
    Stateless deterministic builder that aggregates existing business models 
    into a unified InterviewContext.
    """
    
    @classmethod
    def build(
        cls,
        candidate_profile: CandidateProfile,
        job_profile: JobProfile,
        match_result: MatchResult,
        interview_session: InterviewSession
    ) -> InterviewContext:
        """
        Validates inputs and builds the InterviewContext.
        """
        if not candidate_profile or not job_profile or not match_result or not interview_session:
            raise ValueError("All inputs must be provided to build InterviewContext")
            
        configuration = InterviewConfiguration(
            role=interview_session.role,
            experience_level=interview_session.experience_level,
            duration_minutes=interview_session.duration_minutes,
        )
            
        return InterviewContext(
            candidate=candidate_profile,
            job=job_profile,
            matching=match_result,
            configuration=configuration
        )
