import logging
from app.ai.nlp.validators.base import Validator, T
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.salary_range import SalaryPeriod

logger = logging.getLogger(__name__)

class SalaryRangeValidator(Validator):
    """
    Validates structural correctness of salary ranges for JD entities.
    Rejects malformed ranges instead of correcting them.
    """

    ISO_4217_CURRENCIES = {"USD", "INR", "EUR", "GBP", "AUD", "CAD", "SGD", "JPY"}

    def validate(self, entities: T) -> T:
        if not isinstance(entities, ExtractedJDEntities):
            return entities

        if not entities.employment or not entities.employment.salary:
            return entities

        salary = entities.employment.salary
        valid = True

        if salary.minimum is not None and salary.minimum < 0:
            logger.debug(f"Discarding SalaryRange: negative minimum {salary.minimum}")
            valid = False
        
        if salary.maximum is not None and salary.maximum < 0:
            logger.debug(f"Discarding SalaryRange: negative maximum {salary.maximum}")
            valid = False
            
        if salary.minimum is not None and salary.maximum is not None:
            if salary.minimum > salary.maximum:
                logger.debug(f"Discarding SalaryRange: min {salary.minimum} > max {salary.maximum}")
                valid = False
                
        if salary.currency is not None:
            if salary.currency.upper() not in self.ISO_4217_CURRENCIES:
                logger.debug(f"Discarding SalaryRange: invalid currency {salary.currency}")
                valid = False
                
        if salary.period is not None:
            if not isinstance(salary.period, SalaryPeriod):
                logger.debug(f"Discarding SalaryRange: invalid period {salary.period}")
                valid = False

        if not valid:
            new_employment = entities.employment.model_copy(update={"salary": None})
            return entities.model_copy(update={"employment": new_employment})

        return entities
