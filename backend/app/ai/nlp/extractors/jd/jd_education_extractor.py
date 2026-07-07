import re
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.jd.jd_education_schema import JDEducationRecord


class JDEducationExtractor(EntityExtractor):
    """
    Extracts explicit education requirements from a Job Description.
    """

    DEGREE_MAPPING = {
        r"(?i)\b(bachelors?|bs|bsc|ba|b\.?e\.?|b\.?tech|bca|bba)\b": "BACHELOR",
        r"(?i)\b(masters?|ms|msc|ma|m\.?e\.?|m\.?tech|mca|mba)\b": "MASTER",
        r"(?i)\b(phd|doctorate|doctor\s+of\s+philosophy)\b": "PHD"
    }

    @property
    def domain(self) -> str:
        return "education"

    def extract(self, context: ProcessingContext) -> list[JDEducationRecord]:
        text = context.document.cleaned_text
        
        # If it says equivalent experience explicitly overrules, we still just extract the degree
        # "Bachelor's degree or equivalent practical experience" -> Extract BACHELOR
        # "Equivalent practical experience" without degree -> Nothing to extract.
        
        extracted_dict = {}
        
        # We search within sentences to extract field of study cleanly
        sentences = context.processed_document.sentences
        if not sentences:
            # Fallback to simple split if processed_document lacks sentences
            sentences = re.split(r'[\.\n]+', text)
            
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            for pattern_str, canonical_degree in self.DEGREE_MAPPING.items():
                match = re.search(pattern_str, sentence)
                if match:
                    # e.g., "Bachelor's degree in Computer Science" or "Bachelor of Science in IT"
                    field_match = re.search(rf"{pattern_str}(?:\'s)?\s*(?:degree)?\s*(?:of\s+[a-zA-Z]+\s*)?\s*(?:in)\s+([a-zA-Z\s]+?)(?=\b(?:or|and)\b|,|\.|$)", sentence, flags=re.IGNORECASE)
                    if not field_match:
                        field_match = re.search(rf"{pattern_str}.*?(?:in|of)\s+([a-zA-Z\s]+?)(?=\b(?:or|and)\b|,|\.|$)", sentence, flags=re.IGNORECASE)
                    field_of_study = None
                    if field_match:
                        # The captured group is group 2 because group 1 is the degree
                        field_str = field_match.group(2).strip()
                        # Limit length to avoid capturing whole paragraphs
                        words = field_str.split()
                        if 1 <= len(words) <= 5:
                            field_of_study = field_str
                            
                    # Determine confidence based on section
                    confidence = 0.8
                    if self._is_in_education_section(sentence, context):
                        confidence = 1.0
                    elif field_of_study:
                        confidence = 0.9
                        
                    key = (canonical_degree, field_of_study)
                    if key not in extracted_dict or confidence > extracted_dict[key].confidence:
                        extracted_dict[key] = JDEducationRecord(
                            min_degree_level=canonical_degree,
                            field_of_study=field_of_study,
                            confidence=confidence
                        )
                        
        unique_records = list(extracted_dict.values())
        return [r for r in unique_records if r.confidence >= 0.7]
        
    def _is_in_education_section(self, sentence: str, context: ProcessingContext) -> bool:
        if not context.document.sections:
            return False
            
        for sec in context.document.sections.values():
            if sec.section_type.value in ("education", "requirements"):
                if sentence in sec.content:
                    return True
        return False
