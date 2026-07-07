from pydantic import BaseModel, ConfigDict
from .identity import JobIdentity
from .requirements import RequirementsProfile
from .technology import TechnologyProfile
from .employment import EmploymentProfile
from .qualification import QualificationProfile
from .company import CompanyProfile
from .metadata import ProfileMetadata

class JobProfile(BaseModel):
    """
    The business aggregate root for a Job Description.
    """
    model_config = ConfigDict(frozen=True)
    identity: JobIdentity
    requirements: RequirementsProfile
    technology: TechnologyProfile
    qualification: QualificationProfile
    employment: EmploymentProfile
    company: CompanyProfile
    metadata: ProfileMetadata
