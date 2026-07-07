from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.experience_match_result import ExperienceMatchResult

class ExperienceMatcher:
    """
    Stateless deterministic matcher for comparing candidate total experience
    against normalized job experience requirements.
    """
    
    def match(self, candidate: CandidateProfile, job: JobProfile) -> ExperienceMatchResult:
        candidate_months = candidate.career.total_months_experience
        
        min_years = job.qualification.experience.min_years
        max_years = job.qualification.experience.max_years
        
        req_min_months = min_years * 12 if min_years is not None else None
        req_max_months = max_years * 12 if max_years is not None else None
        
        is_satisfied = True
        deficit = 0
        surplus = 0
        
        if req_min_months is not None and candidate_months < req_min_months:
            is_satisfied = False
            deficit = req_min_months - candidate_months
        
        if req_max_months is not None and candidate_months > req_max_months:
            is_satisfied = False
            surplus = candidate_months - req_max_months
            deficit = 0
            
        if is_satisfied and req_min_months is not None:
            surplus = candidate_months - req_min_months
            
        score = 1.0
        if not is_satisfied:
            if deficit > 0 and req_min_months:
                score = round(candidate_months / req_min_months, 4)
            elif surplus > 0 and req_max_months:
                score = round(req_max_months / candidate_months, 4)
            else:
                score = 0.0
                
        has_requirements = req_min_months is not None or req_max_months is not None
        
        stats = MatchStatistics(
            total_required=1 if has_requirements else 0,
            matched_required=1 if (has_requirements and is_satisfied) else 0,
            total_preferred=0,
            matched_preferred=0,
            total_optional=0,
            matched_optional=0,
            total_unknown=0,
            matched_unknown=0,
            total_candidate_items=1,
            extra_candidate_items=0
        )
        
        return ExperienceMatchResult(
            candidate_months=candidate_months,
            required_minimum_months=req_min_months,
            required_maximum_months=req_max_months,
            is_satisfied=is_satisfied,
            deficit_months=deficit,
            surplus_months=surplus,
            statistics=stats,
            score=score
        )
