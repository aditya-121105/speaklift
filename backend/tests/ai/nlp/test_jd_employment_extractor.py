from app.ai.nlp.extractors.jd.jd_employment_extractor import JDEmploymentExtractor
from app.ai.nlp.schemas.jd.jd_employment_schema import EmploymentType, RemoteType
from app.ai.nlp.schemas.jd.salary_range import SalaryPeriod
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument
from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType


def _build_context(text: str, metadata: dict = None, doc_meta: dict = None, sections_dict: dict = None) -> ProcessingContext:
    if sections_dict is None:
        sections_dict = {}
        
    sections = {}
    for key, (sec_type, heading, content) in sections_dict.items():
        sections[key] = DocumentSection(
            section_type=sec_type,
            heading=heading,
            content=content,
            start_char=0,
            end_char=len(content)
        )
        
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
        sections=sections,
        extraction_metadata=doc_meta or {}
    )
    
    proc = ProcessedDocument(
        original_text=text,
        tokens=[], lemmas=[], sentences=[], named_entities=[], noun_chunks=[], pos_tags=[]
    )
    
    return ProcessingContext(
        document=doc,
        processed_document=proc,
        normalized_text=text,
        metadata=metadata or {},
        config={}
    )


def test_job_title_extraction_metadata():
    extractor = JDEmploymentExtractor()
    context = _build_context("Some text", doc_meta={"job_title": "Senior Python Developer"})
    res = extractor.extract(context)
    assert res.job_title == "Senior Python Developer"
    assert res.confidence == 1.0


def test_job_title_extraction_structured():
    extractor = JDEmploymentExtractor()
    context = _build_context("Title: Backend Engineer\nWe are looking for...")
    res = extractor.extract(context)
    assert res.job_title == "Backend Engineer"


def test_employment_type():
    extractor = JDEmploymentExtractor()
    
    res = extractor.extract(_build_context("We need a full-time dev"))
    assert res.employment_type == EmploymentType.FULL_TIME
    
    res = extractor.extract(_build_context("Part time role"))
    assert res.employment_type == EmploymentType.PART_TIME
    
    res = extractor.extract(_build_context("Looking for a contractor"))
    assert res.employment_type == EmploymentType.CONTRACT
    
    res = extractor.extract(_build_context("Summer internship"))
    assert res.employment_type == EmploymentType.INTERNSHIP
    
    res = extractor.extract(_build_context("Just a normal job"))
    assert res.employment_type == EmploymentType.UNKNOWN


def test_remote_type():
    extractor = JDEmploymentExtractor()
    
    res = extractor.extract(_build_context("This is a remote position."))
    assert res.remote_type == RemoteType.REMOTE
    
    res = extractor.extract(_build_context("Hybrid schedule, 3 days a week."))
    assert res.remote_type == RemoteType.HYBRID
    
    res = extractor.extract(_build_context("Must work on-site."))
    assert res.remote_type == RemoteType.ON_SITE
    
    res = extractor.extract(_build_context("No mention of location type"))
    assert res.remote_type == RemoteType.UNKNOWN


def test_salary_normalization_and_ranges():
    extractor = JDEmploymentExtractor()
    
    # Range with LPA
    res = extractor.extract(_build_context("Salary: ₹12–18 LPA"))
    assert res.salary is not None
    assert res.salary.minimum == 1200000.0
    assert res.salary.maximum == 1800000.0
    assert res.salary.currency == "INR"
    assert res.salary.period == SalaryPeriod.YEAR
    
    # Range with USD and annually
    res = extractor.extract(_build_context("Pay is $120k-$150k annually"))
    assert res.salary is not None
    assert res.salary.minimum == 120000.0
    assert res.salary.maximum == 150000.0
    assert res.salary.currency == "USD"
    assert res.salary.period == SalaryPeriod.YEAR

    # Monthly EUR
    res = extractor.extract(_build_context("€5000/month"))
    assert res.salary.minimum == 5000.0
    assert res.salary.maximum is None
    assert res.salary.currency == "EUR"
    assert res.salary.period == SalaryPeriod.MONTH
    
    # Hourly
    res = extractor.extract(_build_context("Pays $60/hour"))
    assert res.salary.minimum == 60.0
    assert res.salary.period == SalaryPeriod.HOUR


def test_missing_salary_period():
    extractor = JDEmploymentExtractor()
    # Missing period should still extract with lower confidence
    res = extractor.extract(_build_context("Salary is $120k - $150k"))
    assert res.salary is not None
    assert res.salary.minimum == 120000.0
    assert res.salary.maximum == 150000.0
    assert res.salary.currency == "USD"
    assert res.salary.period is None
    assert res.salary.confidence < 1.0


def test_missing_currency():
    extractor = JDEmploymentExtractor()
    res = extractor.extract(_build_context("Salary: 120k-150k annually"))
    assert res.salary is not None
    assert res.salary.minimum == 120000.0
    assert res.salary.maximum == 150000.0
    assert res.salary.currency is None
    assert res.salary.period == SalaryPeriod.YEAR
    assert res.salary.confidence < 1.0


def test_empty_jd():
    extractor = JDEmploymentExtractor()
    res = extractor.extract(_build_context(""))
    assert res.job_title is None
    assert res.employment_type == EmploymentType.UNKNOWN
    assert res.remote_type == RemoteType.UNKNOWN
    assert res.salary is None
    assert res.location is None
    assert res.confidence == 0.8
