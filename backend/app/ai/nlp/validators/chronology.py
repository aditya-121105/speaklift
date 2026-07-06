import re
from datetime import datetime

from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator


class ChronologyValidator(Validator):
    """
    Validates the chronological correctness of dates in education and experience.
    Rejects (removes) entries with impossible date ranges.
    """

    def _extract_year(self, date_str: str) -> int | None:
        match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if match:
            return int(match.group(0))
        return None

    def _is_valid_range(self, start: str | None, end: str | None) -> bool:
        if not start or not end or end.lower().strip() in ('present', 'current', 'now'):
            return True
            
        start_year = self._extract_year(start)
        end_year = self._extract_year(end)
        
        if start_year and end_year:
            return start_year <= end_year
            
        return True

    def validate(self, entities: ExtractedEntities) -> ExtractedEntities:
        valid_education = []
        for ed in entities.education:
            if ed.start_year and ed.graduation_year:
                if ed.start_year > ed.graduation_year:
                    continue  # Reject impossible year range
            valid_education.append(ed)

        valid_experience = []
        for ex in entities.experience:
            if not self._is_valid_range(ex.start_date, ex.end_date):
                continue
            valid_experience.append(ex)

        return entities.model_copy(update={
            "education": valid_education,
            "experience": valid_experience
        })
