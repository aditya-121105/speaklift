import re
from pathlib import Path
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.project_schema import ProjectRecord
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class ProjectExtractor(EntityExtractor):
    """
    Extracts project records and related technologies/skills.
    Reuses taxonomy dictionaries from shared TaxonomyResourceManager.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)
        self._technology_categories = TaxonomyResourceManager.get_technology_categories()

    @property
    def domain(self) -> str:
        return "projects"

    def extract(self, context: ProcessingContext) -> list[ProjectRecord]:
        projects = []
        project_sections = self._find_project_sections(context.document.raw_text)

        for text in project_sections:
            record = self._parse_project(text)
            if record:
                projects.append(record)

        return projects

    def _find_project_sections(self, text: str) -> list[str]:
        # Identify the projects section
        # We look for a "Projects" heading and extract until the next heading
        lines = text.split('\n')
        sections = []
        in_projects = False
        current_section = []
        
        heading_pattern = re.compile(r'^(?:[A-Z][a-z]+(?:[ \t]+[A-Z][a-z&]+)*)[ \t]*(?:\:|\s*-)?\s*$')

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_section:
                    current_section.append(line)
                continue
            
            # Check if it's a heading
            if len(stripped) < 40 and (stripped.isupper() or heading_pattern.match(stripped)):
                if re.search(r'\b(projects?|personal projects?|academic projects?)\b', stripped, re.IGNORECASE):
                    in_projects = True
                    current_section = []
                    continue
                elif in_projects:
                    # Hit a new heading
                    if re.search(r'\b(education|experience|skills|certifications|summary|contact|profile|work|employment|licenses?|languages)\b', stripped, re.IGNORECASE):
                        if current_section:
                            sections.append('\n'.join(current_section).strip())
                            current_section = []
                        in_projects = False
            
            if in_projects:
                current_section.append(line)
                
        if current_section:
            sections.append('\n'.join(current_section).strip())

        # If we found a block, try to split it into individual projects
        project_texts = []
        for section in sections:
            # Fallback splitting by double newline
            parts = re.split(r'\n\s*\n', section)
            for part in parts:
                if part.strip():
                    project_texts.append(part.strip())

        return project_texts

    def _parse_project(self, text: str) -> ProjectRecord | None:
        if not text.strip():
            return None
            
        name = self._extract_name(text)
        if not name:
            return None
            
        start_date, end_date = self._extract_dates(text)
        technologies = self._extract_technologies(text)
        description = self._extract_description(text, name)
        
        confidence = 0.5
        if description: confidence += 0.2
        if technologies: confidence += 0.2
        if start_date: confidence += 0.1
        
        confidence = min(1.0, confidence)
        
        return ProjectRecord(
            name=name,
            description=description,
            technologies=technologies,
            skills=technologies,  # We populate skills with the same list as technologies based on schema
            start_date=start_date,
            end_date=end_date,
            confidence=confidence,
            raw_text=text,
            normalized_name=name.strip()
        )
        
    def _extract_name(self, text: str) -> str | None:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove leading bullets
            line = re.sub(r'^[-•*]\s*', '', line)
            
            # Common pattern: Project Name - Description
            match = re.match(r'^([^|–\-:(]+)', line)
            if match:
                name = match.group(1).strip()
                # Ensure we don't pick up a line that is too long or contains a lot of description
                if 2 < len(name) < 60 and not re.match(r'^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})', name, re.IGNORECASE) and len(name.split()) < 7:
                    return name
            
            # If no separator, just take the first line as name if it's short
            if 2 < len(line) < 60 and not re.match(r'^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})', line, re.IGNORECASE) and len(line.split()) < 7:
                return line
                
        return None

    def _extract_dates(self, text: str) -> tuple[str | None, str | None]:
        pattern = re.compile(
            r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4})\s*(?:-|to|–|—)\s*((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4}|Present|Current)',
            re.IGNORECASE
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
            
        # Single date (e.g. 2022)
        single_pattern = re.compile(r'\b(20\d{2})\b')
        match = single_pattern.search(text)
        if match:
            return match.group(1).strip(), None
            
        return None, None

    def _extract_technologies(self, text: str) -> list[str]:
        techs = set()
        for name, (normalized, category) in self._taxonomy.items():
            pattern = rf"(?<!\w){re.escape(name)}(?!\w)"
            if re.search(pattern, text, flags=re.IGNORECASE):
                techs.add(normalized)
        
        for pattern_str, normalized in self._synonyms.items():
            if re.search(pattern_str, text, flags=re.IGNORECASE):
                techs.add(normalized)
                
        return sorted(list(techs))

    def _extract_description(self, text: str, name: str) -> str | None:
        lines = text.split('\n')
        desc_lines = []
        name_found = False
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            if name.lower() in line_str.lower() and not name_found:
                name_found = True
                # The line might contain name + description
                desc_part = re.sub(r'^.*?[-|–:]\s*', '', line_str, count=1)
                if desc_part and desc_part.lower() != name.lower():
                    desc_lines.append(desc_part)
            else:
                desc_lines.append(line_str)
                
        if not desc_lines:
            return None
            
        return ' '.join(desc_lines)
