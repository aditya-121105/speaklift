import pytest
from pydantic import ValidationError

from app.ai.nlp.schemas.jd import (
    SalaryRange,
    SalaryPeriod,
    JDSkillRecord,
    RequirementTier,
    JDExperienceRecord,
    JDEducationRecord,
    JDEmploymentRecord,
    JDResponsibilityRecord,
    JDCompanyRecord,
    ExtractedJDEntities,
)
from app.ai.nlp.extractors.jd import get_jd_extractor_registry
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.document_processing.schemas import DocumentContent


def test_schema_immutability():
    """Verify that JD schemas are frozen/immutable."""
    salary = SalaryRange(minimum=100, maximum=150, currency="USD", period=SalaryPeriod.YEAR, confidence=1.0)
    
    with pytest.raises(ValidationError):
        salary.minimum = 200

    skill = JDSkillRecord(name="Python", requirement_tier=RequirementTier.REQUIRED, confidence=1.0)
    with pytest.raises(ValidationError):
        skill.name = "Java"

    exp = JDExperienceRecord(min_years=3, max_years=5, domain="Backend", confidence=0.9)
    with pytest.raises(ValidationError):
        exp.min_years = 4

    edu = JDEducationRecord(min_degree_level="Bachelors", field_of_study="CS", confidence=0.8)
    with pytest.raises(ValidationError):
        edu.min_degree_level = "Masters"

    emp = JDEmploymentRecord(job_title="Dev", location="Remote", remote_type="Full", salary=salary, confidence=0.95)
    with pytest.raises(ValidationError):
        emp.job_title = "Senior Dev"

    resp = JDResponsibilityRecord(description="Code", confidence=0.99)
    with pytest.raises(ValidationError):
        resp.description = "Test"

    comp = JDCompanyRecord(company_name="Tech", industry="IT", company_size="10-50", culture_keywords=[], website=None, confidence=0.9)
    with pytest.raises(ValidationError):
        comp.company_name = "NewTech"


def test_registry_wiring():
    """Verify the JD extractor registry initializes correctly with valid domains."""
    registry = get_jd_extractor_registry()
    assert registry.schema_cls == ExtractedJDEntities
    
    valid_domains = registry._valid_domains
    expected_domains = {
        "employment", "skills", "experience", "education",
        "responsibilities", "company", "source_filename",
        "pipeline_version", "processing_time_ms", "document_language", "model_version"
    }
    assert valid_domains == expected_domains


def test_pipeline_accepts_jd_registry():
    """Verify the NLPPipeline can process a document using the empty JD registry."""
    processor = SpacyProcessor()
    normalizer = Normalizer()
    registry = get_jd_extractor_registry()
    
    pipeline = NLPPipeline(processor=processor, normalizer=normalizer, registry=registry)
    
    doc = DocumentContent(
        raw_text="Sample JD text",
        cleaned_text="Sample JD text",
        source_filename="test_jd.pdf"
    )
    
    result = pipeline.run(doc)
    
    assert isinstance(result, ExtractedJDEntities)
    assert result.source_filename == "test_jd.pdf"
    assert result.pipeline_version == "C.5.2"
    # Verify defaults are constructed correctly for empty registry
    assert result.employment.job_title is None
    assert result.company.company_name is None
    assert result.skills == []
    assert result.experience == []


def test_package_exports():
    """Verify package __init__ exports everything correctly."""
    import app.ai.nlp.schemas.jd as jd_schemas
    
    assert hasattr(jd_schemas, "SalaryRange")
    assert hasattr(jd_schemas, "ExtractedJDEntities")
    assert hasattr(jd_schemas, "RequirementTier")
