from pydantic import BaseModel, ConfigDict


class CertificationRecord(BaseModel):
    """A single certification entry."""
    model_config = ConfigDict(frozen=True)

    name: str
    issuing_organization: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None
    confidence: float = 0.0
    raw_text: str
    normalized_name: str | None = None
