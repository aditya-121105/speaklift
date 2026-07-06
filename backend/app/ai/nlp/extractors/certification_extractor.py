import re
from pathlib import Path
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.certification_schema import CertificationRecord
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class CertificationExtractor(EntityExtractor):
    """
    Extracts certification records.
    Reuses taxonomy dictionaries from shared TaxonomyResourceManager.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)

    @property
    def domain(self) -> str:
        return "certifications"

    def extract(self, context: ProcessingContext) -> list[CertificationRecord]:
        certifications = []
        cert_sections = self._find_certification_sections(context.document.raw_text)

        for text in cert_sections:
            record = self._parse_certification(text)
            if record:
                certifications.append(record)

        return certifications

    def _find_certification_sections(self, text: str) -> list[str]:
        lines = text.split('\n')
        sections = []
        in_certs = False
        current_section = []
        
        heading_pattern = re.compile(r'^(?:[A-Z][a-z]+(?:[ \t]+(?:&|and|[A-Z][a-z]+))*)[ \t]*(?:\:|\s*-)?\s*$')

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_section:
                    current_section.append(line)
                continue
            
            if len(stripped) < 40 and (stripped.isupper() or heading_pattern.match(stripped)):
                if re.search(r'\b(certifications?|licenses?|credentials?)\b', stripped, re.IGNORECASE):
                    in_certs = True
                    current_section = []
                    continue
                elif in_certs:
                    if re.search(r'\b(education|experience|skills|projects?|summary|contact|profile|work|employment|languages)\b', stripped, re.IGNORECASE):
                        if current_section:
                            sections.append('\n'.join(current_section).strip())
                            current_section = []
                        in_certs = False
            
            if in_certs:
                current_section.append(line)
                
        if current_section:
            sections.append('\n'.join(current_section).strip())

        cert_texts = []
        for section in sections:
            parts = re.split(r'\n\s*\n', section)
            for part in parts:
                if part.strip():
                    cert_texts.append(part.strip())

        return cert_texts

    def _parse_certification(self, text: str) -> CertificationRecord | None:
        if not text.strip():
            return None
            
        name = self._extract_name(text)
        if not name:
            return None
            
        issuer = self._extract_issuer(text, name)
        issue_date, expiry_date = self._extract_dates(text)
        credential_id = self._extract_credential_id(text)
        credential_url = self._extract_url(text)
        
        confidence = 0.5
        if issuer: confidence += 0.2
        if issue_date: confidence += 0.1
        if credential_id: confidence += 0.2
        
        confidence = min(1.0, confidence)
        
        # Determine normalized name from taxonomy if possible
        normalized_name = name.strip()
        name_lower = normalized_name.lower()
        if name_lower in self._taxonomy:
            normalized_name = self._taxonomy[name_lower][0]
        else:
            for pattern_str, normalized in self._synonyms.items():
                if re.search(pattern_str, name, flags=re.IGNORECASE):
                    normalized_name = normalized
                    break
        
        return CertificationRecord(
            name=name,
            issuing_organization=issuer,
            issue_date=issue_date,
            expiry_date=expiry_date,
            credential_id=credential_id,
            credential_url=credential_url,
            confidence=confidence,
            raw_text=text,
            normalized_name=normalized_name
        )

    def _extract_name(self, text: str) -> str | None:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = re.sub(r'^[-•*]\s*', '', line)
            
            match = re.match(r'^([^|–\-:(]+)', line)
            if match:
                name = match.group(1).strip()
                # Exclude if it looks like a date or common word
                if 2 < len(name) < 100 and not re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', name, re.IGNORECASE):
                    return name
            
            if 2 < len(line) < 100:
                return line
                
        return None

    def _extract_issuer(self, text: str, name: str) -> str | None:
        # Common issuers
        issuers = ['AWS', 'Amazon Web Services', 'Microsoft', 'Google', 'Cisco', 'CompTIA', 'Oracle', 'IBM', 'Coursera', 'Udemy', 'edX']
        
        # Look for "Issued by X"
        match = re.search(r'(?:Issued by|Issuer|Authority)[\s:]*([A-Za-z0-9\s.,]+)', text, re.IGNORECASE)
        if match:
            # Clean up the match (stop at newline)
            return match.group(1).split('\n')[0].strip()

        for issuer in issuers:
            if re.search(rf'\b{re.escape(issuer)}\b', text, re.IGNORECASE):
                # Don't return issuer if it's identical to name (e.g. they just listed "AWS")
                if issuer.lower() not in name.lower() or len(name) > len(issuer) + 5:
                    return issuer
                    
        return None

    def _extract_dates(self, text: str) -> tuple[str | None, str | None]:
        # Issue Date
        issue_match = re.search(r'(?:Issued|Earned|Date|Obtained)[\s:]*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}-\d{2}|\d{2}/\d{4}|\d{4})', text, re.IGNORECASE)
        issue_date = issue_match.group(1).strip() if issue_match else None
        
        # Expiry Date
        expiry_match = re.search(r'(?:Expires|Valid until|Expiration)[\s:]*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}-\d{2}|\d{2}/\d{4}|\d{4})', text, re.IGNORECASE)
        expiry_date = expiry_match.group(1).strip() if expiry_match else None
        
        if not issue_date and not expiry_date:
            # Fallback to finding any date
            pattern = re.compile(r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4})\b', re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                issue_date = matches[0].strip()
                if len(matches) > 1:
                    expiry_date = matches[1].strip()
                    
        return issue_date, expiry_date

    def _extract_credential_id(self, text: str) -> str | None:
        match = re.search(r'(?:Credential ID|Cert(?:ification)? ID|License Number|ID)[\s:]*([A-Za-z0-9-]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
        
    def _extract_url(self, text: str) -> str | None:
        match = re.search(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
