import pytest
from unittest.mock import MagicMock
from app.services.interview_context.schemas.interview_context import InterviewContext
from app.services.interview_planner.planner import InterviewPlanner
from app.services.interview_planner.schemas.interview_plan import InterviewPlan
from app.services.interview_planner.schemas.interview_phase import InterviewPhase
from app.services.interview_planner.schemas.interview_objective import InterviewObjective
from app.services.candidate_profile.schemas.profile import CandidateProfile
from app.services.job_profile.schemas.profile import JobProfile
from app.services.job_profile.schemas.requirements import RequirementsProfile, SkillRequirement
from app.services.candidate_profile.schemas.candidate_project import CandidateProject
from app.services.interview_context.schemas.interview_configuration import InterviewConfiguration
from app.shared.enums import ExperienceLevel
from pydantic import ValidationError

def test_interview_planner_success():
    context = MagicMock(spec=InterviewContext)
    
    candidate = MagicMock(spec=CandidateProfile)
    project = MagicMock(spec=CandidateProject)
    project.name = "My Project"
    candidate.projects = [project]
    
    job = MagicMock(spec=JobProfile)
    job.requirements = MagicMock(spec=RequirementsProfile)
    skill = MagicMock(spec=SkillRequirement)
    skill.name = "Python"
    job.requirements.required_skills = [skill]
    
    config = MagicMock(spec=InterviewConfiguration)
    config.duration_minutes = 60
    config.role = "Backend"
    config.experience_level = ExperienceLevel.MID
    
    context.candidate = candidate
    context.job = job
    context.configuration = config
    
    plan = InterviewPlanner.build(context)
    
    assert isinstance(plan, InterviewPlan)
    assert plan.total_duration_minutes == 60
    assert len(plan.phases) == 5
    
    intro = plan.phases[0]
    assert intro.name == "Introduction"
    assert intro.ordering == 1
    assert intro.allocated_minutes == 6  # 10% of 60
    
    projects = plan.phases[1]
    assert projects.name == "Projects"
    assert projects.ordering == 2
    assert projects.allocated_minutes == 15  # 25% of 60
    assert len(projects.objectives) == 1
    assert projects.objectives[0].name == "My Project"
    
    tech = plan.phases[2]
    assert tech.name == "Technical"
    assert tech.ordering == 3
    assert tech.allocated_minutes == 27  # 45% of 60
    assert len(tech.objectives) == 1
    assert tech.objectives[0].name == "Python"
    
    behavioral = plan.phases[3]
    assert behavioral.name == "Behavioral"
    assert behavioral.ordering == 4
    assert behavioral.allocated_minutes == 9  # 15% of 60
    
    closing = plan.phases[4]
    assert closing.name == "Closing"
    assert closing.ordering == 5
    assert closing.allocated_minutes == 3  # Remaining

def test_immutability():
    obj = InterviewObjective(name="Test", description="Test", priority=5)
    with pytest.raises(ValidationError):
        obj.name = "Mutated"
        
    phase = InterviewPhase(name="Test", description="Test", ordering=1, allocated_minutes=10)
    with pytest.raises(ValidationError):
        phase.allocated_minutes = 20
        
    plan = InterviewPlan(total_duration_minutes=60, role="Backend", experience_level=ExperienceLevel.MID)
    with pytest.raises(ValidationError):
        plan.total_duration_minutes = 30
