from app.ai.document_processing.schemas import DocumentContent
from app.ai.nlp.pipeline import NLPPipeline
from app.ai.nlp.processors.spacy_processor import SpacyProcessor
from app.ai.nlp.processors.normalizer import Normalizer
from app.ai.nlp.extractors.base import ExtractorRegistry, EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext


class DummySkillExtractor(EntityExtractor):
    @property
    def domain(self) -> str:
        return "skills"

    def extract(self, context: ProcessingContext):
        from app.ai.nlp.schemas.skill_schema import SkillSet
        return SkillSet(skills=[], technologies=[])


def test_nlp_pipeline_empty_registry():
    processor = SpacyProcessor()
    normalizer = Normalizer()
    registry = ExtractorRegistry()
    
    pipeline = NLPPipeline(processor, normalizer, registry)
    
    doc = DocumentContent(
        raw_text="Test Document",
        cleaned_text="Test Document",
        source_filename="test.pdf"
    )
    
    result = pipeline.run(doc)
    
    assert result.source_filename == "test.pdf"
    assert result.pipeline_version == "C.4.2"
    assert result.processing_time_ms >= 0
    assert result.document_language == "en"
    
    # Assert defaults were correctly instantiated
    assert result.contact.email is None
    assert len(result.skills.skills) == 0
    assert len(result.education) == 0


def test_nlp_pipeline_with_plugin():
    processor = SpacyProcessor()
    normalizer = Normalizer()
    registry = ExtractorRegistry()
    
    registry.register(DummySkillExtractor())
    
    pipeline = NLPPipeline(processor, normalizer, registry)
    
    doc = DocumentContent(
        raw_text="Test Document",
        cleaned_text="Test Document",
        source_filename="test.pdf"
    )
    
    result = pipeline.run(doc)
    
    assert result.skills is not None
