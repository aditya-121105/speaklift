import pytest
from unittest.mock import MagicMock
from app.services.interview_context.builder import InterviewContextBuilder
from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.matching.schemas.match_result import MatchResult
from app.models.interview_session import InterviewSession
from app.services.interview_context.schemas.interview_context import InterviewContext
from app.shared.enums import ExperienceLevel
from pydantic import ValidationError

def test_interview_context_builder_success():
    candidate = MagicMock(spec=CandidateProfile)
    job = MagicMock(spec=JobProfile)
    matching = MagicMock(spec=MatchResult)
    session = MagicMock(spec=InterviewSession)
    session.role = "Backend Developer"
    session.experience_level = ExperienceLevel.MID
    session.duration_minutes = 60
    
    context = InterviewContextBuilder.build(
        candidate_profile=candidate,
        job_profile=job,
        match_result=matching,
        interview_session=session
    )
    
    assert isinstance(context, InterviewContext)
    assert context.candidate == candidate
    assert context.job == job
    assert context.matching == matching
    assert context.configuration.role == "Backend Developer"
    assert context.configuration.experience_level == ExperienceLevel.MID
    assert context.configuration.duration_minutes == 60

def test_interview_context_builder_missing_input():
    candidate = MagicMock(spec=CandidateProfile)
    job = MagicMock(spec=JobProfile)
    matching = MagicMock(spec=MatchResult)
    session = MagicMock(spec=InterviewSession)
    session.role = "Backend Developer"
    session.experience_level = ExperienceLevel.MID
    session.duration_minutes = 60
    
    with pytest.raises(ValueError):
        InterviewContextBuilder.build(
            candidate_profile=candidate,
            job_profile=job,
            match_result=matching,
            interview_session=None
        )
    with pytest.raises(ValueError):
        InterviewContextBuilder.build(
            candidate_profile=None,
            job_profile=job,
            match_result=matching,
            interview_session=session
        )

def test_interview_context_immutability():
    candidate = MagicMock(spec=CandidateProfile)
    job = MagicMock(spec=JobProfile)
    matching = MagicMock(spec=MatchResult)
    session = MagicMock(spec=InterviewSession)
    session.role = "Backend Developer"
    session.experience_level = ExperienceLevel.MID
    session.duration_minutes = 60
    
    context = InterviewContextBuilder.build(
        candidate_profile=candidate,
        job_profile=job,
        match_result=matching,
        interview_session=session
    )
    
    with pytest.raises(ValidationError):
        context.candidate = MagicMock(spec=CandidateProfile)
