import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock
from app.services.matching.builder import MatchResultBuilder
from app.services.matching.schemas.match_statistics import MatchStatistics
from app.services.matching.schemas.skill_match_result import SkillMatchResult
from app.services.matching.schemas.experience_match_result import ExperienceMatchResult
from app.services.matching.schemas.education_match_result import EducationMatchResult

def test_match_result_builder_aggregation():
    # Setup mock statistics
    skill_stats = MatchStatistics(
        total_required=5, matched_required=4,
        total_preferred=3, matched_preferred=2,
        total_optional=1, matched_optional=0,
        total_unknown=0, matched_unknown=0,
        total_candidate_items=10, extra_candidate_items=4
    )
    
    exp_stats = MatchStatistics(
        total_required=1, matched_required=1,
        total_preferred=0, matched_preferred=0,
        total_optional=0, matched_optional=0,
        total_unknown=0, matched_unknown=0,
        total_candidate_items=1, extra_candidate_items=0
    )
    
    edu_stats = MatchStatistics(
        total_required=2, matched_required=1,
        total_preferred=0, matched_preferred=0,
        total_optional=0, matched_optional=0,
        total_unknown=0, matched_unknown=0,
        total_candidate_items=2, extra_candidate_items=0
    )

    # Setup mock results (using MagicMock to bypass frozen Pydantic models for testing)
    skill_result = MagicMock(spec=SkillMatchResult)
    skill_result.statistics = skill_stats
    skill_result.score = 0.8
    
    exp_result = MagicMock(spec=ExperienceMatchResult)
    exp_result.statistics = exp_stats
    exp_result.score = 1.0
    
    edu_result = MagicMock(spec=EducationMatchResult)
    edu_result.statistics = edu_stats
    edu_result.score = 0.5
    
    # Build
    builder = MatchResultBuilder()
    result = builder.build(skill_result, exp_result, edu_result)
    
    # Assert Score Aggregation
    assert result.score == round((0.8 + 1.0 + 0.5) / 3.0, 4)
    
    # Assert Stats Aggregation
    assert result.statistics.total_required == 5 + 1 + 2
    assert result.statistics.matched_required == 4 + 1 + 1
    assert result.statistics.total_preferred == 3 + 0 + 0
    assert result.statistics.matched_preferred == 2 + 0 + 0
    assert result.statistics.total_optional == 1 + 0 + 0
    assert result.statistics.matched_optional == 0 + 0 + 0
    assert result.statistics.total_candidate_items == 10 + 1 + 2
    assert result.statistics.extra_candidate_items == 4 + 0 + 0

def test_match_result_immutability():
    builder = MatchResultBuilder()
    
    # Use dummy valid results that can be instantiated
    stats = MatchStatistics(
        total_required=0, matched_required=0, total_preferred=0, matched_preferred=0,
        total_optional=0, matched_optional=0, total_unknown=0, matched_unknown=0,
        total_candidate_items=0, extra_candidate_items=0
    )
    
    skill_result = SkillMatchResult(
        matched_required=[], missing_required=[], matched_preferred=[],
        missing_preferred=[], matched_optional=[], missing_optional=[],
        matched_unknown=[], missing_unknown=[], extra_candidate_skills=[],
        extra_candidate_technologies=[],
        statistics=stats, score=0.0
    )
    
    exp_result = ExperienceMatchResult(
        candidate_months=0, required_minimum_months=None, required_maximum_months=None,
        is_satisfied=True, deficit_months=0, surplus_months=0, statistics=stats, score=0.0
    )
    
    edu_result = EducationMatchResult(
        highest_qualification=None, required_qualification=None, qualification_satisfied=True,
        matched_degrees=[], missing_degrees=[], statistics=stats, score=0.0
    )
    
    result = builder.build(skill_result, exp_result, edu_result)
    
    with pytest.raises(ValidationError):
        result.score = 1.0
