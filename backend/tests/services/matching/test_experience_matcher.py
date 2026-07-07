import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from app.services.matching.matchers.experience_matcher import ExperienceMatcher

def create_mock_candidate(months: int):
    candidate = MagicMock()
    candidate.career.total_months_experience = months
    return candidate

def create_mock_job(min_y: int | None, max_y: int | None):
    job = MagicMock()
    job.qualification.experience.min_years = min_y
    job.qualification.experience.max_years = max_y
    return job

def test_experience_matcher_below_minimum():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(24) # 2 years
    job = create_mock_job(3, None) # 3 years minimum
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is False
    assert result.deficit_months == 12
    assert result.surplus_months == 0
    assert result.score == round(24 / 36, 4)
    assert result.statistics.total_required == 1
    assert result.statistics.matched_required == 0

def test_experience_matcher_exact_minimum():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(36)
    job = create_mock_job(3, None)
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is True
    assert result.deficit_months == 0
    assert result.surplus_months == 0
    assert result.score == 1.0
    assert result.statistics.total_required == 1
    assert result.statistics.matched_required == 1

def test_experience_matcher_above_minimum():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(48) # 4 years
    job = create_mock_job(3, None)
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is True
    assert result.deficit_months == 0
    assert result.surplus_months == 12
    assert result.score == 1.0

def test_experience_matcher_exceeds_maximum():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(120) # 10 years
    job = create_mock_job(3, 5) # 3 to 5 years
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is False
    assert result.deficit_months == 0
    assert result.surplus_months == 60 # 120 - 60
    assert result.score == round(60 / 120, 4)

def test_experience_matcher_no_maximum_specified():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(240) # 20 years
    job = create_mock_job(5, None)
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is True
    assert result.surplus_months == 180

def test_experience_matcher_zero_experience():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(0)
    job = create_mock_job(1, None)
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is False
    assert result.deficit_months == 12
    assert result.score == 0.0

def test_experience_matcher_empty_requirements():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(36)
    job = create_mock_job(None, None)
    
    result = matcher.match(candidate, job)
    
    assert result.is_satisfied is True
    assert result.score == 1.0
    assert result.statistics.total_required == 0
    assert result.statistics.matched_required == 0
    
def test_experience_match_result_immutability():
    matcher = ExperienceMatcher()
    candidate = create_mock_candidate(36)
    job = create_mock_job(3, None)
    
    result = matcher.match(candidate, job)
    
    with pytest.raises(ValidationError):
        result.score = 0.5
