from pydantic import BaseModel, ConfigDict
from .candidate_project import CandidateProject
from .candidate_certification import CandidateCertification

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
    projects: list[CandidateProject]
    certifications: list[CandidateCertification]
    metadata: ProfileMetadata
