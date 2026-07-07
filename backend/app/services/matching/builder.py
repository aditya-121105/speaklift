from app.services.matching.schemas.skill_match_result import SkillMatchResult
from app.services.matching.schemas.experience_match_result import ExperienceMatchResult
from app.services.matching.schemas.education_match_result import EducationMatchResult
from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.match_result import MatchResult

class MatchResultBuilder:
    """
    Stateless deterministic builder that aggregates individual matcher results
    into a final immutable MatchResult.
    """
    
    def build(
        self,
        skill_result: SkillMatchResult,
        experience_result: ExperienceMatchResult,
        education_result: EducationMatchResult
    ) -> MatchResult:
        
        # Aggregate statistics
        stats_list = [skill_result.statistics, experience_result.statistics, education_result.statistics]
        
        aggregated_stats = MatchStatistics(
            total_required=sum(s.total_required for s in stats_list),
            matched_required=sum(s.matched_required for s in stats_list),
            total_preferred=sum(s.total_preferred for s in stats_list),
            matched_preferred=sum(s.matched_preferred for s in stats_list),
            total_optional=sum(s.total_optional for s in stats_list),
            matched_optional=sum(s.matched_optional for s in stats_list),
            total_unknown=sum(s.total_unknown for s in stats_list),
            matched_unknown=sum(s.matched_unknown for s in stats_list),
            total_candidate_items=sum(s.total_candidate_items for s in stats_list),
            extra_candidate_items=sum(s.extra_candidate_items for s in stats_list),
        )
        
        # Calculate overall score deterministically
        # Taking the average of the 3 domains ensures equal weighting of skills, experience, and education matching rules.
        overall_score = round((skill_result.score + experience_result.score + education_result.score) / 3.0, 4)
        
        return MatchResult(
            skill_result=skill_result,
            experience_result=experience_result,
            education_result=education_result,
            statistics=aggregated_stats,
            score=overall_score
        )
