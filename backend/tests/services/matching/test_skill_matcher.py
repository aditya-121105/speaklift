from unittest.mock import MagicMock

from app.services.candidate_profile.schemas.technology import TechNode, TechnologyProfile as CandTechProfile
from app.services.job_profile.schemas.requirements import RequirementsProfile, SkillRequirement
from app.services.job_profile.schemas.technology import TechnologyProfile as JobTechProfile

from app.services.matching.matchers.skill_matcher import SkillMatcher

def get_empty_cand_tech():
    return CandTechProfile(
        languages=[], frameworks=[], libraries=[], databases=[], cloud=[],
        devops=[], ai_ml=[], testing=[], operating_systems=[], tools=[]
    )

def get_empty_job_tech():
    return JobTechProfile(
        languages=[], frameworks=[], libraries=[], databases=[], cloud=[],
        devops=[], ai_ml=[], testing=[], operating_systems=[], tools=[]
    )

def test_skill_matcher_exact_match():
    cand_tech = get_empty_cand_tech()
    cand_tech.languages.append(TechNode(name="Python", years_applied=3.0, last_used_year=2024, source_count=1))
    
    job_tech = get_empty_job_tech()
    job_tech.languages.append(TechNode(name="Python", years_applied=0.0, last_used_year=None, source_count=1))
    
    req_profile = RequirementsProfile(
        required_skills=[SkillRequirement(name="Python")],
        preferred_skills=[],
        optional_skills=[],
        unknown_skills=[],
        responsibilities=[]
    )
    
    cand = MagicMock()
    cand.technology = cand_tech
    
    job = MagicMock()
    job.technology = job_tech
    job.requirements = req_profile
    
    matcher = SkillMatcher()
    result = matcher.match(cand, job)
    
    assert len(result.matched_required) == 1
    assert result.matched_required[0].name == "Python"
    assert len(result.missing_required) == 0
    assert result.score == 1.0
    assert result.statistics.total_required == 1
    assert result.statistics.matched_required == 1

def test_skill_matcher_missing_required():
    cand_tech = get_empty_cand_tech()
    job_tech = get_empty_job_tech()
    job_tech.languages.append(TechNode(name="Python", years_applied=0.0, last_used_year=None, source_count=1))
    
    req_profile = RequirementsProfile(
        required_skills=[SkillRequirement(name="Python")],
        preferred_skills=[],
        optional_skills=[],
        unknown_skills=[],
        responsibilities=[]
    )
    
    cand = MagicMock()
    cand.technology = cand_tech
    
    job = MagicMock()
    job.technology = job_tech
    job.requirements = req_profile
    
    matcher = SkillMatcher()
    result = matcher.match(cand, job)
    
    assert len(result.matched_required) == 0
    assert len(result.missing_required) == 1
    assert result.missing_required[0].name == "Python"
    assert result.score == 0.0
    assert result.statistics.total_required == 1
    assert result.statistics.matched_required == 0

def test_skill_matcher_extra_candidate_skills():
    cand_tech = get_empty_cand_tech()
    cand_tech.languages.append(TechNode(name="Rust", years_applied=1.0, last_used_year=None, source_count=1))
    
    job_tech = get_empty_job_tech()
    req_profile = RequirementsProfile(
        required_skills=[],
        preferred_skills=[],
        optional_skills=[],
        unknown_skills=[],
        responsibilities=[]
    )
    
    cand = MagicMock()
    cand.technology = cand_tech
    
    job = MagicMock()
    job.technology = job_tech
    job.requirements = req_profile
    
    matcher = SkillMatcher()
    result = matcher.match(cand, job)
    
    assert len(result.extra_candidate_technologies) == 1
    assert result.extra_candidate_technologies[0].name == "Rust"
    assert result.score == 1.0 # No requirements means perfect match

def test_skill_matcher_partial_match():
    cand_tech = get_empty_cand_tech()
    cand_tech.languages.append(TechNode(name="Python", years_applied=3.0, last_used_year=None, source_count=1))
    cand_tech.frameworks.append(TechNode(name="React", years_applied=1.0, last_used_year=None, source_count=1))
    
    job_tech = get_empty_job_tech()
    job_tech.languages.append(TechNode(name="Python", years_applied=0.0, last_used_year=None, source_count=1))
    job_tech.frameworks.append(TechNode(name="Django", years_applied=0.0, last_used_year=None, source_count=1))
    job_tech.tools.append(TechNode(name="Docker", years_applied=0.0, last_used_year=None, source_count=1))
    
    req_profile = RequirementsProfile(
        required_skills=[SkillRequirement(name="Python"), SkillRequirement(name="Django")],
        preferred_skills=[SkillRequirement(name="Docker")],
        optional_skills=[],
        unknown_skills=[],
        responsibilities=[]
    )
    
    cand = MagicMock()
    cand.technology = cand_tech
    
    job = MagicMock()
    job.technology = job_tech
    job.requirements = req_profile
    
    matcher = SkillMatcher()
    result = matcher.match(cand, job)
    
    assert len(result.matched_required) == 1
    assert result.matched_required[0].name == "Python"
    
    assert len(result.missing_required) == 1
    assert result.missing_required[0].name == "Django"
    
    assert len(result.missing_preferred) == 1
    assert result.missing_preferred[0].name == "Docker"
    
    assert len(result.extra_candidate_technologies) == 1
    assert result.extra_candidate_technologies[0].name == "React"
    
    # Python (Req) = 1.0 earned
    # Django (Req) = 0.0 earned (total 2.0 for req)
    # Docker (Pref) = 0.0 earned (total 0.5 for pref)
    # Earned: 1.0. Total: 2.5
    # Score: 1.0 / 2.5 = 0.4
    assert result.score == 0.4000
    
    stats = result.statistics
    assert stats.total_required == 2
    assert stats.matched_required == 1
    assert stats.total_preferred == 1
    assert stats.matched_preferred == 0
