import re
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.jd.jd_responsibility_schema import JDResponsibilityRecord


class JDResponsibilityExtractor(EntityExtractor):
    """
    Extracts responsibilities from a Job Description.
    Extracts from both action-verb phrases and responsibility noun phrases.
    """

    ACTION_VERBS = {
        "design", "build", "develop", "create", "maintain", "architect", "lead", 
        "collaborate", "deploy", "manage", "write", "test", "ensure", "optimize", 
        "implement", "work", "troubleshoot", "participate", "drive", "deliver", 
        "own", "support", "assist", "execute", "monitor", "evaluate", "review",
        "analyze", "plan", "mentor", "guide", "integrate", "translate", "provide",
        "building", "developing", "creating", "maintaining", "architecting", "leading",
        "collaborating", "deploying", "managing", "writing", "testing", "ensuring",
        "optimizing", "implementing", "working", "troubleshooting", "participating",
        "driving", "delivering", "owning", "supporting", "assisting", "executing",
        "monitoring", "evaluating", "reviewing", "analyzing", "planning", "mentoring",
        "guiding", "integrating", "translating", "providing"
    }

    @property
    def domain(self) -> str:
        return "responsibilities"

    def extract(self, context: ProcessingContext) -> list[JDResponsibilityRecord]:
        extracted_dict: dict[str, JDResponsibilityRecord] = {}
        
        # 1. Process structured sections
        if context.document.sections:
            for sec in context.document.sections.values():
                if sec.section_type.value == "responsibilities":
                    self._extract_from_text(sec.content, 1.0, extracted_dict, in_section=True)
                else:
                    self._extract_from_text(sec.content, 0.8, extracted_dict, in_section=False)
        else:
            # No sections detected, parse whole document with lower confidence
            self._extract_from_text(context.document.cleaned_text, 0.8, extracted_dict, in_section=False)
            
        # Deduplicate deterministically, preserving highest confidence
        unique_records = list(extracted_dict.values())
        return [r for r in unique_records if r.confidence >= 0.7]

    def _extract_from_text(
        self, 
        text: str, 
        base_confidence: float, 
        extracted_dict: dict[str, JDResponsibilityRecord],
        in_section: bool
    ) -> None:
        # Split by newlines or bullet points
        lines = re.split(r'\n+', text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_bullet = False
            # Check if it starts with a bullet character or bullet-like string
            if re.match(r'^[\-\*\•\>]\s+', line) or re.match(r'^\d+\.\s+', line):
                is_bullet = True
                # Clean the bullet
                line = re.sub(r'^[\-\*\•\>]\s+', '', line)
                line = re.sub(r'^\d+\.\s+', '', line)
                
            line = line.strip()
            if not line:
                continue
                
            first_word = line.split()[0].lower()
            first_word_cleaned = re.sub(r'[^a-z]', '', first_word)
            
            is_action = first_word_cleaned in self.ACTION_VERBS
            
            if is_action:
                confidence = base_confidence
                self._add_record(line, confidence, extracted_dict)
            elif in_section:
                # If we are explicitly in a RESPONSIBILITIES section, we can extract noun phrases
                # Avoid extracting short skills or experience sentences
                if self._is_valid_noun_phrase(line):
                    confidence = 0.9 # Slightly lower for noun phrases just to differentiate from explicit action verbs
                    self._add_record(line, confidence, extracted_dict)
            elif is_bullet:
                # If it's a bullet outside responsibilities section, we need strong action verb, which failed above.
                # So we discard it to avoid extracting requirements as responsibilities.
                pass

    def _is_valid_noun_phrase(self, line: str) -> bool:
        # Exclude experience requirements
        if re.search(r'\b(years?|experience|freshers?|graduates?)\b', line, re.IGNORECASE):
            return False
        # Exclude pure technical skills (usually short)
        words = line.split()
        if len(words) < 2:
            return False
        # If it's just a list of technologies like "Python, Django, AWS", skip
        if ',' in line and not any(w.lower() in ("design", "architecture", "support", "maintenance", "ownership", "optimization", "response", "assurance") for w in words):
             # heuristic: if no responsibility-like nouns, it might be a skills list
             pass 
        return True
        
    def _add_record(self, description: str, confidence: float, extracted_dict: dict) -> None:
        key = description.lower()
        if key not in extracted_dict or confidence > extracted_dict[key].confidence:
            extracted_dict[key] = JDResponsibilityRecord(
                description=description,
                confidence=confidence
            )
