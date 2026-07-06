import pytest
from app.ai.nlp.extractors.base import EntityExtractor, ExtractorRegistry
from app.ai.nlp.schemas.processing_context import ProcessingContext


class MockValidExtractor(EntityExtractor):
    @property
    def domain(self) -> str:
        return "skills"  # A valid domain in ExtractedEntities

    def extract(self, context: ProcessingContext) -> str:
        return "mock_result"


class MockInvalidExtractor(EntityExtractor):
    @property
    def domain(self) -> str:
        return "invalid_domain"

    def extract(self, context: ProcessingContext) -> str:
        return "mock_result"


def test_extractor_registry_valid_registration():
    registry = ExtractorRegistry()
    extractor = MockValidExtractor()
    
    assert len(registry.get_all()) == 0
    
    registry.register(extractor)
    
    all_extractors = registry.get_all()
    assert len(all_extractors) == 1
    assert all_extractors[0] is extractor
    assert all_extractors[0].domain == "skills"


def test_extractor_registry_rejects_duplicate_domain():
    registry = ExtractorRegistry()
    extractor1 = MockValidExtractor()
    extractor2 = MockValidExtractor()  # Same domain "skills"
    
    registry.register(extractor1)
    
    with pytest.raises(ValueError, match="Cannot register multiple extractors for the same domain"):
        registry.register(extractor2)


def test_extractor_registry_rejects_unknown_domain():
    registry = ExtractorRegistry()
    invalid_extractor = MockInvalidExtractor()
    
    with pytest.raises(ValueError, match="unknown domain"):
        registry.register(invalid_extractor)

