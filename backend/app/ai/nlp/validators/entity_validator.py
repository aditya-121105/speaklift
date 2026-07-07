from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator, T
from app.ai.nlp.validators.duplicate import DuplicateValidator
from app.ai.nlp.validators.chronology import ChronologyValidator
from app.ai.nlp.validators.confidence import ConfidenceValidator
from app.ai.nlp.validators.url import URLValidator


class EntityValidator:
    """
    Orchestrator for all entity validators.
    Applies the validation rules sequentially to the ExtractedEntities object.
    """

    def __init__(self, validators: list[Validator] | None = None):
        if validators is None:
            self.validators = [
                DuplicateValidator(),
                ChronologyValidator(),
                ConfidenceValidator(),
                URLValidator()
            ]
        else:
            self.validators = validators

    def validate_entities(self, entities: T) -> T:
        """
        Runs the full suite of validators over the entities in sequence.
        """
        current_entities = entities
        for validator in self.validators:
            current_entities = validator.validate(current_entities)
        return current_entities
