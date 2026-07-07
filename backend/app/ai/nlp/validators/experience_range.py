import logging
from app.ai.nlp.validators.base import Validator, T
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities

logger = logging.getLogger(__name__)

class ExperienceRangeValidator(Validator):
    """
    Validates structural correctness of experience ranges for JD entities.
    Rejects malformed records instead of inferring values.
    """

    MAX_YEARS_ALLOWED = 100

    def validate(self, entities: T) -> T:
        if not isinstance(entities, ExtractedJDEntities):
            return entities

        if not entities.experience:
            return entities

        valid_experience = []
        for exp in entities.experience:
            valid = True

            if exp.min_years is not None and exp.min_years < 0:
                logger.debug(f"Discarding JDExperienceRecord: negative min_years {exp.min_years}")
                valid = False
                
            if exp.max_years is not None and exp.max_years < 0:
                logger.debug(f"Discarding JDExperienceRecord: negative max_years {exp.max_years}")
                valid = False
                
            if exp.min_years is not None and exp.min_years > self.MAX_YEARS_ALLOWED:
                logger.debug(f"Discarding JDExperienceRecord: min_years > {self.MAX_YEARS_ALLOWED}")
                valid = False
                
            if exp.max_years is not None and exp.max_years > self.MAX_YEARS_ALLOWED:
                logger.debug(f"Discarding JDExperienceRecord: max_years > {self.MAX_YEARS_ALLOWED}")
                valid = False
                
            if exp.min_years is not None and exp.max_years is not None:
                if exp.min_years > exp.max_years:
                    logger.debug(f"Discarding JDExperienceRecord: min {exp.min_years} > max {exp.max_years}")
                    valid = False

            if valid:
                valid_experience.append(exp)

        return entities.model_copy(update={"experience": valid_experience})
