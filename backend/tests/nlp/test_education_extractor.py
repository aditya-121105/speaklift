import pytest
from app.ai.document_processing.schemas import DocumentContent, DocumentSection
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument
from app.ai.nlp.extractors.education_extractor import EducationExtractor


def create_context(text: str, sections: dict = None):
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
        sections=sections or {},
        source_filename="test.pdf"
    )
    processed = ProcessedDocument(
        original_text=text,
        tokens=[],
        lemmas=[],
        pos_tags=[],
        noun_chunks=[],
        named_entities=[],
        sentences=[]
    )
    return ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=text,
        metadata={},
        config={}
    )


def test_education_extractor_single_degree():
    text = "B.S. in Computer Science\nStanford University\n2018 - 2022\nCGPA: 3.9"
    context = create_context(text)
    
    extractor = EducationExtractor()
    records = extractor.extract(context)
    
    assert len(records) == 1
    record = records[0]
    
    assert record.degree == "B.S."
    assert record.institution == "Stanford University"
    assert record.field_of_study == "Computer Science"
    assert record.start_year == 2018
    assert record.graduation_year == 2022
    assert record.cgpa == 3.9
    assert record.is_current is False


def test_education_extractor_multiple_degrees():
    text = "M.S. in Data Science\nMassachusetts Institute of Technology\n2022 - 2024\n\nB.Tech in Mechanical Engineering\nIndian Institute of Technology Bombay\n2018 - 2022\n75.5%"
    context = create_context(text)
    
    extractor = EducationExtractor()
    records = extractor.extract(context)
    
    assert len(records) == 2
    
    ms_record = records[0]
    assert ms_record.degree == "M.S."
    assert ms_record.institution == "Massachusetts Institute of Technology"
    assert ms_record.field_of_study == "Data Science"
    assert ms_record.graduation_year == 2024
    
    btech_record = records[1]
    assert btech_record.degree == "B.Tech"
    assert btech_record.institution == "Indian Institute of Technology Bombay"
    assert btech_record.field_of_study == "Mechanical Engineering"
    assert btech_record.graduation_year == 2022
    assert btech_record.percentage == 75.5


def test_education_extractor_ongoing_education():
    text = "Ph.D. in Artificial Intelligence\nHarvard University\n2023 - Present"
    context = create_context(text)
    
    extractor = EducationExtractor()
    records = extractor.extract(context)
    
    assert len(records) == 1
    record = records[0]
    
    assert record.degree == "Ph.D."
    assert record.institution == "Harvard University"
    assert record.start_year == 2023
    assert record.is_current is True
    assert record.graduation_year is None


def test_education_extractor_in_section():
    text = "Some random text before.\nB.S. in Computer Science\nUniversity of California, Los Angeles\n2020\n"
    sections = {
        "education": DocumentSection(
            section_type="education",
            heading="Education",
            content=text,
            start_char=0,
            end_char=len(text)
        )
    }
    context = create_context("Full text...", sections)
    
    extractor = EducationExtractor()
    records = extractor.extract(context)
    
    assert len(records) == 1
    assert records[0].degree == "B.S."
    assert records[0].institution == "University of California, Los Angeles"
    assert records[0].graduation_year == 2020
    # Higher confidence because it was found in the education section
    assert records[0].confidence >= 0.5
