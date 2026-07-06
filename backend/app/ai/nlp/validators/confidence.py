from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator


class ConfidenceValidator(Validator):
    """
    Clamps confidence values to be strictly within the [0.0, 1.0] range.
    """

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def validate(self, entities: ExtractedEntities) -> ExtractedEntities:
        skills = [s.model_copy(update={"confidence": self._clamp(s.confidence)}) for s in entities.skills.skills]
        tech = [t.model_copy(update={"confidence": self._clamp(t.confidence)}) for t in entities.skills.technologies]
        
        education = [e.model_copy(update={"confidence": self._clamp(e.confidence)}) for e in entities.education]
        experience = [e.model_copy(update={"confidence": self._clamp(e.confidence)}) for e in entities.experience]
        projects = [p.model_copy(update={"confidence": self._clamp(p.confidence)}) for p in entities.projects]
        certifications = [c.model_copy(update={"confidence": self._clamp(c.confidence)}) for c in entities.certifications]

        new_skills = entities.skills.model_copy(update={"skills": skills, "technologies": tech})
        
        return entities.model_copy(update={
            "skills": new_skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications
        })
