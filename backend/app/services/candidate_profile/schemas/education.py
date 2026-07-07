from pydantic import BaseModel, ConfigDict
from .academic_degree import AcademicDegree
from .candidate_certification import CandidateCertification


class EducationProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    highest_qualification: str | None = None
    latest_institution: str | None = None
    is_currently_studying: bool = False
    degrees: list[AcademicDegree]
    certifications: list[CandidateCertification]
