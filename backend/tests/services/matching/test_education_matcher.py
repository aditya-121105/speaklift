import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from app.services.matching.matchers.education_matcher import EducationMatcher

def create_mock_candidate(highest_qual: str | None, degrees: list = None):
    candidate = MagicMock()
    candidate.education.highest_qualification = highest_qual
    candidate.education.degrees = degrees or []
    return candidate

def create_mock_job(min_degree: str | None, degrees: list[str] = None):
    job = MagicMock()
    job.qualification.education.minimum_degree = min_degree
    job.qualification.education.degrees = degrees or []
    return job

def create_mock_degree(degree: str | None, field_of_study: str | None):
    deg = MagicMock()
    deg.degree = degree
    deg.field_of_study = field_of_study
    return deg

def test_education_matcher_exact_qualification():
    matcher = EducationMatcher()
    candidate = create_mock_candidate("Bachelor")
    job = create_mock_job("Bachelor")
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is True
    assert result.score == 1.0
    assert result.statistics.total_required == 1
    assert result.statistics.matched_required == 1

def test_education_matcher_above_minimum_qualification():
    matcher = EducationMatcher()
    candidate = create_mock_candidate("Master")
    job = create_mock_job("Bachelor")
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is True
    assert result.score == 1.0

def test_education_matcher_below_minimum_qualification():
    matcher = EducationMatcher()
    candidate = create_mock_candidate("Associate")
    job = create_mock_job("Bachelor")
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is False
    assert result.score == 0.0

def test_education_matcher_matching_degree_by_name():
    matcher = EducationMatcher()
    deg1 = create_mock_degree("B.S.", "Computer Science")
    candidate = create_mock_candidate("Bachelor", [deg1])
    job = create_mock_job("Bachelor", ["B.S."])
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is True
    assert "B.S." in result.matched_degrees
    assert len(result.missing_degrees) == 0
    assert result.score == 1.0

def test_education_matcher_matching_degree_by_field_of_study():
    matcher = EducationMatcher()
    deg1 = create_mock_degree("B.S.", "Computer Science")
    candidate = create_mock_candidate("Bachelor", [deg1])
    job = create_mock_job("Bachelor", ["Computer Science"])
    
    result = matcher.match(candidate, job)
    
    assert "Computer Science" in result.matched_degrees
    assert result.score == 1.0

def test_education_matcher_missing_degree():
    matcher = EducationMatcher()
    deg1 = create_mock_degree("B.A.", "History")
    candidate = create_mock_candidate("Bachelor", [deg1])
    job = create_mock_job("Bachelor", ["Computer Science"])
    
    result = matcher.match(candidate, job)
    
    assert "Computer Science" in result.missing_degrees
    assert len(result.matched_degrees) == 0
    assert result.score == 0.5  # 1 out of 2 satisfied (minimum degree ok, specific degree missing)

def test_education_matcher_empty_education():
    matcher = EducationMatcher()
    candidate = create_mock_candidate(None)
    job = create_mock_job("Bachelor", ["Computer Science"])
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is False
    assert result.score == 0.0

def test_education_matcher_empty_requirements():
    matcher = EducationMatcher()
    deg1 = create_mock_degree("B.A.", "History")
    candidate = create_mock_candidate("Bachelor", [deg1])
    job = create_mock_job(None, [])
    
    result = matcher.match(candidate, job)
    
    assert result.qualification_satisfied is True
    assert result.score == 1.0
    assert result.statistics.total_required == 0
    
def test_education_matcher_immutability():
    matcher = EducationMatcher()
    candidate = create_mock_candidate("Bachelor")
    job = create_mock_job("Bachelor")
    
    result = matcher.match(candidate, job)
    
    with pytest.raises(ValidationError):
        result.score = 0.5
