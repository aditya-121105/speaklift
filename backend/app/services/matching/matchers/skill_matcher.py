from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.candidate_profile.schemas.technology import TechNode, TechnologyProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.job_profile.schemas.requirements import RequirementsProfile

from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.skill_match_result import SkillMatchResult

class SkillMatcher:
    """
    Deterministic, stateless matcher for comparing candidate and job technologies.
    """
    
    def match(self, candidate_profile: CandidateProfile, job_profile: JobProfile) -> SkillMatchResult:
        candidate_nodes = self._extract_technodes(candidate_profile.technology)
        job_nodes = self._extract_technodes(job_profile.technology)
        
        job_tiers = self._get_job_skill_tiers(job_profile.requirements)
        
        candidate_map = {node.name.lower(): node for node in candidate_nodes}
        job_map = {node.name.lower(): node for node in job_nodes}
        
        matched_required = []
        missing_required = []
        matched_preferred = []
        missing_preferred = []
        matched_optional = []
        missing_optional = []
        matched_unknown = []
        missing_unknown = []
        
        for job_skill_lower, job_node in job_map.items():
            tier = job_tiers.get(job_skill_lower, "UNKNOWN")
            is_matched = job_skill_lower in candidate_map
            
            if tier == "REQUIRED":
                if is_matched:
                    matched_required.append(candidate_map[job_skill_lower])
                else:
                    missing_required.append(job_node)
            elif tier == "PREFERRED":
                if is_matched:
                    matched_preferred.append(candidate_map[job_skill_lower])
                else:
                    missing_preferred.append(job_node)
            elif tier == "OPTIONAL":
                if is_matched:
                    matched_optional.append(candidate_map[job_skill_lower])
                else:
                    missing_optional.append(job_node)
            else:
                if is_matched:
                    matched_unknown.append(candidate_map[job_skill_lower])
                else:
                    missing_unknown.append(job_node)
                    
        extra = []
        for cand_skill_lower, cand_node in candidate_map.items():
            if cand_skill_lower not in job_map:
                extra.append(cand_node)
                
        # Sort lists to ensure deterministic ordering (e.g. alphabetical by name)
        matched_required.sort(key=lambda x: x.name.lower())
        missing_required.sort(key=lambda x: x.name.lower())
        matched_preferred.sort(key=lambda x: x.name.lower())
        missing_preferred.sort(key=lambda x: x.name.lower())
        matched_optional.sort(key=lambda x: x.name.lower())
        missing_optional.sort(key=lambda x: x.name.lower())
        matched_unknown.sort(key=lambda x: x.name.lower())
        missing_unknown.sort(key=lambda x: x.name.lower())
        extra.sort(key=lambda x: x.name.lower())
                
        stats = MatchStatistics(
            total_required=len(matched_required) + len(missing_required),
            matched_required=len(matched_required),
            total_preferred=len(matched_preferred) + len(missing_preferred),
            matched_preferred=len(matched_preferred),
            total_optional=len(matched_optional) + len(missing_optional),
            matched_optional=len(matched_optional),
            total_unknown=len(matched_unknown) + len(missing_unknown),
            matched_unknown=len(matched_unknown),
            total_candidate_items=len(candidate_map),
            extra_candidate_items=len(extra)
        )
        
        score = self._compute_score(stats)
        
        return SkillMatchResult(
            matched_required=matched_required,
            missing_required=missing_required,
            matched_preferred=matched_preferred,
            missing_preferred=missing_preferred,
            matched_optional=matched_optional,
            missing_optional=missing_optional,
            matched_unknown=matched_unknown,
            missing_unknown=missing_unknown,
            extra_candidate_technologies=extra,
            statistics=stats,
            score=score
        )
        
    def _extract_technodes(self, tech_profile: TechnologyProfile) -> list[TechNode]:
        return (
            tech_profile.languages +
            tech_profile.frameworks +
            tech_profile.libraries +
            tech_profile.databases +
            tech_profile.cloud +
            tech_profile.devops +
            tech_profile.ai_ml +
            tech_profile.testing +
            tech_profile.operating_systems +
            tech_profile.tools
        )
        
    def _get_job_skill_tiers(self, req_profile: RequirementsProfile) -> dict[str, str]:
        tiers = {}
        for skill in req_profile.required_skills:
            tiers[skill.name.lower()] = "REQUIRED"
        for skill in req_profile.preferred_skills:
            tiers[skill.name.lower()] = "PREFERRED"
        for skill in req_profile.optional_skills:
            tiers[skill.name.lower()] = "OPTIONAL"
        for skill in req_profile.unknown_skills:
            tiers[skill.name.lower()] = "UNKNOWN"
        return tiers

    def _compute_score(self, stats: MatchStatistics) -> float:
        total_weight = 0.0
        earned_weight = 0.0
        
        if stats.total_required > 0:
            total_weight += stats.total_required * 1.0
            earned_weight += stats.matched_required * 1.0
            
        if stats.total_preferred > 0:
            total_weight += stats.total_preferred * 0.5
            earned_weight += stats.matched_preferred * 0.5
            
        if stats.total_optional > 0:
            total_weight += stats.total_optional * 0.2
            earned_weight += stats.matched_optional * 0.2
            
        if stats.total_unknown > 0:
            total_weight += stats.total_unknown * 0.1
            earned_weight += stats.matched_unknown * 0.1
            
        if total_weight == 0.0:
            return 1.0 if stats.total_candidate_items > 0 else 0.0
            
        return round(earned_weight / total_weight, 4)
