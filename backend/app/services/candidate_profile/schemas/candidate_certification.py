from pydantic import BaseModel, ConfigDict

class CandidateCertification(BaseModel):
    """A single certification entry mapped into the business domain."""
    model_config = ConfigDict(frozen=True)

    name: str
    issuing_organization: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None
