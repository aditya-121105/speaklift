from app.ai.nlp.validators.entity_validator import EntityValidator
from app.ai.nlp.validators.duplicate import DuplicateValidator
from app.ai.nlp.validators.salary_range import SalaryRangeValidator
from app.ai.nlp.validators.experience_range import ExperienceRangeValidator
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.jd_employment_schema import JDEmploymentRecord, EmploymentType, RemoteType
from app.ai.nlp.schemas.jd.jd_experience_schema import JDExperienceRecord
from app.ai.nlp.schemas.jd.salary_range import SalaryRange, SalaryPeriod
from app.ai.nlp.schemas.jd.jd_company_schema import JDCompanyRecord

def _build_entities() -> ExtractedJDEntities:
    employment = JDEmploymentRecord(
        job_title="Engineer",
        employment_type=EmploymentType.FULL_TIME,
        remote_type=RemoteType.REMOTE,
        location="Remote",
        # Invalid salary: min > max
        salary=SalaryRange(minimum=150, maximum=100, currency="USD", period=SalaryPeriod.YEAR, confidence=1.0),
        confidence=1.0
    )
    return ExtractedJDEntities(
        employment=employment,
        skills=[],
        experience=[
            JDExperienceRecord(min_years=2, max_years=5, domain="Python", confidence=1.0),
            JDExperienceRecord(min_years=2, max_years=5, domain="Python", confidence=0.8), # Duplicate
            JDExperienceRecord(min_years=-1, max_years=5, domain="Java", confidence=1.0) # Invalid range
        ],
        education=[],
        responsibilities=[],
        company=JDCompanyRecord(company_name="Test Co", industry=None, company_size=None, culture_keywords=[], website=None, confidence=1.0),
        source_filename="test.txt",
        pipeline_version="1.0",
        processing_time_ms=100,
        document_language="en",
        model_version="1.0"
    )

def test_entity_validator_jd_chain():
    # Construct the validator with JD-specific chain
    validator = EntityValidator(validators=[
        DuplicateValidator(),
        SalaryRangeValidator(),
        ExperienceRangeValidator()
    ])
    
    entities = _build_entities()
    validated = validator.validate_entities(entities)
    
    # Check immutable output (different object)
    assert id(validated) != id(entities)
    
    # Salary should be stripped due to min > max
    assert validated.employment.salary is None
    
    # Experience should have exactly 1 valid unique record
    assert len(validated.experience) == 1
    assert validated.experience[0].domain == "Python"
    assert validated.experience[0].confidence == 1.0 # Kept highest confidence
