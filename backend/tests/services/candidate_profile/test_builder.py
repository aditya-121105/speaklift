import pytest
from pydantic import ValidationError
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.schemas.contact_schema import ContactInfo
from app.ai.nlp.schemas.skill_schema import SkillSet, SkillEntry
from app.ai.nlp.schemas.education_schema import EducationRecord
from app.ai.nlp.schemas.experience_schema import ExperienceRecord
from app.ai.nlp.schemas.project_schema import ProjectRecord
from app.ai.nlp.schemas.certification_schema import CertificationRecord

from app.services.candidate_profile.builder import CandidateProfileBuilder
from app.services.candidate_profile.schemas.career import CareerStage
from app.services.candidate_profile.schemas.career_position import CareerPosition
from app.services.candidate_profile.schemas.academic_degree import AcademicDegree
from app.services.candidate_profile.schemas.candidate_certification import CandidateCertification
from app.services.candidate_profile.schemas.candidate_project import CandidateProject


def create_dummy_entities() -> ExtractedEntities:
    return ExtractedEntities(
        contact=ContactInfo(
            full_name="John Doe",
            email="john@example.com",
            phone="123",
            location="NY",
            linkedin_url="https://linkedin",
            github_url="https://github",
            portfolio_url=None,
            leetcode_url=None,
            hackerrank_url=None,
            kaggle_url=None
        ),
        skills=SkillSet(
            skills=[
                SkillEntry(normalized_name="Python", raw_text="python", category="Language", confidence=1.0, source_section="skills"),
            ],
            technologies=[
                SkillEntry(normalized_name="React", raw_text="react", category="Framework", confidence=1.0, source_section="skills"),
            ]
        ),
        education=[
            EducationRecord(
                degree="Master of Science",
                field_of_study="CS",
                institution="MIT",
                start_year=2020,
                graduation_year=2022,
                raw_text="...",
                is_current=False,
                confidence=1.0
            ),
            EducationRecord(
                degree="PhD Candidate",
                field_of_study="AI",
                institution="Stanford",
                start_year=2023,
                graduation_year=None,
                raw_text="...",
                is_current=True,
                confidence=1.0
            )
        ],
        experience=[
            ExperienceRecord(
                job_title="Software Engineer Intern",
                company="Tech A",
                employment_type="Internship",
                start_date="Jan 2020",
                end_date="May 2020",
                is_current=False,
                duration_months=5,
                technologies_used=["Python"],
                raw_text="...",
                confidence=1.0
            ),
            ExperienceRecord(
                job_title="Senior Dev",
                company="Tech B",
                employment_type="Full-time",
                start_date="Jun 2020",
                end_date="Present",
                is_current=True,
                duration_months=40,
                technologies_used=["Python", "React"],
                raw_text="...",
                confidence=1.0
            )
        ],
        projects=[
            ProjectRecord(
                name="Proj X",
                description="desc",
                technologies=["React"],
                skills=[],
                start_date="2021",
                end_date="2022",
                raw_text="...",
                confidence=1.0
            )
        ],
        certifications=[
            CertificationRecord(
                name="AWS Certified",
                issuing_organization="AWS",
                issue_date="2021",
                confidence=1.0,
                raw_text="..."
            )
        ],
        source_filename="test.pdf",
        pipeline_version="1.0",
        processing_time_ms=100,
        document_language="en",
        model_version="1.0"
    )

def test_builder_identity():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert profile.identity.full_name == "John Doe"
    assert profile.identity.contact.email == "john@example.com"
    assert profile.identity.social.github == "https://github"

def test_builder_career():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert profile.career.total_months_experience == 45
    assert profile.career.internship_months == 5
    assert profile.career.career_stage == CareerStage.ASSOCIATE
    assert profile.career.current_role == "Senior Dev"
    assert profile.career.most_recent_employer == "Tech B"
    
    assert len(profile.career.positions) == 2
    assert isinstance(profile.career.positions[0], CareerPosition)
    assert profile.career.positions[0].company == "Tech A"
    assert profile.career.positions[0].employment_type == "Internship"

def test_career_position_immutability():
    position = CareerPosition(
        job_title="Dev",
        company="Tech",
        employment_type="Full-time",
        location=None,
        start_date="2020",
        end_date="2021",
        is_current=False,
        duration_months=12,
        description="Coding",
        technologies_used=["Python"]
    )
    
    with pytest.raises(ValidationError):
        position.job_title = "Lead Dev"

def test_builder_education():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert profile.education.highest_qualification == "Phd"
    assert profile.education.is_currently_studying is True
    assert profile.education.latest_institution == "Stanford"
    
    assert len(profile.education.degrees) == 2
    assert isinstance(profile.education.degrees[0], AcademicDegree)
    assert profile.education.degrees[0].institution == "MIT"
    
    assert len(profile.education.certifications) == 1
    assert isinstance(profile.education.certifications[0], CandidateCertification)
    assert profile.education.certifications[0].issuing_organization == "AWS"

def test_builder_projects_and_certifications():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert len(profile.projects) == 1
    assert isinstance(profile.projects[0], CandidateProject)
    assert profile.projects[0].name == "Proj X"
    
    assert len(profile.certifications) == 1
    assert isinstance(profile.certifications[0], CandidateCertification)
    assert profile.certifications[0].name == "AWS Certified"

def test_new_schemas_immutability():
    degree = AcademicDegree(
        degree="BSc", field_of_study="CS", institution="MIT", graduation_year=None
    )
    with pytest.raises(ValidationError):
        degree.degree = "MSc"
        
    cert = CandidateCertification(
        name="Cert"
    )
    with pytest.raises(ValidationError):
        cert.name = "Other"
        
    proj = CandidateProject(
        name="Proj", description="Desc", technologies=[], skills=[]
    )
    with pytest.raises(ValidationError):
        proj.name = "Other"

def test_builder_technology():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert len(profile.technology.languages) == 1
    python_node = profile.technology.languages[0]
    assert python_node.name == "Python"
    assert python_node.years_applied == 3.8  # 45 months / 12 = 3.75 -> 3.8
    assert python_node.source_count == 2
    
    assert len(profile.technology.frameworks) == 1
    react_node = profile.technology.frameworks[0]
    assert react_node.name == "React"
    assert react_node.source_count == 2

def test_builder_metadata():
    entities = create_dummy_entities()
    builder = CandidateProfileBuilder()
    profile = builder.build(entities)
    
    assert profile.metadata.average_confidence == 1.0
    assert profile.metadata.pipeline_version == "1.0"
