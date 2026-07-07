import pytest
from pydantic import ValidationError
from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.skill_match_result import SkillMatchResult
from app.services.candidate_profile.schemas.technology import TechNode

def test_skill_match_result_immutability():
    stats = MatchStatistics(
        total_required=1, matched_required=1,
        total_preferred=0, matched_preferred=0,
        total_optional=0, matched_optional=0,
        total_unknown=0, matched_unknown=0,
        total_candidate_items=1, extra_candidate_items=0
    )
    
    node = TechNode(name="Python", years_applied=2.0, last_used_year=2024, source_count=1)
    
    result = SkillMatchResult(
        matched_required=[node],
        missing_required=[],
        matched_preferred=[],
        missing_preferred=[],
        matched_optional=[],
        missing_optional=[],
        matched_unknown=[],
        missing_unknown=[],
        extra_candidate_technologies=[],
        statistics=stats,
        score=1.0
    )
    
    with pytest.raises(ValidationError):
        result.score = 0.5
