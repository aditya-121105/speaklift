import pytest
from datetime import datetime
from pydantic import ValidationError

from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.jd_skill_schema import JDSkillRecord, RequirementTier
from app.ai.nlp.schemas.jd.jd_employment_schema import JDEmploymentRecord, EmploymentType as NLP_EmploymentType, RemoteType as NLP_RemoteType
from app.ai.nlp.schemas.jd.salary_range import SalaryRange, SalaryPeriod as NLP_SalaryPeriod
from app.ai.nlp.schemas.jd.jd_experience_schema import JDExperienceRecord
from app.ai.nlp.schemas.jd.jd_education_schema import JDEducationRecord
from app.ai.nlp.schemas.jd.jd_responsibility_schema import JDResponsibilityRecord
from app.ai.nlp.schemas.jd.jd_company_schema import JDCompanyRecord

from app.services.job_profile.builder import JobProfileBuilder
from app.services.job_profile.schemas import RemoteType, EmploymentType, SalaryPeriod

def test_job_profile_builder():
    entities = ExtractedJDEntities(
        employment=JDEmploymentRecord(
            job_title="Software Engineer",
            location="New York",
            remote_type=NLP_RemoteType.HYBRID,
            employment_type=NLP_EmploymentType.FULL_TIME,
            salary=SalaryRange(minimum=100, maximum=150, currency="USD", period=NLP_SalaryPeriod.YEAR, confidence=1.0),
            confidence=1.0
        ),
        skills=[
            JDSkillRecord(name="Python", normalized_name="python", requirement_tier=RequirementTier.REQUIRED, confidence=1.0),
            JDSkillRecord(name="React", normalized_name="react", requirement_tier=RequirementTier.PREFERRED, confidence=1.0),
            JDSkillRecord(name="AWS", normalized_name="aws", requirement_tier=RequirementTier.OPTIONAL, confidence=1.0),
            JDSkillRecord(name="Unknown", normalized_name="unknown", requirement_tier=RequirementTier.UNKNOWN, confidence=1.0),
        ],
        experience=[
            JDExperienceRecord(min_years=3, max_years=5, domain="Backend", confidence=1.0)
        ],
        education=[
            JDEducationRecord(min_degree_level="Bachelors", field_of_study="Computer Science", confidence=1.0)
        ],
        responsibilities=[
            JDResponsibilityRecord(description="Build things", confidence=1.0)
        ],
        company=JDCompanyRecord(company_name="Acme Corp", industry="Tech", company_size="10-50", culture_keywords=["fast"], website=None, confidence=1.0),
        source_filename="test.pdf",
        pipeline_version="1.0",
        processing_time_ms=100,
        document_language="en",
        model_version="1.0"
    )

    # We need to initialize the taxonomy manager
    from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager
    TaxonomyResourceManager.load_if_needed()
    
    builder = JobProfileBuilder()
    profile = builder.build(entities)

    # Identity
    assert profile.identity.job_title == "Software Engineer"
    assert profile.identity.remote_type == RemoteType.HYBRID

    # Requirements
    assert len(profile.requirements.required_skills) == 1
    assert profile.requirements.required_skills[0].name == "Python"
    assert len(profile.requirements.preferred_skills) == 1
    assert profile.requirements.preferred_skills[0].name == "React"
    assert len(profile.requirements.optional_skills) == 1
    assert len(profile.requirements.unknown_skills) == 1
    assert len(profile.requirements.responsibilities) == 1
    assert profile.requirements.responsibilities[0].description == "Build things"

    # Technology
    assert len(profile.technology.languages) == 1
    assert profile.technology.languages[0].name == "Python"
    assert profile.technology.languages[0].years_applied == 0.0
    assert len(profile.technology.frameworks) == 1
    assert len(profile.technology.cloud) == 1

    # Qualification
    assert profile.qualification.experience.min_years == 3
    assert profile.qualification.experience.max_years == 5
    assert profile.qualification.education.minimum_degree == "Bachelors"
    assert profile.qualification.education.degrees == ["Bachelors"]

    # Employment
    assert profile.employment.employment_type == EmploymentType.FULL_TIME
    assert profile.employment.salary.minimum == 100
    assert profile.employment.salary.maximum == 150
    assert profile.employment.salary.currency == "USD"
    assert profile.employment.salary.period == SalaryPeriod.YEAR

    # Company
    assert profile.company.name == "Acme Corp"
    assert profile.company.culture_keywords == ["fast"]

    # Metadata
    assert profile.metadata.source_filename == "test.pdf"
    assert not hasattr(profile.metadata, "processing_time_ms")

    # Immutability
    with pytest.raises(ValidationError):
        profile.identity.job_title = "Other"

