from abc import ABC, abstractmethod
from typing import Any
from app.ai.nlp.schemas.processing_context import ProcessingContext


class EntityExtractor(ABC):
    """
    Abstract base class for all domain entity extractors.
    Each extractor operates purely on the provided ProcessingContext.
    """

    @property
    @abstractmethod
    def domain(self) -> str:
        """
        The domain name for this extractor, which maps directly 
        to a field name in the ExtractedEntities schema.
        Example: 'skills', 'education', 'contact'
        """
        pass

    @abstractmethod
    def extract(self, context: ProcessingContext) -> Any:
        """
        Extract structured entities from the given processing context.
        """
        pass


from app.ai.nlp.schemas.extracted_entities import ExtractedEntities


class ExtractorRegistry:
    """
    Registry for EntityExtractors to support a plugin-based architecture.
    """
    def __init__(self) -> None:
        self._extractors: list[EntityExtractor] = []
        self._registered_domains: set[str] = set()
        # Valid domains are the fields defined on the ExtractedEntities output schema
        self._valid_domains: set[str] = set(ExtractedEntities.model_fields.keys())

    def register(self, extractor: EntityExtractor) -> None:
        """Register an instantiated extractor."""
        domain = extractor.domain

        if domain not in self._valid_domains:
            raise ValueError(f"Cannot register extractor with unknown domain: '{domain}'. Valid domains: {self._valid_domains}")

        if domain in self._registered_domains:
            raise ValueError(f"Cannot register multiple extractors for the same domain: '{domain}'")

        self._extractors.append(extractor)
        self._registered_domains.add(domain)

    def get_all(self) -> list[EntityExtractor]:
        """Return all registered extractors."""
        return list(self._extractors)
