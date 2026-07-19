from app.ai.nlp.validators.experience_range import ExperienceRangeValidator
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.jd_employment_schema import JDEmploymentRecord, EmploymentType, RemoteType
from app.ai.nlp.schemas.jd.jd_experience_schema import JDExperienceRecord
from app.ai.nlp.schemas.jd.jd_company_schema import JDCompanyRecord

def _build_entities(exp_records: list[JDExperienceRecord]) -> ExtractedJDEntities:
    employment = JDEmploymentRecord(
        job_title="Engineer",
        employment_type=EmploymentType.FULL_TIME,
        remote_type=RemoteType.REMOTE,
        location="Remote",
        salary=None,
        confidence=1.0
    )
    return ExtractedJDEntities(
        employment=employment,
        skills=[],
        experience=exp_records,
        education=[],
        responsibilities=[],
        company=JDCompanyRecord(company_name="Test Co", industry=None, company_size=None, culture_keywords=[], website=None, confidence=1.0),
        source_filename="test.txt",
        pipeline_version="1.0",
        processing_time_ms=100,
        document_language="en",
        model_version="1.0"
    )

def test_valid_range():
    validator = ExperienceRangeValidator()
    exp = JDExperienceRecord(min_years=2, max_years=5, domain="Python", confidence=1.0)
    entities = _build_entities([exp])
    validated = validator.validate(entities)
    assert len(validated.experience) == 1

def test_invalid_range():
    validator = ExperienceRangeValidator()
    # min > max
    exp = JDExperienceRecord(min_years=5, max_years=2, domain="Python", confidence=1.0)
    entities = _build_entities([exp])
    validated = validator.validate(entities)
    assert len(validated.experience) == 0

def test_negative_years():
    validator = ExperienceRangeValidator()
    exp = JDExperienceRecord(min_years=-1, max_years=5, domain="Python", confidence=1.0)
    entities = _build_entities([exp])
    validated = validator.validate(entities)
    assert len(validated.experience) == 0

def test_unrealistic_years():
    validator = ExperienceRangeValidator()
    exp = JDExperienceRecord(min_years=2, max_years=150, domain="Python", confidence=1.0)
    entities = _build_entities([exp])
    validated = validator.validate(entities)
    assert len(validated.experience) == 0

def test_missing_max():
    validator = ExperienceRangeValidator()
    exp = JDExperienceRecord(min_years=3, max_years=None, domain="Python", confidence=1.0)
    entities = _build_entities([exp])
    validated = validator.validate(entities)
    assert len(validated.experience) == 1
