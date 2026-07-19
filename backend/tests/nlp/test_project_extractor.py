import pytest
from app.ai.nlp.extractors.project_extractor import ProjectExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext

from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType
from app.ai.nlp.schemas.processed_document import ProcessedDocument

def create_context(text: str) -> ProcessingContext:
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            content = '\n'.join(lines[i+1:])
            break
    else:
        content = text
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
        sections={"projects": DocumentSection(section_type=SectionType.PROJECTS, heading="Projects", content=content, start_char=0, end_char=len(content))},
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

def test_project_extractor_single_project():
    text = """
    Projects
    SpeakLift - AI Interview Platform
    Jan 2026 - Present
    Developed an AI-powered interview platform using Python, FastAPI, and PostgreSQL.
    """
    context = create_context(text)
    
    extractor = ProjectExtractor()
    extractor._taxonomy = {
        "python": ("Python", "languages"),
        "fastapi": ("FastAPI", "frameworks"),
        "postgresql": ("PostgreSQL", "databases")
    }
    extractor._synonyms = {}
    extractor._technology_categories = {"languages", "frameworks", "databases"}
    
    projects = extractor.extract(context)
    assert len(projects) == 1
    p = projects[0]
    assert p.name == "SpeakLift"
    assert "AI Interview Platform" in p.description or "Developed an AI-powered" in p.description
    assert "Jan 2026" in p.start_date
    assert "Present" in p.end_date
    assert set(p.technologies) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(p.skills) == {"Python", "FastAPI", "PostgreSQL"}
    assert p.confidence > 0.8
    assert p.normalized_name == "SpeakLift"

def test_project_extractor_multiple_projects():
    text = """
    Personal Projects
    
    Task Tracker
    2023
    A simple task tracker using React and Node.js.
    
    Weather App
    2024
    Displays weather forecasts using Vue and AWS.
    """
    context = create_context(text)
    
    extractor = ProjectExtractor()
    extractor._taxonomy = {
        "react": ("React", "libraries"),
        "node.js": ("Node.js", "languages"),
        "vue": ("Vue", "libraries"),
        "aws": ("AWS", "cloud")
    }
    extractor._synonyms = {}
    
    projects = extractor.extract(context)
    assert len(projects) == 2
    assert projects[0].name == "Task Tracker"
    assert projects[0].start_date == "2023"
    assert set(projects[0].technologies) == {"React", "Node.js"}
    
    assert projects[1].name == "Weather App"
    assert projects[1].start_date == "2024"
    assert set(projects[1].technologies) == {"Vue", "AWS"}

def test_project_extractor_missing_dates():
    text = """
    Projects
    - E-commerce Website
      Built a scalable e-commerce site using Django.
    """
    context = create_context(text)
    extractor = ProjectExtractor()
    extractor._taxonomy = {"django": ("Django", "frameworks")}
    extractor._synonyms = {}
    
    projects = extractor.extract(context)
    assert len(projects) == 1
    assert projects[0].name == "E-commerce Website"
    assert projects[0].start_date is None
    assert projects[0].end_date is None
    assert set(projects[0].technologies) == {"Django"}
