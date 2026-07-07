import pytest
from pydantic import ValidationError
from app.services.matching.schemas.match_statistics import MatchStatistics

def test_match_statistics_immutability():
    stats = MatchStatistics(
        total_required=5,
        matched_required=3,
        total_preferred=2,
        matched_preferred=1,
        total_optional=1,
        matched_optional=0,
        total_unknown=0,
        matched_unknown=0,
        total_candidate_items=10,
        extra_candidate_items=6
    )
    
    with pytest.raises(ValidationError):
        stats.total_required = 10
        
def test_match_statistics_equality():
    stats1 = MatchStatistics(
        total_required=5,
        matched_required=3,
        total_preferred=2,
        matched_preferred=1,
        total_optional=1,
        matched_optional=0,
        total_unknown=0,
        matched_unknown=0,
        total_candidate_items=10,
        extra_candidate_items=6
    )
    
    stats2 = MatchStatistics(
        total_required=5,
        matched_required=3,
        total_preferred=2,
        matched_preferred=1,
        total_optional=1,
        matched_optional=0,
        total_unknown=0,
        matched_unknown=0,
        total_candidate_items=10,
        extra_candidate_items=6
    )
    
    assert stats1 == stats2
