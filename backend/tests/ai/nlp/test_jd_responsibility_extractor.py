import pytest
from app.ai.nlp.extractors.jd.jd_responsibility_extractor import JDResponsibilityExtractor
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
    
    proc = ProcessedDocument(
        original_text=text,
        tokens=[], lemmas=[], sentences=[], named_entities=[], noun_chunks=[], pos_tags=[]
    )
    
    return ProcessingContext(
        document=doc,
        processed_document=proc,
        normalized_text=text,
        metadata={},
        config={}
    )


def test_action_verb_extraction():
    extractor = JDResponsibilityExtractor()
    text = "Build REST APIs"
    
    context = _build_context(text, sections_dict={
        "reqs": (SectionType.RESPONSIBILITIES, "Responsibilities", "- Build REST APIs\n- Design scalable systems")
    })
    
    res = extractor.extract(context)
    
    assert len(res) == 2
    descriptions = [r.description for r in res]
    assert "Build REST APIs" in descriptions
    assert "Design scalable systems" in descriptions
    assert res[0].confidence == 1.0


def test_responsibility_noun_phrase_extraction():
    extractor = JDResponsibilityExtractor()
    
    context = _build_context("", sections_dict={
        "resp": (SectionType.RESPONSIBILITIES, "Responsibilities", "- Architecture design\n- Performance optimization\n- 5 years of Python")
    })
    
    res = extractor.extract(context)
    
    # 5 years of Python should be filtered out
    assert len(res) == 2
    descriptions = [r.description for r in res]
    assert "Architecture design" in descriptions
    assert "Performance optimization" in descriptions
    # Noun phrases should be slightly lower confidence than explicit action verbs, or 0.9
    assert res[0].confidence == 0.9


def test_deduplication():
    extractor = JDResponsibilityExtractor()
    
    context = _build_context("", sections_dict={
        "resp": (SectionType.RESPONSIBILITIES, "Responsibilities", "- Build REST APIs\n- Build REST APIs")
    })
    
    res = extractor.extract(context)
    assert len(res) == 1
    assert res[0].description == "Build REST APIs"


def test_mixed_sections():
    extractor = JDResponsibilityExtractor()
    
    context = _build_context("", sections_dict={
        "resp": (SectionType.RESPONSIBILITIES, "Responsibilities", "- Build REST APIs"),
        "reqs": (SectionType.REQUIREMENTS, "Requirements", "- 3 years of Python\n- Deploy infrastructure")
    })
    
    res = extractor.extract(context)
    
    assert len(res) == 2
    descriptions = [r.description for r in res]
    assert "Build REST APIs" in descriptions
    assert "Deploy infrastructure" in descriptions


def test_empty_document():
    extractor = JDResponsibilityExtractor()
    res = extractor.extract(_build_context(""))
    assert len(res) == 0
