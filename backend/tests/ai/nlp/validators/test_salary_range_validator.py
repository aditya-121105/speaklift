from app.ai.nlp.validators.salary_range import SalaryRangeValidator
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.jd_employment_schema import JDEmploymentRecord, EmploymentType, RemoteType
from app.ai.nlp.schemas.jd.salary_range import SalaryRange, SalaryPeriod
from app.ai.nlp.schemas.jd.jd_company_schema import JDCompanyRecord

def _build_entities(salary: SalaryRange | None) -> ExtractedJDEntities:
    employment = JDEmploymentRecord(
        job_title="Engineer",
        employment_type=EmploymentType.FULL_TIME,
        remote_type=RemoteType.REMOTE,
        location="Remote",
        salary=salary,
        confidence=1.0
    )
    return ExtractedJDEntities(
        employment=employment,
        skills=[],
        experience=[],
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
    validator = SalaryRangeValidator()
    salary = SalaryRange(minimum=100, maximum=150, currency="USD", period=SalaryPeriod.YEAR, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is not None
    assert validated.employment.salary.minimum == 100

def test_invalid_min_max():
    validator = SalaryRangeValidator()
    # min > max
    salary = SalaryRange(minimum=150, maximum=100, currency="USD", period=SalaryPeriod.YEAR, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is None

def test_negative_salary():
    validator = SalaryRangeValidator()
    # min < 0
    salary = SalaryRange(minimum=-10, maximum=100, currency="USD", period=SalaryPeriod.YEAR, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is None

def test_missing_currency():
    validator = SalaryRangeValidator()
    # currency None should be fine structurally (handled as valid)
    salary = SalaryRange(minimum=100, maximum=150, currency=None, period=SalaryPeriod.YEAR, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is not None

def test_missing_period():
    validator = SalaryRangeValidator()
    # period None should be fine structurally
    salary = SalaryRange(minimum=100, maximum=150, currency="USD", period=None, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is not None

def test_invalid_currency():
    validator = SalaryRangeValidator()
    salary = SalaryRange(minimum=100, maximum=150, currency="INVALID", period=SalaryPeriod.YEAR, confidence=1.0)
    entities = _build_entities(salary)
    validated = validator.validate(entities)
    assert validated.employment.salary is None
