from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.education_match_result import EducationMatchResult

class EducationMatcher:
    """
    Stateless deterministic matcher for comparing candidate education
    against normalized job education requirements.
    """
    
    HIERARCHY = ["phd", "master", "bachelor", "diploma", "associate", "certificate"]

    def match(self, candidate: CandidateProfile, job: JobProfile) -> EducationMatchResult:
        highest_qual = candidate.education.highest_qualification
        req_qual = job.qualification.education.minimum_degree
        req_degrees = job.qualification.education.degrees or []
        cand_degrees = candidate.education.degrees or []
        
        qual_satisfied = self._satisfies_minimum_degree(highest_qual, req_qual)
        
        matched_degrees = []
        missing_degrees = []
        
        for req_deg in req_degrees:
            req_lower = req_deg.lower()
            matched = False
            for cand_deg in cand_degrees:
                cand_degree_lower = (cand_deg.degree or "").lower()
                cand_field_lower = (cand_deg.field_of_study or "").lower()
                if req_lower == cand_degree_lower or (cand_field_lower and req_lower == cand_field_lower):
                    matched = True
                    break
            
            if matched:
                matched_degrees.append(req_deg)
            else:
                missing_degrees.append(req_deg)
                
        total_reqs = (1 if req_qual else 0) + len(req_degrees)
        matched_reqs = (1 if req_qual and qual_satisfied else 0) + len(matched_degrees)
        
        if total_reqs == 0:
            score = 1.0
        else:
            score = round(matched_reqs / total_reqs, 4)
            
        stats = MatchStatistics(
            total_required=total_reqs,
            matched_required=matched_reqs,
            total_preferred=0,
            matched_preferred=0,
            total_optional=0,
            matched_optional=0,
            total_unknown=0,
            matched_unknown=0,
            total_candidate_items=len(cand_degrees) + (1 if highest_qual else 0),
            extra_candidate_items=0
        )
        
        return EducationMatchResult(
            highest_qualification=highest_qual,
            required_qualification=req_qual,
            qualification_satisfied=qual_satisfied,
            matched_degrees=matched_degrees,
            missing_degrees=missing_degrees,
            statistics=stats,
            score=score
        )

    def _satisfies_minimum_degree(self, candidate_highest: str | None, req_minimum: str | None) -> bool:
        if not req_minimum:
            return True
        if not candidate_highest:
            return False
            
        cand_lower = candidate_highest.lower()
        req_lower = req_minimum.lower()
        
        if cand_lower == req_lower:
            return True
            
        if cand_lower in self.HIERARCHY and req_lower in self.HIERARCHY:
            return self.HIERARCHY.index(cand_lower) <= self.HIERARCHY.index(req_lower)
            
        return False
