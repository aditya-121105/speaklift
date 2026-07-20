import re
from pathlib import Path
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.skill_schema import SkillSet, SkillEntry
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class SkillExtractor(EntityExtractor):
    """
    Extracts skills from a document using taxonomy matching and synonym normalization.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)
        self._technology_categories = (
            TaxonomyResourceManager.get_technology_categories()
        )

    @property
    def domain(self) -> str:
        return "skills"

    def extract(self, context: ProcessingContext) -> SkillSet:
        # Generate skill candidates from spaCy output
        candidates = set()

        # 1. Add single tokens (alphabetic only) and lemmas
        for token in context.processed_document.tokens:
            candidates.add(token.strip().lower())
        for lemma in context.processed_document.lemmas:
            candidates.add(lemma.strip().lower())

        # 2. Add noun chunks
        for chunk in context.processed_document.noun_chunks:
            candidates.add(chunk.strip().lower())

        # 3. Add named entities
        for ent in context.processed_document.named_entities:
            candidates.add(ent.text.strip().lower())

        # Clean candidates (remove empty, single characters except 'c' and 'g' which are languages/technologies)
        candidates = {c for c in candidates if len(c) > 1 or c in ("c", "g")}

        extracted_skills: dict[
            str, SkillEntry
        ] = {}  # maps normalized_name -> SkillEntry
        sections = context.document.sections
        content_dict = (
            {sec_type: sec.content for sec_type, sec in sections.items()}
            if sections
            else {"other": context.document.cleaned_text}
        )

        # For each candidate, check if it matches a synonym or direct taxonomy name
        for candidate in candidates:
            # A. Check synonyms first
            matched_synonym = False
            for pattern_str, normalized_name in self._synonyms.items():
                if re.search(pattern_str, candidate, flags=re.IGNORECASE):
                    matched_synonym = True
                    _, category = self._taxonomy.get(
                        normalized_name.lower(), (normalized_name, "tools")
                    )
                    self._add_skill_entry(
                        normalized_name=normalized_name,
                        candidate=candidate,
                        category=category,
                        content_dict=content_dict,
                        extracted_skills=extracted_skills,
                    )
                    break

            if matched_synonym:
                continue

            # B. Check direct taxonomy matching
            if candidate in self._taxonomy:
                normalized_name, category = self._taxonomy[candidate]
                self._add_skill_entry(
                    normalized_name=normalized_name,
                    candidate=candidate,
                    category=category,
                    content_dict=content_dict,
                    extracted_skills=extracted_skills,
                )

        # Categorize into skills and technologies
        all_entries = list(extracted_skills.values())
        skills = all_entries
        technologies = [
            entry
            for entry in all_entries
            if entry.category in self._technology_categories
        ]

        return SkillSet(skills=skills, technologies=technologies)

    def _add_skill_entry(
        self,
        normalized_name: str,
        candidate: str,
        category: str,
        content_dict: dict[str, str],
        extracted_skills: dict[str, SkillEntry],
    ) -> None:
        # Search for the candidate in the document sections to find the best match
        escaped_candidate = re.escape(candidate)
        pattern = rf"(?<!\w){escaped_candidate}(?!\w)"

        for section_type, content in content_dict.items():
            match = re.search(pattern, content, flags=re.IGNORECASE)
            if match:
                raw_text = match.group(0)
                confidence = self._calculate_confidence(section_type)

                # If we haven't extracted this skill yet, or if the new match has higher confidence
                if normalized_name not in extracted_skills:
                    extracted_skills[normalized_name] = SkillEntry(
                        normalized_name=normalized_name,
                        raw_text=raw_text,
                        category=category,
                        confidence=confidence,
                        source_section=section_type,
                    )
                else:
                    existing = extracted_skills[normalized_name]
                    if confidence > existing.confidence:
                        extracted_skills[normalized_name] = SkillEntry(
                            normalized_name=normalized_name,
                            raw_text=raw_text,
                            category=category,
                            confidence=confidence,
                            source_section=section_type,
                        )
                return

        # Fallback if not found in any section content (should be rare)
        if normalized_name not in extracted_skills:
            extracted_skills[normalized_name] = SkillEntry(
                normalized_name=normalized_name,
                raw_text=candidate,
                category=category,
                confidence=0.7,
                source_section="other",
            )

    def _calculate_confidence(self, section_type: str) -> float:
        if section_type in ("skills", "technical_skills", "core_competencies"):
            return 1.0
        elif section_type in ("experience", "work_experience", "projects"):
            return 0.9
        else:
            return 0.7
