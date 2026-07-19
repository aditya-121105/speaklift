import pytest
from app.ai.nlp.extractors.jd.jd_skill_extractor import JDSkillExtractor
from app.ai.nlp.schemas.jd.jd_skill_schema import RequirementTier
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument
from app.ai.document_processing.schemas import DocumentContent, DocumentSection, SectionType


@pytest.fixture
def extractor(monkeypatch):
    # Mock taxonomy and synonyms directly to avoid loading files
    def mock_taxonomy(*args):
        return {
            "python": ("Python", "language"),
            "react": ("React", "framework"),
            "docker": ("Docker", "tools"),
            "aws": ("AWS", "cloud"),
            "kafka": ("Kafka", "tools"),
            "terraform": ("Terraform", "tools"),
            "fastapi": ("FastAPI", "framework")
        }
    
    def mock_synonyms(*args):
        return {
            r"\btensor flow\b": "TensorFlow",
            r"\bnodejs\b": "Node.js",
            r"\bpostgres\b": "PostgreSQL",
            r"\breactjs\b": "React"
        }
        
    import app.ai.nlp.resources.taxonomy_resource as tax
    monkeypatch.setattr(tax.TaxonomyResourceManager, "get_taxonomy", mock_taxonomy)
    monkeypatch.setattr(tax.TaxonomyResourceManager, "get_synonyms", mock_synonyms)
    
    return JDSkillExtractor(taxonomy_dir=None)


def _build_context(text: str, sections_dict: dict = None, tokens: list = None) -> ProcessingContext:
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
        tokens=tokens or text.lower().replace(".", "").replace(":", "").split(),
        lemmas=[],
        sentences=[],
        named_entities=[],
        noun_chunks=[],
        pos_tags=[]
    )
    
    return ProcessingContext(
        document=doc,
        processed_document=proc,
        normalized_text=text,
        metadata={},
        config={}
    )


def test_required_tier(extractor):
    text = "Must have Python. Minimum experience with Docker. Required: AWS"
    context = _build_context(text)
    
    skills = extractor.extract(context)
    
    python = next(s for s in skills if s.name == "Python")
    assert python.requirement_tier == RequirementTier.REQUIRED
    
    docker = next(s for s in skills if s.name == "Docker")
    assert docker.requirement_tier == RequirementTier.REQUIRED

    aws = next(s for s in skills if s.name == "AWS")
    assert aws.requirement_tier == RequirementTier.REQUIRED


def test_preferred_tier(extractor):
    text = "Preferred: React. Ideally you have Kubernetes. Strongly desired: AWS."
    # We add kubernetes to tokens but it's not in our mock taxonomy, so we only test React and AWS
    context = _build_context(text, tokens=["preferred", "react", "ideally", "aws"])
    
    skills = extractor.extract(context)
    
    react = next(s for s in skills if s.name == "React")
    assert react.requirement_tier == RequirementTier.PREFERRED
    
    aws = next(s for s in skills if s.name == "AWS")
    assert aws.requirement_tier == RequirementTier.PREFERRED


def test_optional_tier(extractor):
    text = "Nice to have Kafka. Bonus if you know Terraform."
    context = _build_context(text, tokens=["kafka", "terraform"])
    
    skills = extractor.extract(context)
    
    kafka = next(s for s in skills if s.name == "Kafka")
    assert kafka.requirement_tier == RequirementTier.OPTIONAL
    
    terraform = next(s for s in skills if s.name == "Terraform")
    assert terraform.requirement_tier == RequirementTier.OPTIONAL


def test_unknown_tier(extractor):
    text = "Experience with FastAPI"
    context = _build_context(text, tokens=["fastapi"])
    
    skills = extractor.extract(context)
    
    fastapi = next(s for s in skills if s.name == "FastAPI")
    assert fastapi.requirement_tier == RequirementTier.UNKNOWN


def test_taxonomy_normalization(extractor):
    text = "Must have Python."
    context = _build_context(text, tokens=["python"])
    skills = extractor.extract(context)
    assert skills[0].name == "Python"
    assert skills[0].confidence == 1.0


def test_synonym_resolution(extractor):
    text = "Must have NodeJS and ReactJS. Bonus: tensor flow."
    # we need to simulate the multi-word candidate for tensor flow
    tokens = ["nodejs", "reactjs"]
    context = _build_context(text, tokens=tokens)
    # mock noun chunks for tensor flow
    new_proc = context.processed_document.model_copy(
        update={"noun_chunks": ["tensor flow"]}
    )
    context = context.model_copy(update={"processed_document": new_proc})
    
    skills = extractor.extract(context)
    
    assert len(skills) == 3
    names = {s.name for s in skills}
    assert names == {"Node.js", "React", "TensorFlow"}
    
    # Synonyms have 0.9 confidence
    node = next(s for s in skills if s.name == "Node.js")
    assert node.confidence == 0.9
    assert node.requirement_tier == RequirementTier.REQUIRED


def test_duplicate_removal(extractor):
    text = "Must have Python. Nice to have Python."
    context = _build_context(text, tokens=["python"])
    
    skills = extractor.extract(context)
    
    assert len(skills) == 1
    # REQUIRED tier has higher priority than OPTIONAL
    assert skills[0].requirement_tier == RequirementTier.REQUIRED


def test_confidence_filtering(extractor):
    text = "Must have Python."
    context = _build_context(text, tokens=["python"])
    
    # We monkeypatch the extractor to return low confidence for Python
    def mock_calc(candidate, norm, is_syn):
        return 0.4
    
    extractor._calculate_confidence = mock_calc
    
    skills = extractor.extract(context)
    assert len(skills) == 0


def test_section_aware_extraction(extractor):
    text = ""
    sections_dict = {
        "reqs": (SectionType.REQUIREMENTS, "Requirements", "Python and Docker"),
        "pref": (SectionType.OTHER, "Preferred Qualifications", "React"),
        "nice": (SectionType.OTHER, "Nice to have", "Kafka")
    }
    
    context = _build_context(text, sections_dict, tokens=["python", "docker", "react", "kafka"])
    
    skills = extractor.extract(context)
    
    assert len(skills) == 4
    python = next(s for s in skills if s.name == "Python")
    assert python.requirement_tier == RequirementTier.REQUIRED
    
    react = next(s for s in skills if s.name == "React")
    assert react.requirement_tier == RequirementTier.PREFERRED
    
    kafka = next(s for s in skills if s.name == "Kafka")
    assert kafka.requirement_tier == RequirementTier.OPTIONAL


def test_empty_document(extractor):
    context = _build_context("", tokens=[])
    skills = extractor.extract(context)
    assert len(skills) == 0
