from app.ai.document_processing.schemas import DocumentContent, DocumentSection
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.extractors.skill_extractor import SkillExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext


def test_skill_extractor_normalization_and_taxonomy():
    # Snippet with edge case skills
    # NodeJS -> Node.js
    # ReactJS -> React
    # Tensor Flow -> TensorFlow
    # Postgres -> PostgreSQL
    # Python -> Python (direct taxonomy match)
    raw_text = """
    My skills include Python, NodeJS, ReactJS, Tensor Flow, and Postgres.
    """

    doc = DocumentContent(
        raw_text=raw_text,
        cleaned_text=raw_text,
        source_filename="skills_resume.pdf"
    )

    processor = SpacyProcessor()
    processed = processor.process(doc.cleaned_text)
    
    normalizer = Normalizer()
    normalized_text = normalizer.normalize(processed)

    context = ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=normalized_text,
        metadata={},
        config={}
    )

    extractor = SkillExtractor()
    skill_set = extractor.extract(context)

    # Convert to maps for easy testing
    skills_map = {s.normalized_name: s for s in skill_set.skills}

    # Verify normalization edge cases
    assert "Python" in skills_map
    assert "Node.js" in skills_map
    assert "React" in skills_map
    assert "TensorFlow" in skills_map
    assert "PostgreSQL" in skills_map

    # Check that raw texts are preserved correctly
    assert skills_map["Node.js"].raw_text.lower() == "nodejs"
    assert skills_map["React"].raw_text.lower() == "reactjs"
    assert "tensor" in skills_map["TensorFlow"].raw_text.lower()
    assert skills_map["PostgreSQL"].raw_text.lower() == "postgres"

    # Verify categories (from taxonomy JSON file names)
    assert skills_map["Python"].category == "programming_languages"
    assert skills_map["React"].category == "frameworks"
    assert skills_map["TensorFlow"].category == "libraries"
    assert skills_map["PostgreSQL"].category == "databases"

    # Verify technologies classification (databases is a technology)
    tech_names = {t.normalized_name for t in skill_set.technologies}
    assert "PostgreSQL" in tech_names
    # Python is not under databases, cloud, devops, tools, or operating_systems, so it's not a technology
    assert "Python" in tech_names


def test_skill_extractor_sections_and_confidence():
    # Define sections
    sections = {
        "skills": DocumentSection(
            section_type="skills",
            heading="Technical Skills",
            content="Python, Docker",
            start_char=0,
            end_char=14
        ),
        "experience": DocumentSection(
            section_type="experience",
            heading="Professional Experience",
            content="Developed app using Kubernetes and Python.",
            start_char=15,
            end_char=57
        )
    }

    doc = DocumentContent(
        raw_text="Technical Skills\nPython, Docker\nProfessional Experience\nDeveloped app using Kubernetes and Python.",
        cleaned_text="Technical Skills\nPython, Docker\nProfessional Experience\nDeveloped app using Kubernetes and Python.",
        source_filename="sections.pdf",
        sections=sections
    )

    processor = SpacyProcessor()
    processed = processor.process(doc.cleaned_text)
    
    normalizer = Normalizer()
    normalized_text = normalizer.normalize(processed)

    context = ProcessingContext(
        document=doc,
        processed_document=processed,
        normalized_text=normalized_text,
        metadata={},
        config={}
    )

    extractor = SkillExtractor()
    skill_set = extractor.extract(context)

    skills_map = {s.normalized_name: s for s in skill_set.skills}

    # Verify skills found
    assert "Python" in skills_map
    assert "Docker" in skills_map
    assert "Kubernetes" in skills_map

    # Verify dynamic confidence scoring and source section mapping
    # Python was found in "skills" first, so its source_section is "skills" with confidence 1.0
    assert skills_map["Python"].source_section == "skills"
    assert skills_map["Python"].confidence == 1.0

    # Docker is in skills
    assert skills_map["Docker"].source_section == "skills"
    assert skills_map["Docker"].confidence == 1.0

    # Kubernetes is only in experience
    assert skills_map["Kubernetes"].source_section == "experience"
    assert skills_map["Kubernetes"].confidence == 0.9
