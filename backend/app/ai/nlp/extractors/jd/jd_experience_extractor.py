import re
from pathlib import Path
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.jd.jd_experience_schema import JDExperienceRecord
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class JDExperienceExtractor(EntityExtractor):
    """
    Extracts experience requirements from a Job Description.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)

    @property
    def domain(self) -> str:
        return "experience"

    def extract(self, context: ProcessingContext) -> list[JDExperienceRecord]:
        text = context.document.cleaned_text
        
        # Match "2-5 years", "2 to 5 years", "3+ years", "freshers"
        pattern = re.compile(
            r"(?i)\b(\d+)\s*(?:-|to|–|—|and)\s*(\d+)\+?\s*years?\b|"
            r"\b(\d+)\+?\s*years?\b|"
            r"\b(freshers?|recent\s+graduates?)\b"
        )
        
        extracted = []
        
        for match in pattern.finditer(text):
            min_r, max_r, single_y, fresher = match.groups()
            
            min_years = None
            max_years = None
            
            if min_r and max_r:
                min_years = int(min_r)
                max_years = int(max_r)
            elif single_y:
                min_years = int(single_y)
            elif fresher:
                min_years = 0
                max_years = 0
                
            sentence = self._get_sentence_containing(text, match.start())
            
            domains = self._find_domains_in_sentence(sentence)
            
            if not domains:
                # General experience
                extracted.append(JDExperienceRecord(
                    min_years=min_years,
                    max_years=max_years,
                    domain=None,
                    confidence=0.8
                ))
            else:
                for domain, is_synonym in domains:
                    conf = 1.0 if not is_synonym else 0.9
                    extracted.append(JDExperienceRecord(
                        min_years=min_years,
                        max_years=max_years,
                        domain=domain,
                        confidence=conf
                    ))

        # Remove duplicates, keeping highest confidence
        unique_records = {}
        for r in extracted:
            key = (r.min_years, r.max_years, r.domain)
            if key not in unique_records or r.confidence > unique_records[key].confidence:
                unique_records[key] = r

        return list(unique_records.values())

    def _get_sentence_containing(self, text: str, index: int) -> str:
        start = text.rfind(".", 0, index)
        if start == -1:
            start = text.rfind("\n", 0, index)
            start = 0 if start == -1 else start + 1
        else:
            start += 1
            
        end = text.find(".", index)
        if end == -1:
            end = text.find("\n", index)
            end = len(text) if end == -1 else end
                
        return text[start:end].strip()

    def _find_domains_in_sentence(self, sentence: str) -> list[tuple[str, bool]]:
        """
        Returns a list of tuples (normalized_domain_name, is_synonym).
        """
        domains = []
        
        # Check synonyms
        sentence_lower = sentence.lower()
        matched_synonyms = set()
        for pattern_str, normalized_name in self._synonyms.items():
            if re.search(pattern_str, sentence_lower):
                domains.append((normalized_name, True))
                matched_synonyms.add(normalized_name.lower())
                
        # Check explicit taxonomy
        for key, (normalized_name, _) in self._taxonomy.items():
            if normalized_name.lower() in matched_synonyms:
                continue
                
            # Use word boundaries to avoid partial matches
            escaped_key = re.escape(key)
            if re.search(rf"(?<!\w){escaped_key}(?!\w)", sentence_lower):
                domains.append((normalized_name, False))
                
        return domains
