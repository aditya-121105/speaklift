from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator


class DuplicateValidator(Validator):
    """
    Removes duplicate skills, projects, and certifications based on their normalized names.
    """

    def validate(self, entities: ExtractedEntities) -> ExtractedEntities:
        seen_skills = set()
        unique_skills = []
        for s in entities.skills.skills:
            key = s.normalized_name.lower()
            if key not in seen_skills:
                seen_skills.add(key)
                unique_skills.append(s)

        seen_tech = set()
        unique_tech = []
        for t in entities.skills.technologies:
            key = t.normalized_name.lower()
            if key not in seen_tech:
                seen_tech.add(key)
                unique_tech.append(t)
                
        seen_projects = set()
        unique_projects = []
        for p in entities.projects:
            key = (p.normalized_name or p.name or "").lower()
            if key and key not in seen_projects:
                seen_projects.add(key)
                unique_projects.append(p)
            elif not key:
                unique_projects.append(p)
                
        seen_certs = set()
        unique_certs = []
        for c in entities.certifications:
            key = (c.normalized_name or c.name or "").lower()
            if key and key not in seen_certs:
                seen_certs.add(key)
                unique_certs.append(c)
            elif not key:
                unique_certs.append(c)

        new_skills = entities.skills.model_copy(update={
            "skills": unique_skills, 
            "technologies": unique_tech
        })

        return entities.model_copy(update={
            "skills": new_skills,
            "projects": unique_projects,
            "certifications": unique_certs
        })
