import re
from pathlib import Path

from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.jd.jd_skill_schema import JDSkillRecord, RequirementTier
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class JDSkillExtractor(EntityExtractor):
    """
    Extracts skill requirements from a Job Description.
    Determines RequirementTier deterministically from linguistic cues and section context.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)

    @property
    def domain(self) -> str:
        return "skills"

    def extract(self, context: ProcessingContext) -> list[JDSkillRecord]:
        candidates = set()
        
        # Collect candidates
        for token in context.processed_document.tokens:
            candidates.add(token.strip().lower())
        for lemma in context.processed_document.lemmas:
            candidates.add(lemma.strip().lower())
        for chunk in context.processed_document.noun_chunks:
            candidates.add(chunk.strip().lower())
        for ent in context.processed_document.named_entities:
            candidates.add(ent.text.strip().lower())

        # Clean candidates
        candidates = {c for c in candidates if len(c) > 1 or c in ("c", "g")}

        extracted_skills: dict[str, JDSkillRecord] = {}
        
        sections = context.document.sections
        content_dict = {sec_type: sec for sec_type, sec in sections.items()} if sections else {}
        
        for candidate in candidates:
            matched_synonym = False
            for pattern_str, normalized_name in self._synonyms.items():
                if re.search(pattern_str, candidate, flags=re.IGNORECASE):
                    matched_synonym = True
                    self._add_skill_entry(
                        normalized_name=normalized_name,
                        candidate=candidate,
                        context=context,
                        content_dict=content_dict,
                        extracted_skills=extracted_skills,
                        is_synonym=True
                    )
                    break
            
            if matched_synonym:
                continue

            if candidate in self._taxonomy:
                normalized_name, _ = self._taxonomy[candidate]
                self._add_skill_entry(
                    normalized_name=normalized_name,
                    candidate=candidate,
                    context=context,
                    content_dict=content_dict,
                    extracted_skills=extracted_skills,
                    is_synonym=False
                )

        return list(extracted_skills.values())

    def _add_skill_entry(
        self,
        normalized_name: str,
        candidate: str,
        context: ProcessingContext,
        content_dict: dict,
        extracted_skills: dict[str, JDSkillRecord],
        is_synonym: bool
    ) -> None:
        # Find highest confidence match across text
        escaped_candidate = re.escape(candidate)
        pattern = rf"(?<!\w){escaped_candidate}(?!\w)"

        best_tier = RequirementTier.UNKNOWN
        best_confidence = 0.0

        # Try to find match in sections first
        found = False
        for section_type, sec in content_dict.items():
            match = re.search(pattern, sec.content, flags=re.IGNORECASE)
            if match:
                found = True
                # Get surrounding sentence to check linguistic cues
                sentence = self._get_sentence_containing(sec.content, match.start())
                
                tier = self._determine_tier(sentence, sec.section_type.value, sec.heading)
                confidence = self._calculate_confidence(candidate, normalized_name, is_synonym)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_tier = tier

        if not found:
            # Fallback to general text
            match = re.search(pattern, context.document.cleaned_text, flags=re.IGNORECASE)
            if match:
                sentence = self._get_sentence_containing(context.document.cleaned_text, match.start())
                tier = self._determine_tier(sentence, "other", "")
                confidence = self._calculate_confidence(candidate, normalized_name, is_synonym)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_tier = tier

        # Discard low-confidence candidates (< 0.5)
        if best_confidence < 0.5:
            return

        # If already extracted, keep the one with higher confidence, or stronger tier
        if normalized_name in extracted_skills:
            existing = extracted_skills[normalized_name]
            
            # Tier priority: REQUIRED > PREFERRED > OPTIONAL > UNKNOWN
            tier_priority = {
                RequirementTier.REQUIRED: 4,
                RequirementTier.PREFERRED: 3,
                RequirementTier.OPTIONAL: 2,
                RequirementTier.UNKNOWN: 1
            }
            
            replace = False
            if best_confidence > existing.confidence:
                replace = True
            elif best_confidence == existing.confidence and tier_priority[best_tier] > tier_priority[existing.requirement_tier]:
                replace = True
                
            if replace:
                extracted_skills[normalized_name] = JDSkillRecord(
                    name=normalized_name,
                    requirement_tier=best_tier,
                    confidence=best_confidence
                )
        else:
            if best_confidence > 0.0:
                extracted_skills[normalized_name] = JDSkillRecord(
                    name=normalized_name,
                    requirement_tier=best_tier,
                    confidence=best_confidence
                )

    def _get_sentence_containing(self, text: str, index: int) -> str:
        # Simple sentence extraction using punctuation boundaries
        start = text.rfind(".", 0, index)
        if start == -1:
            start = text.rfind("\n", 0, index)
            if start == -1:
                start = 0
            else:
                start += 1
        else:
            start += 1
            
        end = text.find(".", index)
        if end == -1:
            end = text.find("\n", index)
            if end == -1:
                end = len(text)
                
        return text[start:end].strip()

    def _determine_tier(self, sentence: str, section_type: str, heading: str) -> RequirementTier:
        # 1. Linguistic cues (Highest priority)
        required_patterns = r"(?i)\b(must(\s+have)?|required|minimum|essential|needs?|mandatory|prerequisite)\b"
        preferred_patterns = r"(?i)\b(preferred|ideally|strongly\s+desired|desired|advantage(ous)?|plus)\b"
        optional_patterns = r"(?i)\b(nice\s+to\s+have|bonus|optional|good\s+to\s+have)\b"

        if re.search(required_patterns, sentence):
            return RequirementTier.REQUIRED
        if re.search(preferred_patterns, sentence):
            return RequirementTier.PREFERRED
        if re.search(optional_patterns, sentence):
            return RequirementTier.OPTIONAL

        # 2. Section heading cues
        if re.search(preferred_patterns, heading):
            return RequirementTier.PREFERRED
        if re.search(optional_patterns, heading):
            return RequirementTier.OPTIONAL
        
        # 3. Section type rules
        if section_type == "requirements":
            return RequirementTier.REQUIRED
        
        # Ambiguous
        return RequirementTier.UNKNOWN

    def _calculate_confidence(self, candidate: str, normalized_name: str, is_synonym: bool) -> float:
        # Exact taxonomy match -> highest confidence
        if not is_synonym and candidate.lower() == normalized_name.lower():
            return 1.0
        
        # Synonym match -> slightly lower
        if is_synonym:
            return 0.9
            
        # Lemma/chunk matching variations -> lower
        return 0.8
