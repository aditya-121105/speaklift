from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.validators.base import Validator, T


from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities

class DuplicateValidator(Validator):
    """
    Removes duplicate skills, projects, certifications, responsibilities, education, and experience based on their normalized properties.
    """

    def validate(self, entities: T) -> T:
        if isinstance(entities, ExtractedEntities):
            return self._validate_candidate(entities)
        elif isinstance(entities, ExtractedJDEntities):
            return self._validate_jd(entities)
        return entities

    def _validate_candidate(self, entities: ExtractedEntities) -> ExtractedEntities:
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

    def _validate_jd(self, entities: ExtractedJDEntities) -> ExtractedJDEntities:
        # Deduplicate skills
        seen_skills = set()
        unique_skills = []
        for s in entities.skills:
            key = s.normalized_name.lower()
            if key not in seen_skills:
                seen_skills.add(key)
                unique_skills.append(s)

        # Deduplicate experience
        seen_exp = set()
        unique_exp = []
        for e in entities.experience:
            key = (e.min_years, e.max_years, (e.domain or "").lower())
            if key not in seen_exp:
                seen_exp.add(key)
                unique_exp.append(e)

        # Deduplicate responsibilities
        seen_resp = set()
        unique_resp = []
        for r in entities.responsibilities:
            key = r.description.lower()
            if key not in seen_resp:
                seen_resp.add(key)
                unique_resp.append(r)

        # Deduplicate education
        seen_edu = set()
        unique_edu = []
        for ed in entities.education:
            key = (ed.min_degree_level or "", (ed.field_of_study or "").lower())
            if key not in seen_edu:
                seen_edu.add(key)
                unique_edu.append(ed)

        return entities.model_copy(update={
            "skills": unique_skills,
            "experience": unique_exp,
            "responsibilities": unique_resp,
            "education": unique_edu
        })
