from pydantic import BaseModel, ConfigDict
from app.ai.nlp.schemas.education_schema import EducationRecord
from app.ai.nlp.schemas.certification_schema import CertificationRecord


class EducationProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    highest_qualification: str | None = None
    latest_institution: str | None = None
    is_currently_studying: bool = False
    degrees: list[EducationRecord]
    certifications: list[CertificationRecord]