def test_builder_empty_entities():
    # ExtractedJDEntities allows lists to be empty, but requires the lists.
    # Employment and company are allowed to be None by default in some cases,
    # but let's initialize them as expected by the NLP defaults.
    entities = ExtractedJDEntities(
        employment=JDEmploymentRecord(job_title=None, location=None, remote_type=None, employment_type=None, salary=None, confidence=0.0),
        skills=[],
        experience=[],
        education=[],
        responsibilities=[],
        company=JDCompanyRecord(company_name=None, industry=None, company_size=None, culture_keywords=[], website=None, confidence=0.0),
        source_filename="empty.txt",
        pipeline_version="1.0",
        processing_time_ms=10,
        document_language="en",
        model_version="1.0"
    )
    
    builder = JobProfileBuilder()
    profile = builder.build(entities)
    
    # Assert graceful fallbacks
    assert profile.company.name is None
    assert profile.company.industry is None
    assert profile.identity.job_title is None
    assert profile.identity.remote_type is None
    assert profile.employment.employment_type is None
    assert profile.employment.salary is None
    
    assert len(profile.requirements.required_skills) == 0
    assert len(profile.requirements.preferred_skills) == 0
    assert len(profile.requirements.optional_skills) == 0
    assert len(profile.requirements.unknown_skills) == 0
    assert len(profile.requirements.responsibilities) == 0
    
    assert len(profile.technology.languages) == 0
    assert len(profile.technology.tools) == 0
    
    assert profile.qualification.experience.min_years is None
    assert profile.qualification.experience.max_years is None
    assert profile.qualification.education.minimum_degree is None
    assert len(profile.qualification.education.degrees) == 0


def test_builder_taxonomy_fallback():
    # Intentionally use a skill name that is absolutely not in taxonomy
    entities = ExtractedJDEntities(
        employment=JDEmploymentRecord(job_title=None, location=None, remote_type=None, employment_type=None, salary=None, confidence=0.0),
        skills=[
            JDSkillRecord(name="SuperSecretTech9000", normalized_name="supersecrettech9000", requirement_tier=RequirementTier.REQUIRED, confidence=1.0)
        ],
        experience=[],
        education=[],
        responsibilities=[],
        company=JDCompanyRecord(company_name=None, industry=None, company_size=None, culture_keywords=[], website=None, confidence=0.0),
        source_filename="fallback.txt",
        pipeline_version="1.0",
        processing_time_ms=10,
        document_language="en",
        model_version="1.0"
    )
    
    from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager
    TaxonomyResourceManager.load_if_needed()
    
    builder = JobProfileBuilder()
    profile = builder.build(entities)
    
    # Should fall back into tools
    assert len(profile.technology.tools) == 1
    assert profile.technology.tools[0].name == "SuperSecretTech9000"
    
    # Ensure it's not in languages or frameworks
    assert len(profile.technology.languages) == 0
    assert len(profile.technology.frameworks) == 0


def test_builder_enum_fallback():
    # The NLP layer strictly types JDEmploymentRecord fields to Enum | None using 
    # NLP_RemoteType and NLP_EmploymentType. Pydantic validation guarantees that 
    # ExtractedJDEntities cannot contain an invalid enum string literal at runtime.
    # Therefore, the try/except block in the builder is technically defensive against 
    # future schema drifts, but unreachable under the current strictly-typed AI DTO.
    # We will test that a valid AI enum maps perfectly to the Business Enum.
    
    entities = ExtractedJDEntities(
        employment=JDEmploymentRecord(
            job_title="Software Engineer", 
            location="Remote", 
            remote_type=NLP_RemoteType.ON_SITE, 
            employment_type=NLP_EmploymentType.INTERNSHIP, 
            salary=None, 
            confidence=1.0
        ),
        skills=[],
        experience=[],
        education=[],
        responsibilities=[],
        company=JDCompanyRecord(company_name=None, industry=None, company_size=None, culture_keywords=[], website=None, confidence=0.0),
        source_filename="fallback.txt",
        pipeline_version="1.0",
        processing_time_ms=10,
        document_language="en",
        model_version="1.0"
    )
    
    builder = JobProfileBuilder()
    profile = builder.build(entities)
    
    assert profile.identity.remote_type == RemoteType.ON_SITE
    assert profile.employment.employment_type == EmploymentType.INTERNSHIP

