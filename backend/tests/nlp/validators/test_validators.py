import pytest
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.schemas.contact_schema import ContactInfo
from app.ai.nlp.schemas.skill_schema import SkillSet, SkillEntry
from app.ai.nlp.schemas.education_schema import EducationRecord
from app.ai.nlp.schemas.experience_schema import ExperienceRecord
from app.ai.nlp.schemas.project_schema import ProjectRecord
from app.ai.nlp.schemas.certification_schema import CertificationRecord

from app.ai.nlp.validators.duplicate import DuplicateValidator
from app.ai.nlp.validators.chronology import ChronologyValidator
from app.ai.nlp.validators.confidence import ConfidenceValidator
from app.ai.nlp.validators.url import URLValidator
from app.ai.nlp.validators.entity_validator import EntityValidator


def create_dummy_entities() -> ExtractedEntities:
    return ExtractedEntities(
        contact=ContactInfo(
            full_name="John Doe",
            email="john@example.com",
            phone=None,
            location=None,
            linkedin_url="https://linkedin.com/in/johndoe",
            github_url="invalid-url",
            portfolio_url=None,
            leetcode_url="https://github.com/johndoe",  # invalid domain for leetcode
            hackerrank_url=None,
            kaggle_url=None
        ),
        skills=SkillSet(
            skills=[
                SkillEntry(normalized_name="Python", raw_text="python", category="language", confidence=1.5, source_section="skills"),
                SkillEntry(normalized_name="Python", raw_text="Python", category="language", confidence=0.9, source_section="skills"),
            ],
            technologies=[
                SkillEntry(normalized_name="React", raw_text="React", category="framework", confidence=-0.5, source_section="skills"),
                SkillEntry(normalized_name="React", raw_text="react.js", category="framework", confidence=0.8, source_section="skills"),
            ]
        ),
        education=[
            EducationRecord(
                degree="B.S.",
                field_of_study="CS",
                institution="MIT",
                start_year=2020,
                graduation_year=2018,  # invalid chronology
                raw_text="...",
                confidence=1.2
            ),
            EducationRecord(
                degree="M.S.",
                field_of_study="CS",
                institution="MIT",
                start_year=2018,
                graduation_year=2020,  # valid chronology
                raw_text="...",
                confidence=0.8
            )
        ],
        experience=[
            ExperienceRecord(
                job_title="Dev",
                company="Tech",
                start_date="Jan 2020",
                end_date="Dec 2019", # invalid chronology
                raw_text="...",
                confidence=0.9
            ),
            ExperienceRecord(
                job_title="Dev 2",
                company="Tech",
                start_date="Jan 2020",
                end_date="Present", # valid chronology
                raw_text="...",
                confidence=0.9
            )
        ],
        projects=[
            ProjectRecord(name="Proj A", description="", technologies=[], skills=[], raw_text="...", normalized_name="Proj A"),
            ProjectRecord(name="proj a", description="", technologies=[], skills=[], raw_text="...", normalized_name="Proj A"), # duplicate
        ],
        certifications=[
            CertificationRecord(name="Cert X", raw_text="...", normalized_name="Cert X", credential_url="http://invalid url"),
            CertificationRecord(name="cert x", raw_text="...", normalized_name="Cert X", credential_url="https://verify.org/123"), # duplicate
        ],
        source_filename="test.pdf",
        pipeline_version="1.0",
        processing_time_ms=100,
        document_language="en",
        model_version="1.0"
    )


def test_duplicate_validator():
    entities = create_dummy_entities()
    validator = DuplicateValidator()
    result = validator.validate(entities)

    assert len(result.skills.skills) == 1
    assert len(result.skills.technologies) == 1
    assert len(result.projects) == 1
    assert len(result.certifications) == 1


def test_chronology_validator():
    entities = create_dummy_entities()
    validator = ChronologyValidator()
    result = validator.validate(entities)

    assert len(result.education) == 1
    assert result.education[0].degree == "M.S."

    assert len(result.experience) == 1
    assert result.experience[0].job_title == "Dev 2"


def test_confidence_validator():
    entities = create_dummy_entities()
    validator = ConfidenceValidator()
    result = validator.validate(entities)

    assert result.skills.skills[0].confidence == 1.0
    assert result.skills.technologies[0].confidence == 0.0
    assert result.education[0].confidence == 1.0


def test_url_validator():
    entities = create_dummy_entities()
    validator = URLValidator()
    result = validator.validate(entities)

    assert result.contact.linkedin_url == "https://linkedin.com/in/johndoe"
    assert result.contact.github_url is None
    assert result.contact.leetcode_url is None
    assert result.certifications[0].credential_url is None


def test_entity_validator_orchestrator():
    entities = create_dummy_entities()
    validator = EntityValidator()
    result = validator.validate_entities(entities)

    # Duplicates removed
    assert len(result.skills.skills) == 1
    assert len(result.projects) == 1
    
    # Chronology validated
    assert len(result.education) == 1
    assert len(result.experience) == 1
    
    # Confidence clamped
    assert result.skills.skills[0].confidence == 1.0
    
    # URLs validated
    assert result.contact.github_url is None
    assert result.contact.leetcode_url is None
