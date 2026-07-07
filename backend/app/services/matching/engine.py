from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_result import MatchResult
from app.services.matching.matchers.skill_matcher import SkillMatcher
from app.services.matching.matchers.experience_matcher import ExperienceMatcher
from app.services.matching.matchers.education_matcher import EducationMatcher
from app.services.matching.builder import MatchResultBuilder

class MatchingEngine:
    """
    Stateless top-level orchestrator for the deterministic Matching subsystem.
    Executes underlying matchers and delegates aggregation to the MatchResultBuilder.
    """
    
    def __init__(
        self,
        skill_matcher: SkillMatcher,
        experience_matcher: ExperienceMatcher,
        education_matcher: EducationMatcher,
        result_builder: MatchResultBuilder
    ):
        self._skill_matcher = skill_matcher
        self._experience_matcher = experience_matcher
        self._education_matcher = education_matcher
        self._result_builder = result_builder
        
    def match(self, candidate: CandidateProfile, job: JobProfile) -> MatchResult:
        """
        Executes all underlying matchers and returns a unified immutable MatchResult.
        """
        skill_result = self._skill_matcher.match(candidate, job)
        experience_result = self._experience_matcher.match(candidate, job)
        education_result = self._education_matcher.match(candidate, job)
        
        return self._result_builder.build(
            skill_result=skill_result,
            experience_result=experience_result,
            education_result=education_result
        )
