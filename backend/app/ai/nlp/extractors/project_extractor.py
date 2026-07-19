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
        project_sections = self._find_project_sections(context)

        for text in project_sections:
            record = self._parse_project(text)
            if record:
                projects.append(record)

        return projects

    def _find_project_sections(self, context: ProcessingContext) -> list[str]:
        sections = []
        if 'projects' in context.document.sections:
            sections.append(context.document.sections['projects'].content)
            
        if not sections:
            return []

        # If we found a block, try to split it into individual projects
        project_texts = []
        for section in sections:
            # Better splitting: look for dates or bolded headers
            # Fallback splitting by double newline or bullet lists
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
        summary, achievements = self._extract_description(text, name)
        
        confidence = 0.5
        if summary: confidence += 0.2
        if technologies: confidence += 0.2
        if start_date: confidence += 0.1
        
        confidence = min(1.0, confidence)
        
        return ProjectRecord(
            name=name,
            summary=summary,
            achievements=achievements,
            description=summary,
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

    def _extract_description(self, text: str, name: str) -> tuple[str | None, list[str]]:
        lines = text.split('\n')
        summary_lines = []
        achievements = []
        name_found = False
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            if name.lower() in line_str.lower() and not name_found:
                name_found = True
                # The line might contain name + description
                desc_part = re.sub(r'^.*?[-|–:]\s*', '', line_str, count=1)
                if desc_part and desc_part.lower() != name.lower() and len(desc_part) > 10:
                    summary_lines.append(desc_part)
            else:
                if re.match(r'^[-•*]', line_str):
                    achievements.append(re.sub(r'^[-•*]\s*', '', line_str))
                elif line_str.lower() not in ('technologies:', 'skills:', 'tools:'):
                    summary_lines.append(line_str)
                
        summary = ' '.join(summary_lines).strip() if summary_lines else None
        return summary, achievements
