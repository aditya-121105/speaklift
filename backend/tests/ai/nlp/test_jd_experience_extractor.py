import pytest
from app.ai.nlp.extractors.jd.jd_experience_extractor import JDExperienceExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.processed_document import ProcessedDocument
from app.ai.document_processing.schemas import DocumentContent


@pytest.fixture
def extractor(monkeypatch):
    def mock_taxonomy(*args):
        return {
            "python": ("Python", "language"),
            "backend development": ("Backend", "domain"),
            "react": ("React", "framework")
        }
    
    def mock_synonyms(*args):
        return {
            r"\bnodejs\b": "Node.js"
        }
        
    import app.ai.nlp.resources.taxonomy_resource as tax
    monkeypatch.setattr(tax.TaxonomyResourceManager, "get_taxonomy", mock_taxonomy)
    monkeypatch.setattr(tax.TaxonomyResourceManager, "get_synonyms", mock_synonyms)
    
    return JDExperienceExtractor(taxonomy_dir=None)


def _build_context(text: str) -> ProcessingContext:
    doc = DocumentContent(
        raw_text=text,
        cleaned_text=text,
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


def test_explicit_ranges(extractor):
    text = "We need 2-5 years of backend development."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 2
    assert res[0].max_years == 5
    assert res[0].domain == "Backend"
    assert res[0].confidence == 1.0


def test_open_ended_ranges(extractor):
    text = "Requires 3+ years of Python."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 3
    assert res[0].max_years is None
    assert res[0].domain == "Python"
    assert res[0].confidence == 1.0


def test_freshers(extractor):
    text = "Freshers welcome to apply."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 0
    assert res[0].max_years == 0
    assert res[0].domain is None


def test_technology_association(extractor):
    # Tests synonyms
    text = "2 years of nodejs experience."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 2
    assert res[0].domain == "Node.js"
    assert res[0].confidence == 0.9


def test_duplicate_removal(extractor):
    text = "3+ years Python. Also requires 3+ years Python."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 3
    assert res[0].domain == "Python"


def test_ignore_ambiguous_seniority(extractor):
    # Extractor should completely ignore "Senior Engineer" and only pick up deterministic ranges
    text = "Senior Engineer. 5 years Python."
    res = extractor.extract(_build_context(text))
    
    assert len(res) == 1
    assert res[0].min_years == 5
    assert res[0].domain == "Python"


def test_empty_jd(extractor):
    res = extractor.extract(_build_context(""))
    assert len(res) == 0
