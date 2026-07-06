from abc import ABC, abstractmethod
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities


class Validator(ABC):
    """
    Abstract base class for all entity validators.
    Validators operate on the ExtractedEntities object.
    They must be deterministic, stateless, and not perform any text extraction.
    """

    @abstractmethod
    def validate(self, entities: ExtractedEntities) -> ExtractedEntities:
        """
        Validate the extracted entities and return a potentially modified copy.
        Because ExtractedEntities is frozen, this must return a new instance.
        """
        pass
