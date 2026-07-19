import pytest
from app.ai.document_processing.schemas import DocumentContent, DocumentSection
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument, NamedEntity
from app.ai.nlp.extractors.experience_extractor import ExperienceExtractor


def create_context(text: str):
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
        sections={},
        source_filename="test.pdf"
    )
    processed = ProcessedDocument(
        original_text=text,
        tokens=[],
        lemmas=[],
        pos_tags=[],
        noun_chunks=[],
        named_entities=[
            NamedEntity(text="Google", label="ORG", start_char=0, end_char=6),
            NamedEntity(text="San Francisco", label="GPE", start_char=0, end_char=13)
        ],
        sentences=[]
    )
    return ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=text,
        metadata={},
        config={}
    )


def test_experience_extractor_full_time():
    text = "Senior Software Engineer\nGoogle\nSan Francisco\nJan 2020 - Dec 2022\n- Built scalable APIs in Python\n- Managed PostgreSQL databases"
    context = create_context(text)
    
    extractor = ExperienceExtractor()
    extractor._taxonomy = {
        "python": ("Python", "languages"),
        "postgresql": ("PostgreSQL", "databases")
    }
    extractor._synonyms = {}
    extractor._technology_categories = {"languages", "databases"}
    records = extractor.extract(context)
    
    assert len(records) == 1
    record = records[0]
    
    assert record.job_title == "Senior Software Engineer"
    assert record.company == "Google"
    assert record.location == "San Francisco"
    assert record.start_date == "Jan 2020"
    assert record.end_date == "Dec 2022"
    assert record.is_current is False
    assert record.duration_months == 35
    assert "Python" in record.technologies_used
    assert "PostgreSQL" in record.technologies_used


def test_experience_extractor_internship_and_present():
    text = "Data Scientist Intern\nAcme Corp\nRemote\n2023 - Present\n• Analyzed big data using Pandas and TensorFlow"
    context = create_context(text)
    
    extractor = ExperienceExtractor()
    extractor._taxonomy = {
        "pandas": ("Pandas", "tools"),
        "tensorflow": ("TensorFlow", "tools")
    }
    extractor._synonyms = {}
    extractor._technology_categories = {"tools"}
    records = extractor.extract(context)
    
    assert len(records) == 1
    record = records[0]
    
    assert record.job_title == "Data Scientist Intern" # internship is in employment_type
    assert record.employment_type == "Internship"
    assert record.location == "Remote"
    assert record.start_date == "2023"
    assert record.is_current is True
    assert "Pandas" in record.technologies_used
    assert "TensorFlow" in record.technologies_used


def test_experience_extractor_multiple_companies():
    text = "Frontend Developer\nFacebook Inc.\n2018 - 2019\n- Used React and Redux\n\nBackend Developer\nAmazon Inc.\n2019 - 2020\n- AWS, Node.js"
    context = create_context(text)
    
    extractor = ExperienceExtractor()
    extractor._taxonomy = {
        "react": ("React", "libraries"),
        "aws": ("AWS", "cloud"),
        "node.js": ("Node.js", "languages")
    }
    extractor._synonyms = {}
    extractor._technology_categories = {"libraries", "cloud", "languages"}
    records = extractor.extract(context)
    
    assert len(records) == 2
    
    fb = records[0]
    assert fb.job_title == "Frontend Developer"
    assert fb.company == "Facebook Inc."
    assert "React" in fb.technologies_used
    
    amzn = records[1]
    assert amzn.job_title == "Backend Developer"
    assert amzn.company == "Amazon Inc."
    assert "AWS" in amzn.technologies_used
    assert "Node.js" in amzn.technologies_used


def test_experience_extractor_hybrid_and_technologies():
    text = "Project Manager (Hybrid)\nMicrosoft\nMay 2021 - Jun 2023\n- Led Azure migration\n- Coordinated with C# teams"
    context = create_context(text)
    
    extractor = ExperienceExtractor()
    extractor._taxonomy = {
        "azure": ("Azure", "cloud"),
        "c#": ("C#", "languages")
    }
    extractor._synonyms = {}
    extractor._technology_categories = {"cloud", "languages"}
    records = extractor.extract(context)
    
    assert len(records) == 1
    record = records[0]
    
    assert record.job_title == "Project Manager"
    assert record.location == "Hybrid"
    assert "Azure" in record.technologies_used
    assert "C#" in record.technologies_used
