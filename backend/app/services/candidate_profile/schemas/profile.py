from pydantic import BaseModel, ConfigDict
from app.ai.nlp.schemas.project_schema import ProjectRecord
from app.ai.nlp.schemas.certification_schema import CertificationRecord

from .identity import IdentityProfile
from .career import CareerProfile
from .education import EducationProfile
from .technology import TechnologyProfile
from .metadata import ProfileMetadata


class CandidateProfile(BaseModel):
    """
    The definitive business aggregate representing a candidate.
    This is an immutable snapshot used by all downstream systems.
    """
    model_config = ConfigDict(frozen=True)

    identity: IdentityProfile
    career: CareerProfile
    education: EducationProfile
    technology: TechnologyProfile
    projects: list[ProjectRecord]
    certifications: list[CertificationRecord]
    metadata: ProfileMetadata
