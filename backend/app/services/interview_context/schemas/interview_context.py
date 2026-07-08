from pydantic import BaseModel, ConfigDict
from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_result import MatchResult
from .interview_configuration import InterviewConfiguration

class InterviewContext(BaseModel):
    """
    Immutable business aggregate representing the complete runtime context
    for planning and executing an interview.
    """
    model_config = ConfigDict(frozen=True)
    
    candidate: CandidateProfile
    job: JobProfile
    matching: MatchResult
    configuration: InterviewConfiguration
