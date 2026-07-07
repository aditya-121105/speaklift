import pytest
from unittest.mock import MagicMock
from app.services.matching.engine import MatchingEngine
from app.services.matching.matchers.skill_matcher import SkillMatcher
from app.services.matching.matchers.experience_matcher import ExperienceMatcher
from app.services.matching.matchers.education_matcher import EducationMatcher
from app.services.matching.builder import MatchResultBuilder
from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_result import MatchResult

def test_matching_engine_orchestration():
    mock_skill_matcher = MagicMock(spec=SkillMatcher)
    mock_exp_matcher = MagicMock(spec=ExperienceMatcher)
    mock_edu_matcher = MagicMock(spec=EducationMatcher)
    mock_builder = MagicMock(spec=MatchResultBuilder)
    
    mock_candidate = MagicMock(spec=CandidateProfile)
    mock_job = MagicMock(spec=JobProfile)
    
    mock_skill_result = MagicMock()
    mock_exp_result = MagicMock()
    mock_edu_result = MagicMock()
    mock_final_result = MagicMock(spec=MatchResult)
    
    mock_skill_matcher.match.return_value = mock_skill_result
    mock_exp_matcher.match.return_value = mock_exp_result
    mock_edu_matcher.match.return_value = mock_edu_result
    mock_builder.build.return_value = mock_final_result
    
    engine = MatchingEngine(
        skill_matcher=mock_skill_matcher,
        experience_matcher=mock_exp_matcher,
        education_matcher=mock_edu_matcher,
        result_builder=mock_builder
    )
    
    result = engine.match(mock_candidate, mock_job)
    
    mock_skill_matcher.match.assert_called_once_with(mock_candidate, mock_job)
    mock_exp_matcher.match.assert_called_once_with(mock_candidate, mock_job)
    mock_edu_matcher.match.assert_called_once_with(mock_candidate, mock_job)
    
    mock_builder.build.assert_called_once_with(
        skill_result=mock_skill_result,
        experience_result=mock_exp_result,
        education_result=mock_edu_result
    )
    
    assert result == mock_final_result

def test_matching_engine_failure_propagation():
    mock_skill_matcher = MagicMock(spec=SkillMatcher)
    mock_exp_matcher = MagicMock(spec=ExperienceMatcher)
    mock_edu_matcher = MagicMock(spec=EducationMatcher)
    mock_builder = MagicMock(spec=MatchResultBuilder)
    
    mock_candidate = MagicMock(spec=CandidateProfile)
    mock_job = MagicMock(spec=JobProfile)
    
    mock_skill_matcher.match.side_effect = ValueError("Skill match failed")
    
    engine = MatchingEngine(
        skill_matcher=mock_skill_matcher,
        experience_matcher=mock_exp_matcher,
        education_matcher=mock_edu_matcher,
        result_builder=mock_builder
    )
    
    with pytest.raises(ValueError, match="Skill match failed"):
        engine.match(mock_candidate, mock_job)
