import pytest
from app.ai.nlp.extractors.jd.jd_education_extractor import JDEducationExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument
from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType


def _build_context(text: str, sections_dict: dict = None) -> ProcessingContext:
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
        sections=sections
    )
    
    # Split text into sentences naive for testing
    sentences = text.replace('\n', '. ').split('. ')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    proc = ProcessedDocument(
        original_text=text,
        tokens=[], lemmas=[], sentences=sentences, named_entities=[], noun_chunks=[], pos_tags=[]
    )
    
    return ProcessingContext(
        document=doc,
        processed_document=proc,
        normalized_text=text,
        metadata={},
        config={}
    )


def test_bachelor_extraction():
    extractor = JDEducationExtractor()
    text = "Requires a Bachelor's degree."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_degree_level == "BACHELOR"
    assert res[0].field_of_study is None


def test_master_extraction():
    extractor = JDEducationExtractor()
    text = "Master's preferred."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_degree_level == "MASTER"
    assert res[0].field_of_study is None


def test_phd_extraction():
    extractor = JDEducationExtractor()
    text = "PhD or Doctorate required."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_degree_level == "PHD"
    assert res[0].field_of_study is None


def test_indian_degrees():
    extractor = JDEducationExtractor()
    text = "B.Tech in Computer Science or M.Tech in AI."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 2
    degrees = [r.min_degree_level for r in res]
    fields = [r.field_of_study for r in res]
    
    assert "BACHELOR" in degrees
    assert "MASTER" in degrees
    assert "Computer Science" in fields
    assert "AI" in fields


def test_field_of_study_extraction():
    extractor = JDEducationExtractor()
    text = "Bachelor of Science in Information Technology or equivalent."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_degree_level == "BACHELOR"
    assert res[0].field_of_study == "Information Technology"


def test_equivalent_practical_experience():
    extractor = JDEducationExtractor()
    text = "Equivalent practical experience in lieu of a degree is fine."
    res = extractor.extract(_build_context(text))
    
    # "a degree" is generic and doesn't match our specific canonical ones
    # But let's check a more common case:
    text2 = "Bachelor's degree or equivalent practical experience."
    res2 = extractor.extract(_build_context(text2))
    
    # It extracts the Bachelor's degree properly.
    assert len(res2) == 1
    assert res2[0].min_degree_level == "BACHELOR"
    
    # Check if purely equivalent practical experience yields nothing
    text3 = "Needs equivalent practical experience and hard work."
    res3 = extractor.extract(_build_context(text3))
    assert len(res3) == 0


def test_empty_document():
    extractor = JDEducationExtractor()
    res = extractor.extract(_build_context(""))
    assert len(res) == 0
