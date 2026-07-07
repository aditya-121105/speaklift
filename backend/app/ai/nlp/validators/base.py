from abc import ABC, abstractmethod
from app.ai.nlp.schemas.extracted_entities import ExtractedEntities


from typing import TypeVar, Generic

T = TypeVar('T')

class Validator(ABC, Generic[T]):
    """
    Abstract base class for all entity validators.
    Validators operate on the entities object (Candidate or JD).
    They must be deterministic, stateless, and not perform any text extraction.
    """

    @abstractmethod
    def validate(self, entities: T) -> T:
        """
        Validate the extracted entities and return a potentially modified copy.
        Because entities are frozen, this must return a new instance.
        """
        pass
