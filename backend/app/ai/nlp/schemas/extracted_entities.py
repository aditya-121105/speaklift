from pydantic import BaseModel, ConfigDict
from app.ai.nlp.schemas.contact_schema import ContactInfo
from app.ai.nlp.schemas.skill_schema import SkillSet
from app.ai.nlp.schemas.education_schema import EducationRecord
from app.ai.nlp.schemas.experience_schema import ExperienceRecord
from app.ai.nlp.schemas.project_schema import ProjectRecord
from app.ai.nlp.schemas.certification_schema import CertificationRecord


class ExtractedEntities(BaseModel):
    """
    The complete output of the NLP pipeline for one resume document.
    This is the primary contract consumed by business services and ML.
    """
    model_config = ConfigDict(frozen=True)

    contact: ContactInfo
    skills: SkillSet
    education: list[EducationRecord]
    experience: list[ExperienceRecord]
    projects: list[ProjectRecord]
    certifications: list[CertificationRecord]
    source_filename: str
    pipeline_version: str
    processing_time_ms: int
    document_language: str
    model_version: str
